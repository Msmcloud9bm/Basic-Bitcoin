import axios from 'axios'
import * as bitcoin from 'bitcoinjs-lib'
import bip39 from 'bip39'

const NETWORK = bitcoin.networks.bitcoin
const API = 'https://blockstream.info/api' // mainnet; change to /testnet/api for testnet

export function generateWalletFromWIF(wif) {
  const keyPair = bitcoin.ECPair.fromWIF(wif, NETWORK)
  const { address } = bitcoin.payments.p2wpkh({ pubkey: keyPair.publicKey, network: NETWORK })
  return { wif, keyPair, address }
}

export async function getAddressBalance(address) {
  try {
    const r = await axios.get(`${API}/address/${address}`)
    // blockstream returns chain_stats and mempool_stats with funded_txo_sum, spent_txo_sum
    const chain = r.data.chain_stats || {}
    const mem = r.data.mempool_stats || {}
    // balance in sats
    const balance = (chain.funded_txo_sum + mem.funded_txo_sum) - (chain.spent_txo_sum + mem.spent_txo_sum)
    return balance
  } catch (e) {
    console.error(e)
    return 0
  }
}

export async function getAddressTxs(address) {
  try {
    const r = await axios.get(`${API}/address/${address}/txs`)
    // return simplified list
    return r.data.slice(0,10).map(tx => ({ txid: tx.txid, result: tx.status ? `confirmed in ${tx.status.block_height}` : 'unconfirmed' }))
  } catch (e) { console.error(e); return [] }
}

export async function createAndSignTx(wif, toAddress, amountBTC) {
  const wallet = generateWalletFromWIF(wif)
  const addr = wallet.address
  // fetch UTXOs
  const utxoRes = await axios.get(`${API}/address/${addr}/utxo`)
  const utxos = utxoRes.data
  if (!utxos || utxos.length === 0) throw new Error('No UTXOs available')
  // select UTXO(s) until amount+fee covered
  const satsNeeded = Math.round(amountBTC * 1e8)
  let selected = []
  let total = 0
  for (const u of utxos) {
    selected.push(u)
    total += u.value
    if (total >= satsNeeded + 10000) break // naive fee reserve 10k sats
  }
  if (total < satsNeeded + 10000) throw new Error('Insufficient funds (including fee reserve)')

  const psbt = new bitcoin.Psbt({ network: NETWORK })
  // add inputs
  for (const u of selected) {
    // For P2WPKH the witnessUtxo script is derived from address
    const script = bitcoin.payments.p2wpkh({ pubkey: wallet.keyPair.publicKey, network: NETWORK }).output
    psbt.addInput({ hash: u.txid, index: u.vout, witnessUtxo: { script, value: u.value } })
  }
  // add output to recipient
  psbt.addOutput({ address: toAddress, value: satsNeeded })
  // change
  const change = total - satsNeeded - 10000
  if (change > 0) {
    psbt.addOutput({ address: addr, value: change })
  }

  // sign inputs
  selected.forEach((u, idx) => {
    psbt.signInput(idx, wallet.keyPair)
  })
  psbt.finalizeAllInputs()
  const tx = psbt.extractTransaction()
  const hex = tx.toHex()

  // Optionally broadcast using Blockstream API (uncomment to broadcast)
  // await axios.post(`${API}/tx`, hex)
  return hex
}
