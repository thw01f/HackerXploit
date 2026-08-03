<template>
  <div class="space-y-8">
    <AdminSubNav />

    <div>
      <span class="px-2.5 py-1 rounded bg-purple-950 text-purple-400 font-mono text-xs font-bold uppercase border border-purple-500/30">SECURITY & RETENTION CENTER</span>
      <h1 class="text-3xl font-extrabold text-white mt-2">Security, Audit & Retention Management</h1>
      <p class="text-slate-400 text-sm mt-1">Admin visibility into authentication attempts, device force-kicks, and competition retention timers.</p>
    </div>

      <!-- Navigation Tabs -->
      <div class="flex flex-wrap gap-3 border-b border-slate-800 pb-3">
        <button 
          @click="activeTab = 'activity'" 
          :class="activeTab === 'activity' ? 'btn-neon-cyan' : 'bg-slate-900 text-slate-400 hover:text-white'" 
          class="text-xs py-2 px-4 rounded-lg font-mono font-bold uppercase transition"
        >
          Login Activity Feed
        </button>
        <button 
          @click="activeTab = 'sessions'" 
          :class="activeTab === 'sessions' ? 'btn-neon-cyan' : 'bg-slate-900 text-slate-400 hover:text-white'" 
          class="text-xs py-2 px-4 rounded-lg font-mono font-bold uppercase transition"
        >
          Active Sessions & Force-Kick
        </button>
        <button 
          @click="activeTab = 'retention'" 
          :class="activeTab === 'retention' ? 'btn-neon-violet' : 'bg-slate-900 text-slate-400 hover:text-white'" 
          class="text-xs py-2 px-4 rounded-lg font-mono font-bold uppercase transition"
        >
          Competition Retention Settings
        </button>
      </div>

      <!-- Tab 1: Login Activity Feed -->
      <div v-if="activeTab === 'activity'" class="space-y-6">
        <div class="glass-panel p-4 flex flex-wrap gap-4 items-center">
          <input v-model="filterUsername" placeholder="Filter by username..." type="text" class="input-field text-xs w-64" />
          <select v-model="filterSuccess" class="input-field text-xs w-48">
            <option value="">All Statuses</option>
            <option value="true">Success Only</option>
            <option value="false">Failed Only</option>
          </select>
          <button @click="fetchActivities" class="btn-neon-cyan text-xs py-2 px-4">Apply Filters</button>
        </div>

        <div class="glass-panel p-6 space-y-4">
          <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3">Authentication Log Feed</h3>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs font-mono">
              <thead class="bg-slate-900 text-slate-400 uppercase">
                <tr>
                  <th class="p-3">Timestamp</th>
                  <th class="p-3">Username Attempted</th>
                  <th class="p-3">IP Address</th>
                  <th class="p-3">Result</th>
                  <th class="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-800 text-slate-300">
                <tr v-for="act in activities" :key="act.id" class="hover:bg-slate-800/40">
                  <td class="p-3 text-slate-500">{{ formatDate(act.created_at || act.timestamp) }}</td>
                  <td class="p-3 font-bold text-white">{{ act.username_attempted || act.email_attempted }}</td>
                  <td class="p-3 text-cyan-400">{{ act.ip_address }}</td>
                  <td class="p-3 font-bold">
                    <span :class="act.success ? 'text-emerald-400' : 'text-red-400'">
                      {{ act.success ? 'SUCCESS' : 'FAILED' }}
                    </span>
                  </td>
                  <td class="p-3 text-right">
                    <button v-if="act.user_id && !act.success" @click="unlockUser(act.user_id)" class="text-amber-400 hover:underline font-bold text-[11px]">
                      Manual Unlock
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Tab 2: Admin Session Search & Force Kick -->
      <div v-if="activeTab === 'sessions'" class="space-y-6">
        <div class="glass-panel p-4 flex gap-4 items-center">
          <input v-model="searchUsername" placeholder="Search member username..." type="text" class="input-field text-xs w-64" />
          <button @click="fetchSessions" class="btn-neon-cyan text-xs py-2 px-4">Search Devices</button>
        </div>

        <div class="glass-panel p-6 space-y-4">
          <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3 flex justify-between items-center">
            <span>Member Active Sessions</span>
            <span class="text-xs font-mono text-cyan-400">{{ sessions.length }} SESSIONS</span>
          </h3>

          <div class="space-y-3">
            <div v-for="s in sessions" :key="s.id" class="p-4 bg-slate-900/80 rounded-xl border border-slate-800 flex justify-between items-center">
              <div>
                <span class="font-bold text-white">@{{ s.username }}</span>
                <span class="text-xs text-slate-400 ml-2 font-mono">IP: {{ s.ip_address }}</span>
                <p class="text-xs text-slate-400 mt-1 font-mono">{{ s.device_label || s.user_agent }}</p>
              </div>
              <div class="flex space-x-2">
                <button @click="forceKickSingle(s.id)" class="btn-neon-violet text-xs py-1.5 px-3">
                  Kick Device
                </button>
                <button @click="forceKickAllUser(s.user_id, s.username)" class="bg-red-900/80 text-red-300 text-xs py-1.5 px-3 rounded font-bold border border-red-500/40">
                  Kick ALL for User
                </button>
              </div>
            </div>

            <div v-if="sessions.length === 0" class="text-center py-6 text-slate-500 text-xs font-mono">
              No active sessions found for query.
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 3: Competition Retention & Auto-Delete Settings -->
      <div v-if="activeTab === 'retention'" class="space-y-6">
        <div class="glass-panel p-6 space-y-6 max-w-2xl">
          <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3 flex items-center gap-2">
            <span>Retention & Cleanup Policy</span>
          </h3>

          <div class="space-y-4 text-xs">
            <div>
              <label class="block font-mono text-slate-300 uppercase mb-1">Competitions Auto-Delete Schedule (Daily Celery Job)</label>
              <select v-model="retentionSettings.competitions_auto_delete" class="input-field text-xs py-2">
                <option value="never">Never Auto-Delete</option>
                <option value="1_month">1 Month After Event End Date</option>
                <option value="3_month">3 Months After Event End Date</option>
                <option value="6_month">6 Months After Event End Date</option>
              </select>
            </div>

            <div>
              <label class="block font-mono text-slate-300 uppercase mb-1">Delete Mode Strategy</label>
              <select v-model="retentionSettings.competitions_delete_mode" class="input-field text-xs py-2">
                <option value="archive">Archive (Keeps participation rows & student certificates permanently)</option>
                <option value="hard_delete">Hard Delete (Permanently remove competition and all records)</option>
              </select>
            </div>

            <div class="pt-2 flex justify-between items-center">
              <button @click="saveRetention" class="btn-neon-cyan text-xs py-2 px-5">
                Save Policy
              </button>

              <button @click="clearHistoryNow" class="bg-red-950 hover:bg-red-900 text-red-300 border border-red-600/40 text-xs py-2 px-4 rounded font-mono font-bold">
                Clear Ended Competitions History Now
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
import AdminSubNav from '../components/AdminSubNav.vue'

const prefs = usePreferences()
const formatDate = (isoStr) => {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleString(undefined, { hour12: prefs.is12h.value })
}

const activeTab = ref('activity')

const activities = ref([])
const filterUsername = ref('')
const filterSuccess = ref('')

const sessions = ref([])
const searchUsername = ref('')

const retentionSettings = ref({
  competitions_auto_delete: 'never',
  competitions_delete_mode: 'archive'
})

const fetchActivities = async () => {
  try {
    const res = await axios.get('/api/admin/security/login-activity', {
      params: { username: filterUsername.value, success: filterSuccess.value }
    })
    activities.value = res.data.activities
  } catch (err) {
    console.error(err)
  }
}

const fetchSessions = async () => {
  try {
    const res = await axios.get('/api/admin/security/sessions', {
      params: { username: searchUsername.value }
    })
    sessions.value = res.data.sessions
  } catch (err) {
    console.error(err)
  }
}

const fetchRetention = async () => {
  try {
    const res = await axios.get('/api/admin/retention')
    retentionSettings.value = res.data
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  fetchActivities()
  fetchSessions()
  fetchRetention()
})

const unlockUser = async (userId) => {
  try {
    const res = await axios.post(`/api/admin/security/login-activity/${userId}/unlock`)
    alert(res.data.message)
    await fetchActivities()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to unlock user')
  }
}

const forceKickSingle = async (sessionId) => {
  try {
    await axios.delete(`/api/admin/security/sessions/${sessionId}`)
    await fetchSessions()
  } catch (err) {
    alert('Failed to kick session')
  }
}

const forceKickAllUser = async (userId, username) => {
  if (!confirm(`Force kick ALL active device sessions for @${username}?`)) return
  try {
    const res = await axios.delete(`/api/admin/security/sessions/user/${userId}`)
    alert(res.data.message)
    await fetchSessions()
  } catch (err) {
    alert('Failed to kick user sessions')
  }
}

const saveRetention = async () => {
  try {
    await axios.post('/api/admin/retention', retentionSettings.value)
    alert('Retention settings saved successfully')
  } catch (err) {
    alert('Failed to save retention settings')
  }
}

const clearHistoryNow = async () => {
  if (!confirm('Execute bulk cleanup of ended competitions now?')) return
  try {
    const res = await axios.post('/api/admin/competitions/clear-history')
    alert(res.data.message)
  } catch (err) {
    alert('Clear history operation failed')
  }
}
</script>
