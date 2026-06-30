#!/usr/bin/env python3
"""Check SonarCloud for open issues and exit non-zero if any are found.

Usage:
    python scripts/check_sonarcloud.py

Optional environment variable:
    SONAR_TOKEN — SonarCloud authentication token (required for private projects)

Exit codes:
    0 — no open issues
    1 — open issues found (details printed to stdout)
    2 — API error
"""

from __future__ import annotations

import json
import os
import pathlib
import ssl
import sys
import urllib.error
import urllib.request

PROJECT_KEY = "pyArchimate_pyArchimate"
API_URL = f"https://sonarcloud.io/api/issues/search?componentKeys={PROJECT_KEY}&statuses=OPEN,CONFIRMED&ps=500"

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load_env_file() -> None:
    """Load KEY=VALUE pairs from .env in the repo root into os.environ (no-op if absent)."""
    env_file = _REPO_ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and key not in os.environ:
            os.environ[key] = value


def _fetch_issues() -> dict:
    _load_env_file()
    req = urllib.request.Request(API_URL)
    token = os.environ.get("SONAR_TOKEN")
    if token:
        import base64

        credentials = base64.b64encode(f"{token}:".encode()).decode()
        req.add_header("Authorization", f"Basic {credentials}")
    ssl_context = ssl.create_default_context()
    try:
        import certifi

        ssl_context.load_verify_locations(certifi.where())
    except ImportError:  # noqa: S110
        pass
    with urllib.request.urlopen(req, timeout=30, context=ssl_context) as resp:  # noqa: S310
        return json.loads(resp.read().decode())


def main() -> int:
    try:
        data = _fetch_issues()
    except urllib.error.URLError as exc:
        print(f"ERROR: Could not reach SonarCloud API: {exc}", file=sys.stderr)
        return 2

    issues = data.get("issues", [])
    total = data.get("total", len(issues))

    if total == 0:
        print(f"SonarCloud: no open issues for {PROJECT_KEY}")
        return 0

    print(f"SonarCloud: {total} open issue(s) for {PROJECT_KEY}\n")
    for issue in issues:
        component = issue.get("component", "").replace(f"{PROJECT_KEY}:", "")
        line = issue.get("line", "?")
        rule = issue.get("rule", "?")
        message = issue.get("message", "")
        severity = issue.get("severity", "")
        print(f"  [{severity}] {component}:{line}  {rule}  {message}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
