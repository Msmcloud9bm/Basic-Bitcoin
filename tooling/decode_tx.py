#!/usr/bin/env python3
"""
decode_tx.py
If bitcoin-cli is available, uses decoderawtransaction. Otherwise prints raw hex.
Usage: python3 decode_tx.py signed_tx.hex
"""
import sys, subprocess
if len(sys.argv) < 2:
    print('Usage: decode_tx.py <signed_tx.hex>')
    sys.exit(1)
raw = open(sys.argv[1]).read().strip()
try:
    out = subprocess.check_output(['bitcoin-cli', 'decoderawtransaction', raw], stderr=subprocess.STDOUT)
    print(out.decode())
except Exception as e:
    print('bitcoin-cli decoderawtransaction not available or failed. Raw hex:')
    print(raw)
