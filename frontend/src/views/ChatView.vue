<template>
  <div class="max-w-5xl mx-auto px-4 py-8">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
      <div>
        <div class="flex items-center space-x-3">
          <h1 class="text-2xl font-bold text-white tracking-tight">General Chat</h1>
          <span v-if="chatEnabled" class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span> Live Text Channel
          </span>
          <span v-else class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            Disabled by Admin
          </span>
        </div>
        <p class="text-xs text-slate-400 mt-1">Real-time club discussion channel. Strictly text-only.</p>
      </div>

      <!-- Admin Actions -->
      <div v-if="authStore.isAdmin" class="flex items-center space-x-3">
        <button @click="showResetModal = true" class="btn-ghost text-xs py-1.5 px-3 border-rose-500/30 text-rose-400 hover:bg-rose-500/10">
          ⚠️ Reset Chat Room
        </button>
      </div>
    </div>

    <!-- Main Chat Window Card -->
    <div class="glass-panel border border-slate-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-[650px]">
      <!-- Messages Scroll Area -->
      <div ref="chatContainer" class="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-950/40">
        <div v-if="messages.length === 0" class="text-center py-16">
          <p class="text-sm text-slate-500 font-mono">No messages yet. Start the conversation!</p>
        </div>

        <div v-for="msg in messages" :key="msg.id" class="flex items-start space-x-3 group">
          <img :src="msg.sender_avatar || '/uploads/avatars/default.png'" class="w-9 h-9 rounded-full object-cover border border-slate-700 mt-0.5" />
          <div class="flex-1 min-w-0">
            <div class="flex items-center space-x-2">
              <span class="text-xs font-bold text-white">{{ msg.sender_username }}</span>
              <span :class="getRoleColor(msg.sender_role)" class="text-[10px] font-semibold uppercase px-1.5 py-0.2 bg-slate-800 rounded">
                {{ msg.sender_role }}
              </span>
              <span class="text-[10px] text-slate-500">{{ formatTimestamp(msg.timestamp) }}</span>

              <!-- Message Actions -->
              <div class="opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-2 ml-auto">
                <button v-if="!msg.is_deleted" @click="openReportModal(msg)" class="text-[11px] text-slate-500 hover:text-amber-400">
                  Report
                </button>
                <button v-if="authStore.isTeacher && !msg.is_deleted" @click="softDeleteMessage(msg.id)" class="text-[11px] text-slate-500 hover:text-rose-400">
                  Delete
                </button>
              </div>
            </div>

            <!-- Content Rendering -->
            <div v-if="msg.is_deleted" class="mt-1 text-xs text-rose-400/80 italic font-mono bg-rose-500/5 px-3 py-1.5 rounded-lg border border-rose-500/10 inline-block">
              {{ msg.content }}
            </div>
            <div v-else class="mt-1 text-sm text-slate-200 bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 leading-relaxed break-words max-w-3xl">
              {{ msg.content }}
            </div>
          </div>
        </div>
      </div>

      <!-- Chat Input Section (STRICTLY TEXT ONLY - NO UPLOADS) -->
      <div class="p-4 bg-slate-900/90 border-t border-slate-800">
        <div v-if="!chatEnabled" class="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-center">
          <p class="text-xs font-semibold text-rose-400">General chat has been temporarily paused by an administrator.</p>
        </div>
        <form v-else @submit.prevent="sendMessage" class="flex items-center space-x-3">
          <input
            v-model="newMessageText"
            type="text"
            placeholder="Type a message (text-only)..."
            class="input-field flex-1 py-2.5 text-sm"
            :disabled="sending"
          />
          <button type="submit" :disabled="sending || !newMessageText.trim()" class="btn-neon-cyan py-2.5 px-6 text-xs font-bold">
            Send
          </button>
        </form>
      </div>
    </div>

    <!-- Hard Reset Confirmation Modal (ADMIN ONLY) -->
    <div v-if="showResetModal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-slate-900 border border-rose-500/30 rounded-2xl p-6 max-w-md w-full shadow-2xl">
        <h3 class="text-lg font-bold text-rose-400">⚠️ Confirm Room Hard-Reset</h3>
        <p class="text-xs text-slate-300 mt-2">Are you sure you want to hard-reset the general chat room? This will permanently delete ALL message history for all members.</p>
        <div class="flex justify-end space-x-3 mt-6">
          <button @click="showResetModal = false" class="btn-ghost text-xs py-2 px-4">Cancel</button>
          <button @click="executeHardReset" class="btn-neon-pink text-xs py-2 px-4">Yes, Purge History</button>
        </div>
      </div>
    </div>

    <!-- Report Modal -->
    <div v-if="showReportModal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl">
        <h3 class="text-base font-bold text-white">Report Chat Message</h3>
        <p class="text-xs text-slate-400 mt-1">Submit this message for staff moderation review.</p>
        <textarea
          v-model="reportReason"
          rows="3"
          placeholder="Reason for report (e.g. inappropriate behavior)..."
          class="input-field w-full mt-3 text-xs"
        ></textarea>
        <div class="flex justify-end space-x-3 mt-4">
          <button @click="showReportModal = false" class="btn-ghost text-xs py-2 px-4">Cancel</button>
          <button @click="submitReport" :disabled="!reportReason.trim()" class="btn-neon-cyan text-xs py-2 px-4">Submit Report</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const authStore = useAuthStore()
const messages = ref([])
const chatEnabled = ref(true)
const newMessageText = ref('')
const sending = ref(false)
const chatContainer = ref(null)

const showResetModal = ref(false)
const showReportModal = ref(false)
const targetReportMsg = ref(null)
const reportReason = ref('')

const fetchMessages = async () => {
  try {
    const res = await axios.get('/api/chat/messages?channel=general')
    messages.value = res.data.messages || []
    chatEnabled.value = res.data.chat_enabled !== false
    await scrollToBottom()
  } catch (err) {
    console.error('Failed to load chat messages', err)
  }
}

const sendMessage = async () => {
  if (!newMessageText.value.trim() || sending.value) return
  sending.value = true
  try {
    const res = await axios.post('/api/chat/messages', {
      channel: 'general',
      content: newMessageText.value.trim()
    })
    messages.value.push(res.data)
    newMessageText.value = ''
    await scrollToBottom()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to send message')
  } finally {
    sending.value = false
  }
}

const softDeleteMessage = async (msgId) => {
  if (!confirm('Soft-delete this chat message?')) return
  try {
    const res = await axios.delete(`/api/chat/messages/${msgId}`)
    const idx = messages.value.findIndex(m => m.id === msgId)
    if (idx !== -1) {
      messages.value[idx] = res.data.chat_message
    }
  } catch (err) {
    alert('Failed to delete message')
  }
}

const executeHardReset = async () => {
  try {
    await axios.post('/api/chat/reset', { channel: 'general' })
    showResetModal.value = false
    messages.value = []
    alert('Chat room history purged')
  } catch (err) {
    alert('Failed to reset chat room')
  }
}

const openReportModal = (msg) => {
  targetReportMsg.value = msg
  reportReason.value = ''
  showReportModal.value = true
}

const submitReport = async () => {
  if (!targetReportMsg.value || !reportReason.value.trim()) return
  try {
    await axios.post(`/api/chat/messages/${targetReportMsg.value.id}/report`, {
      reason: reportReason.value.trim()
    })
    showReportModal.value = false
    alert('Report submitted for moderation')
  } catch (err) {
    alert('Failed to submit report')
  }
}

const getRoleColor = (role) => {
  if (role === 'root_admin' || role === 'admin') return 'text-purple-400 border border-purple-500/30'
  if (role === 'teacher') return 'text-cyan-400 border border-cyan-500/30'
  return 'text-slate-400'
}

const formatTimestamp = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

onMounted(() => {
  fetchMessages()
})
</script>
