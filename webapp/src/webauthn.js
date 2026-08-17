// WebAuthn prototype helper (client-side only)
// This is a small demonstration of using the WebAuthn Platform credential API to register a platform credential
// and to request an assertion. This prototype stores the credential id in localStorage and sets a local "unlocked" flag
// when an assertion succeeds. This is NOT a full production WebAuthn implementation — it demonstrates the interactions
// and can be extended to wrap/unlock encrypted key material stored in IndexedDB.

export async function createPlatformCredential() {
  if (!window.PublicKeyCredential) throw new Error('WebAuthn not supported in this browser')
  // Simple challenge — in production, use a server-generated challenge to avoid replay. For local-only prototype we use random bytes.
  const challenge = crypto.getRandomValues(new Uint8Array(32))
  const publicKey = {
    challenge: challenge,
    rp: { name: 'Local WebAuthn Demo' },
    user: {
      id: Uint8Array.from(String(Math.random()), c => c.charCodeAt(0)),
      name: 'local-user',
      displayName: 'Local User'
    },
    pubKeyCredParams: [{ type: 'public-key', alg: -7 }], // ES256
    authenticatorSelection: { authenticatorAttachment: 'platform', userVerification: 'required' },
    timeout: 60000,
    attestation: 'none'
  }
  const cred = await navigator.credentials.create({ publicKey })
  const idB64 = btoa(String.fromCharCode(...new Uint8Array(cred.rawId)))
  localStorage.setItem('webauthn_cred_id', idB64)
  // We could store attestationResult or other data if needed
  return idB64
}

export async function getAssertion() {
  const idB64 = localStorage.getItem('webauthn_cred_id')
  if (!idB64) throw new Error('No credential registered')
  const rawId = Uint8Array.from(atob(idB64), c => c.charCodeAt(0))
  const challenge = crypto.getRandomValues(new Uint8Array(32))
  const publicKey = {
    challenge,
    allowCredentials: [{ id: rawId, type: 'public-key' }],
    timeout: 60000,
    userVerification: 'required'
  }
  const assertion = await navigator.credentials.get({ publicKey })
  // On success, return assertion info — in prototype, just set unlocked flag
  sessionStorage.setItem('webauthn_unlocked', '1')
  return assertion
}

export function isUnlocked() {
  return sessionStorage.getItem('webauthn_unlocked') === '1'
}

export function clearUnlocked() {
  sessionStorage.removeItem('webauthn_unlocked')
}
