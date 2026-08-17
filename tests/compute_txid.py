#!/usr/bin/env python3
# tests/compute_txid.py
# Compute bitcoin txid (double SHA256, little-endian) from a raw tx hex input

import sys
import hashlib

if len(sys.argv) != 2:
    print("Usage: compute_txid.py <raw_tx_hex>")
    sys.exit(2)

hexstr = sys.argv[1].strip()
try:
    tx = bytes.fromhex(hexstr)
except Exception as e:
    print("Invalid hex:", e)
    sys.exit(2)

h = hashlib.sha256(hashlib.sha256(tx).digest()).digest()[::-1]
print(h.hex())
