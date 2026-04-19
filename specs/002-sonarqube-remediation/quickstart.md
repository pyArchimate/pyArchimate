# Quickstart: SonarQube Critical Issue Remediation

**Branch**: `002-sonarqube-remediation`

---

## Prerequisites

```bash
# Poetry and Python 3.12 must be installed
poetry install

# Java runtime required for local SonarCloud scan
sudo apt-get install -y default-jre

# SONAR_TOKEN must be set (value in project .env — do NOT commit)
export SONAR_TOKEN=<value-from-.env>
```

---

## Run the full pre-push check suite

```bash
bash scripts/pre_push_checks.sh
```

This runs: ruff → pyright → mypy → pytest unit (80% coverage gate) → pytest legacy → pytest integration → behave.

---

## Run unit tests with coverage

```bash
poetry run pytest tests/unit/ --cov=src --cov-report=term-missing
```

---

## Run a specific test file

```bash
poetry run pytest tests/unit/writers/test_archimateWriter.py -v
```

---

## Trigger a local SonarCloud scan

```bash
poetry run pysonar --sonar-token=$SONAR_TOKEN
```

The scan results appear at: https://sonarcloud.io/project/issues?id=pyArchimate_pyArchimate&severities=CRITICAL

---

## Check cognitive complexity of a single file (ruff)

ruff does not report cognitive complexity directly; use the SonarCloud scan or `radon`:

```bash
poetry run radon cc src/pyArchimate/readers/archiReader.py -s -a
```

Complexity grade A–C is acceptable; D–F indicates S3776 risk.

---

## Verify SonarCloud exclusions are applied

After pushing to the branch, open:
```
https://sonarcloud.io/project/issues?id=pyArchimate_pyArchimate&branch=002-sonarqube-remediation
```

Legacy test violations should not appear under CRITICAL issues.

---

## Commit convention

Each fix category is one commit:

```
fix(sonar): exclude legacy tests from sonarcloud analysis
fix(tests): replace identity checks with equality assertions (S5727)
fix(writers): extract duplicate string literal to constant (S1192)
fix(legacy): delete _legacy.py with no live callers (S5754)
fix(bdd): add comment to placeholder step function (S1186)
refactor(element): reduce cognitive complexity below 15 (S3776)
refactor(view): reduce cognitive complexity below 15 (S3776)
refactor(writers): reduce cognitive complexity below 15 (S3776)
refactor(readers): reduce cognitive complexity below 15 (S3776)
```

---

## Validate output fidelity after writer refactoring

```bash
poetry run pytest tests/integration/test_writer_fidelity.py -v
```

This test reads fixture files, writes them back, and compares the canonical XML tree to confirm no output regression.
