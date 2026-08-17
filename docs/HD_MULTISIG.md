# HD & Multisig Guide (docs/HD_MULTISIG.md)

This document explains the demo HD & multisig helpers included in the webapp.

HD wallet demo
- generateMnemonic(): creates a BIP39 24-word mnemonic (entropy 256 bits)
- mnemonicToSeed(), seedToNode(), nodeToXpub(): convert mnemonic to seed, BIP32 node, and xpub
- deriveAddressFromXprv(): example of deriving a BIP84 native segwit address from an xprv/node

Multisig demo
- createMultisigAddress(pubkeysHex, m): given 3 pubkey hex strings returns a 2-of-3 P2WSH address and scripts
- Do NOT store private keys for each cosigner in the same place in production. Use hardware wallets for cosigners.

PSBT building
- buildPsbtExample() shows how to build an unsigned PSBT for a P2WPKH input using bitcoinjs-lib. This is a demo — production PSBTs should include additional metadata and fee estimation.

Security
- Never expose xprv or private keys in the webapp in production. Use encrypted storage + WebAuthn/HSM to gate access.
- For multisig, use separate hardware devices for each cosigner and follow best practices for PSBT signing.
