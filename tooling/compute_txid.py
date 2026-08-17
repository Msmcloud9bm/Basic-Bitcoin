#!/usr/bin/env python3
"""
compute_txid.py
Compute TXID (double SHA256, little-endian) from a raw transaction hex file.
Usage: python3 compute_txid.py signed_tx.hex
"""
import sys, hashlib
if len(sys.argv) < 2:
    print('Usage: compute_txid.py <signed_tx.hex>')
    sys.exit(1)
raw = open(sys.argv[1]).read().strip()
rawb = bytes.fromhex(raw)
h = hashlib.sha256(hashlib.sha256(rawb).digest()).digest()[::-1].hex()
print(h)
