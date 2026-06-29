# KMM Rollback

## Repository rollback

1. Identify the last known-good commit.
2. Reset the server checkout to that commit.
3. Reinstall KMM from that checkout.

## Runtime rollback

If a cutover breaks KMM-managed runtime behavior:

1. Restore the backed-up KMM scripts in the server agent script directory
2. Restore any backed-up KMM module directories under the server agent plugin directory
3. Re-run:

```bash
<server-agent-home>/scripts/verify_plugin.sh
python3 <server-agent-home>/scripts/gray_validation_suite.py
```

## Data safety rule

KMM rollback should never delete note data by default.
