#!/usr/bin/env python3
"""
Mempool.space API Integration for Bitcoin Transaction Monitoring

This module provides real-time access to:
- Mempool statistics and transaction pool info
- Fee estimation (fastest, half-hour, hour, economy)
- Blockchain data and recent blocks
- Transaction tracking and RBF monitoring
- Live fee market analysis
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

MEMPOOL_API_URL = "https://mempool.space/api"
TESTNET_API_URL = "https://mempool.space/testnet/api"


@dataclass
class FeeData:
    """Fee rate data from mempool"""
    fastest_fee: int  # sat/vB
    half_hour_fee: int
    hour_fee: int
    economy_fee: int
    minimum_fee: int

    def to_dict(self):
        return {
            "fastest": self.fastest_fee,
            "half_hour": self.half_hour_fee,
            "hour": self.hour_fee,
            "economy": self.economy_fee,
            "minimum": self.minimum_fee
        }


@dataclass
class MempoolStats:
    """Current mempool statistics"""
    size: int  # Number of transactions
    bytes: int  # Total size in bytes
    usage: int  # Memory usage
    total_fee: float  # Total fees in BTC
    min_fee: float  # Minimum fee rate
    vbytes_per_second: int


@dataclass
class BlockInfo:
    """Bitcoin block information"""
    height: int
    hash: str
    timestamp: int
    tx_count: int
    size: int
    weight: int
    median_fee: float
    fee_range: List[float]
    pool_name: Optional[str]


@dataclass
class TransactionInfo:
    """Pending transaction information"""
    txid: str
    fee: int  # satoshis
    vsize: int  # virtual bytes
    value: int  # satoshis
    rate: float  # sat/vB


class MempoolAPI:
    """Client for mempool.space API"""

    def __init__(self, network: str = "mainnet"):
        """
        Initialize Mempool API client

        Args:
            network: 'mainnet' or 'testnet'
        """
        self.network = network
        self.base_url = TESTNET_API_URL if network == "testnet" else MEMPOOL_API_URL
        self.session = requests.Session()

    def get_fee_estimates(self) -> FeeData:
        """
        Get current fee estimates

        Returns:
            FeeData object with fee rates in sat/vB
        """
        try:
            resp = self.session.get(f"{self.base_url}/v1/fees/recommended", timeout=10)
            resp.raise_for_status()
            data = resp.json()

            return FeeData(
                fastest_fee=data.get("fastestFee", 2),
                half_hour_fee=data.get("halfHourFee", 2),
                hour_fee=data.get("hourFee", 2),
                economy_fee=data.get("economyFee", 1),
                minimum_fee=data.get("minimumFee", 1)
            )
        except Exception as e:
            print(f"❌ Error fetching fee estimates: {e}")
            return FeeData(2, 2, 2, 1, 1)

    def get_mempool_info(self) -> MempoolStats:
        """
        Get current mempool statistics

        Returns:
            MempoolStats object
        """
        try:
            resp = self.session.get(f"{self.base_url}/mempool", timeout=10)
            resp.raise_for_status()
            data = resp.json()

            return MempoolStats(
                size=data.get("vsize", 0),
                bytes=data.get("bytes", 0),
                usage=data.get("usage", 0),
                total_fee=data.get("total_fee", 0),
                min_fee=data.get("mempool_min_fee", 0),
                vbytes_per_second=data.get("vBytesPerSecond", 0)
            )
        except Exception as e:
            print(f"❌ Error fetching mempool info: {e}")
            return None

    def get_transaction(self, txid: str) -> Dict:
        """
        Get transaction details

        Args:
            txid: Transaction ID

        Returns:
            Transaction data
        """
        try:
            resp = self.session.get(f"{self.base_url}/tx/{txid}", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ Error fetching transaction {txid}: {e}")
            return None

    def get_transaction_status(self, txid: str) -> Dict:
        """
        Get transaction confirmation status

        Args:
            txid: Transaction ID

        Returns:
            Status data with confirmation info
        """
        try:
            resp = self.session.get(f"{self.base_url}/tx/{txid}/status", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ Error fetching transaction status: {e}")
            return None

    def get_address_info(self, address: str) -> Dict:
        """
        Get address information and transaction history

        Args:
            address: Bitcoin address

        Returns:
            Address data
        """
        try:
            resp = self.session.get(f"{self.base_url}/address/{address}", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ Error fetching address info: {e}")
            return None

    def get_address_utxos(self, address: str) -> List[Dict]:
        """
        Get unspent outputs for an address

        Args:
            address: Bitcoin address

        Returns:
            List of UTXOs
        """
        try:
            resp = self.session.get(f"{self.base_url}/address/{address}/utxo", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ Error fetching UTXOs: {e}")
            return []

    def get_block(self, block_hash_or_height: str) -> Dict:
        """
        Get block information

        Args:
            block_hash_or_height: Block hash or height

        Returns:
            Block data
        """
        try:
            resp = self.session.get(f"{self.base_url}/block/{block_hash_or_height}", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ Error fetching block: {e}")
            return None

    def get_blocks(self, start_height: Optional[int] = None) -> List[Dict]:
        """
        Get recent blocks

        Args:
            start_height: Optional starting height

        Returns:
            List of recent blocks
        """
        try:
            url = f"{self.base_url}/blocks"
            if start_height:
                url += f"?start_height={start_height}"
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ Error fetching blocks: {e}")
            return []

    def get_mempool_blocks(self) -> List[Dict]:
        """
        Get mempool blocks (projected next blocks)

        Returns:
            List of mempool blocks with fee data
        """
        try:
            resp = self.session.get(f"{self.base_url}/v1/blocks-flow-old", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ Error fetching mempool blocks: {e}")
            return []

    def calculate_fee(self, vsize: int, fee_rate: int) -> Tuple[int, float]:
        """
        Calculate transaction fee

        Args:
            vsize: Virtual size in bytes
            fee_rate: Fee rate in sat/vB

        Returns:
            (fee_in_sats, fee_in_btc)
        """
        fee_sats = vsize * fee_rate
        fee_btc = fee_sats / 1e8
        return fee_sats, fee_btc


class TransactionEstimator:
    """Estimate transaction fees and confirmation times"""

    def __init__(self, api: MempoolAPI):
        self.api = api

    def estimate_p2pkh(self, input_count: int, output_count: int) -> Dict:
        """
        Estimate P2PKH transaction size and fee

        Args:
            input_count: Number of inputs
            output_count: Number of outputs

        Returns:
            Estimation data
        """
        # P2PKH: input ~148 bytes, output ~34 bytes, overhead ~10 bytes
        vsize = 10 + (148 * input_count) + (34 * output_count)

        fees = self.api.get_fee_estimates()

        return {
            "type": "P2PKH",
            "estimated_vsize": vsize,
            "inputs": input_count,
            "outputs": output_count,
            "fees": {
                "fastest": {"sat": vsize * fees.fastest_fee, "btc": vsize * fees.fastest_fee / 1e8},
                "half_hour": {"sat": vsize * fees.half_hour_fee, "btc": vsize * fees.half_hour_fee / 1e8},
                "hour": {"sat": vsize * fees.hour_fee, "btc": vsize * fees.hour_fee / 1e8},
                "economy": {"sat": vsize * fees.economy_fee, "btc": vsize * fees.economy_fee / 1e8}
            }
        }

    def estimate_segwit(self, input_count: int, output_count: int) -> Dict:
        """
        Estimate SegWit transaction size and fee

        Args:
            input_count: Number of inputs
            output_count: Number of outputs

        Returns:
            Estimation data
        """
        # SegWit: input ~68 vbytes, output ~31 vbytes, overhead ~10.75 vbytes
        vsize = int(10.75 + (68 * input_count) + (31 * output_count))

        fees = self.api.get_fee_estimates()

        return {
            "type": "SegWit",
            "estimated_vsize": vsize,
            "inputs": input_count,
            "outputs": output_count,
            "fees": {
                "fastest": {"sat": vsize * fees.fastest_fee, "btc": vsize * fees.fastest_fee / 1e8},
                "half_hour": {"sat": vsize * fees.half_hour_fee, "btc": vsize * fees.half_hour_fee / 1e8},
                "hour": {"sat": vsize * fees.hour_fee, "btc": vsize * fees.hour_fee / 1e8},
                "economy": {"sat": vsize * fees.economy_fee, "btc": vsize * fees.economy_fee / 1e8}
            }
        }


class MempoolMonitor:
    """Monitor transactions and mempool activity"""

    def __init__(self, api: MempoolAPI):
        self.api = api

    def monitor_transaction(self, txid: str) -> Dict:
        """
        Monitor transaction until confirmed

        Args:
            txid: Transaction ID

        Returns:
            Final transaction status
        """
        print(f"\n📡 Monitoring transaction: {txid}")

        while True:
            status = self.api.get_transaction_status(txid)

            if not status:
                return None

            if status.get("confirmed"):
                block_height = status.get("block_height")
                block_hash = status.get("block_hash")
                print(f"\n✅ CONFIRMED!")
                print(f"   Block: {block_height}")
                print(f"   Hash: {block_hash}")
                return status

            print(f"⏳ Unconfirmed... (waiting for block inclusion)")
            input("Press Enter to check again...")

    def analyze_mempool(self) -> Dict:
        """
        Analyze current mempool state

        Returns:
            Analysis data
        """
        print("\n" + "=" * 70)
        print("  MEMPOOL ANALYSIS")
        print("=" * 70)

        stats = self.api.get_mempool_info()
        fees = self.api.get_fee_estimates()
        blocks = self.api.get_mempool_blocks()

        print(f"\n📊 Mempool Status:")
        print(f"   Transactions: {stats.size:,}")
        print(f"   Memory Usage: {stats.usage / 1e9:.2f} GB")
        print(f"   vBytes/sec: {stats.vbytes_per_second}")

        print(f"\n💰 Current Fee Rates (sat/vB):")
        print(f"   Fastest (next block): {fees.fastest_fee}")
        print(f"   Half-hour: {fees.half_hour_fee}")
        print(f"   1 hour: {fees.hour_fee}")
        print(f"   Economy: {fees.economy_fee}")

        if blocks:
            print(f"\n📦 Next Blocks in Mempool:")
            for i, block in enumerate(blocks[:3]):
                med_fee = block.get("medianFee", 0)
                tx_count = block.get("nTx", 0)
                print(f"   Block {i+1}: {tx_count} tx, median fee {med_fee:.1f} sat/vB")

        return {
            "mempool": stats,
            "fees": fees.to_dict(),
            "blocks": blocks
        }


# Example usage
if __name__ == "__main__":
    # Initialize API client
    api = MempoolAPI("mainnet")

    # Get current fees
    print("=" * 70)
    print("  Bitcoin Fee Estimation")
    print("=" * 70)

    fees = api.get_fee_estimates()
    print(f"\n💰 Current Fee Rates (sat/vB):")
    print(f"   Fastest:  {fees.fastest_fee}")
    print(f"   Half-hr:  {fees.half_hour_fee}")
    print(f"   1 hour:   {fees.hour_fee}")
    print(f"   Economy:  {fees.economy_fee}")
    print(f"   Minimum:  {fees.minimum_fee}")

    # Estimate transaction fees
    print("\n" + "=" * 70)
    print("  Transaction Fee Estimates")
    print("=" * 70)

    estimator = TransactionEstimator(api)

    p2pkh = estimator.estimate_p2pkh(2, 2)
    print(f"\nP2PKH (2 in, 2 out):")
    print(f"   vSize: {p2pkh['estimated_vsize']} vB")
    print(f"   Fastest: {p2pkh['fees']['fastest']['btc']:.8f} BTC ({p2pkh['fees']['fastest']['sat']} sats)")
    print(f"   Half-hr: {p2pkh['fees']['half_hour']['btc']:.8f} BTC ({p2pkh['fees']['half_hour']['sat']} sats)")

    segwit = estimator.estimate_segwit(2, 2)
    print(f"\nSegWit (2 in, 2 out):")
    print(f"   vSize: {segwit['estimated_vsize']} vB")
    print(f"   Fastest: {segwit['fees']['fastest']['btc']:.8f} BTC ({segwit['fees']['fastest']['sat']} sats)")
    print(f"   Half-hr: {segwit['fees']['half_hour']['btc']:.8f} BTC ({segwit['fees']['half_hour']['sat']} sats)")

    # Analyze mempool
    monitor = MempoolMonitor(api)
    analysis = monitor.analyze_mempool()
