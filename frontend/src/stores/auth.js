import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // Session identity lives entirely in an HttpOnly cookie set by the backend;
    // the SPA never reads or stores the raw session token (avoids XSS session theft).
    user: null,
    authChecked: false,
    sessions: [],
    publicSettings: { general_chat_enabled: true },
    loading: false,
    error: null
  }),
  getters: {
    isAuthenticated: (state) => !!state.user,
    isRootAdmin: (state) => state.user?.role === 'root_admin',
    isAdmin: (state) => ['root_admin', 'admin'].includes(state.user?.role),
    isTeacher: (state) => ['root_admin', 'admin', 'teacher'].includes(state.user?.role),
    userRole: (state) => state.user?.role || 'guest'
  },
  actions: {
    async login(emailOrUsername, password, captchaToken) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.post('/api/auth/login', {
          email_or_username: emailOrUsername,
          password,
          captcha_token: captchaToken
        })
        this.user = res.data.user
        this.authChecked = true
        return res.data
      } catch (err) {
        this.error = err.response?.data?.error || 'Login failed'
        throw new Error(this.error)
      } finally {
        this.loading = false
      }
    },

    async register(payload) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.post('/api/auth/register', payload)
        return res.data
      } catch (err) {
        this.error = err.response?.data?.error || 'Registration failed'
        throw new Error(this.error)
      } finally {
        this.loading = false
      }
    },

    async fetchMe() {
      try {
        const res = await axios.get('/api/auth/me')
        this.user = res.data.user
        return this.user
      } catch (err) {
        this.user = null
        return null
      } finally {
        this.authChecked = true
      }
    },

    async fetchSessions() {
      if (!this.user) return
      try {
        const res = await axios.get('/api/auth/sessions')
        this.sessions = res.data.sessions
      } catch (err) {
        console.error('Failed to fetch active device sessions', err)
      }
    },

    async revokeSession(sessionId) {
      try {
        await axios.post(`/api/auth/sessions/${sessionId}/revoke`)
        await this.fetchSessions()
      } catch (err) {
        throw new Error(err.response?.data?.error || 'Failed to revoke session')
      }
    },

    async logout() {
      try {
        if (this.user) {
          await axios.post('/api/auth/logout')
        }
      } catch (e) {
        // ignore
      } finally {
        this.user = null
        this.sessions = []
      }
    },

    async fetchPublicSettings() {
      try {
        const res = await axios.get('/api/auth/public-settings')
        this.publicSettings = res.data
        return res.data
      } catch (err) {
        console.error('Failed to fetch public settings', err)
      }
    }
  }
})
