# Mainnet Operational Runbook

This runbook is a step-by-step, paste-ready set of commands and checks for preparing, signing (offline or hardware wallet), verifying, and broadcasting a mainnet Bitcoin transaction. DO NOT run any commands that expose private keys on an internet-connected machine. Use the PSBT + HWI workflow for secure hardware signing.

Sections:
- Preconditions
- Prepare unsigned PSBT on online machine
- Transfer PSBT to offline signing machine or hardware wallet host
- Sign PSBT with HWI (hardware device) or with WIF locally (air-gapped)
- Finalize PSBT and broadcast from online machine
- Post-broadcast verification and incident steps

Important safety rules (read before proceeding)
- Never paste or upload your private key or WIF.
- Generate private keys only on a machine you control; preferably an air-gapped machine or hardware wallet.
- Use PSBT for hardware signing. Avoid raw hex + private key signing on internet-connected hosts.
- Test the entire flow on testnet/regtest first.

A. Preconditions
1. Online machine: has internet access, runs bitcoin-core node (mainnet) or uses a trusted broadcaster service; has bitcoin-cli installed.
2. Offline signing machine or hardware wallet host: This is a separate machine that may be air-gapped (recommended). Has HWI installed if using hardware wallet.
3. Hardware wallet (optional but recommended): Trezor, Ledger, Coldcard, or similar with latest firmware.
4. Tools on both machines: jq, openssl, tar, python3 (for helper scripts in repository).

B. Prepare unsigned PSBT on the online machine (walletcreatefundedpsbt)

1) Create or choose a wallet that will provide inputs. For mainnet, use a watch-only or funding wallet as appropriate.

2) Build a PSBT with bitcoin-cli using walletcreatefundedpsbt. Example (paste-ready):

# Example: create a PSBT to send 0.5 BTC to recipient
RECIPIENT_ADDR="<RECIPIENT_MAINNET_ADDR>"
CHANGE_ADDR="<CHANGE_ADDR_FROM_YOUR_WALLET>"

# Create PSBT (adjust feeRate or set options to control fee)
PSBT_JSON=$(bitcoin-cli -rpcwallet=walletname walletcreatefundedpsbt \
  '[{"txid":"<UTXO_TXID>","vout":<VOUT>}]' \
  "{\"$RECIPIENT_ADDR\":0.5, \"$CHANGE_ADDR\":(TOTAL - 0.5 - FEE)}" \
  0 '{"includeWatching":true}' true)

# Extract PSBT base64
echo "$PSBT_JSON" | jq -r '.psbt' > unsigned.psbt.base64

Notes:
- If you use walletcreatefundedpsbt with no explicit inputs, the wallet will select inputs automatically.
- You can pass "feeRate" or control options to set the fee. Always verify the fee and total inputs before exporting the PSBT.

C. Transfer PSBT to offline signer or hardware wallet host
- Export unsigned.psbt.base64 to a USB drive or transfer via an air-gapped method. Do NOT transfer the wallet's private keys.

D. Signing with HWI (Hardware Wallet Interface)

Prerequisites:
- HWI installed and the hardware device connected (to the signing host). See docs/hwi_readme.md for install help.

Paste-ready signing sequence (on the signing host):

# enumerate devices
hwi enumerate

# Suppose device path or type is identified; sign the PSBT
# HWI accepts a base64 PSBT string. Example for Trezor (device index 0):
PSBT_BASE64=$(cat unsigned.psbt.base64)

# For many HWI versions the command is:
hwi --device-type 0 signtx "$PSBT_BASE64" > signed.psbt.base64

# or using device path:
hwi --device-path /dev/hidrawX signtx "$PSBT_BASE64" > signed.psbt.base64

# After signing, move signed.psbt.base64 back to the online machine safely.

E. Finalize PSBT and broadcast on the online machine

# On the online machine, read the signed PSBT and finalize
SIGNED_BASE64=$(cat signed.psbt.base64)
FINAL_JSON=$(bitcoin-cli walletprocesspsbt "$SIGNED_BASE64" true)
# The "hex" field contains the final transaction hex if complete
echo "$FINAL_JSON" | jq -r '.hex' > signed_tx.hex

# Verify txid
python3 tooling/compute_txid.py signed_tx.hex
# Broadcast
TXID=$(bitcoin-cli sendrawtransaction "$(cat signed_tx.hex)")
echo "Broadcast TXID: $TXID"

F. Offline signing with WIF (air-gapped)
1) On the online machine, prepare an unsigned raw transaction (createrawtransaction) or a PSBT.
2) Transfer the unsigned data to the offline machine by removable media.
3) On the offline machine, import your WIF into a local wallet or use bitcoin-cli signrawtransactionwithkey with the WIF read from a protected file or prompt.
4) Transfer the signed hex back to the online machine and broadcast.

G. Verification and post-broadcast checks
- Confirm the txid with compute_txid.py
- Use getrawtransaction <txid> 1 to view block inclusion
- Monitor mempool and confirmations

H. Incident handling
- If the transaction is missing inputs: abort and verify UTXO ownership/address and node rescan/state.
- If the transaction is malformed or rejected: do not retry broadcasting; analyze raw hex with decoderawtransaction and review scripts/signatures.

I. Operational notes & best practices
- Prefer hardware wallets and PSBT workflows for mainnet operations.
- Keep a written, offline runbook for emergency key recovery and incident response.
- Rotate keys and use multisig for large holdings.

---

This runbook is included in the repository at docs/runbook_mainnet.md. Use it as the authoritative, printable operational guide for mainnet transactions.
