# Web Wallet README

This lightweight React web wallet demo demonstrates a browser-based wallet that can: import WIF, derive a native segwit (P2WPKH) address, fetch balance and tx history via Blockstream API, encrypt/decrypt the private key in-memory using WebCrypto AES-GCM, and build+sign a simple transaction using bitcoinjs-lib.

Important security notes
- This demo is for educational purposes only. Do NOT use this app on an untrusted machine with real mainnet funds.
- Prefer hardware wallets (PSBT + HWI) for mainnet transactions.
- This app keeps keys in memory; encryption uses password in-browser and the 'encrypted blob' can be saved by you externally.

How to run (local)
1. Ensure Node 18+ and npm installed.
2. cd webapp
3. npm install
4. npm run dev
5. Open http://localhost:5173 in your browser

How to use
- Paste a WIF into the Import box and click Import WIF. The derived address and balance will show.
- Use Encrypt to produce an encrypted blob (copy/paste it to a safe place).
- Decrypt by pasting the blob and providing the password.
- Send: provide recipient and amount (BTC), click Build & Sign. The app will build and sign a transaction using a naive fee (10,000 sats). This is a demo; fee estimation and UTXO selection are simplistic.

Customization / production notes
- Replace Blockstream API endpoints with your own indexed backend or electrumx for privacy.
- Add PSBT support for hardware wallets (the repo already contains HWI scripts in the root).
- Do NOT hardcode private keys. Always generate & store keys on secure devices.
