# Mempool.space Integration Guide

## Real-Time Bitcoin Fee Monitoring & Transaction Tracking

Get live fee data, track transactions, and monitor the mempool using mempool.space API.

---

## Quick Start

### Get Current Fees

```python
import requests

API = "https://mempool.space/api"

# Get current fee rates
fees = requests.get(f"{API}/v1/fees/recommended").json()

print(f"Fastest (next block): {fees['fastestFee']} sat/vB")
print(f"Half-hour: {fees['halfHourFee']} sat/vB")
print(f"1 hour: {fees['hourFee']} sat/vB")
print(f"Economy: {fees['economyFee']} sat/vB")
```

**Output:**
```
Fastest (next block): 8 sat/vB
Half-hour: 8 sat/vB
1 hour: 8 sat/vB
Economy: 4 sat/vB
```

### Estimate Transaction Fee

```python
def estimate_fee(inputs, outputs, rate_sat_vb, segwit=True):
    """Calculate transaction fee"""
    if segwit:
        # SegWit: ~68 bytes per input, ~31 per output
        vsize = int(10.75 + (68 * inputs) + (31 * outputs))
    else:
        # P2PKH: ~148 bytes per input, ~34 per output
        vsize = 10 + (148 * inputs) + (34 * outputs)
    
    fee_sat = vsize * rate_sat_vb
    fee_btc = fee_sat / 1e8
    
    return {
        "vsize": vsize,
        "fee_sat": fee_sat,
        "fee_btc": fee_btc
    }

# Example: 2 inputs, 2 outputs, SegWit
estimate = estimate_fee(2, 2, 8)  # 8 sat/vB
print(f"vSize: {estimate['vsize']} vB")
print(f"Fee: {estimate['fee_btc']:.8f} BTC")
```

---

## API Endpoints

### Fee Estimation

```
GET https://mempool.space/api/v1/fees/recommended

Response:
{
  "fastestFee": 8,
  "halfHourFee": 8,
  "hourFee": 8,
  "economyFee": 4,
  "minimumFee": 2
}
```

### Get Transaction Status

```
GET https://mempool.space/api/tx/{txid}/status

Response:
{
  "confirmed": true/false,
  "block_height": 837043,
  "block_hash": "0000...",
  "block_time": 1711850338
}
```

### Get Address UTXOs

```
GET https://mempool.space/api/address/{address}/utxo

Response: [
  {
    "txid": "...",
    "vout": 0,
    "value": 1000000,
    "status": {
      "confirmed": true,
      "block_height": 837040
    }
  }
]
```

### Get Recent Blocks

```
GET https://mempool.space/api/blocks

Response: [
  {
    "id": "000...",
    "height": 837050,
    "timestamp": 1711854927,
    "tx_count": 2659,
    "size": 2137871,
    "weight": 3992678,
    "extras": {
      "medianFee": 8.97,
      "totalFees": 10929414
    }
  }
]
```

### Get Mempool Info

```
GET https://mempool.space/api/mempool

Response:
{
  "loaded": true,
  "size": 112686,           # tx count
  "bytes": 175691391,       # total bytes
  "usage": 856780672,       # memory usage
  "total_fee": 5.10536864,  # total fees (BTC)
  "maxmempool": 300000000,  # max size
  "mempoolminfee": 0.00001305,
  "vBytesPerSecond": 2364
}
```

### Broadcast Transaction

```
POST https://mempool.space/api/tx
Content-Type: application/x-www-form-urlencoded

Request body: signed_tx_hex

Response: txid (on success)
```

---

## Fee Calculation Examples

### P2PKH (Legacy)

```python
inputs = 2
outputs = 2
rate = 8  # sat/vB

# P2PKH formula: 10 + (148 * inputs) + (34 * outputs)
vsize = 10 + (148 * inputs) + (34 * outputs)
# vsize = 10 + 296 + 68 = 374 bytes

fee_sat = 374 * 8 = 2992 sats
fee_btc = 2992 / 1e8 = 0.00002992 BTC
```

### SegWit (P2WPKH)

```python
inputs = 2
outputs = 2
rate = 8  # sat/vB

# SegWit formula: 10.75 + (68 * inputs) + (31 * outputs)
vsize = int(10.75 + (68 * inputs) + (31 * outputs))
# vsize = 10.75 + 136 + 62 = ~209 vB

fee_sat = 209 * 8 = 1672 sats
fee_btc = 1672 / 1e8 = 0.00001672 BTC

# SegWit saves ~30% compared to P2PKH!
```

### Comparison

| Type | 2-in/2-out | @8 sat/vB |
|------|-----------|-----------|
| P2PKH | 374 vB | 0.00002992 BTC |
| SegWit | 209 vB | 0.00001672 BTC |
| Savings | 44% smaller | 44% cheaper |

---

## Monitor Transaction

```python
import time
import requests

def monitor_tx(txid, max_checks=60):
    """Monitor until confirmed"""
    api = "https://mempool.space/api"
    
    for check in range(max_checks):
        status = requests.get(f"{api}/tx/{txid}/status").json()
        
        if status.get("confirmed"):
            print(f"✅ CONFIRMED at block {status['block_height']}")
            return status
        
        print(f"⏳ Attempt {check+1}: Unconfirmed")
        time.sleep(10)  # Wait 10 seconds
    
    print("⚠️ Transaction not confirmed after", max_checks * 10, "seconds")
    return None
```

---

## Real-Time Fee Watcher

```python
import time
import requests

def watch_fees(interval=60, duration=300):
    """Watch fees over time"""
    api = "https://mempool.space/api/v1/fees/recommended"
    
    start = time.time()
    while time.time() - start < duration:
        fees = requests.get(api).json()
        
        print(f"⚡ {fees['fastestFee']} | ⏱️ {fees['halfHourFee']} | 🐢 {fees['economyFee']} sat/vB")
        time.sleep(interval)

# Watch fees every 60 seconds for 5 minutes
watch_fees(60, 300)
```

---

## Use in Transaction Builder

```python
from transaction_builder import build_and_broadcast
from mempool_api import get_fees, estimate_fee

# Get current fees
fees = get_fees()
recommended_rate = fees['halfHourFee']

# Estimate cost for your tx
estimate = estimate_fee(2, 2, recommended_rate)
print(f"Estimated fee: {estimate['fee_btc']:.8f} BTC")

# Check balance is sufficient
if wallet_balance > estimate['fee_btc']:
    # Build and broadcast
    build_and_broadcast(...)
else:
    print("❌ Insufficient balance")
```

---

## Networks

### Mainnet
- API: `https://mempool.space/api`
- Explorer: `https://mempool.space/`

### Testnet
- API: `https://mempool.space/testnet/api`
- Explorer: `https://mempool.space/testnet`

### Signet
- API: `https://mempool.space/signet/api`
- Explorer: `https://mempool.space/signet`

---

## Rate Limits

- **Free tier**: 10 req/sec (unauthenticated)
- **Recommended**: 5 requests/minute for polling

---

## Best Practices

✅ **DO:**
- Cache fee data (update every 30-60 seconds)
- Add buffer to estimated fees (5-10% extra)
- Check address UTXOs before building transaction
- Monitor high-value transactions until confirmed

❌ **DON'T:**
- Poll fees faster than every 10 seconds
- Trust unconfirmed transaction amounts
- Send below minimum fee (`minimumFee`)
- Broadcast identical transactions multiple times

---

## Resources

- **API Docs**: https://mempool.space/api
- **GitHub**: https://github.com/mempool/mempool
- **Status**: https://mempool.space/
- **Fee Chart**: https://mempool.space/graphs/mempool#24h

---

*Last Updated: 2026-05-17*
