<template>
  <div class="max-w-7xl mx-auto px-4 py-8 space-y-6">
    
    <!-- Top Header Bar -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-[#1f293d]">
      <div class="flex items-center space-x-3">
        <div class="p-2.5 rounded-xl bg-gradient-to-br from-[#9fef00]/20 to-[#00f0ff]/20 border border-[#9fef00]/30 text-[#9fef00]">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <div>
          <h1 class="text-2xl font-mono font-extrabold text-white tracking-tight flex items-center gap-2">
            HackerXploit <span class="text-[#9fef00]">Platform Inbox</span>
          </h1>
          <p class="text-xs text-slate-400 font-mono mt-0.5">Official platform communications, announcements, and support messaging.</p>
        </div>
      </div>

      <div class="flex items-center space-x-3">
        <router-link to="/inbox/compose" class="btn-htb text-xs py-2.5 px-4 flex items-center space-x-2 font-mono font-bold shadow-lg">
          <span>✉️ New Message</span>
        </router-link>
        <router-link v-if="authStore.isAdmin" to="/admin/inbox-log" class="btn-ghost text-xs py-2.5 px-4 font-mono font-semibold flex items-center space-x-1.5">
          <span>📊 Admin Audit Logs</span>
        </router-link>
      </div>
    </div>

    <!-- Main Grid Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      <!-- Left Folder Navigation Sidebar -->
      <div class="lg:col-span-3 space-y-3">
        <div class="glass-panel border border-[#1f293d] rounded-2xl p-3 bg-[#0d1420]/80 space-y-1.5 shadow-xl">
          
          <button 
            @click="setFolder('inbox')" 
            :class="[
              'w-full text-left px-3.5 py-2.5 rounded-xl text-xs font-mono font-bold flex justify-between items-center transition-all',
              currentFolder === 'inbox' ? 'bg-[#9fef00]/15 text-[#9fef00] border border-[#9fef00]/40 shadow-[0_0_15px_rgba(159,239,0,0.15)]' : 'text-slate-400 hover:bg-[#151f30] hover:text-white'
            ]"
          >
            <div class="flex items-center space-x-2.5">
              <span>📥 Inbox</span>
            </div>
            <span v-if="unreadCount > 0" class="bg-[#9fef00] text-black px-2 py-0.5 rounded-full text-[10px] font-mono font-extrabold animate-pulse">
              {{ unreadCount }}
            </span>
          </button>

          <button 
            @click="setFolder('sent')" 
            :class="[
              'w-full text-left px-3.5 py-2.5 rounded-xl text-xs font-mono font-bold flex justify-between items-center transition-all',
              currentFolder === 'sent' ? 'bg-[#00f0ff]/15 text-[#00f0ff] border border-[#00f0ff]/40 shadow-[0_0_15px_rgba(0,240,255,0.15)]' : 'text-slate-400 hover:bg-[#151f30] hover:text-white'
            ]"
          >
            <div class="flex items-center space-x-2.5">
              <span>📤 Sent Messages</span>
            </div>
          </button>

          <button 
            @click="setFolder('archived')" 
            :class="[
              'w-full text-left px-3.5 py-2.5 rounded-xl text-xs font-mono font-bold flex justify-between items-center transition-all',
              currentFolder === 'archived' ? 'bg-amber-500/15 text-amber-400 border border-amber-500/40 shadow-[0_0_15px_rgba(245,158,11,0.15)]' : 'text-slate-400 hover:bg-[#151f30] hover:text-white'
            ]"
          >
            <div class="flex items-center space-x-2.5">
              <span>📦 Archived</span>
            </div>
          </button>

        </div>

        <!-- System Status Banner -->
        <div class="glass-panel border border-[#1f293d] rounded-2xl p-4 bg-[#0d1420]/80 space-y-2 text-xs font-mono">
          <div class="flex items-center space-x-2 text-[#9fef00]">
            <span class="w-2 h-2 rounded-full bg-[#9fef00]"></span>
            <span class="font-bold uppercase tracking-wider text-[10px]">Encrypted Channel Active</span>
          </div>
          <p class="text-slate-400 text-[11px] leading-relaxed">
            All messages are monitored under Cyber Club governance guidelines.
          </p>
        </div>
      </div>

      <!-- Right Message Listing & Filter Container -->
      <div class="lg:col-span-9 space-y-4">
        <div class="glass-panel border border-[#1f293d] rounded-2xl overflow-hidden shadow-2xl bg-[#0d1420]/90">
          
          <!-- Filter Tabs Header Bar -->
          <div class="p-4 border-b border-[#1f293d] bg-[#0b0e14]/80 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <div class="flex items-center space-x-2">
              <span class="text-xs font-mono font-extrabold text-white uppercase tracking-wider">
                {{ currentFolder.toUpperCase() }}
              </span>
              <span class="text-xs font-mono text-slate-500">({{ displayList.length }})</span>
            </div>

            <!-- Filter Chips (All, Direct 1-on-1, Broadcasts) -->
            <div v-if="currentFolder === 'inbox'" class="flex items-center space-x-1.5 bg-[#151f30] p-1 rounded-xl border border-[#1f293d]">
              <button 
                @click="filterMode = 'all'" 
                :class="['px-3 py-1 rounded-lg text-[11px] font-mono font-bold transition-all', filterMode === 'all' ? 'bg-[#9fef00] text-black shadow' : 'text-slate-400 hover:text-white']"
              >
                All
              </button>
              <button 
                @click="filterMode = 'direct'" 
                :class="['px-3 py-1 rounded-lg text-[11px] font-mono font-bold transition-all', filterMode === 'direct' ? 'bg-[#00f0ff] text-black shadow' : 'text-slate-400 hover:text-white']"
              >
                💬 Direct 1-on-1
              </button>
              <button 
                v-if="authStore.isTeacher || authStore.isAdmin"
                @click="filterMode = 'broadcast'" 
                :class="['px-3 py-1 rounded-lg text-[11px] font-mono font-bold transition-all', filterMode === 'broadcast' ? 'bg-amber-400 text-black shadow' : 'text-slate-400 hover:text-white']"
              >
                📣 Broadcasts
              </button>
            </div>
          </div>

          <!-- Message Cards List -->
          <div class="divide-y divide-[#1f293d]/80 max-h-[620px] overflow-y-auto">
            <div v-if="loading" class="p-12 text-center text-xs font-mono text-slate-500 animate-pulse">
              Loading communications stream...
            </div>

            <div v-else-if="displayList.length === 0" class="p-12 text-center text-xs font-mono text-slate-500 space-y-2">
              <span class="block text-2xl">📭</span>
              <p>No communications found in this view.</p>
            </div>

            <!-- Message Item Card -->
            <div
              v-else
              v-for="msg in displayList"
              :key="msg.recipient_id || msg.message_id || msg.id"
              @click="openMessage(msg)"
              :class="[
                'p-4 transition-all cursor-pointer flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:bg-[#151f30]/60',
                !msg.is_read && currentFolder === 'inbox' ? 'bg-[#151f30]/90 border-l-4 border-[#9fef00]' : ''
              ]"
            >
              <div class="flex items-start space-x-3.5 min-w-0 flex-1">
                <!-- Avatar Preview -->
                <img 
                  :src="msg.sender_avatar || '/uploads/avatars/default.png'" 
                  @error="$event.target.src='https://api.dicebear.com/7.x/bottts/svg?seed=' + (msg.sender_username || 'user')"
                  class="w-10 h-10 rounded-xl object-cover border border-[#1f293d] flex-shrink-0 mt-0.5" 
                />

                <div class="space-y-1 min-w-0 flex-1 font-mono">
                  <!-- Top Meta: Sender name & Scope badge -->
                  <div class="flex items-center space-x-2 flex-wrap gap-y-1">
                    <span :class="['text-xs font-bold truncate', !msg.is_read && currentFolder === 'inbox' ? 'text-white font-extrabold' : 'text-slate-300']">
                      {{ msg.sender_name || msg.sender_username }}
                    </span>
                    <span class="text-[10px] text-slate-500">(@{{ msg.sender_username }})</span>
                    
                    <!-- Role Pill -->
                    <span :class="getRoleBadgeClass(msg.sender_role)" class="text-[9px] font-bold uppercase px-2 py-0.2 rounded border">
                      {{ msg.sender_role }}
                    </span>

                    <!-- Scope Badge -->
                    <span :class="getScopeBadgeClass(msg.scope)" class="text-[9px] font-extrabold uppercase px-2 py-0.2 rounded border shadow">
                      {{ getScopeLabel(msg.scope) }}
                    </span>
                  </div>

                  <!-- Subject & Body Snippet -->
                  <h4 :class="['text-xs font-bold leading-snug truncate', !msg.is_read && currentFolder === 'inbox' ? 'text-[#9fef00]' : 'text-slate-200']">
                    {{ msg.subject }}
                  </h4>
                  <p class="text-xs text-slate-400 line-clamp-1 leading-relaxed">
                    {{ msg.body }}
                  </p>
                </div>
              </div>

              <!-- Right Info: Sent date & actions -->
              <div class="flex items-center space-x-3 text-right flex-shrink-0 self-end md:self-center font-mono">
                <span class="text-[11px] text-slate-500">{{ formatDate(msg.sent_at) }}</span>

                <!-- Quick Action Buttons -->
                <div v-if="currentFolder !== 'sent'" class="flex items-center space-x-1.5" @click.stop>
                  <button 
                    @click="toggleArchive(msg)" 
                    class="p-1.5 rounded-lg text-slate-400 hover:text-[#00f0ff] hover:bg-[#151f30] transition-colors" 
                    :title="msg.is_archived ? 'Unarchive' : 'Archive'"
                  >
                    📦
                  </button>
                  <button 
                    @click="deleteFromInbox(msg)" 
                    class="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-[#151f30] transition-colors" 
                    title="Remove from my inbox"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- View Message Thread & Interactive Reply Modal -->
    <div v-if="selectedMsg" class="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
      <div class="glass-panel border border-[#1f293d] bg-[#0d1420] rounded-2xl p-6 max-w-2xl w-full shadow-2xl space-y-5 max-h-[85vh] overflow-y-auto">
        
        <!-- Modal Header -->
        <div class="flex justify-between items-start border-b border-[#1f293d] pb-4">
          <div class="space-y-1 font-mono">
            <div class="flex items-center space-x-2">
              <span :class="getScopeBadgeClass(selectedMsg.scope)" class="text-[9px] font-extrabold uppercase px-2 py-0.5 rounded border">
                {{ getScopeLabel(selectedMsg.scope) }}
              </span>
              <span class="text-[11px] text-slate-400">{{ formatDate(selectedMsg.sent_at) }}</span>
            </div>
            <h3 class="text-lg font-bold text-white leading-snug">{{ selectedMsg.subject }}</h3>
            <p class="text-xs text-slate-400">
              From: <span class="text-white font-bold">{{ selectedMsg.sender_name }}</span> (@{{ selectedMsg.sender_username }})
              &bull; <span class="text-[#9fef00] uppercase font-bold text-[10px]">{{ selectedMsg.sender_role }}</span>
            </p>
          </div>
          <button @click="selectedMsg = null" class="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#151f30] transition-colors">✕</button>
        </div>

        <!-- Message Body -->
        <div class="text-xs font-mono text-slate-200 bg-[#070a10] p-4 rounded-xl border border-[#1f293d] leading-relaxed whitespace-pre-wrap">
          {{ selectedMsg.body }}
        </div>

        <!-- Interactive Reply Section -->
        <div v-if="selectedMsg.allow_reply && currentFolder !== 'sent'" class="border-t border-[#1f293d] pt-4 space-y-3 font-mono">
          <h4 class="text-xs font-bold text-[#00f0ff] uppercase tracking-wider flex items-center gap-1.5">
            <span>💬 Send Direct Reply</span>
          </h4>
          <textarea 
            v-model="replyText" 
            rows="3" 
            placeholder="Write your response message..." 
            class="input-field w-full text-xs font-mono"
          ></textarea>
          <div class="flex justify-end">
            <button 
              @click="submitReply" 
              :disabled="!replyText.trim() || sendingReply" 
              class="btn-neon-cyan text-xs py-2 px-5 font-mono font-bold"
            >
              {{ sendingReply ? 'Sending...' : 'Send Reply' }}
            </button>
          </div>
        </div>
        <div v-else-if="!selectedMsg.allow_reply && currentFolder !== 'sent'" class="text-xs font-mono text-amber-400/80 italic bg-amber-950/20 p-3 rounded-lg border border-amber-500/20">
          🔒 Direct replies are disabled by the sender for this message.
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
const filterMode = ref('all') // 'all' | 'direct' | 'broadcast'
const loading = ref(true)
const inboxMessages = ref([])
const sentMessages = ref([])
const unreadCount = ref(0)

const selectedMsg = ref(null)
const replyText = ref('')
const sendingReply = ref(false)

const setFolder = (folder) => {
  currentFolder.value = folder
  if (folder === 'sent' && sentMessages.value.length === 0) {
    fetchSent()
  }
}

const fetchInbox = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/inbox')
    inboxMessages.value = res.data.inbox || []
    unreadCount.value = res.data.unread_count || 0
  } catch (err) {
    console.error('Failed to load inbox', err)
  } finally {
    loading.value = false
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

const displayList = computed(() => {
  let list = []
  if (currentFolder.value === 'inbox') {
    list = inboxMessages.value.filter(m => !m.is_archived)
  } else if (currentFolder.value === 'archived') {
    list = inboxMessages.value.filter(m => m.is_archived)
  } else if (currentFolder.value === 'sent') {
    list = sentMessages.value
  }

  if (currentFolder.value === 'inbox') {
    if (filterMode.value === 'direct') {
      list = list.filter(m => m.scope === 'individual' || m.scope === 'custom_list')
    } else if (filterMode.value === 'broadcast') {
      list = list.filter(m => m.scope !== 'individual' && m.scope !== 'custom_list')
    }
  }

  return list
})

const openMessage = async (msg) => {
  selectedMsg.value = msg
  replyText.value = ''
  if (!msg.is_read && currentFolder.value === 'inbox') {
    msg.is_read = true
    if (unreadCount.value > 0) unreadCount.value--
    try {
      await axios.put(`/api/inbox/recipients/${msg.recipient_id}/read`)
    } catch (err) {
      console.error('Failed to mark read', err)
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
    alert('Failed to remove message from inbox')
  }
}

const submitReply = async () => {
  if (!selectedMsg.value || !replyText.value.trim()) return
  sendingReply.value = true
  try {
    await axios.post(`/api/inbox/${selectedMsg.value.message_id || selectedMsg.value.id}/reply`, {
      body: replyText.value
    })
    alert('Reply sent successfully!')
    replyText.value = ''
    selectedMsg.value = null
    fetchInbox()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to send reply')
  } finally {
    sendingReply.value = false
  }
}

const getRoleBadgeClass = (role) => {
  if (role === 'root_admin' || role === 'admin') return 'bg-purple-950/80 text-purple-400 border-purple-800'
  if (role === 'teacher') return 'bg-amber-950/80 text-amber-400 border-amber-800'
  return 'bg-slate-800 text-slate-400 border-slate-700'
}

const getScopeBadgeClass = (scope) => {
  if (scope === 'all_members' || scope === 'all_teachers') return 'bg-amber-500/15 text-amber-400 border-amber-500/30'
  if (scope?.startswith && scope.startswith('role:')) return 'bg-purple-500/15 text-purple-400 border-purple-500/30'
  return 'bg-[#00f0ff]/15 text-[#00f0ff] border-[#00f0ff]/30'
}

const getScopeLabel = (scope) => {
  if (scope === 'all_members') return 'BROADCAST: ALL MEMBERS'
  if (scope === 'all_teachers') return 'BROADCAST: TEACHERS'
  if (scope === 'role:member') return 'MEMBERS ONLY'
  if (scope === 'role:teacher') return 'TEACHERS ONLY'
  return 'DIRECT MESSAGE'
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleDateString([], { month: 'short', day: 'numeric' }) + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  fetchInbox()
})
</script>
