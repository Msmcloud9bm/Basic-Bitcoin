import React, { useState, useEffect } from 'react'
import { generateWalletFromWIF, createAndSignTx, getAddressBalance, getAddressTxs } from './wallet'
import { encryptKey, decryptKey } from './crypto'

export default function App() {
  const [wif, setWif] = useState('')
  const [encrypted, setEncrypted] = useState('')
  const [password, setPassword] = useState('')
  const [address, setAddress] = useState('')
  const [balance, setBalance] = useState(0)
  const [txs, setTxs] = useState([])
  const [recipient, setRecipient] = useState('')
  const [amount, setAmount] = useState('')
  const [status, setStatus] = useState('')

  useEffect(() => {
    if (address) {
      (async () => {
        const b = await getAddressBalance(address)
        setBalance(b)
        const history = await getAddressTxs(address)
        setTxs(history)
      })()
    }
  }, [address])

  const handleImportWif = async () => {
    try {
      const wallet = generateWalletFromWIF(wif.trim())
      setAddress(wallet.address)
      setStatus('WIF imported — address set')
    } catch (e) {
      setStatus('Invalid WIF')
    }
  }

  const handleEncrypt = async () => {
    if (!wif || !password) { setStatus('Provide WIF and password'); return }
    const blob = await encryptKey(wif.trim(), password)
    setEncrypted(blob)
    setWif('')
    setStatus('Encrypted key stored (in memory). You can save the blob to disk via copy/paste.')
  }

  const handleDecrypt = async () => {
    if (!encrypted || !password) { setStatus('Provide encrypted blob and password'); return }
    try {
      const k = await decryptKey(encrypted, password)
      setWif(k)
      const wallet = generateWalletFromWIF(k)
      setAddress(wallet.address)
      setStatus('Key decrypted and address set')
    } catch (e) {
      setStatus('Decryption failed')
    }
  }

  const handleSend = async () => {
    if (!encrypted && !wif) { setStatus('No key available to sign'); return }
    try {
      const signingWif = wif || await decryptKey(encrypted, password)
      setStatus('Building and signing tx...')
      const hex = await createAndSignTx(signingWif.trim(), recipient.trim(), parseFloat(amount))
      setStatus('Signed hex: ' + hex.slice(0, 80) + '...')
    } catch (e) {
      setStatus('Send failed: ' + e.message)
    }
  }

  return (
    <div className="container">
      <h1>Basic Bitcoin Web Wallet (Demo)</h1>
      <p className="warn">This demo stores keys in memory only. Do not use on untrusted hosts for mainnet funds. Prefer hardware wallets / PSBT.</p>

      <section>
        <h2>Import / Generate Key</h2>
        <textarea placeholder="Paste WIF here" value={wif} onChange={e=>setWif(e.target.value)} rows={2} />
        <div>
          <button onClick={handleImportWif}>Import WIF</button>
        </div>
      </section>

      <section>
        <h2>Encrypt / Decrypt Local Key</h2>
        <input placeholder="Password" value={password} type="password" onChange={e=>setPassword(e.target.value)} />
        <div>
          <button onClick={handleEncrypt}>Encrypt WIF (in-memory blob)</button>
          <button onClick={handleDecrypt}>Decrypt blob</button>
        </div>
        <textarea placeholder="encrypted blob" value={encrypted} onChange={e=>setEncrypted(e.target.value)} rows={3} />
        <p>Copy the encrypted blob to a safe place. Use the same password to decrypt.</p>
      </section>

      <section>
        <h2>Address & Balance</h2>
        <p>Address: <code>{address}</code></p>
        <p>Balance (sats): {balance}</p>
        <h3>Recent TXs</h3>
        <ul>
          {txs.map(t=> <li key={t.txid}><code>{t.txid}</code> — {t.result}</li>)}
        </ul>
      </section>

      <section>
        <h2>Send</h2>
        <input placeholder="recipient address" value={recipient} onChange={e=>setRecipient(e.target.value)} />
        <input placeholder="amount (BTC)" value={amount} onChange={e=>setAmount(e.target.value)} />
        <div>
          <button onClick={handleSend}>Build & Sign (WIF or decrypted blob)</button>
        </div>
      </section>

      <section>
        <h2>Status</h2>
        <pre>{status}</pre>
      </section>

    </div>
  )
}
