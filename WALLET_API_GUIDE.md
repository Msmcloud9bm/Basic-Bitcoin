# BlockCypher Wallet API Integration Guide

## Overview

The Wallet API allows you to group multiple Bitcoin addresses under a single name without storing private keys. This guide covers creating, managing, and checking balances before spending.

⚠️ **CRITICAL**: Always verify wallet balance BEFORE creating transactions.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Regular Wallets](#regular-wallets)
3. [HD (Hierarchical Deterministic) Wallets](#hd-wallets)
4. [Balance Verification](#balance-verification)
5. [Complete Workflow](#complete-workflow)
6. [API Reference](#api-reference)

---

## Getting Started

### Prerequisites

```bash
pip install requests
```

### Setup

```python
from wallet_api import BlockCypherWalletAPI, Network

# Initialize API client
api = BlockCypherWalletAPI(
    api_token="YOUR_BLOCKCYPHER_TOKEN",
    network=Network.MAINNET  # or Network.TESTNET
)
```

Get your token from [BlockCypher Dashboard](https://www.blockcypher.com/users/login)

---

## Regular Wallets

### What is a Regular Wallet?

A regular wallet is a collection of public addresses managed under one name. It holds **only public information** - no private keys.

```
Wallet "alice"
├── 1JcX75oraJEmzXXHpDjRctw3BX6qDmFM8e
├── 13cj1QtfW61kQHoqXm3khVRYPJrgQiRM6j
└── 14LcPtRSGjYb1s8kfxsVDbXvA7VYCmoFho
```

### Create Regular Wallet

```python
wallet = api.create_wallet(
    wallet_name="alice",
    addresses=[
        "1JcX75oraJEmzXXHpDjRctw3BX6qDmFM8e",
        "13cj1QtfW61kQHoqXm3khVRYPJrgQiRM6j"
    ]
)

print(f"Created wallet: {wallet['name']}")
print(f"Addresses: {wallet['addresses']}")
```

### List Wallets

```python
wallet_names = api.list_wallets()
# Output: ['alice', 'bob', 'charlie']
```

### Get Wallet Details

```python
wallet = api.get_wallet("alice")

print(f"Wallet: {wallet['name']}")
print(f"Addresses: {wallet['addresses']}")
```

### Get Wallet Addresses

```python
addresses = api.get_wallet_addresses("alice")

for addr in addresses:
    print(f"- {addr}")
```

### Add Addresses to Wallet

```python
api.add_addresses_to_wallet(
    "alice",
    [
        "1A1z7agoatXxXxXxXxXxXxXxXxXxXxXxXx",
        "3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy"
    ]
)
```

### Remove Address from Wallet

```python
api.remove_address_from_wallet(
    "alice",
    "1A1z7agoatXxXxXxXxXxXxXxXxXxXxXxXx"
)
```

### Generate New Address in Wallet

```python
result = api.generate_address_in_wallet("alice", bech32=True)

new_address = result['address']
print(f"New address: {new_address}")
```

### Delete Wallet

```python
api.delete_wallet("alice")
```

---

## HD Wallets

### What is an HD Wallet?

HD (Hierarchical Deterministic) wallets derive all addresses from a single **extended public key** using BIP32 standard. No manual address management needed.

```
HD Wallet "bob"
├── m/0 → 1FHz8bpEE5qUZ9XhfjzAbCCwo5bT1HMNAc
├── m/1 → 1J8QDN1u7iDMbJktbqXPSrAqruNjkmRFmT
└── m/2 → 1MWNKnYfE2LVdvAzFUioF3F3JXFpRfDCQb
```

### Supported Standards

#### BIP32 (Generic HD Wallet)

```python
# Use extended public key of m/0' or m/44'/0'/0'
api.create_hd_wallet(
    wallet_name="bob",
    extended_public_key="xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8"
)
```

#### BIP44 (Multi-Account Hierarchy)

```python
# For Bitcoin Mainnet with account 0
# Use extended public key of m/44'/0'/0'
api.create_hd_wallet(
    wallet_name="bip44_wallet",
    extended_public_key="xpub...",
    subchain_indexes=[0, 1]  # [external, internal]
)

# Subchain 0: External chain (m/44'/0'/0'/0/k)
# Subchain 1: Internal chain (m/44'/0'/0'/1/k)
```

#### BIP84 (Native SegWit/Bech32)

```python
# For Bitcoin Testnet with Bech32 addresses
# Use extended public key of m/84'/0'/0' (mainnet) or m/84'/1'/0' (testnet)
api.create_hd_wallet(
    wallet_name="bech32_wallet",
    extended_public_key="vpub5bnSQvUJV6VKG...",  # vpub for testnet
    subchain_indexes=[0, 1]
)

# Generates: tb1q... addresses
```

### Create HD Wallet

```python
hd_wallet = api.create_hd_wallet(
    wallet_name="my_hd_wallet",
    extended_public_key="xpub661MyMwAqRbcFtXgS5...",
    subchain_indexes=[0, 1]  # Optional: for BIP44/84
)

print(f"HD Wallet: {hd_wallet['name']}")
print(f"Extended Public Key: {hd_wallet['extended_public_key']}")
```

### Get HD Wallet Details

```python
hd_wallet = api.get_hd_wallet("my_hd_wallet")

for chain in hd_wallet['chains']:
    print(f"Chain {chain['index']}:")
    for addr_info in chain['chain_addresses']:
        print(f"  {addr_info['path']} → {addr_info['address']}")
```

### Get HD Wallet Addresses

```python
addresses = api.get_hd_wallet_addresses("my_hd_wallet")

# Optional: Filter used/unused or zero/non-zero balance
used_addresses = api.get_hd_wallet_addresses(
    "my_hd_wallet",
    used_only=True
)

empty_addresses = api.get_hd_wallet_addresses(
    "my_hd_wallet",
    zero_balance_only=True
)
```

### Derive New Addresses in HD Wallet

```python
# Generate 1 new address on default chain
new_addrs = api.derive_address_in_hd_wallet("my_hd_wallet")

# Generate multiple addresses on specific subchain
new_addrs = api.derive_address_in_hd_wallet(
    "my_hd_wallet",
    count=5,
    subchain_index=1  # internal chain for BIP44/84
)

for chain in new_addrs['chains']:
    for addr_info in chain['chain_addresses']:
        print(f"{addr_info['path']} → {addr_info['address']}")
```

### Delete HD Wallet

```python
api.delete_hd_wallet("my_hd_wallet")
```

---

## Balance Verification

### ⚠️ CRITICAL: Always Check Before Spending

**Never create a transaction without verifying sufficient balance first!**

### Get Individual Address Balance

```python
balance = api.get_address_balance("1JcX75oraJEmzXXHpDjRctw3BX6qDmFM8e")

print(f"Balance: {balance.total_balance} sats")
print(f"Confirmed: {balance.confirmed_balance} sats")
print(f"Unconfirmed: {balance.unconfirmed_balance} sats")
print(f"Total received: {balance.total_received} sats")
print(f"Total sent: {balance.total_sent} sats")
print(f"Transactions: {balance.tx_count}")
```

### Get Wallet Balance (All Addresses)

```python
balance = api.get_wallet_balance("alice", is_hd=False)

print(f"Total: {balance['balance']} sats")
print(f"Unconfirmed: {balance['unconfirmed_balance']} sats")
```

### Pre-Transaction Verification (Recommended)

```python
# BEFORE creating any transaction:
has_funds, balance_data = api.verify_before_transaction(
    wallet_name="alice",
    required_amount_btc=0.01,  # 0.01 BTC = 1,000,000 sats
    is_hd=False
)

if has_funds:
    print("✅ Sufficient balance - proceed with transaction")
    # Build and broadcast transaction
else:
    print("❌ Insufficient balance - cannot proceed")
    # Request more funds or reduce amount
```

### Get Full Address Info with UTXOs

```python
addr_full = api.get_address_full("1JcX75oraJEmzXXHpDjRctw3BX6qDmFM8e")

print(f"Transactions: {addr_full['tx_count']}")
print(f"Balance: {addr_full['balance']} sats")

# Get only unspent outputs (UTXOs)
utxos = api.get_address_full(
    "1JcX75oraJEmzXXHpDjRctw3BX6qDmFM8e",
    unspent_only=True
)

for utxo in utxos['utxo']:
    print(f"UTXO: {utxo['tx_hash']} vout:{utxo['tx_output_n']} = {utxo['value']} sats")
```

---

## Complete Workflow

### Example: Send Bitcoin from Wallet to Another Address

```python
#!/usr/bin/env python3

from wallet_api import BlockCypherWalletAPI, Network
from transaction_builder import build_transaction_from_wallet

# Step 1: Initialize
api = BlockCypherWalletAPI("YOUR_TOKEN", Network.TESTNET)

# Step 2: Create wallet (if needed)
api.create_wallet(
    "send_wallet",
    ["mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn"]
)

# Step 3: CHECK BALANCE FIRST
required_amount = 0.001  # 0.001 BTC

print("\n" + "=" * 70)
print("  PRE-TRANSACTION SAFETY CHECK")
print("=" * 70)

has_sufficient, balance_data = api.verify_before_transaction(
    "send_wallet",
    required_amount,
    is_hd=False
)

if not has_sufficient:
    print("\n❌ Cannot proceed - insufficient funds")
    exit(1)

# Step 4: Get wallet addresses
addresses = api.get_wallet_addresses("send_wallet")

# Step 5: Build transaction
print("\n" + "=" * 70)
print("  BUILDING TRANSACTION")
print("=" * 70)

outputs = {
    "mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn": required_amount
}

# Use transaction_builder.py to create and sign
raw_tx, txid = build_transaction(
    network="testnet",
    utxos=addresses,
    outputs=outputs,
    fee_rate_sat_per_vbyte=5
)

# Step 6: Confirm before broadcast
print("\n⚠️  Ready to broadcast transaction")
confirm = input("Type CONFIRM to proceed: ")

if confirm == "CONFIRM":
    # Broadcast transaction
    print("✅ Transaction sent!")
else:
    print("❌ Cancelled")
```

---

## API Reference

### Regular Wallet Methods

| Method | Description |
|--------|-------------|
| `create_wallet(name, addresses)` | Create new wallet |
| `get_wallet(name)` | Get wallet details |
| `list_wallets()` | List all wallets |
| `get_wallet_addresses(name)` | Get all addresses |
| `add_addresses_to_wallet(name, addresses)` | Add addresses |
| `remove_address_from_wallet(name, address)` | Remove address |
| `generate_address_in_wallet(name, bech32)` | Generate new address |
| `delete_wallet(name)` | Delete wallet |

### HD Wallet Methods

| Method | Description |
|--------|-------------|
| `create_hd_wallet(name, xpub, subchains)` | Create HD wallet |
| `get_hd_wallet(name)` | Get HD wallet details |
| `get_hd_wallet_addresses(name, used_only, zero_balance_only)` | Get addresses with filters |
| `derive_address_in_hd_wallet(name, count, subchain, lookahead)` | Derive new addresses |
| `delete_hd_wallet(name)` | Delete HD wallet |

### Balance Methods

| Method | Description |
|--------|-------------|
| `get_address_balance(address)` | Single address balance |
| `get_wallet_balance(name, is_hd)` | Wallet total balance |
| `verify_before_transaction(name, amount, is_hd)` | Pre-transaction check |
| `get_address_full(address, unspent_only)` | Full address info + UTXOs |

---

## Safety Best Practices

### ✅ DO

- ✅ Always call `verify_before_transaction()` before spending
- ✅ Check balance includes enough for fees (add 0.0001 BTC buffer)
- ✅ Use TESTNET for testing first
- ✅ Keep your BlockCypher token secret
- ✅ Monitor unconfirmed transactions

### ❌ DON'T

- ❌ Skip balance verification
- ❌ Use private keys in wallets (public addresses only)
- ❌ Assume unconfirmed funds are spendable on mainnet
- ❌ Share your API token in code/repos
- ❌ Create transaction without checking fees

---

## Common Issues

### "Insufficient Funds"

```python
# Add extra to account for fees
has_funds, data = api.verify_before_transaction(
    "wallet",
    0.001 + 0.0001,  # amount + fee buffer
    is_hd=False
)
```

### "Invalid Address"

Ensure address matches your network:
- Mainnet: starts with 1, 3, or bc1
- Testnet: starts with m, n, 2, or tb1

### "Unconfirmed Balance Not Spendable"

Wait for confirmation before spending:

```python
balance = api.get_address_balance(address)

if balance.unconfirmed_balance > 0:
    print("⏳ Waiting for confirmation...")
```

---

## Resources

- [BlockCypher API Docs](https://www.blockcypher.com/dev/bitcoin/)
- [BIP32 Standard](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)
- [BIP44 Standard](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki)
- [BIP84 Standard](https://github.com/bitcoin/bips/blob/master/bip-0084.mediawiki)

---

*Last Updated: 2026-05-17*
*Remember: With great power comes great responsibility. Always verify balances before spending!*
