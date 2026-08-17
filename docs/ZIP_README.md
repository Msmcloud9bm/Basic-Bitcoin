# ZIP_README.md

This file explains the purpose of the prebuilt repo ZIP helper and how to create/download the repository ZIP which excludes secrets (keys/) and large artifacts.

Purpose
- Provide a single ZIP file of the repository containing all non‑secret demo code, webapp source, packaging scripts, README templates, and demos so you can download a single archive and run the local packaging steps.
- The ZIP intentionally excludes keys/, .git, node_modules, webapp/dist, and any existing encrypted archives.

How to create the ZIP locally
1. Make the helper script executable:
   chmod +x scripts/create_repo_zip_no_keys.sh
2. Run the script to produce the ZIP (default name full_repo_no_keys.zip):
   ./scripts/create_repo_zip_no_keys.sh --out full_repo_no_keys.zip
3. The produced ZIP will be in the repository root. You can then copy it to another machine if needed.

Alternative: download the GitHub branch ZIP directly
- Release: https://github.com/Msmcloud9bm/Basic-Bitcoin/archive/refs/heads/mainnet-transaction-demo.zip

Security note
- This ZIP will NOT contain any private keys or wallet files. You must add keys/ locally on the machine where you will create the final encrypted package. Never commit or upload keys/ to GitHub.
