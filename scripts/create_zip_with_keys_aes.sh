#!/usr/bin/env bash
set -euo pipefail

# create_zip_with_keys_aes.sh
# Create an AES-256-GCM encrypted tar.gz archive containing the repo copy + your local ./keys directory.
# Run this locally. It does NOT upload anything.
# Usage:
#   ./scripts/create_zip_with_keys_aes.sh --out final_package_with_keys.tar.gz.enc
# The script will prompt you for a passphrase (twice) and will derive a key using PBKDF2.

OUTFILE=""
while (("$#")); do
  case "$1" in
    --out) OUTFILE="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [ -z "$OUTFILE" ]; then
  echo "Usage: $0 --out final_package_with_keys.tar.gz.enc"; exit 1
fi

if [ ! -d "keys" ]; then
  echo "No keys/ directory found in current working directory. Generate keys locally first: ./scripts/generate_keys_local.sh"; exit 1
fi

TMPDIR=$(mktemp -d)
cp -r . "$TMPDIR/repo"
mkdir -p "$TMPDIR/repo/keys"
cp -r keys/* "$TMPDIR/repo/keys/"

pushd "$TMPDIR/repo" >/dev/null

# Prompt for passphrase (twice)
read -s -p "Enter passphrase to encrypt archive: " PASS
echo
read -s -p "Confirm passphrase: " PASS2
echo
if [ "$PASS" != "$PASS2" ]; then
  echo "Passphrases do not match"; popd >/dev/null; rm -rf "$TMPDIR"; exit 1
fi

# Create the tar stream and encrypt with AES-256-GCM using PBKDF2
# PBKDF2 iteration count set high for better resistance; adjust as needed for your CPU
ITER=200000

# Use openssl enc with -pbkdf2 and -iter (OpenSSL >= 1.1.1 required for -pbkdf2 and -iter)
# We pass the passphrase via -pass stdin to avoid leaking it in process list; to do that, we use printf to provide the passphrase.

printf "%s" "$PASS" | tar czf - . | openssl enc -aes-256-gcm -pbkdf2 -iter $ITER -salt -pass stdin -out "$OUTFILE"

# Zero the PASS variables in memory (best-effort)
PASS=''
PASS2=''

popd >/dev/null

# Move output to current working directory
mv "$TMPDIR/repo/$OUTFILE" "$PWD/" 2>/dev/null || true

# If openssl wrote to stdout or different path, ensure OUTFILE is at $PWD
if [ ! -f "$OUTFILE" ]; then
  echo "Encrypted archive not found at expected location. Searching temp dir..."
  find "$TMPDIR" -type f -name "$OUTFILE" -exec mv {} "$PWD/" \;
fi

rm -rf "$TMPDIR"

echo "Created encrypted archive: $OUTFILE"

echo "To decrypt later:"
echo "  openssl enc -d -aes-256-gcm -pbkdf2 -iter $ITER -in $OUTFILE -out final_package_with_keys.tar.gz"
echo "  tar xzf final_package_with_keys.tar.gz"
