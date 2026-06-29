# KMM Release Checklist

## Before release

1. Run `pytest -q`
2. Run `python -m compileall src scripts tests`
3. Run `python scripts/sensitive_scan.py`
4. Verify `README.md` and `README_EN.md` only describe repository-backed behavior
5. Verify `configs/managed_scripts.txt` matches the scripts actually installed by `install.sh`
6. Update `docs/CONTINUOUS_DEVELOPMENT.md`

## Before server cutover

1. Backup the server repository checkout
2. Backup KMM-managed files under the server agent script directory
3. Record current checksums and cron entries
4. Run repository installer in non-interactive mode
5. Run `verify_plugin.sh`
6. Run `gray_validation_suite.py`

## After release

1. Confirm GitHub push completed
2. Confirm server checkout points at the released commit
3. Confirm `docs/CONTINUOUS_DEVELOPMENT.md` reflects the new state
