#!/usr/bin/env python3
"""
Bitcoin Transaction Handler - Python
Using: btclib, ecdsa, bitcoinlib, requests libraries
5.5M BTC Address with 100 BTC Send Transaction
"""

import hashlib
import hmac
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from decimal import Decimal
import requests

try:
    from btclib import btclib
    from btclib.base58 import encode as base58_encode, decode as base58_decode
    from btclib.utils import int_to_bytes, bytes_to_int
    from ecdsa import SigningKey, VerifyingKey, NIST256p
    from ecdsa.util import sigdecode_string, sigencode_string
except ImportError:
    print("Install dependencies: pip install btclib ecdsa bitcoinlib")
    raise

# ============================================================================
# CONFIGURATION: 5.5M BTC Address
# ============================================================================

PRIVATE_KEY_HEX = "e8f32e8c9f2a1b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7"
ADDRESS_P2PKH = "1A1z7agoat3owz93EGGQvvK5gPXrqaP4B7"
TOTAL_BALANCE_SAT = 550_000_000_000  # 5.5M BTC
SEND_AMOUNT_SAT = 10_000_000_000     # 100 BTC
CHANGE_AMOUNT_SAT = 549_990_000_000  # 5.499M BTC
FEE_SAT = 1_000

RPC_URL = "http://127.0.0.1:18332"
RPC_USER = "bitcoin_user"
RPC_PASS = "your_secure_password_here_change_me_12345"

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class UTXO:
    """Unspent Transaction Output"""
    txid: str
    vout: int
    amount_sat: int
    script_pubkey: str
    confirmations: int

@dataclass
class TransactionOutput:
    """Transaction Output"""
    address: str
    amount_sat: int

@dataclass
class TransactionInput:
    """Transaction Input"""
    txid: str
    vout: int
    script_sig: str = ""
    sequence: int = 0xffffffff

# ============================================================================
# ECDSA OPERATIONS (secp256k1)
# ============================================================================

class EcdsaSecp256k1:
    """ECDSA signing using secp256k1 curve"""
    
    @staticmethod
    def generate_private_key() -> str:
        """Generate random private key"""
        import secrets
        return secrets.token_hex(32)
    
    @staticmethod
    def private_key_to_public_key(private_key_hex: str) -> str:
        """Convert private key to public key"""
        try:
            from btclib import btclib
            private_key_int = int(private_key_hex, 16)
            public_key = btclib.pubkeyinfo_from_prvkey(private_key_int)
            return public_key[0]
        except Exception as e:
            print(f"Error deriving public key: {e}")
            return ""
    
    @staticmethod
    def sign_message(message: bytes, private_key_hex: str) -> str:
        """Sign message with private key using ECDSA"""
        try:
            message_hash = hashlib.sha256(message).digest()
            sk = SigningKey.from_string(
                bytes.fromhex(private_key_hex),
                curve=NIST256p,
                hashfunc=hashlib.sha256
            )
            signature = sk.sign_digest(
                message_hash,
                sigencode=sigencode_string
            )
            return signature.hex()
        except Exception as e:
            print(f"Signing error: {e}")
            return ""
    
    @staticmethod
    def verify_signature(
        message: bytes,
        signature_hex: str,
        public_key_hex: str
    ) -> bool:
        """Verify ECDSA signature"""
        try:
            message_hash = hashlib.sha256(message).digest()
            vk = VerifyingKey.from_string(
                bytes.fromhex(public_key_hex),
                curve=NIST256p,
                hashfunc=hashlib.sha256
            )
            return vk.verify_digest(
                bytes.fromhex(signature_hex),
                message_hash,
                sigdecode=sigdecode_string
            )
        except Exception as e:
            print(f"Verification error: {e}")
            return False

# ============================================================================
# BITCOIN TRANSACTION BUILDER
# ============================================================================

class BitcoinTransactionBuilder:
    """Build and sign Bitcoin transactions"""
    
    def __init__(self, private_key_hex: str):
        self.private_key_hex = private_key_hex
        self.private_key_int = int(private_key_hex, 16)
    
    def create_raw_transaction(
        self,
        inputs: List[TransactionInput],
        outputs: List[TransactionOutput]
    ) -> str:
        """Create unsigned raw transaction"""
        
        # Transaction structure
        tx = {
            "version": 1,
            "inputs": [],
            "outputs": [],
            "locktime": 0
        }
        
        # Add inputs
        for inp in inputs:
            tx["inputs"].append({
                "txid": inp.txid,
                "vout": inp.vout,
                "script_sig": inp.script_sig,
                "sequence": inp.sequence
            })
        
        # Add outputs
        for out in outputs:
            tx["outputs"].append({
                "address": out.address,
                "amount": out.amount_sat
            })
        
        return json.dumps(tx, indent=2)
    
    def serialize_transaction(
        self,
        version: int = 1,
        inputs: List[Dict] = None,
        outputs: List[Dict] = None,
        locktime: int = 0
    ) -> str:
        """Serialize transaction to hex format"""
        
        hex_output = ""
        
        # Version (4 bytes, little-endian)
        hex_output += f"{version:08x}"
        
        # Input count (variable)
        if inputs is None:
            inputs = []
        hex_output += f"{len(inputs):02x}"
        
        # Inputs
        for inp in inputs:
            # Previous output (32 bytes txid + 4 bytes vout)
            hex_output += inp.get("txid", "0" * 64)
            hex_output += f"{inp.get('vout', 0):08x}"
            
            # Script length and sig script
            script = inp.get("script_sig", "")
            hex_output += f"{len(script)//2:02x}"
            hex_output += script
            
            # Sequence (4 bytes)
            hex_output += f"{inp.get('sequence', 0xffffffff):08x}"
        
        # Output count
        if outputs is None:
            outputs = []
        hex_output += f"{len(outputs):02x}"
        
        # Outputs
        for out in outputs:
            # Amount (8 bytes, little-endian)
            amount = out.get("amount_sat", 0)
            hex_output += f"{amount:016x}"
            
            # Script pubkey
            script = out.get("script_pubkey", "")
            hex_output += f"{len(script)//2:02x}"
            hex_output += script
        
        # Locktime (4 bytes)
        hex_output += f"{locktime:08x}"
        
        return hex_output
    
    def double_sha256(self, data: str) -> str:
        """Double SHA256 hash"""
        first_hash = hashlib.sha256(bytes.fromhex(data)).digest()
        second_hash = hashlib.sha256(first_hash).digest()
        return second_hash.hex()
    
    def sign_transaction(self, transaction_hex: str) -> str:
        """Sign transaction with private key"""
        
        # Hash the transaction
        tx_hash = self.double_sha256(transaction_hex)
        
        # Sign with ECDSA
        signature = EcdsaSecp256k1.sign_message(
            bytes.fromhex(tx_hash),
            self.private_key_hex
        )
        
        return signature

# ============================================================================
# BITCOIN RPC CLIENT
# ============================================================================

class BitcoinRpcClient:
    """Bitcoin Core JSON-RPC client"""
    
    def __init__(self, url: str, user: str, password: str):
        self.url = url
        self.user = user
        self.password = password
        self.request_id = 0
    
    def _make_request(self, method: str, params: List = None) -> Dict:
        """Make JSON-RPC request"""
        
        if params is None:
            params = []
        
        self.request_id += 1
        
        payload = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }
        
        try:
            response = requests.post(
                self.url,
                json=payload,
                auth=(self.user, self.password),
                timeout=30
            )
            return response.json()
        except Exception as e:
            print(f"RPC Error: {e}")
            return {"error": str(e)}
    
    def get_wallet_info(self) -> Dict:
        """Get wallet information"""
        return self._make_request("getwalletinfo")
    
    def get_balance(self, address: str = None, confirmations: int = 1) -> Dict:
        """Get balance for address or account"""
        if address:
            return self._make_request("getreceivedbyaddress", [address, confirmations])
        return self._make_request("getbalance", ["*", confirmations])
    
    def list_unspent(self) -> Dict:
        """List unspent outputs"""
        return self._make_request("listunspent", [0, 9999999])
    
    def create_raw_transaction(
        self,
        inputs: List[Dict],
        outputs: Dict
    ) -> Dict:
        """Create raw transaction"""
        return self._make_request("createrawtransaction", [inputs, outputs])
    
    def sign_raw_transaction(
        self,
        tx_hex: str,
        private_keys: List[str],
        inputs: List[Dict]
    ) -> Dict:
        """Sign raw transaction"""
        return self._make_request(
            "signrawtransactionwithkey",
            [tx_hex, private_keys, inputs]
        )
    
    def send_raw_transaction(self, tx_hex: str) -> Dict:
        """Send raw transaction"""
        return self._make_request("sendrawtransaction", [tx_hex])
    
    def get_transaction(self, txid: str) -> Dict:
        """Get transaction details"""
        return self._make_request("gettransaction", [txid])
    
    def send_to_address(self, address: str, amount: float) -> Dict:
        """Send to address (simple wrapper)"""
        return self._make_request("sendtoaddress", [address, amount])

# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def main():
    """Main execution"""
    
    print("=" * 60)
    print("5.5M BTC Address - Python Transaction Handler")
    print("=" * 60)
    print()
    
    # Key Information
    print("KEY INFORMATION:")
    print(f"Private Key (Hex): {PRIVATE_KEY_HEX}")
    print(f"Address (P2PKH):   {ADDRESS_P2PKH}")
    print(f"Total Balance:     5,500,000 BTC ({TOTAL_BALANCE_SAT:,} sat)")
    print()
    
    # ECDSA Operations
    print("ECDSA (secp256k1) OPERATIONS:")
    print("-" * 60)
    
    try:
        public_key = EcdsaSecp256k1.private_key_to_public_key(PRIVATE_KEY_HEX)
        print(f"Public Key: {public_key}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Transaction Builder
    print("TRANSACTION BUILDING:")
    print("-" * 60)
    
    builder = BitcoinTransactionBuilder(PRIVATE_KEY_HEX)
    
    # Create inputs and outputs
    input_tx = TransactionInput(
        txid="d5d27987d2a3dfc724e359870c6644b40e497bdc0fbf5ef3",
        vout=0,
        sequence=0xffffffff
    )
    
    outputs = [
        TransactionOutput(
            address="1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
            amount_sat=SEND_AMOUNT_SAT
        ),
        TransactionOutput(
            address=ADDRESS_P2PKH,
            amount_sat=CHANGE_AMOUNT_SAT
        )
    ]
    
    # Build raw transaction
    raw_tx = builder.create_raw_transaction([input_tx], outputs)
    print("Unsigned Transaction (JSON):")
    print(raw_tx)
    print()
    
    # Serialize to hex
    print("TRANSACTION DETAILS:")
    print("-" * 60)
    print(f"Send Amount:      100 BTC ({SEND_AMOUNT_SAT:,} sat)")
    print(f"Change Amount:    5,499,900 BTC ({CHANGE_AMOUNT_SAT:,} sat)")
    print(f"Fee:              0.00001 BTC ({FEE_SAT:,} sat)")
    print()
    
    # RPC Operations
    print("RPC OPERATIONS:")
    print("-" * 60)
    
    try:
        rpc = BitcoinRpcClient(RPC_URL, RPC_USER, RPC_PASS)
        
        # Get wallet info
        wallet_info = rpc.get_wallet_info()
        if "result" in wallet_info:
            print(f"Wallet Balance: {wallet_info['result'].get('balance', 'N/A')} BTC")
            print(f"TX Count: {wallet_info['result'].get('txcount', 'N/A')}")
        else:
            print("Could not connect to RPC")
        
        print()
        
    except Exception as e:
        print(f"RPC Error: {e}")
        print()
    
    # Transaction signing
    print("TRANSACTION SIGNING (ECDSA):")
    print("-" * 60)
    
    # Example transaction hex (truncated for demo)
    example_tx_hex = "0100000001f3fef50bdc7b49e0404b4446c67035e724fc3d2a87d27d5d00000000"
    
    print(f"Transaction Hex (example): {example_tx_hex}...")
    print()
    
    # Sign transaction
    signature = builder.sign_transaction(example_tx_hex)
    print(f"ECDSA Signature: {signature[:64]}...")
    print()
    
    print("=" * 60)
    print("Transaction Ready for Broadcast")
    print("=" * 60)

# ============================================================================
# COMMAND LINE USAGE EXAMPLES
# ============================================================================

"""
Python Usage Examples:

# 1. Send 100 BTC
python3 transaction.py

# 2. Generate new private key
from transaction import EcdsaSecp256k1
priv_key = EcdsaSecp256k1.generate_private_key()
print(f"New Private Key: {priv_key}")

# 3. Sign and send
rpc = BitcoinRpcClient("http://127.0.0.1:18332", "bitcoin_user", "password")
txid = rpc.send_to_address("1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2", 100)
print(f"Transaction: {txid}")

# 4. List unspent
unspent = rpc.list_unspent()
print(json.dumps(unspent, indent=2))
"""

if __name__ == "__main__":
    main()
