#!/usr/bin/env bash
set -euo pipefail

# create_webapp_zip.sh
# Create a distributable ZIP of the webapp. Optionally include a local keys/ directory if present.
# Usage: ./scripts/create_webapp_zip.sh --out webapp_package.zip

OUT="${1-}" 
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 --out <filename.zip>"
  echo "This will NOT create or include any private keys unless you place them in ./keys on your machine.";
fi

# Simple pack
ZIPOUT="webapp_package.zip"
while (("$#")); do
  case "$1" in
    --out) ZIPOUT="$2"; shift 2;;
    *) shift;;
  esac
done

TMPDIR=$(mktemp -d)
cp -r webapp "$TMPDIR/"
# If keys/ exists in repo working dir, include it
if [ -d "keys" ]; then
  mkdir -p "$TMPDIR/webapp/keys"
  cp -r keys/* "$TMPDIR/webapp/keys/"
  echo "Included local keys/ into package (make sure you want this)"
fi

pushd "$TMPDIR" >/dev/null
zip -r "$OLDPWD/$ZIPOUT" webapp
popd >/dev/null
rm -rf "$TMPDIR"

echo "Created $ZIPOUT (contains webapp; includes keys/ only if present in current working dir)"
