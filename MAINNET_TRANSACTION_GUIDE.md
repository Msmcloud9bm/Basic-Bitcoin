# Bitcoin Mainnet Transaction Guide
## Creating and Spending Transactions on Bitcoin Mainnet

⚠️ **CRITICAL WARNING**: This guide covers mainnet transactions involving **REAL BITCOIN**. Mistakes can result in permanent loss of funds. Always test on testnet first.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Simple Mainnet Spending](#simple-mainnet-spending)
3. [Raw Transaction on Mainnet](#raw-transaction-on-mainnet)
4. [Offline Signing on Mainnet](#offline-signing-on-mainnet)
5. [Security Best Practices](#security-best-practices)
6. [Fee Estimation](#fee-estimation)

---

## Prerequisites

### Setup Bitcoin Core for Mainnet
```bash
# Download and install Bitcoin Core from bitcoin.org
# Create bitcoin.conf in your Bitcoin data directory

# Linux/Mac: ~/.bitcoin/bitcoin.conf
# Windows: %APPDATA%\Bitcoin\bitcoin.conf

# Minimal bitcoin.conf for mainnet
server=1
rpcuser=your_rpc_username
rpcpassword=your_strong_rpc_password
rpcallowip=127.0.0.1
txindex=1  # Optional: needed for transaction history

# Start Bitcoin Core (fully synced mainnet blockchain required)
bitcoind -daemon
```

### Verify Mainnet Connection
```bash
bitcoin-cli getblockchaininfo
# Look for "chain": "main" in the output
```

### Create a Wallet
```bash
# Create a new wallet (if using Bitcoin Core 0.21+)
bitcoin-cli createwallet "mywallet"

# Or load existing wallet
bitcoin-cli loadwallet "mywallet"

# Verify wallet is loaded
bitcoin-cli listwallets
```

---

## Simple Mainnet Spending

### Step 1: Get Your Current Balance
```bash
bitcoin-cli getbalance
# Returns: 1.23456789 (in BTC)
```

### Step 2: Get Your Unspent Outputs (UTXOs)
```bash
bitcoin-cli listunspent
```

**Output Example:**
```json
[
  {
    "txid": "abc123def456...",
    "vout": 0,
    "address": "1A1z7agoat2...",
    "scriptPubKey": "76a914...",
    "amount": 0.5,
    "confirmations": 100,
    "spendable": true,
    "solvable": true
  }
]
```

### Step 3: Create a New Address to Receive Funds
```bash
# Generate a new address in your wallet
RECIPIENT_ADDRESS=$(bitcoin-cli getnewaddress)
echo $RECIPIENT_ADDRESS
# Output: 1BoatSLANXXXXXXXXXXXXXXXXXXXXXXXX
```

### Step 4: Send Bitcoins to Another Address
```bash
# Simple send to another address
AMOUNT=0.01  # in BTC
RECIPIENT="1BoatSLANXXXXXXXXXXXXXXXXXXXXXXXX"

# Send with automatic fee calculation
TXID=$(bitcoin-cli sendtoaddress $RECIPIENT $AMOUNT)
echo $TXID
# Output: f4a5e2c3b8d1a9f7e4c2b5a8d3f6e9c2...
```

### Step 5: Check Transaction Status
```bash
# Get transaction details
bitcoin-cli gettransaction $TXID

# Get raw transaction (more details)
bitcoin-cli getrawtransaction $TXID 1

# Check if confirmed
bitcoin-cli getconfirmations $TXID  # Requires txindex=1
```

---

## Raw Transaction on Mainnet

### Why Use Raw Transactions?
- **Full Control**: Specify exact inputs and outputs
- **Multiple Recipients**: Send to multiple addresses in one transaction
- **Custom Fees**: Set your own transaction fee
- **Advanced Scripting**: Create complex spending conditions

⚠️ **WARNING**: Raw transactions that are incorrectly constructed can cause permanent loss of Bitcoin. Double-check all values.

### Step 1: List Available UTXOs
```bash
bitcoin-cli listunspent 1 999999  # minconf=1, maxconf=999999
```

### Step 2: Select UTXOs to Spend
```bash
# Save UTXO details
UTXO_TXID="abc123def456abc123def456abc123def456abc123def456abc123def456abc123"
UTXO_VOUT=0
UTXO_AMOUNT=1.5  # in BTC
```

### Step 3: Get New Addresses for Recipients
```bash
# Create new addresses for recipients (or use existing ones)
RECIPIENT1="1A1z7agoatXxXxXxXxXxXxXxXxXxXxXxXx"
RECIPIENT2="3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy"
AMOUNT1=0.5
AMOUNT2=0.7
```

### Step 4: Create Raw Transaction
```bash
# Create raw transaction with inputs and outputs
RAW_TX=$(bitcoin-cli createrawtransaction \
  '[
    {
      "txid": "'$UTXO_TXID'",
      "vout": '$UTXO_VOUT'
    }
  ]' \
  '{
    "'$RECIPIENT1'": '$AMOUNT1',
    "'$RECIPIENT2'": '$AMOUNT2'
  }')

echo $RAW_TX
```

**Important Notes:**
- **Change Output**: If inputs > outputs, the difference becomes the fee. Add a change address to recover unused funds.
- **Fee Calculation**: Outputs - Inputs = Transaction Fee

### Step 5: Create Transaction with Change Output
```bash
# Get a change address from your wallet
CHANGE_ADDRESS=$(bitcoin-cli getrawchangeaddress)

# Calculate change: 1.5 - 0.5 - 0.7 = 0.3 BTC
# But subtract miner fee (e.g., 0.0001 BTC)
CHANGE_AMOUNT=0.2999

RAW_TX=$(bitcoin-cli createrawtransaction \
  '[
    {
      "txid": "'$UTXO_TXID'",
      "vout": '$UTXO_VOUT'
    }
  ]' \
  '{
    "'$RECIPIENT1'": '$AMOUNT1',
    "'$RECIPIENT2'": '$AMOUNT2',
    "'$CHANGE_ADDRESS'": '$CHANGE_AMOUNT'
  }')
```

### Step 6: Decode Transaction (Verify Before Signing)
```bash
# ALWAYS verify the transaction is correct before signing!
bitcoin-cli decoderawtransaction $RAW_TX
```

**Verify:**
- ✓ All inputs are correct (txid, vout)
- ✓ All outputs are correct (amounts, addresses)
- ✓ Fee calculation is correct

### Step 7: Sign the Raw Transaction
```bash
# Sign with wallet's private keys
SIGNED_TX=$(bitcoin-cli signrawtransaction $RAW_TX)

# Extract the hex from the response
SIGNED_TX_HEX=$(echo $SIGNED_TX | jq -r '.hex')

# Verify transaction is complete
echo $SIGNED_TX | jq -r '.complete'  # Should output: true
```

### Step 8: Broadcast to Mainnet
```bash
# Send to the network
FINAL_TXID=$(bitcoin-cli sendrawtransaction $SIGNED_TX_HEX)

echo "Transaction sent: $FINAL_TXID"
echo "View on blockchain explorer: https://blockchain.com/btc/tx/$FINAL_TXID"
```

### Step 9: Monitor Transaction
```bash
# Check transaction status
bitcoin-cli gettransaction $FINAL_TXID

# Watch for confirmations (refresh until you see confirmations > 0)
while true; do
  CONFIRMATIONS=$(bitcoin-cli gettransaction $FINAL_TXID | jq -r '.confirmations')
  echo "Confirmations: $CONFIRMATIONS"
  sleep 30  # Check every 30 seconds
done
```

---

## Offline Signing on Mainnet

### Scenario
- **Online Computer**: Has access to wallet but no internet (air-gapped)
- **Offline Computer**: Has internet access, prepares raw transaction

### On Online Computer (Create Transaction)

```bash
# Step 1: Get UTXO info
bitcoin-cli listunspent 6 999999  # 6 confirms for safety

# Step 2: Create raw transaction (unsigned)
RAW_TX=$(bitcoin-cli createrawtransaction \
  '[{"txid":"'$UTXO_TXID'","vout":'$UTXO_VOUT'}]' \
  '{"'$RECIPIENT_ADDRESS'":'$AMOUNT'}')

# Step 3: Get the pubkey script (needed for signing)
PREVIOUS_OUTPUT=$(bitcoin-cli getrawtransaction $UTXO_TXID 1)
PUBKEY_SCRIPT=$(echo $PREVIOUS_OUTPUT | jq -r '.vout['$UTXO_VOUT'].scriptPubKey.hex')

# Step 4: Save for transfer to offline computer
echo $RAW_TX > transaction.txt
echo $PUBKEY_SCRIPT > pubkey_script.txt
echo $UTXO_AMOUNT > utxo_amount.txt
```

### On Offline Computer (Sign Transaction)

⚠️ **SECURITY**: This computer should NOT be connected to the internet.

```bash
# Transfer transaction.txt, pubkey_script.txt, utxo_amount.txt to offline computer

# Read the files
RAW_TX=$(cat transaction.txt)
PUBKEY_SCRIPT=$(cat pubkey_script.txt)
UTXO_AMOUNT=$(cat utxo_amount.txt)

# Sign the transaction
SIGNED_TX=$(bitcoin-cli signrawtransaction "$RAW_TX" \
  '[
    {
      "txid": "'$UTXO_TXID'",
      "vout": '$UTXO_VOUT',
      "scriptPubKey": "'$PUBKEY_SCRIPT'",
      "value": '$UTXO_AMOUNT'
    }
  ]')

# Extract hex
SIGNED_HEX=$(echo $SIGNED_TX | jq -r '.hex')

# Save to file for transfer back to online computer
echo $SIGNED_HEX > signed_transaction.txt
```

### Back to Online Computer (Broadcast)

```bash
# Transfer signed_transaction.txt back to online computer

SIGNED_HEX=$(cat signed_transaction.txt)

# Broadcast
FINAL_TXID=$(bitcoin-cli sendrawtransaction $SIGNED_HEX)

echo "Broadcast successful: $FINAL_TXID"
```

---

## Security Best Practices

### 🔐 Private Key Management

```bash
# ⚠️ NEVER expose private keys
bitcoin-cli dumpprivkey <address>  # Only use when necessary

# Best Practice: Use hardware wallet instead
# - Ledger, Trezor, or ColdCard
# - Signs transactions without exposing keys
```

### 💰 Fund Management

```bash
# Check balance before each transaction
bitcoin-cli getbalance

# Verify recipient address is correct BEFORE sending
# Check: Correct capitalization, length (26-35 chars)
bitcoin-cli validateaddress "recipient_address_here"

# Use P2PKH (starts with 1), P2SH (starts with 3), or Bech32 (starts with bc1)
```

### 📊 Fee Management

```bash
# Get recommended fee rates (in BTC/KB)
bitcoin-cli estimatesmartfee 6  # For confirmation in ~6 blocks

# For faster confirmation (next block):
bitcoin-cli estimatesmartfee 1

# Or manually check: https://bitcoinfees.earn.com
```

---

## Fee Estimation

### Understanding Mainnet Fees

**Fee = Inputs Total - Outputs Total**

```bash
# Example:
# Input UTXO: 1.0 BTC
# Output 1: 0.35 BTC
# Output 2: 0.50 BTC
# Change: 0.14 BTC
# Fee: 1.0 - (0.35 + 0.50 + 0.14) = 0.01 BTC (high fee for mainnet)
```

### Dynamic Fee Calculation

```bash
# Get mempool fee rate
FEERATE=$(bitcoin-cli estimatesmartfee 6 | jq -r '.feerate')
echo "Recommended fee rate: $FEERATE BTC/KB"

# Calculate transaction size (approximate)
# P2PKH input ≈ 148 bytes
# P2PKH output ≈ 34 bytes
# Fixed overhead ≈ 10 bytes

TX_SIZE=$((148 * number_of_inputs + 34 * number_of_outputs + 10))
RECOMMENDED_FEE=$(echo "scale=8; $TX_SIZE * $FEERATE / 1000" | bc)

echo "Estimated fee: $RECOMMENDED_FEE BTC"
```

### Low-Fee vs High-Fee Transactions

```bash
# Conservative (higher fee, faster)
bitcoin-cli estimatesmartfee 1  # Next block

# Standard (medium fee)
bitcoin-cli estimatesmartfee 6  # ~1 hour

# Economy (lower fee, slower)
bitcoin-cli estimatesmartfee 144  # ~24 hours
```

---

## Complete Mainnet Transaction Example

```bash
#!/bin/bash
# Complete example: Send 0.1 BTC from your wallet to another address

set -e  # Exit on error

# Configuration
RECIPIENT="1A1z7agoatXxXxXxXxXxXxXxXxXxXxXxXx"
SEND_AMOUNT=0.1
FEE_RATE=0.00001  # BTC/byte

echo "=== Bitcoin Mainnet Transaction ==="

# Step 1: Verify balance
BALANCE=$(bitcoin-cli getbalance)
echo "Wallet balance: $BALANCE BTC"

if (( $(echo "$BALANCE < $SEND_AMOUNT" | bc -l) )); then
  echo "ERROR: Insufficient balance"
  exit 1
fi

# Step 2: List UTXOs
echo "Available UTXOs:"
bitcoin-cli listunspent 1 999999 | jq -r '.[] | "\(.txid): \(.amount) BTC (confirmations: \(.confirmations))"'

# Step 3: Send transaction
echo ""
echo "Sending $SEND_AMOUNT BTC to $RECIPIENT..."

TXID=$(bitcoin-cli sendtoaddress $RECIPIENT $SEND_AMOUNT)

echo ""
echo "✓ Transaction created: $TXID"
echo ""
echo "View on blockchain:"
echo "  Blockchain.com: https://blockchain.com/btc/tx/$TXID"
echo "  Blockchair.com: https://blockchair.com/bitcoin/transaction/$TXID"
echo ""
echo "Waiting for first confirmation..."

# Step 4: Wait for confirmation
while true; do
  CONFIRMATIONS=$(bitcoin-cli gettransaction $TXID | jq -r '.confirmations')
  if [ "$CONFIRMATIONS" -gt 0 ]; then
    echo "✓ Transaction confirmed! ($CONFIRMATIONS confirmations)"
    break
  fi
  echo "  Waiting... (checked at $(date '+%H:%M:%S'))"
  sleep 60
done

echo ""
echo "=== Transaction Complete ==="
```

---

## Troubleshooting

### Transaction Stuck (Low Fee)

```bash
# Use Replace-By-Fee (RBF) if enabled
bitcoin-cli bumpfee $TXID

# Or create a child transaction spending the same UTXO with higher fee
```

### "Insufficient Funds" Error

```bash
# Check actual balance
bitcoin-cli getbalance

# Account for unconfirmed transactions
bitcoin-cli getunconfirmedbalance

# Check immature coinbase rewards
bitcoin-cli getbalance "" 0  # Include unconfirmed
```

### Transaction Rejected

```bash
# Check if transaction is too large
TX_SIZE=$(echo -n "$RAW_TX" | wc -c)
echo "Transaction size: $((TX_SIZE/2)) bytes"  # Hex string is 2 chars per byte

# Standard block size allows ~1MB
# If > 100KB, may take longer to confirm
```

---

## Additional Resources

- **Bitcoin Core RPC**: https://developer.bitcoin.org/reference/rpc/
- **Transaction Fee Calculator**: https://bitcoinfees.earn.com
- **Blockchain Explorers**: 
  - Blockchain.com
  - Blockchair.com
  - Mempool.space
- **Bitcoin Developer Guide**: https://developer.bitcoin.org/
- **Security Best Practices**: https://developer.bitcoin.org/devguide/operating_modes.html

---

## ⚠️ Final Warnings

1. **Test First**: Always test transactions on testnet before mainnet
2. **Double-Check Addresses**: Typos in addresses cannot be recovered
3. **Backup Your Wallet**: Store backup in secure location
4. **Never Share Private Keys**: Even if someone claims to be support
5. **Use Hardware Wallets**: For storing significant amounts of Bitcoin
6. **Verify Fee**: Ensure fee is reasonable before broadcasting
7. **Keep Bitcoin Core Updated**: Security patches are important

---

*Last Updated: 2026-05-17*
*Remember: With great power comes great responsibility. Use this knowledge wisely.*
