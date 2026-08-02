<template>
  <div class="max-w-[1600px] mx-auto px-4 py-8">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
      <div>
        <div class="flex items-center space-x-3">
          <h1 class="text-2xl font-bold text-white tracking-tight">General Chat</h1>
          <span v-if="chatEnabled" class="px-2.5 py-0.5 rounded-full text-sm font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
            <span class="relative flex h-1.5 w-1.5">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-400"></span>
            </span>
            Live Text Channel
          </span>
          <span v-else class="px-2.5 py-0.5 rounded-full text-sm font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            Disabled by Admin
          </span>
        </div>
        <p class="text-sm text-slate-400 mt-1">Real-time club discussion channel. Strictly text-only.</p>
      </div>

      <!-- Admin Actions -->
      <div v-if="authStore.isAdmin" class="flex items-center space-x-3">
        <button @click="showResetModal = true" class="btn-ghost text-sm py-1.5 px-3 border-rose-500/30 text-rose-400 hover:bg-rose-500/10">
          Reset Chat Room
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-6 items-start">
      <!-- Main Chat Window Card -->
      <div class="glass-panel border border-slate-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-[calc(100vh-260px)] min-h-[480px]">
        <!-- Messages Scroll Area -->
        <div ref="chatContainer" @scroll="handleScroll" class="flex-1 overflow-y-auto p-6 space-y-1 bg-slate-950/40">
          <div v-if="!chatEnabled" class="text-center py-20 space-y-3">
            <div class="w-16 h-16 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-2xl flex items-center justify-center mx-auto">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
            </div>
            <h3 class="text-lg font-bold text-white">General Text Chat Channel Disabled</h3>
            <p class="text-sm text-slate-400 max-w-md mx-auto">Real-time text chat has been temporarily paused site-wide by an administrator.</p>
          </div>

          <div v-else-if="messages.length === 0" class="text-center py-16">
            <p class="text-sm text-slate-500 font-mono">No messages yet. Start the conversation!</p>
          </div>

          <div
            v-else
            v-for="(msg, idx) in groupedMessages"
            :key="msg.id || msg.timestamp"
            class="group flex items-start space-x-3 hover:bg-white/[0.02] rounded-lg px-2 -mx-2"
            :class="msg.showHeader ? 'mt-4' : 'mt-0.5'"
          >
            <img
              v-if="msg.showHeader"
              :src="msg.sender_avatar || '/uploads/avatars/default.png'"
              class="w-9 h-9 rounded-full object-cover border shrink-0"
              :class="isOwnMessage(msg) ? 'border-[#9fef00]/50' : 'border-slate-700'"
            />
            <div v-else class="w-9 shrink-0 flex justify-center">
              <span class="text-[10px] text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity pt-1 tabular-nums">{{ formatTimeOnly(msg.timestamp) }}</span>
            </div>

            <div class="flex-1 min-w-0">
              <div v-if="msg.showHeader" class="flex items-center space-x-2">
                <span class="text-sm font-bold" :class="isOwnMessage(msg) ? 'text-[#9fef00]' : 'text-white'">{{ msg.sender_username }}</span>
                <span :class="getRoleColor(msg.sender_role)" class="text-xs font-semibold uppercase px-1.5 py-0.2 bg-slate-800 rounded">
                  {{ msg.sender_role }}
                </span>
                <span class="text-xs text-slate-500">{{ formatTimestamp(msg.timestamp) }}</span>

                <!-- Message Actions -->
                <div class="opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-2 ml-auto">
                  <button v-if="!msg.is_deleted" @click="openReportModal(msg)" class="text-sm text-slate-500 hover:text-amber-400">
                    Report
                  </button>
                  <button v-if="authStore.isTeacher && !msg.is_deleted" @click="softDeleteMessage(msg.id)" class="text-sm text-slate-500 hover:text-rose-400">
                    Delete
                  </button>
                </div>
              </div>
              <!-- Content Rendering -->
              <div class="flex items-start gap-2" :class="msg.showHeader ? 'mt-1' : ''">
                <div v-if="msg.is_deleted" class="text-sm text-rose-400/80 italic font-mono bg-rose-500/5 px-3 py-1.5 rounded-lg border border-rose-500/10 inline-block">
                  {{ msg.content }}
                </div>
                <div
                  v-else
                  :class="isOwnMessage(msg) ? 'bg-[#9fef00]/10 border-[#9fef00]/20' : 'bg-slate-900/60 border-slate-800/80'"
                  class="text-sm text-slate-200 p-3 rounded-xl border leading-relaxed break-words max-w-3xl"
                >
                  <template v-for="(seg, segIdx) in renderSegments(msg.content)" :key="segIdx">
                    <span
                      v-if="seg.mention"
                      :class="seg.self ? 'bg-[#9fef00]/25 text-[#9fef00] font-semibold rounded px-1' : 'bg-[#00f0ff]/10 text-[#00f0ff] font-semibold rounded px-1'"
                    >{{ seg.text }}</span>
                    <span v-else>{{ seg.text }}</span>
                  </template>
                </div>

                <!-- Actions for grouped (headerless) messages, shown inline next to the bubble -->
                <div v-if="!msg.showHeader" class="opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-2 shrink-0 pt-2">
                  <button v-if="!msg.is_deleted" @click="openReportModal(msg)" class="text-sm text-slate-500 hover:text-amber-400">
                    Report
                  </button>
                  <button v-if="authStore.isTeacher && !msg.is_deleted" @click="softDeleteMessage(msg.id)" class="text-sm text-slate-500 hover:text-rose-400">
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Jump to latest button, shown only when scrolled away from bottom -->
        <transition name="fade">
          <button
            v-if="showJumpToLatest"
            @click="scrollToBottom(true)"
            class="absolute bottom-24 right-8 lg:right-[336px] bg-[#9fef00] text-black text-sm font-bold px-3 py-1.5 rounded-full shadow-lg flex items-center gap-1.5"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"/></svg>
            New messages
          </button>
        </transition>

        <!-- Chat Input Section (STRICTLY TEXT ONLY - NO UPLOADS) -->
        <div class="p-4 bg-slate-900/90 border-t border-slate-800">
          <div v-if="!chatEnabled" class="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-center">
            <p class="text-sm font-semibold text-rose-400">General chat is currently disabled by an administrator.</p>
          </div>
          <form v-else @submit.prevent="sendMessage" class="flex items-center space-x-3">
            <div class="relative flex-1">
              <!-- Mention Autocomplete Dropdown -->
              <div
                v-if="showMentionDropdown"
                class="absolute bottom-full mb-2 left-0 w-64 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl overflow-hidden z-10"
              >
                <button
                  v-for="(u, i) in mentionMatches"
                  :key="u.id"
                  type="button"
                  @mousedown.prevent="selectMention(u)"
                  class="w-full flex items-center gap-2.5 px-3 py-2 text-left transition-colors"
                  :class="i === activeMentionIndex ? 'bg-[#9fef00]/10' : 'hover:bg-slate-800'"
                >
                  <img :src="u.avatar_url || '/uploads/avatars/default.png'" class="w-6 h-6 rounded-full object-cover border border-slate-700 shrink-0" />
                  <span class="min-w-0 flex-1">
                    <span class="text-sm font-semibold text-white block truncate">{{ u.full_name || u.username }}</span>
                    <span class="text-xs text-slate-500 block truncate">@{{ u.username }}</span>
                  </span>
                </button>
              </div>
              <input
                ref="messageInput"
                v-model="newMessageText"
                type="text"
                placeholder="Type a message (text-only)... use @ to mention someone"
                class="input-field w-full py-2.5 text-sm"
                :disabled="sending"
                maxlength="2000"
                @input="handleMentionInput"
                @keydown="handleInputKeydown"
              />
            </div>
            <button type="submit" :disabled="sending || !newMessageText.trim()" class="btn-neon-cyan py-2.5 px-6 text-sm font-bold shrink-0">
              Send
            </button>
          </form>
        </div>
      </div>

      <!-- Online Members Panel -->
      <div class="glass-panel border border-slate-800 rounded-2xl p-4 space-y-3 lg:sticky lg:top-6">
        <h3 class="text-sm font-mono font-bold text-slate-300 uppercase flex items-center gap-2 pb-3 border-b border-slate-800">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-400"></span>
          </span>
          Online Now
          <span class="text-slate-500 font-normal">({{ chatStore.onlineCount }})</span>
        </h3>

        <div class="space-y-2.5 max-h-[calc(100vh-360px)] overflow-y-auto pr-1">
          <div v-for="u in chatStore.onlineUsers" :key="u.id" class="flex items-center gap-2.5">
            <div class="relative shrink-0">
              <img :src="u.avatar_url || '/uploads/avatars/default.png'" class="w-8 h-8 rounded-full object-cover border border-slate-700" />
              <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-400 border-2 border-[#111927]"></span>
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-bold text-white truncate">{{ u.full_name || u.username }}</p>
              <p class="text-[11px] text-slate-500 truncate">@{{ u.username }}</p>
            </div>
            <span :class="getRoleColor(u.role)" class="text-[10px] font-semibold uppercase px-1.5 py-0.2 bg-slate-800 rounded shrink-0">
              {{ u.role }}
            </span>
          </div>

          <p v-if="chatStore.onlineUsers.length === 0" class="text-sm text-slate-500 font-mono text-center py-4">
            Just you right now.
          </p>
        </div>
      </div>
    </div>

    <!-- Hard Reset Confirmation Modal (ADMIN ONLY) -->
    <div v-if="showResetModal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-slate-900 border border-rose-500/30 rounded-2xl p-6 max-w-md w-full shadow-2xl">
        <h3 class="text-lg font-bold text-rose-400">Confirm Room Hard-Reset</h3>
        <p class="text-sm text-slate-300 mt-2">Are you sure you want to hard-reset the general chat room? This will permanently delete ALL message history for all members.</p>
        <div class="flex justify-end space-x-3 mt-6">
          <button @click="showResetModal = false" class="btn-ghost text-sm py-2 px-4">Cancel</button>
          <button @click="executeHardReset" class="btn-neon-pink text-sm py-2 px-4">Yes, Purge History</button>
        </div>
      </div>
    </div>

    <!-- Report Modal -->
    <div v-if="showReportModal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl">
        <h3 class="text-base font-bold text-white">Report Chat Message</h3>
        <p class="text-sm text-slate-400 mt-1">Submit this message for staff moderation review.</p>
        <textarea
          v-model="reportReason"
          rows="3"
          placeholder="Reason for report (e.g. inappropriate behavior)..."
          class="input-field w-full mt-3 text-sm"
        ></textarea>
        <div class="flex justify-end space-x-3 mt-4">
          <button @click="showReportModal = false" class="btn-ghost text-sm py-2 px-4">Cancel</button>
          <button @click="submitReport" :disabled="!reportReason.trim()" class="btn-neon-cyan text-sm py-2 px-4">Submit Report</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useChatStore } from '../stores/chat'
import { usePreferences } from '../stores/preferences'
import axios from 'axios'

const authStore = useAuthStore()
const chatStore = useChatStore()
const prefs = usePreferences()

const chatEnabled = ref(true)
const newMessageText = ref('')
const sending = ref(false)
const chatContainer = ref(null)
const showJumpToLatest = ref(false)

const showResetModal = ref(false)
const showReportModal = ref(false)
const targetReportMsg = ref(null)
const reportReason = ref('')

const messageInput = ref(null)
const showMentionDropdown = ref(false)
const mentionMatches = ref([])
const mentionStartIndex = ref(-1)
const activeMentionIndex = ref(0)

const messages = computed(() => chatStore.messages)

// Group consecutive messages from the same sender within a short window so the
// thread doesn't repeat the avatar/name/timestamp for every single line - a
// standard chat-UX pattern this view was missing entirely.
const GROUP_WINDOW_MS = 4 * 60 * 1000
const groupedMessages = computed(() => {
  return messages.value.map((msg, idx) => {
    const prev = messages.value[idx - 1]
    const sameSender = prev && prev.user_id === msg.user_id && !prev.is_deleted && !msg.is_deleted
    const withinWindow = prev && (new Date(msg.timestamp) - new Date(prev.timestamp)) < GROUP_WINDOW_MS
    return { ...msg, showHeader: !(sameSender && withinWindow) }
  })
})

const isOwnMessage = (msg) => authStore.user && msg.user_id === authStore.user.id

// Discord-style @mention: split message content into plain/mention segments so
// known usernames render highlighted (own username gets an extra distinct style).
const MENTION_RE = /@([a-zA-Z0-9_.]+)/g
const renderSegments = (content) => {
  const segments = []
  const knownUsernames = new Set(chatStore.onlineUsers.map(u => u.username))
  let lastIndex = 0
  let match
  MENTION_RE.lastIndex = 0
  while ((match = MENTION_RE.exec(content)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ text: content.slice(lastIndex, match.index), mention: false })
    }
    const uname = match[1]
    const isSelf = authStore.user && uname === authStore.user.username
    const isKnown = isSelf || knownUsernames.has(uname)
    segments.push({ text: match[0], mention: isKnown, self: isSelf })
    lastIndex = MENTION_RE.lastIndex
  }
  if (lastIndex < content.length) {
    segments.push({ text: content.slice(lastIndex), mention: false })
  }
  return segments
}

// Detects an in-progress "@partial" token right before the caret and shows a
// filtered dropdown of online members to complete it, mirroring Discord's mention UX.
const handleMentionInput = (e) => {
  const cursorPos = e.target.selectionStart
  const textBeforeCursor = newMessageText.value.slice(0, cursorPos)
  const match = textBeforeCursor.match(/(?:^|\s)@([a-zA-Z0-9_.]*)$/)
  if (!match) {
    showMentionDropdown.value = false
    return
  }
  const query = match[1].toLowerCase()
  mentionStartIndex.value = cursorPos - match[1].length - 1
  mentionMatches.value = chatStore.onlineUsers
    .filter(u => u.username.toLowerCase().startsWith(query) || (u.full_name || '').toLowerCase().startsWith(query))
    .slice(0, 6)
  activeMentionIndex.value = 0
  showMentionDropdown.value = mentionMatches.value.length > 0
}

const selectMention = (u) => {
  const cursorPos = messageInput.value ? messageInput.value.selectionStart : newMessageText.value.length
  const before = newMessageText.value.slice(0, mentionStartIndex.value)
  const after = newMessageText.value.slice(cursorPos)
  const insertion = `@${u.username} `
  newMessageText.value = `${before}${insertion}${after}`
  showMentionDropdown.value = false
  nextTick(() => {
    if (!messageInput.value) return
    const newPos = (before + insertion).length
    messageInput.value.focus()
    messageInput.value.setSelectionRange(newPos, newPos)
  })
}

const handleInputKeydown = (e) => {
  if (!showMentionDropdown.value || mentionMatches.value.length === 0) return
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeMentionIndex.value = (activeMentionIndex.value + 1) % mentionMatches.value.length
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeMentionIndex.value = (activeMentionIndex.value - 1 + mentionMatches.value.length) % mentionMatches.value.length
  } else if (e.key === 'Enter' || e.key === 'Tab') {
    e.preventDefault()
    selectMention(mentionMatches.value[activeMentionIndex.value])
  } else if (e.key === 'Escape') {
    showMentionDropdown.value = false
  }
}

const fetchMessages = async () => {
  try {
    chatStore.initSocket()
    await chatStore.joinChannel('general')
    const res = await axios.get('/api/chat/messages?channel=general')
    chatEnabled.value = res.data.chat_enabled !== false
    await scrollToBottom()
  } catch (err) {
    console.error('Failed to load chat messages', err)
  }
}

watch(messages, () => {
  const nearBottom = isNearBottom()
  if (nearBottom) {
    scrollToBottom()
  } else {
    showJumpToLatest.value = true
  }
}, { deep: true })

const isNearBottom = () => {
  const el = chatContainer.value
  if (!el) return true
  return el.scrollHeight - el.scrollTop - el.clientHeight < 150
}

const handleScroll = () => {
  if (isNearBottom()) showJumpToLatest.value = false
}

const sendMessage = async () => {
  const text = newMessageText.value.trim()
  if (!text || sending.value) return
  sending.value = true
  newMessageText.value = ''
  showMentionDropdown.value = false

  try {
    // Send via socket for instant sub-millisecond broadcast
    if (chatStore.socket && chatStore.socket.connected) {
      chatStore.sendMessage(text)
    } else {
      // Fallback via HTTP POST
      const res = await axios.post('/api/chat/messages', {
        channel: 'general',
        content: text
      })
      chatStore.messages.push(res.data)
    }
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
    await chatStore.softDeleteMessage(msgId)
  } catch (err) {
    alert('Failed to delete message')
  }
}

const executeHardReset = async () => {
  try {
    await axios.post('/api/chat/reset', { channel: 'general' })
    showResetModal.value = false
    chatStore.messages = []
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
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: prefs.is12h.value })
}

const formatTimeOnly = (isoStr) => formatTimestamp(isoStr)

const scrollToBottom = async (force) => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    if (force) showJumpToLatest.value = false
  }
}

onMounted(() => {
  fetchMessages()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
