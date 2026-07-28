import { defineStore } from 'pinia'
import { io } from 'socket.io-client'
import axios from 'axios'
import { useAuthStore } from './auth'

export const useChatStore = defineStore('chat', {
  state: () => ({
    socket: null,
    activeChannel: 'general',
    messages: [],
    onlineCount: 1,
    isOpen: false
  }),
  actions: {
    initSocket() {
      const authStore = useAuthStore()
      if (!authStore.token || this.socket) return

      this.socket = io({
        query: { token: authStore.token }
      })

      this.socket.on('presence_update', (data) => {
        this.onlineCount = data.online_count
      })

      this.socket.on('new_message', (msg) => {
        if (msg.channel === this.activeChannel) {
          this.messages.push(msg)
        }
      })

      this.joinChannel(this.activeChannel)
    },

    async joinChannel(channel) {
      this.activeChannel = channel
      if (this.socket) {
        this.socket.emit('join_channel', { channel })
      }
      try {
        const res = await axios.get(`/api/chat/messages?channel=${channel}`)
        this.messages = res.data.messages
      } catch (err) {
        console.error('Failed to fetch chat history', err)
      }
    },

    sendMessage(content) {
      const authStore = useAuthStore()
      if (!this.socket || !content.trim()) return
      this.socket.emit('send_message', {
        token: authStore.token,
        channel: this.activeChannel,
        content: content.trim()
      })
    },

    async softDeleteMessage(msgId) {
      try {
        await axios.delete(`/api/chat/messages/${msgId}`)
        const idx = this.messages.findIndex(m => m.id === msgId)
        if (idx !== -1) {
          this.messages[idx].is_deleted = true
          this.messages[idx].content = '[Message deleted by moderator]'
        }
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to soft delete message')
      }
    }
  }
})
