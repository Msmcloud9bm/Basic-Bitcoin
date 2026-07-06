#!/usr/bin/env node
/**
 * server/sweep.js
 *
 * Usage:
 *  node sweep.js <TARGET_ADDRESS> [--dry-run]
 *  or set env SWEEP_TARGET and run: node sweep.js [--dry-run]
 *
 * Behavior:
 *  - Reads SERVER_PRIVATE_KEY from env and infers source address
 *  - Fetches USDT (TRC20) balance for the source address
 *  - Performs a transfer of the full USDT balance to the target address
 *  - Supports --dry-run to only show what would be sent
 *
 * Security:
 *  - Do NOT put your private key in the repo. Set it in env or secrets at runtime.
 */

const TronWeb = require('tronweb');
require('dotenv').config();

const SERVER_PRIVATE_KEY = process.env.SERVER_PRIVATE_KEY;
const TRONGRID_URL = process.env.TRONGRID_URL || 'https://api.trongrid.io';
const USDT_CONTRACT = process.env.USDT_CONTRACT || 'TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj';

if (!SERVER_PRIVATE_KEY) {
  console.error('ERROR: SERVER_PRIVATE_KEY is not set in the environment. Aborting.');
  process.exit(1);
}

const tronWeb = new TronWeb({ fullHost: TRONGRID_URL, privateKey: SERVER_PRIVATE_KEY });

async function main() {
  try {
    const argv = process.argv.slice(2);
    let target = process.env.SWEEP_TARGET || null;
    let dryRun = false;

    for (const a of argv) {
      if (a === '--dry-run') dryRun = true;
      else if (a === '--help' || a === '-h') {
        console.log('Usage: node sweep.js <TARGET_ADDRESS> [--dry-run]');
        process.exit(0);
      } else if (!a.startsWith('--')) {
        target = a;
      }
    }

    if (!target) {
      console.error('ERROR: No target address provided. Provide as CLI arg or set SWEEP_TARGET env variable.');
      process.exit(1);
    }

    // infer source (base58) from private key
    let sourceAddr;
    try {
      sourceAddr = tronWeb.address.fromPrivateKey(SERVER_PRIVATE_KEY);
    } catch (e) {
      // fallback: try tronWeb.defaultAddress
      sourceAddr = (tronWeb.defaultAddress && tronWeb.defaultAddress.base58) || null;
    }

    if (!sourceAddr) {
      console.error('ERROR: Unable to infer source address from private key.');
      process.exit(1);
    }

    console.log(`Source address: ${sourceAddr}`);
    console.log(`Target address: ${target}`);
    console.log(`USDT contract: ${USDT_CONTRACT}`);

    // get USDT balance
    const contract = await tronWeb.contract().at(USDT_CONTRACT);
    // tronweb accepts base58
    const usdtSun = await contract.methods.balanceOf(sourceAddr).call();
    const usdtNum = Number(usdtSun) / 1e6;

    console.log(`USDT balance (smallest unit): ${usdtSun}`);
    console.log(`USDT balance: ${usdtNum} USDT`);

    if (Number(usdtSun) === 0) {
      console.log('No USDT balance to sweep. Exiting.');
      process.exit(0);
    }

    if (dryRun) {
      console.log('Dry run enabled. No transaction will be sent.');
      process.exit(0);
    }

    console.log('Sending transaction... (this will sign with SERVER_PRIVATE_KEY)');

    // call transfer
    const tx = await contract.methods.transfer(target, String(usdtSun)).send();

    console.log('Send result:', tx);
    console.log('Done. Query transaction info with /api/tx/:txid endpoint or using TronGrid.');
  } catch (err) {
    console.error('Sweep failed:', err && (err.message || err));
    process.exit(1);
  }
}

main();
