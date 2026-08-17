# tooling/psbt_examples.md

PSBT Examples and Notes

1) Create a PSBT sweeping wallet balance to a single address (wallet on node):

  BAL=$(bitcoin-cli -rpcwallet=COMP_WALLET getbalance)
  bitcoin-cli -rpcwallet=COMP_WALLET walletcreatefundedpsbt '[]' "{\"$NEWADDR\":$BAL}" 0 "{\"subtractFeeFromOutputs\":[0],\"feeRate\":0.0005}" true > unsigned_psbt.json

2) Create a PSBT for specific UTXOs (explicit coin control):

  bitcoin-cli -rpcwallet=COMP_WALLET walletcreatefundedpsbt "[{\"txid\":\"$UTXID\",\"vout\":$VOUT}]" "{\"$NEWADDR\":$AMOUNT}" 0 "{\"subtractFeeFromOutputs\":[0],\"feeRate\":0.0005}" true > explicit_psbt.json

3) Sign PSBT on node (fast) or export and sign with hardware wallet (HWI):

  # Node signs (if keys present)
  bitcoin-cli -rpcwallet=COMP_WALLET walletprocesspsbt "$(jq -r '.psbt' unsigned_psbt.json)" true > processed.json

  # Hardware sign with HWI example (on signer host)
  hwi enumerate
  hwi --device-path <path> signtx unsigned_psbt.base64 > signed.psbt.base64

4) Finalize and broadcast

  bitcoin-cli -rpcwallet=COMP_WALLET finalizepsbt "$(cat signed.psbt.base64)" true | jq -r '.hex' > final_hex.tx
  bitcoin-cli sendrawtransaction "$(cat final_hex.tx)"

Notes:
- feeRate in the examples is BTC/kB. Use very aggressive feeRate to outrun attackers when keys are compromised.
- For PSBT signing with HWI, follow your device vendor's instructions. HWI may require a transport layer (USB, WebUSB, or bridge).
