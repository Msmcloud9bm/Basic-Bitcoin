#!/usr/bin/env bash
set -euo pipefail

# broadcast.sh
if [ $# -lt 1 ]; then
  echo "Usage: $0 signed_tx.hex"
  exit 1
fi
HEXFILE="$1"
if [ ! -f "$HEXFILE" ]; then
  echo "File not found: $HEXFILE"; exit 1
fi
RAWHEX=$(cat "$HEXFILE")
TXID=$(bitcoin-cli sendrawtransaction "$RAWHEX")
echo "Broadcast TXID: $TXID"
