#!/usr/bin/env bash
set -euo pipefail

# ci/run_local_tests.sh
# Local test harness that runs python builder example and compute_txid against a deterministic test key (TESTNET/REGTEST only).
# This script is intended to be run locally by developers and CI runners that do not have secrets.

echo "Running local CI tests (test keys only; not mainnet)"

# Requirements: python3, pip install python-bitcoinlib
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found"; exit 1
fi

python3 - <<'PY'
from subprocess import check_call, CalledProcessError
import json, os

# Create test input/output files
inputs = [{
  "txid": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
  "vout": 0
}]
outputs = {"mqdofsXHpePPGBFXuwwypAqCcXi48Xhb2f": 0.0001}

open('ci/inputs.json','w').write(json.dumps(inputs, indent=2))
open('ci/outputs.json','w').write(json.dumps(outputs, indent=2))

# Run the python builder
try:
    check_call(['python3','implementations/python/builder.py','ci/inputs.json','ci/outputs.json','ci/unsigned_tx.hex'])
    print('Builder produced ci/unsigned_tx.hex')
except CalledProcessError as e:
    print('Builder failed', e)
    raise

# Compute txid (should run without error)
from hashlib import sha256
raw = open('ci/unsigned_tx.hex').read().strip()
rawb = bytes.fromhex(raw)
h = sha256(sha256(rawb).digest()).digest()[::-1].hex()
print('Computed TXID (dummy):', h)

print('Local CI tests passed (builder + txid computation).')
PY
