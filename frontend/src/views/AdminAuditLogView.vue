<template>
  <div class="space-y-8">
    <AdminSubNav />

    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <span class="px-2.5 py-1 rounded bg-red-950 text-red-400 font-mono text-xs font-bold uppercase">ADMIN AUDIT TRAIL</span>
        <h1 class="text-3xl font-extrabold text-white mt-2">Site-Wide Audit Log</h1>
        <p class="text-slate-400 text-sm mt-1">Non-repudiable audit records of all administrative actions, user approvals, role changes, and security events.</p>
      </div>
      <button @click="clearBulk" class="btn-neon-violet text-xs py-2.5 px-4 self-start md:self-auto border border-red-500/40">
        Clear History (Bulk Delete)
      </button>
    </div>

      <!-- Filters -->
      <div class="glass-panel p-4 flex flex-wrap gap-4 items-center">
        <input v-model="filterActor" placeholder="Filter by Actor ID..." type="number" class="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-xs" />
        <select v-model="filterAction" class="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-xs">
          <option value="">All Actions</option>
          <option value="approved">approved</option>
          <option value="rejected">rejected</option>
          <option value="suspended">suspended</option>
          <option value="reinstated">reinstated</option>
          <option value="role_changed">role_changed</option>
          <option value="auto_locked">auto_locked</option>
          <option value="manual_unlock">manual_unlock</option>
        </select>
        <button @click="fetchLogs" class="btn-neon-cyan text-xs py-1.5 px-4">Apply Filters</button>
      </div>

      <!-- Audit Log Table -->
      <div class="glass-panel p-6 overflow-x-auto">
        <table class="w-full text-left text-sm text-slate-300">
          <thead class="text-xs uppercase font-mono text-cyan-400 border-b border-slate-800">
            <tr>
              <th class="py-3 px-4">ID</th>
              <th class="py-3 px-4">Timestamp</th>
              <th class="py-3 px-4">Actor</th>
              <th class="py-3 px-4">Action</th>
              <th class="py-3 px-4">Target User</th>
              <th class="py-3 px-4">Notes</th>
              <th class="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60 font-mono text-xs">
            <tr v-for="log in logs" :key="log.id" class="hover:bg-slate-900/40">
              <td class="py-3 px-4 text-slate-500">#{{ log.id }}</td>
              <td class="py-3 px-4 text-slate-400">{{ new Date(log.created_at || log.timestamp).toLocaleString() }}</td>
              <td class="py-3 px-4">
                <span class="text-white font-bold">{{ log.actor_name }}</span>
                <span class="text-[10px] text-purple-400 block uppercase">[{{ log.actor_role }}]</span>
              </td>
              <td class="py-3 px-4">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-cyan-400">{{ log.action }}</span>
              </td>
              <td class="py-3 px-4 text-slate-300">
                {{ log.target_user_id ? 'User #' + log.target_user_id : (log.target_id || '-') }}
              </td>
              <td class="py-3 px-4 text-slate-400 text-[11px] max-w-xs truncate">{{ log.notes }}</td>
              <td class="py-3 px-4 text-right">
                <button @click="deleteRow(log.id)" class="text-red-400 hover:text-red-300 text-xs">Delete</button>
              </td>
            </tr>
            <tr v-if="logs.length === 0">
              <td colspan="7" class="py-8 text-center text-slate-500">No audit log entries found.</td>
            </tr>
          </tbody>
        </table>
      </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import AdminSubNav from '../components/AdminSubNav.vue'

const logs = ref([])
const filterActor = ref('')
const filterAction = ref('')

const fetchLogs = async () => {
  try {
    const res = await axios.get('/api/admin/audit-log', {
      params: { actor_id: filterActor.value, action: filterAction.value }
    })
    logs.value = res.data.audit_logs
  } catch (err) {
    console.error(err)
  }
}

onMounted(fetchLogs)

const deleteRow = async (id) => {
  if (!confirm('Are you sure you want to delete this audit log entry?')) return
  try {
    await axios.delete(`/api/admin/audit-log/${id}`)
    await fetchLogs()
  } catch (err) {
    alert('Failed to delete log entry')
  }
}

const clearBulk = async () => {
  if (!confirm('CONFIRMATION REQUIRED: Are you sure you want to bulk clear ALL audit log history? This action is permanent.')) return
  try {
    const res = await axios.delete('/api/admin/audit-log')
    alert(res.data.message)
    await fetchLogs()
  } catch (err) {
    alert('Failed to clear audit history')
  }
}
</script>
