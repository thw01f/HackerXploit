<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-white tracking-tight">Platform Inbox</h1>
        <p class="text-xs text-slate-400 mt-1">Direct communications, announcements, and club notifications.</p>
      </div>

      <div class="flex items-center space-x-3">
        <router-link v-if="authStore.isTeacher" to="/inbox/compose" class="btn-neon-cyan text-xs py-2 px-4 flex items-center space-x-1.5">
          <span>✉️ Compose Broadcast</span>
        </router-link>
        <router-link v-if="authStore.isAdmin" to="/admin/inbox-log" class="btn-ghost text-xs py-2 px-4">
          📊 Read Logs
        </router-link>
      </div>
    </div>

    <!-- Layout Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Folder Sidebar -->
      <div class="lg:col-span-3 space-y-2">
        <div class="glass-panel border border-slate-800 rounded-xl p-3 space-y-1">
          <button @click="currentFolder = 'inbox'" :class="['w-full text-left px-3 py-2 rounded-lg text-xs font-semibold flex justify-between items-center transition-colors', currentFolder === 'inbox' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'text-slate-400 hover:bg-slate-800/60']">
            <span>📥 Inbox</span>
            <span v-if="unreadCount > 0" class="bg-cyan-500 text-black px-1.5 py-0.5 rounded-full text-[10px] font-bold">{{ unreadCount }}</span>
          </button>

          <button @click="currentFolder = 'archived'" :class="['w-full text-left px-3 py-2 rounded-lg text-xs font-semibold flex justify-between items-center transition-colors', currentFolder === 'archived' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'text-slate-400 hover:bg-slate-800/60']">
            <span>📦 Archived</span>
          </button>

          <button @click="currentFolder = 'sent'" :class="['w-full text-left px-3 py-2 rounded-lg text-xs font-semibold flex justify-between items-center transition-colors', currentFolder === 'sent' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'text-slate-400 hover:bg-slate-800/60']">
            <span>📤 Sent Messages</span>
          </button>
        </div>
      </div>

      <!-- Messages List -->
      <div class="lg:col-span-9">
        <div class="glass-panel border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
          <!-- Filter Header -->
          <div class="p-4 border-b border-slate-800 bg-slate-950/40 flex justify-between items-center">
            <span class="text-xs font-bold text-white uppercase tracking-wider">
              {{ currentFolder.toUpperCase() }} ({{ filteredMessages.length }})
            </span>
          </div>

          <!-- Message Items -->
          <div class="divide-y divide-slate-800/60 max-h-[600px] overflow-y-auto">
            <div v-if="filteredMessages.length === 0" class="p-12 text-center text-xs text-slate-500">
              No messages found in this folder.
            </div>

            <div
              v-for="msg in filteredMessages"
              :key="msg.recipient_id || msg.message_id || msg.id"
              @click="openMessage(msg)"
              :class="['p-4 transition-colors cursor-pointer flex flex-col md:flex-row justify-between items-start md:items-center gap-3', !msg.is_read && currentFolder === 'inbox' ? 'bg-slate-800/50 border-l-4 border-cyan-400' : 'hover:bg-slate-800/30']"
            >
              <div class="space-y-1 flex-1">
                <div class="flex items-center space-x-2">
                  <span :class="['text-xs font-bold', !msg.is_read && currentFolder === 'inbox' ? 'text-white font-extrabold' : 'text-slate-300']">
                    {{ msg.subject }}
                  </span>
                  <span class="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                    {{ msg.scope }}
                  </span>
                </div>
                <p class="text-xs text-slate-400 line-clamp-1">From: {{ msg.sender_name || msg.sender_username }} &bull; {{ msg.body }}</p>
              </div>

              <div class="flex items-center space-x-3 text-right">
                <span class="text-[11px] text-slate-500 whitespace-nowrap">{{ formatDate(msg.sent_at) }}</span>

                <!-- Inbox Row Actions -->
                <div v-if="currentFolder !== 'sent'" class="flex items-center space-x-2" @click.stop>
                  <button @click="toggleArchive(msg)" class="p-1 text-slate-400 hover:text-cyan-400" title="Archive">
                    📦
                  </button>
                  <button @click="deleteFromInbox(msg)" class="p-1 text-slate-400 hover:text-rose-400" title="Delete from my inbox">
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- View Message Detail Modal -->
    <div v-if="selectedMsg" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-2xl w-full shadow-2xl space-y-4 max-h-[85vh] overflow-y-auto">
        <div class="flex justify-between items-start border-b border-slate-800 pb-3">
          <div>
            <h3 class="text-lg font-bold text-white">{{ selectedMsg.subject }}</h3>
            <p class="text-xs text-slate-400 mt-1">From: {{ selectedMsg.sender_name }} ({{ selectedMsg.sender_role }}) &bull; {{ formatDate(selectedMsg.sent_at) }}</p>
          </div>
          <button @click="selectedMsg = null" class="text-slate-400 hover:text-white">✕</button>
        </div>

        <div class="text-sm text-slate-200 bg-slate-950/60 p-4 rounded-xl border border-slate-800 leading-relaxed whitespace-pre-wrap">
          {{ selectedMsg.body }}
        </div>

        <!-- Reply Section -->
        <div v-if="selectedMsg.allow_reply && currentFolder !== 'sent'" class="border-t border-slate-800 pt-4 space-y-3">
          <h4 class="text-xs font-bold text-cyan-400 uppercase tracking-wider">Send Reply</h4>
          <textarea v-model="replyText" rows="3" placeholder="Type your reply message..." class="input-field w-full text-xs"></textarea>
          <div class="flex justify-end">
            <button @click="submitReply" :disabled="!replyText.trim() || sendingReply" class="btn-neon-cyan text-xs py-2 px-5 font-bold">
              Send Reply
            </button>
          </div>
        </div>
        <div v-else-if="!selectedMsg.allow_reply && currentFolder !== 'sent'" class="text-xs text-amber-400/80 italic">
          🔒 Sender explicitly disabled replies for this message.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const authStore = useAuthStore()
const currentFolder = ref('inbox')
const inboxMessages = ref([])
const sentMessages = ref([])
const unreadCount = ref(0)

const selectedMsg = ref(null)
const replyText = ref('')
const sendingReply = ref(false)

const fetchInbox = async () => {
  try {
    const res = await axios.get('/api/inbox')
    inboxMessages.value = res.data.inbox || []
    unreadCount.value = res.data.unread_count || 0
  } catch (err) {
    console.error('Failed to load inbox', err)
  }
}

const fetchSent = async () => {
  try {
    const res = await axios.get('/api/inbox/sent')
    sentMessages.value = res.data.sent || []
  } catch (err) {
    console.error('Failed to load sent messages', err)
  }
}

const filteredMessages = computed(() => {
  if (currentFolder.value === 'inbox') {
    return inboxMessages.value.filter(m => !m.is_archived)
  } else if (currentFolder.value === 'archived') {
    return inboxMessages.value.filter(m => m.is_archived)
  } else if (currentFolder.value === 'sent') {
    return sentMessages.value
  }
  return []
})

const openMessage = async (msg) => {
  selectedMsg.value = msg
  replyText.value = ''
  if (!msg.is_read && msg.recipient_id) {
    try {
      await axios.put(`/api/inbox/recipients/${msg.recipient_id}/read`)
      msg.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch (err) {
      console.error(err)
    }
  }
}

const toggleArchive = async (msg) => {
  if (!msg.recipient_id) return
  try {
    await axios.put(`/api/inbox/recipients/${msg.recipient_id}/archive`)
    msg.is_archived = !msg.is_archived
  } catch (err) {
    alert('Failed to archive message')
  }
}

const deleteFromInbox = async (msg) => {
  if (!msg.recipient_id || !confirm('Remove this message from your inbox?')) return
  try {
    await axios.delete(`/api/inbox/recipients/${msg.recipient_id}`)
    inboxMessages.value = inboxMessages.value.filter(m => m.recipient_id !== msg.recipient_id)
  } catch (err) {
    alert('Failed to delete message from inbox')
  }
}

const submitReply = async () => {
  if (!selectedMsg.value || !replyText.value.trim() || sendingReply.value) return
  sendingReply.value = true
  try {
    await axios.post(`/api/inbox/${selectedMsg.value.message_id || selectedMsg.value.id}/reply`, {
      body: replyText.value.trim()
    })
    alert('Reply sent!')
    selectedMsg.value = null
    replyText.value = ''
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to send reply')
  } finally {
    sendingReply.value = false
  }
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  fetchInbox()
  fetchSent()
})
</script>
