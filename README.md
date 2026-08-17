# Mainnet Transaction Demo

This package provides scripts and examples to build, sign, verify, and package Bitcoin transactions for regtest/testnet/mainnet workflows. **No real mainnet private keys are committed to the repository.** Use the included local helpers to generate keys on your machine and produce a ZIP that contains your keys locally only.

Structure
- README.md (this file)
- scripts/
  - generate_keys_local.sh         # generate private key, WIF, and addresses locally (writes to ./keys)
  - build_raw_tx.sh                # helper to run bitcoin-cli createrawtransaction
  - build_and_sign.sh              # sign a raw tx using bitcoin-cli or local WIF (reads WIF securely)
  - create_zip_with_keys_local.sh  # assemble final ZIP locally and optionally encrypt
  - broadcast.sh                   # helper to broadcast signed tx via bitcoin-cli
- implementations/
  - python/builder.py              # Python example (requires python-bitcoinlib)
  - js/                            # Node.js examples (placeholder)
  - rust/                          # Rust examples (placeholder)
- tooling/
  - compute_txid.py                # compute txid from raw hex
  - decode_tx.py                   # basic decode using bitcoin-cli if available
  - verify_signature.py            # example verifier (requires ecdsa lib)
- example_tx/
  - signed_example_regtest_hex.txt # safe regtest example signed hex
- docs/
  - electrum_howto.md
- SECURITY_NOTICE.md
- LICENSE

Quick workflow (local)
1. Run: ./scripts/generate_keys_local.sh
   - Generates keys/ with private_key.hex, private_key.wif, public_key.hex, and addresses.
2. Build an unsigned tx with build_raw_tx.sh or bitcoin-cli createrawtransaction.
3. Sign with ./scripts/build_and_sign.sh (reads WIF from keys/private_key.wif or stdin).
4. Verify with tooling/compute_txid.py and tooling/decode_tx.py.
5. Create final ZIP locally including keys: ./scripts/create_zip_with_keys_local.sh --encrypt zip --out final_package_with_keys.zip

See scripts/ and docs/ for full details and safety warnings.
