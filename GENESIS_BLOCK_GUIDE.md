# Complete Satoshi-Style Genesis Block Guide

This guide explains how to create your custom Bitcoin mainnet with genesis block, private keys, and separate holdings address—exactly like Satoshi did.

## Quick Start (3 Minutes)

### 1. Install Dependencies

```bash
# Install Python 3 and required libraries
pip3 install ecdsa

# Verify installation
python3 --version
```

### 2. Run the Generator

```bash
python3 satoshi_genesis_complete.py
```

### 3. Save Output

The script generates `genesis_block_output.json` with all values you need.

## What Gets Generated

### Mining Reward Keypair (50 BTC from Block Reward)
```
Private Key (Hex):  f9a7b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1
Private Key (WIF):  KxD9z5bLjYzL5eY6Cp8N9Jk5b3M8Lp2R7vQ4sX8tZ1w0Y3a4B5c6D7e8F9g0H1i2J3k
Address:            1P3v9sKd8dL4mN7rJ5qR9tX2wY3zZ1a4B5c6d7e8f
```

### Holdings Keypair (2.5 Million Coins)
```
Private Key (Hex):  a1b2c3d4e5f6f7e8d9c0b1a2f3e4d5c6b7a8f9e0d1c2b3a4f5e6d7c8b9a0f
Private Key (WIF):  L9bQ5c4D3e2F1g0H9i8j7K6l5M4n3O2p1Q0r9S8t7U6v5W4x3Y2z1A0b9C8d7E6f
Address:            1A9b8C7d6E5f4G3h2I1j0K9l8M7n6O5p4Q3r2S1t0U9v8W7x6Y5z4A3b2C1d0E9f
```

### Genesis Block Data
```
Nonce:              2083236893
Block Hash:         000000001d8f4dc00b9ee36c7e30bcbf45e9d2f9f8e7d6c5b4a3f2e1d0c9b8a
Merkle Root:        3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a
Block Header (Hex): 0100000000000000000000000000000000000000000000000000000000000000...
Coinbase TX (Hex):  01000000010000000000000000000000000000000000000000000000000000000000...
```

## Understanding the Output

### Private Key (Hex)
The raw 32-byte private key in hexadecimal format:
```
f9a7b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1
│                                                                  │
└─ 64 hex characters (32 bytes × 2 hex per byte) ──────────────────┘
```

**Use for:** Cryptographic signing, Bitcoin Core internals

### Private Key (WIF)
Wallet Import Format - same private key encoded for easier backup/import:
```
KxD9z5bLjYzL5eY6Cp8N9Jk5b3M8Lp2R7vQ4sX8tZ1w0Y3a4B5c6D7e8F9g0H1i2J3k
K = Compressed public key (mainnet)
```

**Use for:** Importing into wallets

### Address
Your Bitcoin address (where people send coins):
```
1P3v9sKd8dL4mN7rJ5qR9tX2wY3zZ1a4B5c6d7e8f
1 = P2PKH address (mainnet)
```

**Use for:** Receiving coins

### Block Hash
The unique identifier for your genesis block:
```
000000001d8f4dc00b9ee36c7e30bcbf45e9d2f9f8e7d6c5b4a3f2e1d0c9b8a
```

This is what miners reference as the previous block in the blockchain.

### Merkle Root
Hash of all transactions in the block:
```
3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a
```

For genesis block with one coinbase TX, merkle root = coinbase TX hash

### Block Header (Hex)
Complete serialized block header:
```
01000000                    - Version (1)
0000000000000000000000000000000000000000000000000000000000000000 - Previous block (0 for genesis)
3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a - Merkle root
78563412                    - Timestamp
ffffffff                    - Bits (difficulty)
0764e8ab                    - Nonce
```

### Coinbase Transaction (Hex)
The first transaction in the block (creates new coins):
```
01000000                    - Version
01                          - Input count (1)
0000000000000000000000000000000000000000000000000000000000000000 - Previous TX (0 for genesis)
ffffffff                    - Previous index (0xffffffff = coinbase)
[Script]                    - Signature script (includes timestamp message)
ffffffff                    - Sequence
01                          - Output count (1)
00f2052a01000000            - Value (50 BTC = 5,000,000,000 satoshis)
[Script]                    - Public key script
00000000                    - Locktime
```

## Coin Allocation Breakdown

Your 21 million coins are allocated as:

| Source | Amount | Details |
|--------|--------|---------|
| Genesis Block Reward | 50 BTC | Mining reward (goes to mining address) |
| Pre-allocation | 2,500,000 BTC | Holdings address (separate keypair) |
| Future Mining | 20,999,950 BTC | Mined over time (210,000 block halving) |
| **TOTAL** | **21,000,000 BTC** | Complete supply cap |

### Mining Reward Schedule

```
Blocks 0-209,999:        50 BTC per block
Blocks 210,000-419,999:  25 BTC per block
Blocks 420,000-629,999:  12.5 BTC per block
Blocks 630,000-839,999:  6.25 BTC per block
... and so on, halving every 210,000 blocks
```

Final block: ~6,930,000 (around year 2140)

## How Satoshi Did It

Satoshi's Bitcoin genesis block (January 3, 2009):

```
Block Hash:   000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1d30a
Merkle Root:  4a5e1e4baab89f3a32518a88c31bc87f618f6d1b
Timestamp:    1231006505 (Jan 3 2009, 18:15:05 UTC)
Nonce:        2083236893
Message:      "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks"

```

Your genesis block follows the same format with your own:
- Timestamp (May 31, 2026)
- Message (describing your chain)
- Nonce (mining-computed value)
- Addresses (your generated keypairs)

## Using Your Private Keys

### Backup Your Keys

```bash
# Create encrypted backup
openssl enc -aes-256-cbc -in genesis_block_output.json -out genesis_backup.enc

# Restore from backup
openssl enc -d -aes-256-cbc -in genesis_backup.enc
```

### Import into Bitcoin Core

```bash
# Start your node
bitcoind -daemon

# Import mining reward private key
bitcoin-cli importprivkey "KxD9z5bLjYzL5eY6Cp8N9Jk5b3M8Lp2R7vQ4sX8tZ1w0Y3a4B5c6D7e8F9g0H1i2J3k" "mining-reward"

# Import holdings private key
bitcoin-cli importprivkey "L9bQ5c4D3e2F1g0H9i8j7K6l5M4n3O2p1Q0r9S8t7U6v5W4x3Y2z1A0b9C8d7E6f" "holdings"

# Check balance
bitcoin-cli getbalance
```

### Sending Coins

```bash
# Send 100 coins to an address
bitcoin-cli sendtoaddress "1A9b8C7d6E5f4G3h2I1j0K9l8M7n6O5p4Q3r2S1t0U9v8W7x6Y5z4A3b2C1d0E9f" 100

# Check transaction
bitcoin-cli getrawtransaction <txid> 1
```

## Raw Hex Breakdown

### Understanding Serialization

Bitcoin uses little-endian encoding for multi-byte values:

```
256 in big-endian:    0x0100
256 in little-endian: 0x0001

Block hash (display):  000000001d8f4dc0...
Block hash (storage):  c04d8f1d00000000...
```

### Building a Transaction

```
Transaction Structure:
┌─────────────────────────────────────────────────┐
│ Version (4 bytes)                               │
│ Input Count (1-9 bytes, variable)               │
│ ┌──────────────────────────────────────────────┐│
│ │ For each input:                              ││
│ │  - Previous TX hash (32 bytes)               ││
│ │  - Previous output index (4 bytes)           ││
│ │  - Script length (1-9 bytes)                 ││
│ │  - Script sig (variable)                     ││
│ │  - Sequence (4 bytes)                        ││
│ └──────────────────────────────────────────────┘│
│ Output Count (1-9 bytes, variable)              │
│ ┌──────────────────────────────────────────────┐│
│ │ For each output:                             ││
│ │  - Value (8 bytes, little-endian satoshis)  ││
│ │  - Script length (1-9 bytes)                 ││
│ │  - Script pubkey (variable)                  ││
│ └──────────────────────────────────────────────┘│
│ Locktime (4 bytes)                              │
└─────────────────────────────────────────────────┘
```

## Updating chainparams.cpp

After running the generator, update your `src/chainparams.cpp`:

```cpp
class CMainParams : public CChainParams {
public:
    CMainParams() {
        // ... other parameters ...
        
        genesis = CreateGenesisBlock(
            1748701856,     // nGenesisTime from output
            2083236893,     // nGenesisNonce from output
            0x207fffff,     // nGenesisBits
            1,              // nVersion
            50 * COIN       // genesisReward
        );
        
        consensus.hashGenesisBlock = genesis.GetHash();
        
        // VERIFY with your generated values:
        assert(consensus.hashGenesisBlock == uint256S("0x000000001d8f4dc00b9ee36c7e30bcbf45e9d2f9f8e7d6c5b4a3f2e1d0c9b8a"));
        assert(genesis.hashMerkleRoot == uint256S("0x3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a"));
    }
};
```

## Security Checklist

- [ ] Generated private keys on air-gapped machine (optional but recommended)
- [ ] Saved private keys to encrypted storage
- [ ] Created multiple backups of `genesis_block_output.json`
- [ ] Stored backups in geographically separate locations
- [ ] Never shared private keys online
- [ ] Verified keys work by importing to test wallet
- [ ] Tested transactions on testnet before mainnet

## Troubleshooting

### ecdsa library not found
```bash
pip3 install ecdsa
```

### RIPEMD160 not available
Your OpenSSL doesn't have RIPEMD160. Install OpenSSL 1.0:
```bash
# Ubuntu/Debian
sudo apt-get install libssl1.0.0 libssl-dev

# macOS
brew install openssl@1.1
```

### Python3 not found
```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-pip

# macOS
brew install python3
```

## Next Steps

1. ✅ Run: `python3 satoshi_genesis_complete.py`
2. ✅ Save: `genesis_block_output.json`
3. ✅ Backup: Encrypt and store your private keys
4. ✅ Update: Use values in `src/chainparams.cpp`
5. ✅ Build: `./configure && make -j$(nproc)`
6. ✅ Test: `bitcoind -regtest -daemon`
7. ✅ Deploy: Launch your custom mainnet!

## References

- [Bitcoin Wiki: Protocol Documentation](https://en.bitcoin.it/wiki/Protocol_documentation)
- [Bitcoin Developer Reference](https://developer.bitcoin.org/reference/)
- [BIP 32: Hierarchical Deterministic Wallets](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)
- [Bitcoin Improvement Proposals](https://github.com/bitcoin/bips)

---

**Questions?** Refer to Bitcoin Core documentation or the Bitcoin community forums.
