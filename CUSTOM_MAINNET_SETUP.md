# Custom Bitcoin Mainnet Fork Setup Guide

This guide will walk you through creating your own Bitcoin mainnet fork with 21 million coins, similar to Satoshi's original Bitcoin.

## Prerequisites

Before starting, ensure you have:
- `git` installed
- A Linux or macOS system (Windows requires WSL2)
- `gcc`, `g++`, `make` compiler tools
- `autotools` (autoconf, automake, libtool)
- `pkg-config`
- OpenSSL development libraries
- Berkeley DB 4.8 (for wallet)
- Boost libraries

### Install Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install build-essential libtool autotools-dev automake pkg-config bsdmainutils curl git
sudo apt-get install libssl-dev libevent-dev libboost-all-dev libdb4.8-dev libdb4.8++-dev
```

**macOS (with Homebrew):**
```bash
brew install automake libtool boost pkg-config openssl@3
brew install berkeley-db
```

## Step 1: Fork Bitcoin Core

Clone the official Bitcoin Core repository:

```bash
git clone https://github.com/bitcoin/bitcoin.git
cd bitcoin
git checkout v31.0  # Latest stable version as of 2026
```

## Step 2: Modify Mainnet Parameters

### 2.1 Update Network Magic Bytes

Edit `src/chainparams.cpp` and modify the mainnet magic bytes to be unique:

```cpp
// Change from Bitcoin's 0xD9B4BEF9 to your custom bytes
// This prevents accidental connections to Bitcoin network
pchMessageStart[0] = 0xC0;  // Your custom byte 1
pchMessageStart[1] = 0xDE;  // Your custom byte 2
pchMessageStart[2] = 0xAD;  // Your custom byte 3
pchMessageStart[3] = 0xBE;  // Your custom byte 4
```

### 2.2 Define Custom Chain Parameters

In `src/chainparams.cpp`, update these parameters in the `CMainParams` class

### 2.3 Create Your Genesis Block

Use Bitcoin Core utilities to generate your genesis block with unique hash and merkle root

### 2.4 Update Network Ports

Edit `src/chainparams.cpp` to set custom P2P and RPC ports

## Step 3: Build Your Fork

```bash
./autogen.sh
./configure --prefix=/usr/local
make -j$(nproc)
sudo make install
```

## Step 4: Initialize and Run Your Node

```bash
bitcoind -daemon -datadir=/home/user/.bitcoin
bitcoin-cli getblockcount
```

See additional documentation files for complete setup instructions.