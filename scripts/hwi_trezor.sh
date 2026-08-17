#!/usr/bin/env bash
set -euo pipefail

# hwi_trezor.sh
# Usage (signing host, with HWI and a connected Trezor):
#   ./scripts/hwi_trezor.sh unsigned.psbt.base64 signed.psbt.base64
# Signs a PSBT (base64) using the first Trezor device enumerated by HWI.

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

# Enumerate devices and pick the first Trezor (device type detection may vary)
DEVICES=$(hwi enumerate || true)
if [ -z "$DEVICES" ]; then
  echo "No HWI devices found. Ensure your device is connected and HWI is installed."; exit 1
fi

# Use hwi to signtx; many HWI versions accept device index 0 for the first device
# This command will prompt you on the hardware device to confirm the transaction
hwi --device-type 0 signtx "$PSBT_BASE64" > "$OUTFILE"

echo "Signed PSBT written to $OUTFILE"
