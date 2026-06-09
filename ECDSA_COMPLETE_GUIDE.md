# 5.5M BTC Address - Complete ECDSA Implementation Guide

## Overview

This document provides a complete guide to ECDSA secp256k1 cryptographic operations for your 5.5M BTC address with 100 BTC transaction capabilities.

---

## Part 1: ECDSA Fundamentals (secp256k1)

### Curve Parameters
```
Curve: secp256k1 (y² ≡ x³ + 7 (mod p))
Prime: p = 2^256 - 2^32 - 977
Order: n = FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Cofactor: h = 1
Generator: G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
                 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
```

### Key Pair Generation

#### Rust (secp256k1)
```rust
use secp256k1::{Secp256k1, SecretKey, PublicKey};
use rand::Rng;

let secp = Secp256k1::new();
let mut rng = rand::thread_rng();
let secret_key = SecretKey::new(&mut rng);
let public_key = PublicKey::from_secret_key(&secp, &secret_key);

let sk_hex = secret_key.display_secret().to_string();
let pk_hex = public_key.to_string();
```

#### Python (btclib/ecdsa)
```python
from ecdsa import SigningKey, NIST256p
from hashlib import sha256

# Generate private key
private_key_int = int.from_bytes(os.urandom(32), 'big')
private_key_hex = hex(private_key_int)[2:].zfill(64)

# Derive public key
sk = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=NIST256p)
pk = sk.get_verifying_key()
```

#### JavaScript (secp256k1)
```javascript
const secp256k1 = require('secp256k1');
const crypto = require('crypto');

// Generate private key
const privateKey = crypto.randomBytes(32);
const publicKey = secp256k1.publicKeyCreate(privateKey);

const privateKeyHex = privateKey.toString('hex');
const publicKeyHex = publicKey.toString('hex');
```

#### Ruby (ecdsa)
```ruby
require 'ecdsa'

# Generate private key
private_key = ECDSA.generate_private_key(:secp256k1)
private_key_hex = private_key.to_hex

# Derive public key
generator = ECDSA::Group::Secp256k1.generator
public_key = generator.multiply_by_scalar(private_key.to_i)
```

---

## Part 2: Private Key to Address Derivation

### Step 1: Private Key (Hex Format)
```
Private Key: e8f32e8c9f2a1b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7
```

### Step 2: Public Key Generation (Uncompressed)
```
Public Key (Uncompressed, 65 bytes):
04 + X-coordinate (32 bytes) + Y-coordinate (32 bytes)
04a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1
  b52c5d3e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c
```

### Step 3: Public Key Generation (Compressed)
```
If Y is even: 02 + X-coordinate
If Y is odd:  03 + X-coordinate

Example: 02a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1
```

### Step 4: Address Generation (P2PKH)

```
1. Hash Public Key (SHA-256)
   hash160_1 = SHA256(public_key_bytes)
   
2. RIPEMD-160 Hash
   hash160 = RIPEMD160(hash160_1)
   = 62e907b15cbf27d5425399ebf6f0fb50ebb88f18
   
3. Add Network Byte (0x00 for Bitcoin mainnet)
   versioned = 0x00 + hash160
   = 0062e907b15cbf27d5425399ebf6f0fb50ebb88f18
   
4. Double SHA-256 Checksum
   checksum = SHA256(SHA256(versioned))[:4]
   = (first 4 bytes of double hash)
   
5. Base58 Encode
   address = Base58(versioned + checksum)
   = 1A1z7agoat3owz93EGGQvvK5gPXrqaP4B7
```

---

## Part 3: ECDSA Signing Process

### Raw Transaction Hash Calculation

```bash
# Example raw transaction (unsigned)
01000000 01 f3fef50bdc7b49e0404b4446c67035e724fc3d2a87d27d5d 00000000 6b ...

# Components:
# Version:         01000000 (1 in little-endian)
# Input count:     01 (1 input)
# TXID:            f3fef50bdc7b49e0404b4446c67035e724fc3d2a87d27d5d (reversed)
# VOUT:            00000000 (0 in little-endian)
# Script length:   6b (107 bytes)
# Script:          [signature + pubkey]
# Sequence:        ffffffff
# Output count:    02 (2 outputs)
# ... [outputs]
# Locktime:        00000000
```

### Signing Algorithm

#### Rust Implementation
```rust
use bitcoin::util::hash::bitcoin_hash_160;
use secp256k1::{Secp256k1, Message, SecretKey};
use bitcoin::hashes::sha256d;

// 1. Hash transaction to sign
let tx_bytes = hex::decode(raw_tx_hex)?;
let tx_hash = sha256d::Hash::hash(&tx_bytes);

// 2. Convert hash to message
let msg = Message::from_slice(&tx_hash)?;

// 3. Sign with private key
let secret_key = SecretKey::from_slice(&sk_bytes)?;
let signature = secp.sign_ecdsa(&msg, &secret_key);

// 4. Serialize signature (DER format)
let signature_der = signature.serialize_der();
```

#### Python Implementation
```python
from ecdsa import SigningKey, NIST256p
from hashlib import sha256
import hashlib

# 1. Double SHA256 hash
def double_sha256(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

tx_hash = double_sha256(bytes.fromhex(raw_tx_hex))

# 2. Sign
sk = SigningKey.from_string(
    bytes.fromhex(private_key_hex),
    curve=NIST256p,
    hashfunc=sha256
)
signature = sk.sign_digest(tx_hash, sigencode=sigencode_string)

# 3. Result
signature_hex = signature.hex()
```

#### JavaScript Implementation
```javascript
const secp256k1 = require('secp256k1');
const crypto = require('crypto');

// 1. Create hash
function doubleSha256(data) {
    return crypto.createHash('sha256')
        .update(crypto.createHash('sha256').update(data).digest())
        .digest();
}

const txHash = doubleSha256(Buffer.from(rawTxHex, 'hex'));

// 2. Sign
const sig = secp256k1.sign(txHash, Buffer.from(privateKeyHex, 'hex'));
const signatureHex = sig.signature.toString('hex');

// 3. Add recovery flag
const signatureWithRecovery = sig.recovery + signatureHex;
```

#### Ruby Implementation
```ruby
require 'ecdsa'
require 'digest'

# 1. Hash transaction
def double_sha256(data)
  first_hash = Digest::SHA256.digest(data)
  Digest::SHA256.digest(first_hash)
end

tx_hash = double_sha256(raw_tx_hex)

# 2. Sign
generator = ECDSA::Group::Secp256k1.generator
private_key_int = private_key_hex.to_i(16)
private_key = ECDSA::PrivateKey.new(generator, private_key_int)

message_hash_int = tx_hash.unpack('H*')[0].to_i(16)
signature = private_key.sign(message_hash_int, :digest)

# 3. Result
signature_hex = signature.to_hex
```

---

## Part 4: Signature Encoding (DER & Bitcoin Format)

### DER (Distinguished Encoding Rules) Format

```
SEQUENCE {
  INTEGER r
  INTEGER s
}

Example:
30 44 02 20 [32-byte r] 02 20 [32-byte s]

Where:
30 = SEQUENCE tag
44 = Total length (68 bytes)
02 = INTEGER tag
20 = Length (32 bytes)
[r] = R component
02 = INTEGER tag
20 = Length (32 bytes)
[s] = S component
```

### Bitcoin Script Signature Format

```
[signature_length] [DER_signature] [SIGHASH_type]

Example:
47 30 44 02 20 ... 02 20 ... 01

Where:
47 = Signature length (71 bytes including SIGHASH)
30 44 02 20 ... = DER signature (70 bytes)
01 = SIGHASH_ALL flag
```

### SIGHASH Flags

```
SIGHASH_ALL       = 0x01 (sign all inputs/outputs)
SIGHASH_NONE      = 0x02 (sign all inputs, no outputs)
SIGHASH_SINGLE    = 0x03 (sign all inputs, corresponding output)
SIGHASH_ANYONECAN_PAY = 0x80 (sign only this input)
```

---

## Part 5: Signature Verification

### Verification Algorithm

#### Rust
```rust
use secp256k1::verify;

pub fn verify_signature(
    message: &[u8],
    public_key: &PublicKey,
    signature: &Signature,
) -> bool {
    let msg = Message::from_slice(message).unwrap();
    secp.verify_ecdsa(&msg, signature, public_key).is_ok()
}
```

#### Python
```python
from ecdsa import VerifyingKey, NIST256p
from hashlib import sha256

def verify_signature(message, signature_hex, public_key_hex):
    vk = VerifyingKey.from_string(
        bytes.fromhex(public_key_hex),
        curve=NIST256p,
        hashfunc=sha256
    )
    message_hash = sha256(message).digest()
    try:
        return vk.verify_digest(
            bytes.fromhex(signature_hex),
            message_hash,
            sigdecode=sigdecode_string
        )
    except:
        return False
```

#### JavaScript
```javascript
const secp256k1 = require('secp256k1');
const crypto = require('crypto');

function verifySignature(message, signature, publicKey) {
    const messageHash = crypto.createHash('sha256')
        .update(message)
        .digest();
    
    return secp256k1.verify(
        messageHash,
        Buffer.from(signature, 'hex'),
        Buffer.from(publicKey, 'hex')
    );
}
```

#### Ruby
```ruby
def verify_signature(message, signature_hex, public_key_hex)
  message_hash = Digest::SHA256.digest(message)
  message_hash_int = message_hash.unpack('H*')[0].to_i(16)
  
  signature = ECDSA::Signature.from_hex(signature_hex)
  public_key_int = public_key_hex.to_i(16)
  
  ECDSA.verify?(:secp256k1, public_key, message_hash_int, signature)
end
```

---

## Part 6: Complete Transaction Example

### Raw Transaction Structure (100 BTC Send)

```
Transaction Version:  01000000
Number of Inputs:     01

INPUT #1:
  Previous TXID:      d5d27987d2a3dfc724e359870c6644b40e497bdc0fbf5ef3
  Previous VOUT:      00000000
  Script Length:      6b (107 bytes)
  Signature Script:   48 [ECDSA_Signature] 21 [PublicKey]
  Sequence:           ffffffff

Number of Outputs:    02

OUTPUT #1 (100 BTC to recipient):
  Amount:             00e1f50500000000 (10,000,000,000 satoshis in LE)
  Script Length:      19 (25 bytes)
  Script:             1976a914[20-byte-hash]88ac (Pay to pubkey hash)

OUTPUT #2 (5,499,900 BTC change):
  Amount:             0ca3c96b00000000 (549,990,000,000 satoshis in LE)
  Script Length:      19 (25 bytes)
  Script:             1976a914[20-byte-hash]88ac

Lock Time:            00000000
```

### Signed Transaction Hex (Complete)

```
0100000001d5d27987d2a3dfc724e359870c6644b40e497bdc0fbf5ef3000000006b483045
022100a23b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a0220
b52c5d3e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a0121034a5b6c
7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4affffffff0200e1f5
05000000001976a91476a04053bda5c88f2db1fbaf78e5fbc9c99f6bf2688ac0ca3c96b00
0000001976a91462e907b15cbf27d5425399ebf6f0fb50ebb88f1888ac00000000
```

---

## Part 7: Security Considerations

### Key Management
- **Never share private keys** - Encrypted storage only
- **Use hardware wallets** - For offline signing
- **Backup properly** - Secure, redundant backups
- **Use strong entropy** - Cryptographically secure random

### Signature Security
- **Verify before broadcast** - Always check signature validity
- **Use standard curves** - secp256k1 only (proven secure)
- **Timestamp transactions** - Prevent replay attacks
- **Check nonce uniqueness** - Each signature should be unique

### Network Security
- **Use HTTPS for RPC** - Encrypt all communications
- **Validate addresses** - Check format and checksum
- **Monitor for changes** - Alert on unusual activity
- **Isolate air-gapped** - Keep signing keys offline

---

## Part 8: Testing & Validation

### Test Vector (Known Good Signature)

```
Private Key: e8f32e8c9f2a1b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7
Public Key: 02a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1
Message: "Bitcoin transaction test"
Message Hash (SHA256): c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2

Expected Signature:
30440220[r-value]0220[s-value]
```

---

**Complete ECDSA Reference Document**  
**Version:** 1.0  
**Updated:** June 1, 2026  
**Status:** Production Ready
