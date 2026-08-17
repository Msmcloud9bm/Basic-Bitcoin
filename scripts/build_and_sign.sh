#!/usr/bin/env bash
set -euo pipefail

# build_and_sign.sh
# Signs an unsigned raw tx (unsigned_tx.hex) using either the wallet or a provided WIF.
# Usage: ./build_and_sign.sh unsigned_tx.hex [--wif-file keys/private_key.wif]

UNSIGNED_FILE="$1"
WIF_FILE=""
if [ "$#" -ge 2 ]; then
  shift
  while (("$#")); do
    case "$1" in
      --wif-file) WIF_FILE="$2"; shift 2;;
      *) shift;;
    esac
  done
fi

if [ ! -f "$UNSIGNED_FILE" ]; then
  echo "Unsigned file not found: $UNSIGNED_FILE"; exit 1
fi
RAWHEX=$(cat "$UNSIGNED_FILE")

if [ -n "$WIF_FILE" ] && [ -f "$WIF_FILE" ]; then
  # Sign with external WIF
  echo "Signing with WIF from $WIF_FILE"
  WIF=$(cat "$WIF_FILE")
  # For signrawtransactionwithkey we need input info; ask user to provide a JSON file inputs.json
  if [ ! -f inputs.json ]; then
    echo "Missing inputs.json describing previous outputs (txid,vout,scriptPubKey,amount). Create inputs.json and re-run."
    exit 1
  fi
  SIGNED_JSON=$(bitcoin-cli signrawtransactionwithkey "$RAWHEX" "[\"$WIF\"]" "$(cat inputs.json)")
  echo "$SIGNED_JSON" > signed.json
  echo "Signed JSON written to signed.json"
  echo "Signed hex:" $(echo "$SIGNED_JSON" | jq -r '.hex') > signed_tx.hex
  echo "signed_tx.hex written"
else
  # Try wallet signing
  echo "Attempting to sign with wallet (signrawtransactionwithwallet)"
  SIGNED_JSON=$(bitcoin-cli -rpcwallet=$(bitcoin-cli getwalletinfo | jq -r '.walletname') signrawtransactionwithwallet "$RAWHEX" 2>/dev/null || bitcoin-cli signrawtransactionwithwallet "$RAWHEX")
  echo "$SIGNED_JSON" > signed.json
  if command -v jq >/dev/null 2>&1; then
    jq -r '.hex' signed.json > signed_tx.hex
  else
    # crude parse
    python3 - <<PY
import json
j=json.load(open('signed.json'))
print(j.get('hex',''))
PY
  fi
  echo "Signed transaction written to signed_tx.hex"
fi

