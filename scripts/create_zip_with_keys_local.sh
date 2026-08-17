#!/usr/bin/env bash
set -euo pipefail

# create_zip_with_keys_local.sh
# Run this on your machine. It will copy the repository to a temp dir, insert ./keys, and create a ZIP.
# Usage:
#   ./create_zip_with_keys_local.sh --encrypt none|zip|gpg --out final_package_with_keys.zip [--gpg-recipient user@example.com]

ENC="${1-}
"
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 --encrypt none|zip|gpg --out <filename.zip> [--gpg-recipient <recipient>]"
  exit 1
fi

# Simple arg parse
ENCRYPT=none
OUTFILE="final_package_with_keys.zip"
GPG_RECIP=""
while (("$#")); do
  case "$1" in
    --encrypt) ENCRYPT="$2"; shift 2;;
    --out) OUTFILE="$2"; shift 2;;
    --gpg-recipient) GPG_RECIP="$2"; shift 2;;
    *) shift;;
  esac
done

# Check keys exist
if [ ! -d "keys" ]; then
  echo "No keys/ directory found in current dir. Run scripts/generate_keys_local.sh first."; exit 1
fi

TMPDIR=$(mktemp -d)
cp -r . "$TMPDIR/repo"
mkdir -p "$TMPDIR/repo/keys"
cp -r keys/* "$TMPDIR/repo/keys/"

pushd "$TMPDIR/repo" >/dev/null

case "$ENCRYPT" in
  none)
    zip -r "$OUTFILE" .
    ;;
  zip)
    echo "You will be prompted for a password to encrypt the ZIP (use a strong password)."
    zip -r --encrypt "$OUTFILE" .
    ;;
  gpg)
    if [ -z "$GPG_RECIP" ]; then
      echo "GPG recipient not provided. Use --gpg-recipient user@example.com"; exit 1
    fi
    tar czf - . | gpg --encrypt --recipient "$GPG_RECIP" -o "$OUTFILE.gpg"
    OUTFILE="$OUTFILE.gpg"
    ;;
  *)
    echo "Unknown encrypt option: $ENCRYPT"; exit 1;;
esac

mv "$OUTFILE" "$OLDPWD/"
popd >/dev/null
rm -rf "$TMPDIR"

echo "Created $OUTFILE in current directory. Keep it safe."