# PACKAGE_README.md

This README is included inside the final package to explain the contents and how to safely decrypt and use the archive offline.

Contents
- webapp_dist/ — built web wallet static files (open index.html in a browser)
- keys/ — wallet_dump.txt or wallet.dat (private keys may be inside)
- transactions/ — each <txid>.hex with the raw signed transaction hex
- docs/ — runbooks and instructions

How to decrypt (AES-GCM example)
1. On an offline machine, copy the encrypted archive and the .sha256 checksum file.
2. Verify checksum locally:
   sha256sum -c final_package_with_keys_and_txs.tar.gz.enc.sha256
3. Decrypt and extract:
   openssl enc -d -aes-256-gcm -pbkdf2 -iter 200000 -in final_package_with_keys_and_txs.tar.gz.enc -out final_package.tar.gz
   tar xzf final_package.tar.gz -C /path/to/extract

Security notes
- This package may contain private keys. Keep the passphrase secret.
- Do NOT run the webapp in an untrusted browser when keys are loaded.
- Prefer PSBT + hardware wallet signing for mainnet transactions.

Offline usage
- The webapp is purely client-side. Serve webapp_dist/ files from a local static file server or open index.html directly in a secure browser profile.
- Use the transactions/ directory to import transaction hex into a node or Electrum for auditing or broadcast.

Contact
- This package contains non-secret tooling. The archive itself is only as secure as the passphrase you chose when encrypting it.
