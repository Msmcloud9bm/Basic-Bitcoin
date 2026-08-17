// HD & multisig demo helpers (using bitcoinjs-lib). These are examples only and intended for the webapp demo.
import * as bitcoin from 'bitcoinjs-lib'
import bip39 from 'bip39'

const NETWORK = bitcoin.networks.bitcoin

export function generateMnemonic() {
  return bip39.generateMnemonic(256)
}

export async function mnemonicToSeed(mnemonic) {
  const seed = await bip39.mnemonicToSeed(mnemonic)
  return seed
}

export function seedToNode(seed) {
  return bitcoin.bip32.fromSeed(seed, NETWORK)
}

export function nodeToXpub(node) {
  return node.neutered().toBase58()
}

export function deriveAddressFromXprv(node, path="m/84'/0'/0'/0/0") {
  const child = node.derivePath(path)
  const { address } = bitcoin.payments.p2wpkh({ pubkey: child.publicKey, network: NETWORK })
  return address
}

// Multisig example: create a 2-of-3 P2WSH multisig and return redeem script + address
export function createMultisigAddress(pubkeysHex, m=2) {
  const pubkeys = pubkeysHex.map(h => Buffer.from(h, 'hex'))
  const p2ms = bitcoin.payments.p2ms({ m, pubkeys, network: NETWORK })
  const p2wsh = bitcoin.payments.p2wsh({ redeem: p2ms, network: NETWORK })
  return { address: p2wsh.address, redeemScript: p2ms.output.toString('hex'), witnessScript: p2wsh.redeem.output.toString('hex') }
}

// PSBT builder example: create unsigned PSBT spending a single P2WPKH input
export function buildPsbtExample(input, outputs, xprv) {
  // input: { txid, vout, value }
  // outputs: [{address, value}]
  const psbt = new bitcoin.Psbt({ network: NETWORK })
  const node = xprv ? bitcoin.bip32.fromBase58(xprv, NETWORK) : null
  const keyPair = node ? bitcoin.ECPair.fromPrivateKey(node.privateKey, { network: NETWORK }) : null
  // add input (witnessUtxo required)
  psbt.addInput({ hash: input.txid, index: input.vout, witnessUtxo: { script: bitcoin.payments.p2wpkh({ pubkey: keyPair.publicKey, network: NETWORK }).output, value: input.value } })
  outputs.forEach(o => psbt.addOutput({ address: o.address, value: o.value }))
  return psbt.toBase64()
}
