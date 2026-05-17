#!/usr/bin/env python3
"""
Bitcoin Transaction Builder - Production Grade
Uses: bitcoinlib
Install: pip install bitcoinlib requests

Supports: Mainnet, Testnet, Regtest
"""

from bitcoinlib.transactions import Transaction
from bitcoinlib.keys import Key
import requests
import json
import sys

NETWORK = "bitcoin"  # "bitcoin", "testnet", "regtest"
PRIVATE_KEY_WIF = "YOUR_PRIVATE_KEY_WIF_HERE"

UTXOS = [
    ("ccbcda599e46413e5c0e7e5c2590841c231e15d996d6cfeeb9a2bc875d0a2a2a", 1, 0),
    ("9bfa9bdef63f96f9280d3a02c07d16f3696abb830c3d85282b9939daf62af323", 18, 0),
]

OUTPUTS = {
    "bc1q2yvtl5zuj6vvum3rhdh2wsstrhh2tdsekhd4ud": 1.05000000,
    "bc1q22m4v7keqe3q5jm58jdcet0mjms3tmx496mv71": 0.00062401,
}

FEE_RATE_SAT_PER_VBYTE = 6
CHANGE_ADDRESS = None

MEMPOOL_SPACE_API = {
    "bitcoin": "https://mempool.space/api",
    "testnet": "https://mempool.space/testnet/api",
}

SATS_PER_BTC = 1e8


def get_mempool_api_url(net: str) -> str:
    return MEMPOOL_SPACE_API.get(net, MEMPOOL_SPACE_API["bitcoin"])


def btc_to_sat(btc: float) -> int:
    return int(round(btc * SATS_PER_BTC))


def sat_to_btc(sat: int) -> float:
    return sat / SATS_PER_BTC


def fetch_utxo_value(txid: str, vout: int, network: str = "bitcoin") -> int:
    try:
        url = f"{get_mempool_api_url(network)}/tx/{txid}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        tx_data = resp.json()
        value = tx_data["vout"][vout]["value"]
        print(f"  ✅ UTXO {txid[:16]}...:{vout} = {value:,} sats ({sat_to_btc(value):.8f} BTC)")
        return value
    except Exception as e:
        print(f"  ❌ Error fetching UTXO: {e}")
        return 0


def validate_address(address: str, network: str = "bitcoin") -> bool:
    if network == "bitcoin" and address.startswith(("1", "3", "bc1")):
        return True
    elif network == "testnet" and address.startswith(("m", "n", "2", "tb1")):
        return True
    return False


def build_transaction(network: str = "bitcoin"):
    print("=" * 70)
    print("  Bitcoin Transaction Builder")
    print(f"  Network: {network.upper()}")
    print("=" * 70)

    try:
        key = Key(PRIVATE_KEY_WIF, network=network)
        sender_address = key.address()
    except Exception as e:
        print(f"\n❌ Invalid private key: {e}")
        return None

    print(f"\n🔑 Sender: {sender_address}")

    utxos_filled = []
    print("\n🔍 Processing UTXOs...")

    for txid, vout, value in UTXOS:
        if value == 0:
            value = fetch_utxo_value(txid, vout, network)
            if value == 0:
                continue
        utxos_filled.append((txid, vout, value))

    if not utxos_filled:
        print("❌ No valid UTXOs!")
        return None

    total_input_sats = sum(v for _, _, v in utxos_filled)
    print(f"\n💰 Total input: {total_input_sats:,} sats ({sat_to_btc(total_input_sats):.8f} BTC)")

    total_output_sats = 0
    outputs_list = []

    print(f"\n📤 Outputs:")
    for addr, btc in OUTPUTS.items():
        if not validate_address(addr, network):
            print(f"  ❌ Invalid address: {addr}")
            return None
        sats = btc_to_sat(btc)
        total_output_sats += sats
        outputs_list.append((addr, sats))
        print(f"   {addr} ← {btc:.8f} BTC")

    estimated_vsize = 10 + (68 * len(utxos_filled)) + (31 * len(outputs_list))
    estimated_fee = estimated_vsize * FEE_RATE_SAT_PER_VBYTE

    print(f"\n⛽ Fee: {estimated_fee:,} sats ({FEE_RATE_SAT_PER_VBYTE} sat/vB × {estimated_vsize} vB)")

    remainder = total_input_sats - total_output_sats - estimated_fee

    if remainder < 0:
        print(f"\n❌ Insufficient funds! Short by {abs(remainder):,} sats")
        return None

    print(f"   Remainder: {remainder:,} sats")

    # Verification
    print("\n" + "=" * 70)
    print("  VERIFY BEFORE SIGNING")
    print("=" * 70)

    print(f"\n{'RECIPIENT':<45} {'BTC':>14}  {'SATS':>15}")
    print("-" * 77)
    for addr, sats in outputs_list:
        print(f"{addr:<45} {sat_to_btc(sats):>14.8f}  {sats:>15,}")
    print("-" * 77)
    print(f"{'TOTAL OUTPUT':<45} {sat_to_btc(total_output_sats):>14.8f}  {total_output_sats:>15,}")
    print(f"{'FEE':<45} {sat_to_btc(estimated_fee):>14.8f}  {estimated_fee:>15,}")

    if remainder > 0:
        print(f"{'CHANGE':<45} {sat_to_btc(remainder):>14.8f}  {remainder:>15,}")

    confirm = input("\n✅ Correct? Type YES: ").strip().upper()
    if confirm != "YES":
        return None

    # Build transaction
    print("\n🔨 Building...")
    try:
        t = Transaction(network=network)

        for txid, vout, value in utxos_filled:
            t.add_input(prev_txid=txid, output_n=vout, value=value, address=sender_address)

        for addr, sats in outputs_list:
            t.add_output(value=sats, address=addr)

        if remainder > 546:
            change_addr = CHANGE_ADDRESS or key.address()
            t.add_output(value=remainder, address=change_addr)

        print("\n🔐 Signing...")
        t.sign(key.private_byte)

        if not t.verify():
            print("❌ Signature verification failed!")
            return None

        raw_hex = t.raw_hex()
        txid = t.txid()

        print(f"\n✅ Signed! TXID: {txid}")
        print(f"   Raw: {raw_hex[:80]}...")

        return raw_hex, txid

    except Exception as e:
        print(f"\n❌ Build error: {e}")
        return None


def broadcast_transaction(raw_hex: str, network: str = "bitcoin") -> str:
    print("\n" + "=" * 70)
    print("  📡 BROADCAST")
    print("=" * 70)

    url = f"{get_mempool_api_url(network)}/tx"
    print(f"\n📤 Sending to network...")

    try:
        resp = requests.post(url, data=raw_hex, timeout=30)

        if resp.status_code == 200:
            txid = resp.text.strip()
            print(f"\n🎉 SUCCESS!")
            print(f"   TXID: {txid}")
            explorer = f"{get_mempool_api_url(network).split('/api')[0]}/tx/{txid}"
            print(f"   View: {explorer}")
            return txid
        else:
            print(f"\n❌ Failed: {resp.status_code}")
            print(f"   {resp.text}")
            return None

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def main():
    print("\n🔗 Bitcoin Transaction Builder\n")

    result = build_transaction(NETWORK)

    if not result:
        print("\n❌ Build failed.")
        sys.exit(1)

    raw_hex, txid = result

    broadcast_choice = input("\n📡 Broadcast? Type BROADCAST: ").strip().upper()

    if broadcast_choice == "BROADCAST":
        final = input("\n⚠️  Type CONFIRM to send REAL BITCOIN: ").strip().upper()
        if final == "CONFIRM":
            broadcast_transaction(raw_hex, NETWORK)
        else:
            print("❌ Cancelled")
    else:
        print(f"\n💾 Raw hex:\n{raw_hex}\n")
        with open(f"tx_{NETWORK}.hex", "w") as f:
            f.write(raw_hex)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
