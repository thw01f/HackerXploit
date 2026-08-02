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
    onlineUsers: [],
    isOpen: false
  }),
  actions: {
    initSocket() {
      const authStore = useAuthStore()
      if (!authStore.isAuthenticated || this.socket) return

      this.socket = io({
        withCredentials: true
      })

      this.socket.on('presence_update', (data) => {
        this.onlineCount = data.online_count
        this.onlineUsers = data.online_users || []
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
      if (!this.socket || !content.trim()) return
      this.socket.emit('send_message', {
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
