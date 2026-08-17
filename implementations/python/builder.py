"""
Python example builder: requires python-bitcoinlib
pip install python-bitcoinlib

Usage: python3 builder.py --inputs inputs.json --outputs outputs.json --out unsigned_tx.hex
"""
import sys, json
from pprint import pprint

try:
    from bitcoin.core import b2x
    from bitcoin.core import lx, COutPoint, CTxIn, CTxOut, CTransaction
    from bitcoin.wallet import CBitcoinAddress
except Exception:
    print("python-bitcoinlib not installed. Install: pip install python-bitcoinlib")
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: builder.py inputs.json outputs.json unsigned_tx.hex")
        sys.exit(1)
    inputs_file = sys.argv[1]
    outputs_file = sys.argv[2]
    out_file = sys.argv[3]
    inputs = json.load(open(inputs_file))
    outputs = json.load(open(outputs_file))

    txins = []
    for i in inputs:
        txid = i['txid']
        vout = int(i['vout'])
        outpoint = COutPoint(lx(txid), vout)
        txins.append(CTxIn(outpoint))

    txouts = []
    for addr, amt in outputs.items():
        addr_obj = CBitcoinAddress(addr)
        value = int(round(amt * 1e8))
        txouts.append(CTxOut(value, addr_obj.to_scriptPubKey()))

    tx = CTransaction(txins, txouts)
    raw = b2x(tx.serialize())
    open(out_file, 'w').write(raw)
    print(f"Wrote unsigned tx to {out_file}")
