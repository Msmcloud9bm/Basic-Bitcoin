#!/usr/bin/env bash
set -euo pipefail

# scripts/local_packager.sh
# Automates creating a full encrypted package locally that includes your non-secret repo files plus any
# secret files you copy into the staging area. THIS SCRIPT DOES NOT SEND SECRETS TO ANYONE.
# Usage:
#   chmod +x scripts/local_packager.sh
#   ./scripts/local_packager.sh --repo /path/to/repo --out /path/to/out.enc [--encrypt-method aes|gpg|7z] [--upload transfer|s3]
# Examples:
#   ./scripts/local_packager.sh --repo ~/Basic-Bitcoin --out ~/mastermind_package.tar.gz.enc --encrypt-method aes --upload transfer

print_usage() {
  cat <<'USAGE'
local_packager.sh --repo REPO_ROOT --out OUTFILE [--encrypt-method aes|gpg|7z] [--upload transfer|s3]

--repo           Path to the cloned repo containing non-secret files (required)
--out            Path to write the encrypted output file (required)
--encrypt-method Encryption method: aes (AES-GCM symmetric), gpg (PGP recip), 7z (7z passworded). Default: aes
--upload         Optional upload target: transfer (transfer.sh) or s3 (requires AWS CLI configured)
--recipient      When using --encrypt-method gpg, supply recipient identifier (email or keyid)
--bucket         When using --upload s3, supply s3://bucket/path prefix (example: s3://my-bucket/mastermind)

This script stages the repo, copies files from a local secrets directory you provide interactively,
creates a tarball, encrypts it locally, and optionally uploads only the encrypted file.
USAGE
}

# Defaults
ENCRYPT_METHOD="aes"
UPLOAD_METHOD=""
RECIPIENT=""
S3_TARGET=""

# Parse args
if [ "$#" -eq 0 ]; then print_usage; exit 1; fi
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO_ROOT="$2"; shift 2;;
    --out) OUTFILE="$2"; shift 2;;
    --encrypt-method) ENCRYPT_METHOD="$2"; shift 2;;
    --upload) UPLOAD_METHOD="$2"; shift 2;;
    --recipient) RECIPIENT="$2"; shift 2;;
    --bucket) S3_TARGET="$2"; shift 2;;
    --help) print_usage; exit 0;;
    *) echo "Unknown arg: $1"; print_usage; exit 1;;
  esac
done

if [ -z "${REPO_ROOT:-}" ] || [ -z "${OUTFILE:-}" ]; then
  echo "--repo and --out are required"; print_usage; exit 1
fi

STAGING_DIR="$(mktemp -d)"
PLAINTAR="${STAGING_DIR}/mastermind_package.tar.gz"
PASSFILE="${STAGING_DIR}/mastermind_passphrase.txt"
ENCRYPTED_TMP="${STAGING_DIR}/$(basename "$OUTFILE")"

cleanup() {
  rm -rf "$STAGING_DIR"
}
trap cleanup EXIT

echo "Staging repository (excluding .git, node_modules, and existing archives)..."
rsync -a --exclude='.git' --exclude='node_modules' --exclude='*.zip' --exclude='*.tar.gz' --exclude='*.enc' "$REPO_ROOT"/ "$STAGING_DIR/repo/"

# Ask user to copy secrets into staging/repo/keys and staging/repo/transactions
mkdir -p "$STAGING_DIR/repo/keys" "$STAGING_DIR/repo/transactions"
cat <<-MSG

Please copy your secret files into the staging keys folder now (local only).
  - Keys:   $STAGING_DIR/repo/keys/
  - Tx hex: $STAGING_DIR/repo/transactions/

When ready press ENTER to continue, or CTRL-C to abort.
MSG
read -r

# Optional: build webapp if present
if [ -d "$STAGING_DIR/repo/webapp" ] && command -v npm >/dev/null 2>&1; then
  echo "Building webapp (npm ci && npm run build) inside the staging copy..."
  pushd "$STAGING_DIR/repo/webapp" >/dev/null
  npm ci --no-audit --no-fund || true
  npm run build || true
  popd >/dev/null
fi

# Create plaintext tar.gz
echo "Creating plaintext tarball: $PLAINTAR"
tar czf "$PLAINTAR" -C "$STAGING_DIR" repo

# Generate passphrase (AES and 7z use this file). For GPG, passphrase not required.
openssl rand -base64 32 > "$PASSFILE"
chmod 600 "$PASSFILE"
echo "Passphrase generated and saved to: $PASSFILE"

# Encrypt according to method
case "$ENCRYPT_METHOD" in
  aes)
    echo "Encrypting with AES-256-GCM (PBKDF2) -> $OUTFILE"
    openssl enc -aes-256-gcm -pbkdf2 -iter 200000 -salt -pass file:"$PASSFILE" -in "$PLAINTAR" -out "$ENCRYPTED_TMP"
    ;;
  gpg)
    if [ -z "$RECIPIENT" ]; then
      echo "--recipient is required for gpg encryption"; exit 1
    fi
    echo "Encrypting with recipient public key: $RECIPIENT -> $OUTFILE"
    gpg --batch --yes --encrypt --recipient "$RECIPIENT" -o "$ENCRYPTED_TMP" "$PLAINTAR"
    ;;
  7z)
    PASS=$(cat "$PASSFILE")
    echo "Creating 7z encrypted archive -> $OUTFILE"
    7z a -t7z "$ENCRYPTED_TMP" "$STAGING_DIR/repo" -p"$PASS" -mhe=on >/dev/null
    ;;
  *) echo "Unknown encrypt method: $ENCRYPT_METHOD"; exit 1;;
esac

# Move encrypted file to requested OUTFILE
mv "$ENCRYPTED_TMP" "$OUTFILE"

# shred plaintext tar
shred -u "$PLAINTAR" || rm -f "$PLAINTAR"

# checksum
sha256sum "$OUTFILE" | tee "${OUTFILE}.sha256"

# Optional upload
if [ "$UPLOAD_METHOD" = "transfer" ]; then
  echo "Uploading $OUTFILE to transfer.sh (only encrypted file will be uploaded)..."
  URL=$(curl --silent --upload-file "$OUTFILE" "https://transfer.sh/$(basename "$OUTFILE")")
  echo "Upload URL: $URL"
elif [ "$UPLOAD_METHOD" = "s3" ]; then
  if [ -z "$S3_TARGET" ]; then echo "--bucket is required for s3 upload"; exit 1; fi
  echo "Uploading $OUTFILE to S3: $S3_TARGET/$(basename "$OUTFILE")"
  aws s3 cp "$OUTFILE" "$S3_TARGET/$(basename "$OUTFILE")" --acl private
  URL=$(aws s3 presign "$S3_TARGET/$(basename "$OUTFILE")" --expires-in 604800)
  echo "Presigned URL (7 days): $URL"
fi

echo "Package complete. Encrypted file: $OUTFILE"
echo "Checksum: ${OUTFILE}.sha256"
echo "Passphrase file (local): $PASSFILE — share this OOB (Signal/phone/face-to-face)."

exit 0
