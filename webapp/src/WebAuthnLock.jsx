import React from 'react'
import { createPlatformCredential, getAssertion, isUnlocked, clearUnlocked } from './webauthn'

export default function WebAuthnLock() {
  const [status, setStatus] = React.useState(isUnlocked() ? 'Unlocked' : 'Locked')

  const handleRegister = async () => {
    try {
      setStatus('Registering...')
      const id = await createPlatformCredential()
      setStatus('Credential registered: ' + id.slice(0,8) + '...')
    } catch (e) { setStatus('Register failed: '+e.message) }
  }

  const handleUnlock = async () => {
    try {
      setStatus('Requesting assertion...')
      await getAssertion()
      setStatus('Unlocked (session)')
    } catch (e) { setStatus('Unlock failed: '+e.message) }
  }

  const handleClear = () => {
    clearUnlocked()
    setStatus('Locked')
  }

  return (
    <div style={{border:'1px solid #ddd', padding:12, marginTop:12}}>
      <h3>WebAuthn prototype</h3>
      <p>This is a local demonstration of platform WebAuthn. It registers a credential on your device and uses it to unlock a session flag.</p>
      <div>
        <button onClick={handleRegister}>Register Platform Credential (Face/Touch)</button>
        <button onClick={handleUnlock} style={{marginLeft:8}}>Unlock (assertion)</button>
        <button onClick={handleClear} style={{marginLeft:8}}>Clear</button>
      </div>
      <p>Status: <strong>{status}</strong></p>
    </div>
  )
}
