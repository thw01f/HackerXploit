import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('hx_user')) || null,
    token: localStorage.getItem('hx_token') || null,
    sessions: [],
    publicSettings: { general_chat_enabled: true },
    loading: false,
    error: null
  }),
  getters: {
    isAuthenticated: (state) => !!state.user && !!state.token,
    isRootAdmin: (state) => state.user?.role === 'root_admin',
    isAdmin: (state) => ['root_admin', 'admin'].includes(state.user?.role),
    isTeacher: (state) => ['root_admin', 'admin', 'teacher'].includes(state.user?.role),
    userRole: (state) => state.user?.role || 'guest'
  },
  actions: {
    async login(emailOrUsername, password) {
      this.loading = true
      this.error = null
      try {
        const res = await axios.post('/api/auth/login', {
          email_or_username: emailOrUsername,
          password
        })
        this.token = res.data.token
        this.user = res.data.user
        localStorage.setItem('hx_token', this.token)
        localStorage.setItem('hx_user', JSON.stringify(this.user))
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
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
      if (!this.token) return null
      axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      try {
        const res = await axios.get('/api/auth/me')
        this.user = res.data.user
        localStorage.setItem('hx_user', JSON.stringify(this.user))
        return this.user
      } catch (err) {
        this.logout()
        return null
      }
    },

    async fetchSessions() {
      if (!this.token) return
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
        if (this.token) {
          await axios.post('/api/auth/logout')
        }
      } catch (e) {
        // ignore
      } finally {
        this.user = null
        this.token = null
        this.sessions = []
        localStorage.removeItem('hx_token')
        localStorage.removeItem('hx_user')
        delete axios.defaults.headers.common['Authorization']
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
