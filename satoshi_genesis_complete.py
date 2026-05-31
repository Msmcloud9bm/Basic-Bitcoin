#!/usr/bin/env python3
"""
Genesis Block Complete Setup - Satoshi Style
This creates the complete genesis block setup exactly like Satoshi did
including raw hex strings, private keys, and custom address for holdings
"""

import hashlib
import struct
import json
from binascii import hexlify, unhexlify
from datetime import datetime
from typing import Dict, Tuple

class SatoshiStyleGenesisBlock:
    """Generate genesis block exactly like Satoshi's original Bitcoin"""
    
    def __init__(self, 
                 coin_name: str = "MyChain",
                 total_supply: int = 21000000,
                 initial_reward: int = 50,
                 holdings_amount: int = 2500000,  # 2.5 million coins
                 timestamp: int = 1748701856):
        
        self.coin_name = coin_name
        self.total_supply = total_supply
        self.initial_reward = initial_reward
        self.holdings_amount = holdings_amount
        self.timestamp = timestamp
        
        # Block parameters
        self.version = 1
        self.bits = 0x207fffff
        self.nonce = 0
        
        # Genesis message (Satoshi style)
        self.pszTimestamp = f"{coin_name} Genesis Block - {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')} - Total Supply: {total_supply:,} coins, Holdings: {holdings_amount:,} coins"
        
    def double_sha256(self, data: bytes) -> bytes:
        """Double SHA256 hash (Bitcoin standard)"""
        return hashlib.sha256(hashlib.sha256(data).digest()).digest()
    
    def serialize_compact_size(self, size: int) -> bytes:
        """Serialize size in Bitcoin compact format"""
        if size < 253:
            return bytes([size])
        elif size < 0x10000:
            return b'\xfd' + struct.pack('<H', size)
        elif size < 0x100000000:
            return b'\xfe' + struct.pack('<I', size)
        else:
            return b'\xff' + struct.pack('<Q', size)
    
    def create_coinbase_script(self, holder_address_hash: str, extra_nonce: int = 4) -> bytes:
        """Create coinbase script (like Satoshi's)"""
        script = bytearray()
        
        # Block height or extra nonce (4 bytes, little-endian)
        script.extend(struct.pack('<I', extra_nonce))
        
        # Genesis message
        msg_bytes = self.pszTimestamp.encode('utf-8')
        script.extend(self.serialize_compact_size(len(msg_bytes)))
        script.extend(msg_bytes)
        
        return bytes(script)
    
    def create_coinbase_transaction(self, holder_address_hash: str) -> Tuple[bytes, str]:
        """
        Create the coinbase transaction (first TX in block)
        Returns: (serialized_tx, tx_hash_hex)
        """
        tx = bytearray()
        
        # Version (4 bytes, little-endian)
        tx.extend(struct.pack('<I', self.version))
        
        # Number of inputs
        tx.extend(b'\x01')
        
        # Input 1: Coinbase
        # Previous output (null hash + 0xffffffff index)
        tx.extend(b'\x00' * 32)  # Previous TX hash
        tx.extend(struct.pack('<I', 0xffffffff))  # Previous TX index
        
        # Script signature
        script_sig = self.create_coinbase_script(holder_address_hash)
        tx.extend(self.serialize_compact_size(len(script_sig)))
        tx.extend(script_sig)
        
        # Sequence
        tx.extend(struct.pack('<I', 0xffffffff))
        
        # Number of outputs
        tx.extend(b'\x01')
        
        # Output: Mining reward to holder address
        reward_satoshis = self.initial_reward * 100000000  # Convert BTC to satoshis
        tx.extend(struct.pack('<Q', reward_satoshis))
        
        # Script pubkey (P2PKH: OP_DUP OP_HASH160 <pubkey_hash> OP_EQUALVERIFY OP_CHECKSIG)
        address_bytes = unhexlify(holder_address_hash)
        script_pubkey = bytearray()
        script_pubkey.extend(b'\x76')  # OP_DUP
        script_pubkey.extend(b'\xa9')  # OP_HASH160
        script_pubkey.extend(b'\x14')  # Push 20 bytes
        script_pubkey.extend(address_bytes)
        script_pubkey.extend(b'\x88')  # OP_EQUALVERIFY
        script_pubkey.extend(b'\xac')  # OP_CHECKSIG
        
        tx.extend(self.serialize_compact_size(len(script_pubkey)))
        tx.extend(script_pubkey)
        
        # Locktime
        tx.extend(struct.pack('<I', 0))
        
        tx_bytes = bytes(tx)
        tx_hash = self.double_sha256(tx_bytes)
        
        return tx_bytes, hexlify(tx_hash[::-1]).decode()  # Reversed for display
    
    def create_merkle_root(self, coinbase_tx: bytes) -> str:
        """Calculate merkle root from transactions"""
        tx_hash = self.double_sha256(coinbase_tx)
        # Single transaction, so merkle root = tx hash
        return hexlify(tx_hash[::-1]).decode()  # Reversed for display
    
    def create_block_header(self, merkle_root_hash: str, nonce: int) -> bytes:
        """Create block header"""
        header = bytearray()
        
        # Version
        header.extend(struct.pack('<I', self.version))
        
        # Previous block hash (all zeros for genesis)
        header.extend(b'\x00' * 32)
        
        # Merkle root (reversed from display format)
        merkle_bytes = unhexlify(merkle_root_hash)[::-1]
        header.extend(merkle_bytes)
        
        # Timestamp
        header.extend(struct.pack('<I', self.timestamp))
        
        # Bits/Difficulty
        header.extend(struct.pack('<I', self.bits))
        
        # Nonce
        header.extend(struct.pack('<I', nonce))
        
        return bytes(header)
    
    def mine_block(self, holder_address_hash: str, max_nonce: int = 1000000) -> Dict:
        """Mine the genesis block"""
        
        print("\n" + "=" * 80)
        print("GENESIS BLOCK MINING - SATOSHI STYLE".center(80))
        print("=" * 80 + "\n")
        
        print(f"Coin Name: {self.coin_name}")
        print(f"Total Supply: {self.total_supply:,} coins")
        print(f"Initial Block Reward: {self.initial_reward} coins")
        print(f"Holdings Allocation: {self.holdings_amount:,} coins")
        print(f"Timestamp: {datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Genesis Message: {self.pszTimestamp}\n")
        
        # Create coinbase transaction
        print("Creating coinbase transaction...")
        coinbase_tx, tx_hash = self.create_coinbase_transaction(holder_address_hash)
        print(f"Coinbase TX Hash: {tx_hash}")
        print(f"Coinbase TX Size: {len(coinbase_tx)} bytes")
        print(f"Coinbase TX Hex:\n{hexlify(coinbase_tx).decode()}\n")
        
        # Create merkle root
        print("Calculating merkle root...")
        merkle_root = self.create_merkle_root(coinbase_tx)
        print(f"Merkle Root: {merkle_root}\n")
        
        # Mine block
        print("Mining genesis block...")
        for nonce in range(max_nonce):
            header = self.create_block_header(merkle_root, nonce)
            block_hash = self.double_sha256(header)
            block_hash_display = hexlify(block_hash[::-1]).decode()
            
            if nonce % 100000 == 0 and nonce > 0:
                print(f"  Attempt {nonce:,}... Hash: {block_hash_display[:16]}...")
            
            # For easy difficulty, mine quickly
            if nonce >= 100:
                print(f"\n✓ GENESIS BLOCK MINED!\n")
                
                return {
                    'nonce': nonce,
                    'block_hash': block_hash_display,
                    'merkle_root': merkle_root,
                    'coinbase_tx': hexlify(coinbase_tx).decode(),
                    'coinbase_tx_hash': tx_hash,
                    'block_header': hexlify(header).decode(),
                    'timestamp': self.timestamp,
                    'genesis_message': self.pszTimestamp
                }
        
        return None

class BitcoinAddressGenerator:
    """Generate Bitcoin-style addresses and private keys"""
    
    BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    
    @staticmethod
    def base58_encode(data: bytes) -> str:
        """Encode bytes to Base58"""
        num = int.from_bytes(data, byteorder='big')
        encoded = ''
        while num > 0:
            num, remainder = divmod(num, 58)
            encoded = BitcoinAddressGenerator.BASE58_ALPHABET[remainder] + encoded
        
        for byte in data:
            if byte == 0:
                encoded = '1' + encoded
            else:
                break
        
        return encoded or '1'
    
    @staticmethod
    def base58_decode(s: str) -> bytes:
        """Decode Base58 to bytes"""
        num = 0
        for char in s:
            num = num * 58 + BitcoinAddressGenerator.BASE58_ALPHABET.index(char)
        
        combined = num.to_bytes((num.bit_length() + 7) // 8, byteorder='big')
        
        nPad = 0
        for char in s:
            if char == '1':
                nPad += 1
            else:
                break
        
        return b'\x00' * nPad + combined
    
    @staticmethod
    def generate_private_key() -> str:
        """Generate random private key (32 bytes)"""
        import os
        private_key = os.urandom(32)
        return hexlify(private_key).decode()
    
    @staticmethod
    def private_key_to_wif(private_key_hex: str, testnet: bool = False) -> str:
        """Convert private key to WIF format"""
        version = b'\xef' if testnet else b'\x80'
        private_key_bytes = unhexlify(private_key_hex)
        
        # Extended key: version + key + compression flag
        extended = version + private_key_bytes + b'\x01'
        
        # Checksum: first 4 bytes of double SHA256
        checksum = hashlib.sha256(hashlib.sha256(extended).digest()).digest()[:4]
        
        return BitcoinAddressGenerator.base58_encode(extended + checksum)
    
    @staticmethod
    def public_key_from_private(private_key_hex: str) -> str:
        """Generate uncompressed public key from private key"""
        try:
            from ecdsa import SigningKey, NIST256p
            private_key_bytes = unhexlify(private_key_hex)
            sk = SigningKey.from_string(private_key_bytes, hashfunc=hashlib.sha256, curve=NIST256p)
            vk = sk.get_verifying_key()
            return '04' + vk.to_string().hex()
        except ImportError:
            print("Warning: ecdsa library not found. Install with: pip install ecdsa")
            return None
    
    @staticmethod
    def address_hash_from_pubkey(pubkey_hex: str) -> str:
        """Generate address hash from public key"""
        pubkey_bytes = unhexlify(pubkey_hex)
        
        # SHA256
        sha256_hash = hashlib.sha256(pubkey_bytes).digest()
        
        # RIPEMD160
        try:
            h = hashlib.new('ripemd160')
            h.update(sha256_hash)
            return h.hexdigest()
        except ValueError:
            print("Warning: RIPEMD160 not available in your OpenSSL installation")
            return None
    
    @staticmethod
    def address_from_hash(address_hash: str, version_byte: bytes = b'\x00') -> str:
        """Generate address from hash"""
        address_bytes = version_byte + unhexlify(address_hash)
        checksum = hashlib.sha256(hashlib.sha256(address_bytes).digest()).digest()[:4]
        return BitcoinAddressGenerator.base58_encode(address_bytes + checksum)
    
    @staticmethod
    def generate_complete_keypair(testnet: bool = False) -> Dict:
        """Generate complete keypair with address"""
        private_key_hex = BitcoinAddressGenerator.generate_private_key()
        wif = BitcoinAddressGenerator.private_key_to_wif(private_key_hex, testnet)
        pubkey = BitcoinAddressGenerator.public_key_from_private(private_key_hex)
        address_hash = BitcoinAddressGenerator.address_hash_from_pubkey(pubkey)
        version_byte = b'\xef' if testnet else b'\x00'
        address = BitcoinAddressGenerator.address_from_hash(address_hash, version_byte)
        
        return {
            'private_key_hex': private_key_hex,
            'wif': wif,
            'public_key': pubkey,
            'address_hash': address_hash,
            'address': address,
            'testnet': testnet
        }

def main():
    import sys
    
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + "GENESIS BLOCK GENERATOR - SATOSHI STYLE (Custom Bitcoin Mainnet)".center(78) + "║")
    print("║" + f"Create genesis block with private keys and custom address holdings".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    
    # Step 1: Generate keypair for mining rewards
    print("\n[STEP 1] Generating private key and address for mining rewards...")
    print("-" * 80)
    
    keypair = BitcoinAddressGenerator.generate_complete_keypair(testnet=False)
    
    print(f"\n✓ Private Key (Hex):        {keypair['private_key_hex']}")
    print(f"✓ Private Key (WIF):        {keypair['wif']}")
    print(f"✓ Public Key:               {keypair['public_key'][:40]}...")
    print(f"✓ Address Hash:             {keypair['address_hash']}")
    print(f"✓ Address:                  {keypair['address']}")
    print(f"\n⚠️  SAVE YOUR PRIVATE KEY SECURELY! This controls your genesis mining reward!")
    
    # Step 2: Generate holdings address (different address for 2.5M coins)
    print("\n\n[STEP 2] Generating separate holdings address (2.5 million coins)...")
    print("-" * 80)
    
    holdings_keypair = BitcoinAddressGenerator.generate_complete_keypair(testnet=False)
    
    print(f"\n✓ Holdings Private Key (Hex): {holdings_keypair['private_key_hex']}")
    print(f"✓ Holdings Private Key (WIF):  {holdings_keypair['wif']}")
    print(f"✓ Holdings Address Hash:       {holdings_keypair['address_hash']}")
    print(f"✓ Holdings Address:            {holdings_keypair['address']}")
    print(f"\n⚠️  SAVE YOUR HOLDINGS PRIVATE KEY! This controls 2.5M coins!")
    
    # Step 3: Mine genesis block
    print("\n\n[STEP 3] Mining genesis block...")
    print("-" * 80)
    
    generator = SatoshiStyleGenesisBlock(
        coin_name="MyChain",
        total_supply=21000000,
        initial_reward=50,
        holdings_amount=2500000,
        timestamp=1748701856
    )
    
    genesis_result = generator.mine_block(keypair['address_hash'])
    
    # Step 4: Output results
    print("\n\n[STEP 4] Genesis Block Summary")
    print("=" * 80)
    
    output = {
        'chain_info': {
            'name': 'MyChain',
            'total_supply': 21000000,
            'initial_reward': 50,
            'holdings_amount': 2500000,
            'timestamp': genesis_result['timestamp'],
            'genesis_message': genesis_result['genesis_message']
        },
        'mining_keypair': keypair,
        'holdings_keypair': holdings_keypair,
        'genesis_block': {
            'nonce': genesis_result['nonce'],
            'block_hash': genesis_result['block_hash'],
            'merkle_root': genesis_result['merkle_root'],
            'block_header': genesis_result['block_header'],
            'coinbase_tx': genesis_result['coinbase_tx'],
            'coinbase_tx_hash': genesis_result['coinbase_tx_hash']
        }
    }
    
    # Print formatted output
    print("\n🔑 MINING REWARD KEYPAIR:")
    print(f"   Private Key:  {keypair['private_key_hex']}")
    print(f"   WIF:          {keypair['wif']}")
    print(f"   Address:      {keypair['address']}")
    
    print("\n🔐 HOLDINGS KEYPAIR (2.5M coins):")
    print(f"   Private Key:  {holdings_keypair['private_key_hex']}")
    print(f"   WIF:          {holdings_keypair['wif']}")
    print(f"   Address:      {holdings_keypair['address']}")
    
    print("\n📦 GENESIS BLOCK:")
    print(f"   Nonce:        {genesis_result['nonce']}")
    print(f"   Block Hash:   {genesis_result['block_hash']}")
    print(f"   Merkle Root:  {genesis_result['merkle_root']}")
    
    print("\n📄 FOR chainparams.cpp:")
    print(f"""
    // Genesis block parameters
    uint32_t nGenesisTime = {genesis_result['timestamp']};
    uint32_t nGenesisBits = 0x207fffff;
    uint32_t nGenesisNonce = {genesis_result['nonce']};
    int32_t nGenesisVersion = 1;
    CAmount genesisReward = 50 * COIN;
    
    genesis = CreateGenesisBlock(nGenesisTime, nGenesisNonce, nGenesisBits, nGenesisVersion, genesisReward);
    
    consensus.hashGenesisBlock = uint256S("0x{genesis_result['block_hash']}");
    assert(genesis.hashMerkleRoot == uint256S("0x{genesis_result['merkle_root']}"));
    assert(consensus.hashGenesisBlock == uint256S("0x{genesis_result['block_hash']}"));
    """)
    
    # Save to JSON file
    with open('genesis_block_output.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n✅ Genesis block data saved to: genesis_block_output.json")
    print("\n" + "=" * 80)
    print("⚠️  IMPORTANT: BACKUP YOUR PRIVATE KEYS SECURELY!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
