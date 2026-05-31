# Bitcoin Fork Implementation Checklist

Use this checklist to track your progress in creating a custom Bitcoin mainnet fork.

## Phase 1: Planning & Design

- [ ] Define your chain parameters:
  - [ ] Total coin supply (e.g., 21 million)
  - [ ] Initial block reward (e.g., 50 BTC)
  - [ ] Halving interval (e.g., 210,000 blocks)
  - [ ] Block time target (e.g., 10 minutes)
  - [ ] Difficulty adjustment period (e.g., 2 weeks)
  - [ ] Network magic bytes (unique 4-byte prefix)
  - [ ] Custom RPC/P2P ports
  - [ ] Address prefixes (base58)
  - [ ] Bech32 HRP (e.g., "bc" for Bitcoin, your custom prefix)

- [ ] Plan consensus rules:
  - [ ] Which BIPs to support
  - [ ] Activation heights for features
  - [ ] Transaction validation rules
  - [ ] Any custom consensus changes

- [ ] Design network infrastructure:
  - [ ] Number of seed nodes
  - [ ] DNS seed setup (optional)
  - [ ] Block explorer (optional)
  - [ ] Mining pool (optional)

## Phase 2: Development Setup

- [ ] Install dependencies:
  - [ ] Git
  - [ ] Build tools (gcc, g++, make)
  - [ ] Autotools (autoconf, automake, libtool)
  - [ ] pkg-config
  - [ ] OpenSSL dev libraries
  - [ ] Boost libraries
  - [ ] Berkeley DB 4.8

- [ ] Clone Bitcoin Core:
  ```bash
  git clone https://github.com/bitcoin/bitcoin.git
  git checkout v31.0
  ```

- [ ] Create your fork branch:
  ```bash
  git checkout -b custom-mainnet-fork
  ```

## Phase 3: Modify Core Parameters

### Network Configuration

- [ ] Update `src/chainparams.cpp`:
  - [ ] Change network magic bytes (pchMessageStart)
  - [ ] Set custom RPC port (nRPCPort)
  - [ ] Set custom P2P port (nDefaultPort)
  - [ ] Add/remove seed nodes (vSeeds)
  - [ ] Configure base58 prefixes
  - [ ] Set bech32 HRP

- [ ] Update `src/consensus/params.h`:
  - [ ] Set subsidy halving interval (nSubsidyHalvingInterval)
  - [ ] Configure difficulty parameters
  - [ ] Set block reward halving schedule
  - [ ] Define coinbase maturity (CoinbaseMaturity)

- [ ] Update `src/validation.cpp`:
  - [ ] Implement `GetBlockSubsidy()` function
  - [ ] Update transaction validation rules (if needed)
  - [ ] Configure transaction limits

### Genesis Block

- [ ] Create genesis block:
  - [ ] Define genesis timestamp (nGenesisTime)
  - [ ] Write genesis message (pszTimestamp)
  - [ ] Generate genesis pubkey hash
  - [ ] Set initial difficulty (nGenesisBits)
  - [ ] Mine to find correct nonce

- [ ] Mine genesis block:
  - [ ] Use mining utility or Bitcoin Core
  - [ ] Record genesis block hash
  - [ ] Record merkle root
  - [ ] Record nonce value

- [ ] Update genesis block in code:
  - [ ] Set consensus.hashGenesisBlock
  - [ ] Set genesis.hashMerkleRoot
  - [ ] Add assertions to verify values

## Phase 4: Build & Test

- [ ] Generate build scripts:
  ```bash
  ./autogen.sh
  ```

- [ ] Configure build:
  ```bash
  ./configure --prefix=/usr/local
  ```

- [ ] Build:
  ```bash
  make -j$(nproc)
  ```

- [ ] Install:
  ```bash
  sudo make install
  ```

- [ ] Verify installation:
  - [ ] `bitcoind --version`
  - [ ] `bitcoin-cli --version`
  - [ ] `bitcoin-qt --version` (if GUI enabled)

- [ ] Test on regtest:
  ```bash
  bitcoind -regtest -daemon
  bitcoin-cli -regtest getblockchaininfo
  ```

- [ ] Test genesis block:
  - [ ] Start node: `bitcoind -daemon`
  - [ ] Check block: `bitcoin-cli getblock 0`
  - [ ] Verify: Hash, merkle root, nonce

## Phase 5: Network Setup

### Local Testing

- [ ] Create configuration file (~/.bitcoin/bitcoin.conf)
- [ ] Start first node
- [ ] Mine initial blocks
- [ ] Test transactions
- [ ] Create test wallets

### Seed Node Setup (if needed)

- [ ] Deploy seed node on public server
- [ ] Configure with `-listen -discover`
- [ ] Add DNS records (if using DNS seeds)
- [ ] Test peer connections

### Private Network (Optional)

- [ ] Set up multiple nodes locally
- [ ] Configure them to connect
- [ ] Test P2P communication
- [ ] Verify block propagation
- [ ] Test transaction relay

## Phase 6: Mining Infrastructure

### Solo Mining

- [ ] Test solo mining:
  ```bash
  bitcoind -daemon -generate=1 -genproclimit=4
  ```
- [ ] Monitor block generation
- [ ] Verify rewards in wallet

### Mining Pool (Optional)

- [ ] Choose pool software (MPOS, Stratum, etc.)
- [ ] Install and configure
- [ ] Set up pool difficulty
- [ ] Test miner connections
- [ ] Verify share submission

## Phase 7: Wallet & Exchange Integration

- [ ] Create native wallets:
  - [ ] Desktop (using Bitcoin Core)
  - [ ] Web wallet (optional)
  - [ ] Mobile wallet (optional)

- [ ] Integrate with exchanges (optional):
  - [ ] Implement deposit addresses
  - [ ] Implement withdrawal addresses
  - [ ] Implement transaction confirmation
  - [ ] Set up blockchain scanning

- [ ] Test wallet operations:
  - [ ] Create addresses
  - [ ] Send transactions
  - [ ] Receive transactions
  - [ ] Check balances
  - [ ] Verify fees

## Phase 8: Block Explorer (Optional)

- [ ] Choose explorer software:
  - [ ] Blockstream Esplora
  - [ ] btcpayserver explorer
  - [ ] Other

- [ ] Install and configure
- [ ] Verify data display
- [ ] Test search functionality
- [ ] Set up API endpoints

## Phase 9: Documentation

- [ ] Create README with:
  - [ ] Project overview
  - [ ] How to build
  - [ ] How to run a node
  - [ ] Network parameters
  - [ ] Mining instructions

- [ ] Create API documentation
- [ ] Create RPC documentation
- [ ] Create address format guide
- [ ] Create transaction format guide
- [ ] Create fork differences from Bitcoin

## Phase 10: Security & Audit

- [ ] Security review:
  - [ ] Verify consensus rules are correct
  - [ ] Check for common vulnerabilities
  - [ ] Review cryptographic implementations
  - [ ] Verify no hardcoded credentials

- [ ] Test edge cases:
  - [ ] Double spend attempts
  - [ ] Invalid block submissions
  - [ ] Orphan block handling
  - [ ] Chain reorg scenarios
  - [ ] Large transaction handling

- [ ] Network stress testing:
  - [ ] High transaction volume
  - [ ] Block propagation delays
  - [ ] Connection limits
  - [ ] Memory usage under load

## Phase 11: Mainnet Launch

- [ ] Final checks:
  - [ ] All code reviewed and tested
  - [ ] Genesis block finalized
  - [ ] Network parameters confirmed
  - [ ] Seed nodes operational
  - [ ] Backups created

- [ ] Launch announcement:
  - [ ] Release blog post
  - [ ] Share on social media
  - [ ] Announce to community
  - [ ] Publish mining instructions

- [ ] Mainnet deployment:
  - [ ] Start seed nodes
  - [ ] Deploy block explorer
  - [ ] Open mining pools
  - [ ] Launch exchanges

- [ ] Monitor mainnet:
  - [ ] Watch block production
  - [ ] Monitor network health
  - [ ] Check node connectivity
  - [ ] Track transactions
  - [ ] Collect metrics

## Phase 12: Post-Launch Maintenance

- [ ] Ongoing tasks:
  - [ ] Keep Bitcoin Core updated with security patches
  - [ ] Monitor for issues
  - [ ] Support community
  - [ ] Maintain documentation
  - [ ] Upgrade network when needed

- [ ] Community management:
  - [ ] Maintain GitHub repository
  - [ ] Respond to issues
  - [ ] Merge pull requests
  - [ ] Manage releases
  - [ ] Communicate updates

---

## Estimated Timeline

- **Setup & Configuration:** 1-2 weeks
- **Development & Testing:** 2-4 weeks
- **Beta Testing:** 1-2 weeks
- **Final Audit & Launch:** 1 week
- **Total: 5-10 weeks**

## Resource Requirements

- **Development:** 1-2 developers
- **Servers:** At least 1 seed node, 1 explorer (optional), 1+ mining pool (optional)
- **Storage:** At least 500GB for initial blockchain storage
- **Network:** 100 Mbps+ recommended

## Key Differences to Manage

| Aspect | Bitcoin | Your Fork |
|--------|---------|-----------|
| Magic Bytes | 0xD9B4BEF9 | 0x???? (your choice) |
| P2P Port | 8333 | 18333+ (your choice) |
| RPC Port | 8332 | 18332+ (your choice) |
| Address Prefix | 0x00 | Configurable |
| Bech32 HRP | "bc" | Configurable |
| Genesis Hash | Known Bitcoin hash | Your calculated hash |

---

Last Updated: May 31, 2026
