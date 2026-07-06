const express = require('express');
const TronWeb = require('tronweb');
const fetch = require('node-fetch');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(cors());

const TRONGRID_URL = process.env.TRONGRID_URL || 'https://api.trongrid.io';
const TRONGRID_API_KEY = process.env.TRONGRID_API_KEY || '';
const SERVER_PRIVATE_KEY = process.env.SERVER_PRIVATE_KEY || '';
const USDT_CONTRACT = process.env.USDT_CONTRACT || 'TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj';

// initialize tronweb
const fullHost = TRONGRID_URL;
const tronWeb = new TronWeb(fullHost, fullHost, fullHost, SERVER_PRIVATE_KEY || undefined);

// If API key is provided, set default header (TronGrid)
if (TRONGRID_API_KEY) {
  tronWeb.setHeader({ 'TRON-PRO-API-KEY': TRONGRID_API_KEY });
}

// Helper: get TRX balance (sun)
async function getTrxBalance(address) {
  try {
    const balance = await tronWeb.trx.getBalance(address);
    return balance; // in sun
  } catch (err) {
    console.error('getTrxBalance error', err);
    throw err;
  }
}

// Helper: get TRC20 balance
async function getTokenBalance(address, tokenContractAddress) {
  try {
    const contract = await tronWeb.contract().at(tokenContractAddress);
    const balance = await contract.methods.balanceOf(address).call();
    return balance.toString();
  } catch (err) {
    console.error('getTokenBalance error', err);
    throw err;
  }
}

// GET /api/balance/:address
app.get('/api/balance/:address', async (req, res) => {
  try {
    const address = req.params.address;
    const trxSun = await getTrxBalance(address);
    const usdtBalance = await getTokenBalance(address, USDT_CONTRACT);
    res.json({ address, trxSun, trx: trxSun / 1e6, usdtSun: usdtBalance, usdt: Number(usdtBalance) / 1e6, tokenContract: USDT_CONTRACT });
  } catch (err) {
    res.status(500).json({ error: err.toString() });
  }
});

// GET /api/price  (CoinGecko)
app.get('/api/price', async (req, res) => {
  try {
    const cg = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=tether%2Ctron&vs_currencies=usd');
    const json = await cg.json();
    res.json({ success: true, data: json, timestamp: Date.now() });
  } catch (err) {
    res.status(500).json({ error: err.toString() });
  }
});

// GET /api/tx/:txid
app.get('/api/tx/:txid', async (req, res) => {
  try {
    const txid = req.params.txid;
    const tx = await tronWeb.trx.getTransaction(txid);
    const info = await tronWeb.trx.getTransactionInfo(txid).catch(() => null);
    res.json({ tx, info });
  } catch (err) {
    res.status(500).json({ error: err.toString() });
  }
});

// POST /api/send  - server-side custodial send
// body: { to, amount, token }
app.post('/api/send', async (req, res) => {
  if (!SERVER_PRIVATE_KEY) {
    return res.status(403).json({ error: 'SERVER_PRIVATE_KEY not configured; server-side signing disabled' });
  }
  try {
    const { to, amount, token } = req.body;
    if (!to || !amount) return res.status(400).json({ error: 'to and amount required' });
    if (!token || token === 'USDT') {
      const contract = await tronWeb.contract().at(USDT_CONTRACT);
      const tx = await contract.transfer(to, amount);
      return res.json({ result: true, tx });
    } else if (token === 'TRX') {
      const tx = await tronWeb.trx.sendTransaction(to, amount);
      return res.json({ result: true, tx });
    } else {
      return res.status(400).json({ error: 'Unknown token' });
    }
  } catch (err) {
    res.status(500).json({ error: err.toString() });
  }
});

// Serve static frontend if built
const clientDist = path.join(__dirname, '..', 'client', 'dist');
if (require('fs').existsSync(clientDist)) {
  app.use(express.static(clientDist));
  // Serve index.html for all other routes (SPA)
  app.get('*', (req, res) => {
    res.sendFile(path.join(clientDist, 'index.html'));
  });
}

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
