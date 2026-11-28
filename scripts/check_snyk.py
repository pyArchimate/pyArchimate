#!/usr/bin/env python3
"""Run `snyk test` against this project's dependencies and exit non-zero on findings.

Usage:
    python scripts/check_snyk.py [--severity-threshold low|medium|high|critical]

Requires the `snyk` CLI on PATH and an authenticated session (`snyk auth`).

Exit codes:
    0 — no vulnerabilities at or above the threshold
    1 — vulnerabilities found (details printed to stdout)
    2 — could not run `snyk test` (not installed, not authenticated, API error, ...)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys


def _run_snyk(severity_threshold: str | None) -> tuple[int, dict | None, str]:
    if shutil.which("snyk") is None:
        return 2, None, "snyk CLI not found on PATH — install it or run `snyk auth` first"

    cmd = ["snyk", "test", "--json", "--package-manager=poetry"]
    if severity_threshold:
        cmd.append(f"--severity-threshold={severity_threshold}")

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)  # noqa: S603

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return 2, None, result.stderr.strip() or result.stdout.strip() or "snyk produced no parseable output"

    # snyk test exits 1 when vulnerabilities are found — that's a successful run, not an error.
    if result.returncode not in (0, 1):
        return 2, data, data.get("error", result.stderr.strip())

    return result.returncode, data, ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--severity-threshold",
        choices=["low", "medium", "high", "critical"],
        default=None,
        help="only fail on vulnerabilities at or above this severity",
    )
    args = ap.parse_args()

    returncode, data, error = _run_snyk(args.severity_threshold)

    if returncode == 2:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    vulns = (data or {}).get("vulnerabilities", [])
    if not vulns:
        print(f"snyk: no known vulnerabilities ({(data or {}).get('dependencyCount', '?')} dependencies checked)")
        return 0

    print(f"snyk: {len(vulns)} known vulnerabilit{'y' if len(vulns) == 1 else 'ies'} found\n")
    for v in vulns:
        severity = v.get("severity", "?")
        package = v.get("packageName", "?")
        version = v.get("version", "?")
        title = v.get("title", "")
        vuln_id = v.get("id", "?")
        print(f"  [{severity}] {package}@{version}  {vuln_id}  {title}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
