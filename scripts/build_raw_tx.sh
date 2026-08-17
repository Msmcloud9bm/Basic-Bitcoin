#!/usr/bin/env bash
set -euo pipefail

# build_raw_tx.sh
# Simple wrapper around bitcoin-cli createrawtransaction
# Usage: ./build_raw_tx.sh --txid <txid> --vout <vout> --to <address> --amount <btc> [--change <change_addr> --changeamt <btc>]

ARGS=$(getopt -o '' -l txid:,vout:,to:,amount:,change:,changeamt: -- "$@")
if [ $? -ne 0 ]; then
  echo "Invalid arguments"
  exit 1
fi
eval set -- "$ARGS"
while true; do
  case "$1" in
    --txid) TXID="$2"; shift 2;;
    --vout) VOUT="$2"; shift 2;;
    --to) TO="$2"; shift 2;;
    --amount) AMOUNT="$2"; shift 2;;
    --change) CHANGE="$2"; shift 2;;
    --changeamt) CHANGEAMT="$2"; shift 2;;
    --) shift; break;;
  esac
done

if [ -z "${TXID-}" ] || [ -z "${VOUT-}" ] || [ -z "${TO-}" ] || [ -z "${AMOUNT-}" ]; then
  echo "Usage: $0 --txid <txid> --vout <vout> --to <address> --amount <btc> [--change <change_addr> --changeamt <btc>]"
  exit 1
fi

if [ -z "${CHANGE-}" ]; then
  echo "No change address provided; outputs will equal amount (no change)"
  RAW=$(bitcoin-cli createrawtransaction "[{\"txid\":\"$TXID\",\"vout\":$VOUT}]" "{\"$TO\":$AMOUNT}")
else
  RAW=$(bitcoin-cli createrawtransaction "[{\"txid\":\"$TXID\",\"vout\":$VOUT}]" "{\"$TO\":$AMOUNT, \"$CHANGE\":$CHANGEAMT}")
fi

echo "$RAW" > unsigned_tx.hex
echo "Unsigned transaction written to unsigned_tx.hex"
