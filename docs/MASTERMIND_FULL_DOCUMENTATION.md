# MASTERMIND_FULL_DOCUMENTATION.md

This document is the complete project manual for the "Mastermind" package. It explains architecture, how to build and run demos, how to use the HD & multisig helpers, WebAuthn prototype, packaging & encryption guidance, and emergency procedures.

IMPORTANT: This repo and documentation intentionally exclude all private key material. You MUST add your keys locally and run the packaging scripts on a trusted machine.

Table of contents
- Project overview
- Directory layout
- Building and running the webapp demo
- WebAuthn prototype
- HD & multisig demo
- PSBT and transaction tooling
- Packaging and encryption (local_packager.sh)
- Uploading and sharing encrypted archive
- Emergency key compromise checklist & sweep recipes
- Appendix: useful commands and scripts

Project overview
----------------
The Mastermind package is a demonstration toolkit for offline packaging of wallet artifacts and a set of local demos:
- A static Web UI wallet demo (React) with WebAuthn unlock prototype and HD/multisig helpers.
- Packaging helpers to produce a single encrypted archive containing the webapp build, documentation, keys, and signed transactions.
- Tooling to help compute TXIDs, build PSBTs, and sign via HWI-compatible devices.

Security model
--------------
This project separates non-secret code (committed to GitHub) from secret key material. All secret key handling must occur locally on a trusted machine. The packager scripts are intentionally client-side: they stage secrets locally, create a compressed archive, encrypt it with AES-GCM (or GPG/7z), and produce a checksum.

Directory layout
----------------
- webapp/          React demo and client-side helpers (webauthn, hd_multisig_demo)
- scripts/         packaging scripts (local_packager.sh, create_repo_zip_no_keys.sh)
- docs/            PACKAGE_README.md, HD_MULTISIG.md, ZIP_README.md
- tooling/         helper scripts (txid, psbt examples, HWI snippets)

Building the webapp
-------------------
Prerequisites: node (16+), npm

1. Install dependencies and build:

  cd webapp
  npm ci
  npm run build
  cd ..

2. The built static assets appear in webapp/dist or webapp/build depending on framework. The webapp is purely client-side; you can open index.html in a secure browser profile or serve it via a local static server.

WebAuthn prototype
------------------
Files: webapp/src/webauthn.js, webapp/src/WebAuthnLock.jsx
- The prototype demonstrates registering a platform credential and requesting an assertion to set a session unlock flag.
- Security note: platform authenticator usage is device-specific and not a substitute for hardware wallet signing of transactions.

HD & multisig demo
------------------
Files: webapp/src/hd_multisig_demo.js, docs/HD_MULTISIG.md
- Helpers include mnemonic generation (BIP39), seed -> BIP32 node conversion, deriving native segwit addresses (BIP84), and creating 2-of-3 P2WSH multisig addresses.
- PSBT builder examples demonstrate how to compose a PSBT for P2WPKH inputs using bitcoinjs-lib.
- Always use hardware wallets for xprv or private key storage in production.

PSBT and transaction tooling
---------------------------
See tooling/ for quick scripts to compute TXIDs and manipulate PSBTs. Example included: tests/compute_txid.py which computes the TXID for a given hex.

Packaging and encryption
------------------------
Use scripts/local_packager.sh to create a full encrypted archive locally. The script:
- Stages the repository (non-secret files)
- Lets you copy secret files into the staging keys/ and transactions/ directories
- Builds the webapp (optional)
- Creates a plaintext tar.gz
- Encrypts using AES-256-GCM (PBKDF2) by default, or GPG/7z per options
- Computes SHA256 checksum and optionally uploads the encrypted file to transfer.sh or S3

Local packaging example (AES, transfer.sh):

  chmod +x scripts/local_packager.sh
  ./scripts/local_packager.sh --repo /home/user/Basic-Bitcoin --out /tmp/mastermind_package.tar.gz.enc --encrypt-method aes --upload transfer

The script is interactive: it pauses to let you copy secret files into the staging directory. Do not paste keys into anything online.

Uploading and sharing
---------------------
- Only upload the encrypted file. Never upload the plaintext archive.
- If using symmetric encryption, share the passphrase out of band (Signal/phone/in-person).
- If the recipient has PGP, prefer GPG encryption (script supports --encrypt-method gpg --recipient "email").

Emergency key compromise checklist
---------------------------------
If a private key is exposed (WIF, xprv, or wallet.dat), assume compromise. Immediate steps:
1. Generate a new receiving address on a hardware wallet or air-gapped machine (BIP84 bech32 preferred).
2. Create a high-fee sweep transaction/PSBT spending all compromised UTXOs to the new address.
3. Sign and broadcast immediately — use an aggressive fee to outrun potential attackers.
4. Monitor the mempool for conflicting transactions.
5. Rebuild any host that handled the compromised keys from scratch and rotate any related credentials.

Sweep PSBT recipe (high-level)
1. On your online node (compromised wallet loaded):
   BAL=$(bitcoin-cli -rpcwallet=COMP_WALLET getbalance)
   bitcoin-cli -rpcwallet=COMP_WALLET walletcreatefundedpsbt '[]' "{\"$NEWADDR\":$BAL}" 0 "{\"subtractFeeFromOutputs\":[0],\"feeRate\":0.0005}" true > unsigned_psbt.json
2. Sign locally (fastest if wallet is loaded):
   bitcoin-cli -rpcwallet=COMP_WALLET walletprocesspsbt "$(jq -r '.psbt' unsigned_psbt.json)" true > processed.json
   jq -r '.hex' processed.json > final_tx.hex
   bitcoin-cli sendrawtransaction "$(cat final_tx.hex)"

Appendix: useful scripts
------------------------
- tests/compute_txid.py: compute double‑sha256 txid for a given hex
- tooling/psbt_examples.md: examples how to build PSBTs with bitcoin-cli and bitcoinjs-lib
- scripts/create_repo_zip_no_keys.sh: create a repo zip excluding secrets (already committed)

Contact & changes
-----------------
If you want additional examples added to the documentation or more PSBT sweep templates, open an issue or reply in chat and I will commit more non-secret examples.

