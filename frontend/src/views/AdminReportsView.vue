<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <div class="flex items-center space-x-3 mb-6">
      <router-link to="/admin" class="btn-ghost text-xs py-1.5 px-3">&larr; Control Center</router-link>
      <h1 class="text-2xl font-bold text-white tracking-tight">Unified Moderation Queue</h1>
    </div>

    <!-- Filter Bar -->
    <div class="glass-panel border border-slate-800 rounded-xl p-4 mb-6 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center space-x-3">
        <label class="text-xs font-bold text-slate-400 uppercase">Status:</label>
        <select v-model="statusFilter" @change="fetchReports" class="input-field text-xs py-1 px-3">
          <option value="pending">Pending Only</option>
          <option value="resolved">Resolved Only</option>
          <option value="all">All Statuses</option>
        </select>
      </div>

      <div class="flex items-center space-x-3">
        <label class="text-xs font-bold text-slate-400 uppercase">Target Type:</label>
        <select v-model="targetFilter" @change="fetchReports" class="input-field text-xs py-1 px-3">
          <option value="all">All Types</option>
          <option value="chat_message">Chat Messages</option>
          <option value="comment">Academy Comments</option>
          <option value="opportunity">Opportunities</option>
        </select>
      </div>
    </div>

    <!-- Reports Table / List -->
    <div class="glass-panel border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
      <div class="p-4 border-b border-slate-800 bg-slate-950/40 flex justify-between items-center">
        <span class="text-xs font-bold text-white uppercase tracking-wider">Reported Content Items ({{ reports.length }})</span>
      </div>

      <div class="divide-y divide-slate-800/60 max-h-[650px] overflow-y-auto">
        <div v-if="reports.length === 0" class="p-12 text-center text-xs text-slate-500">
          No reported items matching filter criteria.
        </div>

        <div v-for="rep in reports" :key="rep.id" class="p-5 hover:bg-slate-800/30 transition-colors space-y-3">
          <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-2">
            <div class="flex items-center space-x-2">
              <span :class="getTargetBadgeClass(rep.target_type)" class="text-[10px] font-bold uppercase px-2 py-0.5 rounded border">
                {{ rep.target_type }}
              </span>
              <span class="text-xs text-slate-400">Reported by: <strong>{{ rep.reporter_username }}</strong> &bull; {{ formatDate(rep.created_at) }}</span>
            </div>

            <span v-if="rep.resolved" class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Resolved by {{ rep.resolver_username || 'Staff' }}
            </span>
            <span v-else class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
              Pending Review
            </span>
          </div>

          <!-- Reason & Content Preview -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-950/50 p-4 rounded-xl border border-slate-800/80">
            <div>
              <span class="block text-[10px] font-bold text-slate-400 uppercase">Reason</span>
              <p class="text-xs text-rose-300 font-medium mt-0.5">{{ rep.reason }}</p>
            </div>
            <div>
              <span class="block text-[10px] font-bold text-slate-400 uppercase">Content Preview</span>
              <p class="text-xs text-slate-200 mt-0.5 italic line-clamp-2">"{{ rep.target_preview }}"</p>
            </div>
          </div>

          <!-- Moderation Actions -->
          <div v-if="!rep.resolved" class="flex justify-end space-x-3 pt-1">
            <button @click="dismissReport(rep.id)" class="btn-ghost text-xs py-1.5 px-3">
              Dismiss / Mark Resolved
            </button>
            <button @click="takeAction(rep.id)" class="btn-neon-pink text-xs py-1.5 px-4 font-bold">
              Take Action & Remove Content
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { usePreferences } from '../stores/preferences'

const prefs = usePreferences()
const reports = ref([])
const statusFilter = ref('pending')
const targetFilter = ref('all')

const fetchReports = async () => {
  try {
    const res = await axios.get(`/api/admin/reports?status=${statusFilter.value}&target_type=${targetFilter.value}`)
    reports.value = res.data.reports || []
  } catch (err) {
    console.error('Failed to load moderation reports', err)
  }
}

const dismissReport = async (repId) => {
  try {
    await axios.post(`/api/admin/reports/${repId}/resolve`)
    fetchReports()
  } catch (err) {
    alert('Failed to resolve report')
  }
}

const takeAction = async (repId) => {
  if (!confirm('Take moderation action and remove/close reported content?')) return
  try {
    const res = await axios.post(`/api/admin/reports/${repId}/action`)
    alert(res.data.message)
    fetchReports()
  } catch (err) {
    alert('Failed to execute report action')
  }
}

const getTargetBadgeClass = (type) => {
  if (type === 'chat_message') return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
  if (type === 'comment') return 'bg-purple-500/10 text-purple-400 border-purple-500/30'
  return 'bg-amber-500/10 text-amber-400 border-amber-500/30'
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: prefs.is12h.value })
}

onMounted(() => {
  fetchReports()
})
</script>
