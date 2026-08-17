#!/usr/bin/env bash
set -euo pipefail

# scripts/create_repo_zip_no_keys.sh
# Create a single ZIP of the repository root excluding secrets and large build artifacts
# Usage:
#   chmod +x scripts/create_repo_zip_no_keys.sh
#   ./scripts/create_repo_zip_no_keys.sh --out full_repo_no_keys.zip
# The script will create the zip in the current working directory.

OUT="full_repo_no_keys.zip"
EXCLUDES=(".git/*" "keys/*" "node_modules/*" "webapp/node_modules/*" "webapp/dist/*" "*.zip" "*.tar.gz" "*.tar.gz.enc" "*.gpg")

while (("$#")); do
  case "$1" in
    --out) OUT="$2"; shift 2;;
    --help) echo "Usage: $0 [--out filename.zip]"; exit 0;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

# Ensure zip is available
if ! command -v zip >/dev/null 2>&1; then
  echo "zip not found in PATH. Install zip (apt/yum/brew) and retry."; exit 1
fi

# Build webapp dist if present and node/npm available (non-fatal)
if [ -f "webapp/package.json" ] && command -v npm >/dev/null 2>&1; then
  echo "Building webapp (npm ci && npm run build) to include a fresh dist in the zip..."
  pushd webapp >/dev/null
  npm ci --no-audit --no-fund || npm install --no-audit --no-fund
  npm run build || true
  popd >/dev/null
fi

# Construct exclude args for zip
EXCL_ARGS=()
for e in "${EXCLUDES[@]}"; do
  EXCL_ARGS+=("-x" "$e")
done

# Create temporary staging dir and copy files (to avoid including the zip in itself)
TMPDIR=$(mktemp -d)
RSYNC_EXCLUDES=("--exclude=.git" "--exclude=keys" "--exclude=node_modules" "--exclude=webapp/node_modules" "--exclude=webapp/dist" "--exclude=*.zip" "--exclude=*.tar.gz" "--exclude=*.tar.gz.enc" "--exclude=*.gpg")

echo "Copying repository files to staging directory: $TMPDIR"
rsync -a "${RSYNC_EXCLUDES[@]}" ./ "$TMPDIR/repo/"

pushd "$TMPDIR/repo" >/dev/null

echo "Creating zip: $OUT"
zip -r "$OLDPWD/$OUT" . ${EXCL_ARGS[@]} >/dev/null

popd >/dev/null
rm -rf "$TMPDIR"

echo "Created $OUT"
