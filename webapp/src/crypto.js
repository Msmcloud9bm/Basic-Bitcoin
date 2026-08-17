// crypto.js — simple WebCrypto AES-GCM wrapper for encrypting the WIF with a password

const enc = new TextEncoder()
const dec = new TextDecoder()

export async function encryptKey(wif, password) {
  const pwKey = await getPasswordKey(password)
  const iv = crypto.getRandomValues(new Uint8Array(12))
  const encoded = enc.encode(wif)
  const cipher = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, pwKey, encoded)
  // return base64 payload: iv|cipher
  const buf = new Uint8Array(cipher)
  const joined = new Uint8Array(iv.length + buf.length)
  joined.set(iv, 0)
  joined.set(buf, iv.length)
  return btoa(String.fromCharCode(...joined))
}

export async function decryptKey(blobBase64, password) {
  const data = Uint8Array.from(atob(blobBase64), c => c.charCodeAt(0))
  const iv = data.slice(0, 12)
  const cipher = data.slice(12)
  const pwKey = await getPasswordKey(password)
  const plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, pwKey, cipher)
  return dec.decode(plain)
}

async function getPasswordKey(password) {
  const pwUtf8 = enc.encode(password)
  const pwHash = await crypto.subtle.digest('SHA-256', pwUtf8)
  return crypto.subtle.importKey('raw', pwHash, 'AES-GCM', false, ['encrypt','decrypt'])
}
