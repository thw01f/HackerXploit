<template>
  <div class="space-y-6 font-mono">
    <AdminSubNav />

    <!-- Top Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-[#1f293d]">
      <div>
        <h1 class="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
          Admin <span class="text-[#9fef00]">Message Audit & Broadcast Log</span>
        </h1>
        <p class="text-xs text-slate-400 mt-1">Real-time audit log of all direct communications, announcements, and read-rate metrics.</p>
      </div>

      <!-- Quick Metrics Summary -->
      <div class="flex items-center space-x-3 bg-[#0d1420] p-2 rounded-xl border border-[#1f293d] text-xs">
        <div class="px-3 py-1 text-center border-r border-[#1f293d]">
          <span class="text-slate-400 block text-[10px]">Total Messages</span>
          <span class="text-white font-bold text-sm">{{ logs.length }}</span>
        </div>
        <div class="px-3 py-1 text-center">
          <span class="text-slate-400 block text-[10px]">Avg Read Rate</span>
          <span class="text-[#9fef00] font-bold text-sm">{{ averageReadRate }}%</span>
        </div>
      </div>
    </div>

    <!-- Search & Filter Controls -->
    <div class="flex flex-col sm:flex-row items-center justify-between gap-3 glass-panel p-3 rounded-xl border border-[#1f293d] bg-[#0d1420]/80">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="Search audit logs by subject, sender, or content..." 
        class="input-field w-full sm:w-80 text-xs bg-[#0b0e14]"
      />

      <div class="flex items-center space-x-2 w-full sm:w-auto">
        <select v-model="scopeFilter" class="input-field text-xs bg-[#0b0e14]">
          <option value="all">All Scopes</option>
          <option value="all_members">Broadcasts (All Members)</option>
          <option value="individual">Direct 1-on-1</option>
          <option value="role:teacher">Role: Teachers</option>
          <option value="role:member">Role: Members</option>
        </select>
      </div>
    </div>

    <!-- Audit Log Cards Container -->
    <div class="glass-panel border border-[#1f293d] rounded-2xl overflow-hidden shadow-2xl bg-[#0d1420]/90">
      <div class="p-4 border-b border-[#1f293d] bg-[#0b0e14]/80 flex justify-between items-center text-xs">
        <span class="font-extrabold text-white uppercase tracking-wider">Communication Reach & Read Analytics</span>
        <span class="text-slate-400">Displaying: {{ filteredLogs.length }} records</span>
      </div>

      <div class="divide-y divide-[#1f293d]/80 max-h-[650px] overflow-y-auto">
        <div v-if="filteredLogs.length === 0" class="p-12 text-center text-xs text-slate-500">
          No audit records found matching your filter criteria.
        </div>

        <div 
          v-for="log in filteredLogs" 
          :key="log.message_id" 
          class="p-5 hover:bg-[#151f30]/60 transition-colors space-y-3"
        >
          <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-2">
            <div class="flex items-center space-x-2 flex-wrap gap-y-1">
              <!-- Scope Tag -->
              <span :class="getScopeBadgeClass(log.scope)" class="text-[9px] font-extrabold uppercase px-2 py-0.5 rounded border">
                {{ getScopeLabel(log.scope) }}
              </span>

              <span class="text-sm font-bold text-white leading-snug">{{ log.subject }}</span>
            </div>

            <div class="flex items-center space-x-3 text-xs text-slate-400">
              <span>Sender: <strong class="text-white">@{{ log.sender_username }}</strong> ({{ log.sender_role }})</span>
              <span>&bull;</span>
              <span>{{ formatDate(log.sent_at) }}</span>
            </div>
          </div>

          <p class="text-xs text-slate-300 line-clamp-2 bg-[#070a10] p-3 rounded-lg border border-[#1f293d]/60 leading-relaxed">
            {{ log.body }}
          </p>

          <!-- Read Rate Analytics Bar -->
          <div class="space-y-1.5 pt-1">
            <div class="flex justify-between text-xs font-bold">
              <span class="text-slate-400 text-[11px]">Read Status: {{ log.read_count }} / {{ log.total_recipients }} recipients</span>
              <span :class="log.read_rate_pct > 50 ? 'text-[#9fef00]' : 'text-amber-400'">{{ log.read_rate_pct }}% Read</span>
            </div>
            <div class="w-full h-2 bg-[#151f30] rounded-full overflow-hidden border border-[#1f293d]">
              <div 
                class="h-full bg-gradient-to-r from-[#00f0ff] to-[#9fef00] rounded-full transition-all duration-500" 
                :style="{ width: log.read_rate_pct + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import AdminSubNav from '../components/AdminSubNav.vue'
import { usePreferences } from '../stores/preferences'

const prefs = usePreferences()
const logs = ref([])
const searchQuery = ref('')
const scopeFilter = ref('all')

const fetchLogs = async () => {
  try {
    const res = await axios.get('/api/inbox/admin/log')
    logs.value = res.data.inbox_logs || []
  } catch (err) {
    console.error('Failed to load inbox audit logs', err)
  }
}

const filteredLogs = computed(() => {
  let list = logs.value

  if (scopeFilter.value !== 'all') {
    list = list.filter(l => l.scope === scopeFilter.value)
  }

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(l => 
      l.subject.toLowerCase().includes(q) || 
      l.sender_username.toLowerCase().includes(q) || 
      (l.body && l.body.toLowerCase().includes(q))
    )
  }

  return list
})

const averageReadRate = computed(() => {
  if (logs.value.length === 0) return 0
  const sum = logs.value.reduce((acc, curr) => acc + (curr.read_rate_pct || 0), 0)
  return roundTo(sum / logs.value.length, 1)
})

const roundTo = (num, decimals) => {
  const factor = Math.pow(10, decimals)
  return Math.round(num * factor) / factor
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
  return d.toLocaleDateString([], { month: 'short', day: 'numeric' }) + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: prefs.is12h.value })
}

onMounted(() => {
  fetchLogs()
})
</script>
