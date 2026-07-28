<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <div class="flex items-center space-x-3 mb-6">
      <router-link to="/admin" class="btn-ghost text-xs py-1.5 px-3">&larr; Control Center</router-link>
      <h1 class="text-2xl font-bold text-white tracking-tight">Admin Inbox Broadcast Audit Log</h1>
    </div>

    <div class="glass-panel border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
      <div class="p-4 border-b border-slate-800 bg-slate-950/40 flex justify-between items-center">
        <span class="text-xs font-bold text-white uppercase tracking-wider">Site-Wide Message Reach & Read Analytics</span>
        <span class="text-xs text-slate-400">Total Sent: {{ logs.length }}</span>
      </div>

      <div class="divide-y divide-slate-800/60 max-h-[650px] overflow-y-auto">
        <div v-if="logs.length === 0" class="p-12 text-center text-xs text-slate-500">
          No broadcast messages logged yet.
        </div>

        <div v-for="log in logs" :key="log.message_id" class="p-5 hover:bg-slate-800/30 transition-colors space-y-3">
          <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-2">
            <div>
              <span class="text-xs font-bold text-cyan-400 uppercase tracking-wider px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20 mr-2">
                {{ log.scope }}
              </span>
              <span class="text-sm font-bold text-white">{{ log.subject }}</span>
            </div>
            <span class="text-xs text-slate-400">Sender: {{ log.sender_username }} &bull; {{ formatDate(log.sent_at) }}</span>
          </div>

          <!-- Read Rate Progress Bar -->
          <div class="space-y-1">
            <div class="flex justify-between text-xs font-semibold">
              <span class="text-slate-400">Read Progress: {{ log.read_count }} / {{ log.total_recipients }} recipients</span>
              <span class="text-cyan-400">{{ log.read_rate_pct }}%</span>
            </div>
            <div class="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all" :style="{ width: log.read_rate_pct + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const logs = ref([])

const fetchLogs = async () => {
  try {
    const res = await axios.get('/api/inbox/admin/log')
    logs.value = res.data.inbox_logs || []
  } catch (err) {
    console.error('Failed to load inbox logs', err)
  }
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  fetchLogs()
})
</script>
