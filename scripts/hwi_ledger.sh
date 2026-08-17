#!/usr/bin/env bash
set -euo pipefail

# hwi_ledger.sh
# Usage: ./scripts/hwi_ledger.sh unsigned.psbt.base64 signed.psbt.base64
# Signs a PSBT using a Ledger device (if HWI available for Ledger)

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <unsigned_psbt_base64_file> <out_signed_psbt_base64_file>"
  exit 1
fi

INFILE="$1"
OUTFILE="$2"

if [ ! -f "$INFILE" ]; then
  echo "Unsigned PSBT file not found: $INFILE"; exit 1
fi

PSBT_BASE64=$(cat "$INFILE")

# Enumerate devices
hwi enumerate || true

# Use device index 0 or adjust to match your device path
hwi --device-type 0 signtx "$PSBT_BASE64" > "$OUTFILE"

echo "Signed PSBT written to $OUTFILE"
