#!/usr/bin/env bash
set -euo pipefail

# scripts/make_full_package_local.sh
# Create a complete local package containing:
# - built webapp (webapp/dist)
# - your locally-generated keys/ (must exist in working dir)
# - transaction raw hex files for addresses found in keys/
# - docs and scripts from the repository
# The final output is an AES-256-GCM encrypted tarball (or GPG/ZIP if requested).
#
# IMPORTANT: Run this script locally on your machine. It does NOT upload anything.
# It DOES require your keys/ directory to exist locally and will include them in the archive.
# Do NOT run this on an untrusted machine if you plan to include real mainnet keys.
#
# Usage:
#  chmod +x scripts/make_full_package_local.sh
#  ./scripts/make_full_package_local.sh --out final_package_with_keys_and_txs.tar.gz.enc [--method aes|gpg|zip] [--gpg-recipient user@example.com] [--shred]
#
# Examples:
#  ./scripts/make_full_package_local.sh --out final_package_with_keys_and_txs.tar.gz.enc --method aes
#  ./scripts/make_full_package_local.sh --out package.gpg --method gpg --gpg-recipient you@example.com
#  ./scripts/make_full_package_local.sh --out package.zip --method zip --shred

OUTFILE=""
METHOD="aes"
GPG_RECIP=""
SHRED=false

while (("$#")); do
  case "$1" in
    --out) OUTFILE="$2"; shift 2;;
    --method) METHOD="$2"; shift 2;;
    --gpg-recipient) GPG_RECIP="$2"; shift 2;;
    --shred) SHRED=true; shift;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [ -z "$OUTFILE" ]; then
  echo "Usage: $0 --out <outfile> [--method aes|gpg|zip] [--gpg-recipient <recipient>] [--shred]"; exit 1
fi

# Ensure keys/ exists
if [ ! -d "keys" ]; then
  echo "No keys/ directory found in current working directory. Generate your keys locally first: ./scripts/generate_keys_local.sh"; exit 1
fi

# Create a temp workspace
TMPDIR=$(mktemp -d)
REPO_COPY="$TMPDIR/repo"
mkdir -p "$REPO_COPY"

echo "Copying repository files to temporary workspace..."
# Copy relevant files (exclude node_modules, .git)
rsync -a --exclude='node_modules' --exclude='.git' --exclude='webapp/node_modules' --exclude='webapp/dist' ./ "$REPO_COPY/"

# Build the webapp (if node and npm available). If build fails, we'll copy source instead.
if command -v npm >/dev/null 2>&1 && [ -f "webapp/package.json" ]; then
  echo "Building webapp (npm install & npm run build)..."
  pushd webapp >/dev/null
  npm ci --no-audit --no-fund || npm install --no-audit --no-fund
  npm run build
  popd >/dev/null
  echo "Copying built webapp into package..."
  mkdir -p "$REPO_COPY/webapp_dist"
  cp -r webapp/dist/* "$REPO_COPY/webapp_dist/" || true
else
  echo "npm not available or webapp/package.json not found; copying webapp source instead"
fi

# Gather addresses from keys (support keys/address_p2pkh.txt and any file named *.address)
ADDRESS_FILES=()
if [ -f "keys/address_p2pkh.txt" ]; then
  ADDRESS_FILES+=("keys/address_p2pkh.txt")
fi
# any additional address file pattern
for f in keys/*.address keys/*.addr keys/*.txt; do
  if [ -f "$f" ] && [[ ! " ${ADDRESS_FILES[*]} " =~ " $f " ]]; then
    ADDRESS_FILES+=("$f")
  fi
done

ADDRESSES=()
for af in "${ADDRESS_FILES[@]}"; do
  while IFS= read -r line; do
    line_trimmed=$(echo "$line" | tr -d '\r' | awk '{$1=$1;print}')
    [ -n "$line_trimmed" ] && ADDRESSES+=("$line_trimmed")
  done < "$af"
done

# Deduplicate addresses
if [ ${#ADDRESSES[@]} -gt 0 ]; then
  mapfile -t ADDRESSES < <(printf "%s\n" "${ADDRESSES[@]}" | awk '!seen[$0]++')
fi

if [ ${#ADDRESSES[@]} -eq 0 ]; then
  echo "No addresses found in keys/ (expected keys/address_p2pkh.txt or keys/*.address).";
  echo "You can still create an archive with keys only. Proceeding to package without fetching tx hex."
fi

# Prepare transactions dir in repo copy
mkdir -p "$REPO_COPY/transactions"

# Fetch raw transaction hex for each address using Blockstream API (public) or bitcoin-cli if available
# Note: Using public API will leak the address to that API. If privacy is required, use your own node and bitcoin-cli.
for addr in "${ADDRESSES[@]}"; do
  echo "Fetching tx list for address: $addr"
  # get list of txids
  if command -v bitcoin-cli >/dev/null 2>&1; then
    # If the node has the address in wallet this may not list external; prefer blockstream for generic addresses
    true
  fi
  # Use Blockstream API
  set +e
  TXS_JSON=$(curl -sS "https://blockstream.info/api/address/${addr}/txs" )
  set -e
  if [ -z "$TXS_JSON" ]; then
    echo "Warning: failed to fetch tx list for $addr via blockstream API"
    continue
  fi
  TXIDS=$(echo "$TXS_JSON" | jq -r '.[].txid' || true)
  if [ -z "$TXIDS" ]; then
    echo "No transactions found for $addr"
    continue
  fi
  for txid in $TXIDS; do
    outpath="$REPO_COPY/transactions/${txid}.hex"
    if [ -f "$outpath" ]; then
      echo "Already have $txid.hex, skipping"
      continue
    fi
    echo "Fetching raw tx hex for $txid"
    # prefer using local bitcoin-cli if available and node has the tx
    if command -v bitcoin-cli >/dev/null 2>&1; then
      set +e
      RAWHEX=$(bitcoin-cli getrawtransaction "$txid" 0 2>/dev/null || true)
      set -e
    fi
    if [ -z "${RAWHEX-}" ]; then
      # fall back to blockstream API
      RAWHEX=$(curl -sS "https://blockstream.info/api/tx/${txid}/hex" || true)
    fi
    if [ -n "$RAWHEX" ]; then
      echo "$RAWHEX" > "$outpath"
    else
      echo "Failed to fetch raw hex for $txid"
    fi
  done
done

# Final packaging: create tar of the repo copy (includes keys/ and transactions/) and encrypt
pushd "$REPO_COPY" >/dev/null

echo "Preparing encrypted archive ($METHOD) ..."
ITER=200000
case "$METHOD" in
  aes)
    # Prompt for passphrase twice
    read -s -p "Enter passphrase to encrypt archive: " PASS; echo
    read -s -p "Confirm passphrase: " PASS2; echo
    if [ "$PASS" != "$PASS2" ]; then echo "Passphrases do not match"; popd >/dev/null; rm -rf "$TMPDIR"; exit 1; fi
    printf "%s" "$PASS" | tar czf - . | openssl enc -aes-256-gcm -pbkdf2 -iter $ITER -salt -pass stdin -out "$OUTFILE"
    # zero the pass variables
    PASS=''; PASS2=''
    ;;
  gpg)
    if [ -z "$GPG_RECIP" ]; then echo "GPG recipient required for gpg method"; popd >/dev/null; rm -rf "$TMPDIR"; exit 1; fi
    tar czf - . | gpg --encrypt --recipient "$GPG_RECIP" -o "$OUTFILE"
    ;;
  zip)
    ZIPTMP="${TMPDIR}/package_zip_tmp"
    mkdir -p "$ZIPTMP"
    tar czf "$ZIPTMP/package.tar.gz" .
    # interactive zip encryption
    zip -r --encrypt "$OLDPWD/$OUTFILE" .
    ;;
  *) echo "Unknown method: $METHOD"; popd >/dev/null; rm -rf "$TMPDIR"; exit 1;;
esac

popd >/dev/null

# Move output to current working directory if openssl wrote elsewhere
if [ ! -f "$OUTFILE" ]; then
  echo "Encrypted archive not found at expected location. Searching temp dir..."
  find "$TMPDIR" -type f -name "$(basename "$OUTFILE")" -exec mv {} "$PWD/" \; || true
fi

echo "Created encrypted archive: $OUTFILE"

# Optionally shred plaintext keys
if [ "$SHRED" = true ]; then
  echo "Shredding plaintext keys in working directory..."
  if command -v shred >/dev/null 2>&1; then
    shred -u keys/* || true
  else
    rm -f keys/* || true
  fi
  rm -rf keys || true
  echo "Plaintext keys removed from working directory (best-effort)."
fi

# Cleanup
rm -rf "$TMPDIR"

echo "Done. Archive is local. Keep it safe and encrypted."
