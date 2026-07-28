import axios from 'axios'

let heartbeatTimer = null

export const initHeartbeat = (authStore) => {
  if (heartbeatTimer) clearInterval(heartbeatTimer)

  const sendPing = async () => {
    // Only send ping if tab is active/focused and user is logged in
    if (document.visibilityState !== 'visible' || !authStore.token) return

    const hostname = window.location.hostname
    let subdomain = 'club'
    if (hostname.startsWith('ctf')) subdomain = 'ctf'
    else if (hostname.startsWith('hackerxploit') && !hostname.startsWith('club')) subdomain = 'intro'

    try {
      await axios.post('/api/heartbeat', { subdomain })
    } catch (err) {
      // Silent error for background pings
    }
  }

  // Initial ping on load if visible
  sendPing()

  // Set interval every 60 seconds
  heartbeatTimer = setInterval(sendPing, 60000)

  // Listen for tab focus/visibility changes
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
      sendPing()
    }
  })
}

export const stopHeartbeat = () => {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer)
    heartbeatTimer = null
  }
}
