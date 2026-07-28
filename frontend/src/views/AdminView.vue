<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full space-y-8">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-3xl font-extrabold text-white">Club Control Center</h1>
          <p class="text-slate-400 text-sm mt-1">User approvals, audit logging, and member activity oversight.</p>
        </div>

        <div class="flex items-center space-x-3">
          <router-link v-if="authStore.isAdmin" to="/admin/security/login-activity" class="btn-ghost text-xs py-2 px-4 text-purple-400">
            Security Logs
          </router-link>
          <router-link v-if="authStore.isRootAdmin" to="/admin/manage-admins" class="btn-neon-violet text-xs py-2 px-4">
            Manage Admins (Root Only)
          </router-link>
        </div>
      </div>

      <!-- User Approvals Section -->
      <div class="glass-panel p-6 space-y-4">
        <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3 flex items-center justify-between">
          <span>Registration Approvals Queue</span>
          <span class="text-xs font-mono text-cyan-400">{{ pendingUsers.length }} PENDING</span>
        </h3>

        <div class="space-y-3">
          <div v-for="user in pendingUsers" :key="user.id" class="p-4 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <span class="font-bold text-white">{{ user.full_name }}</span>
              <span class="text-xs text-cyan-400 font-mono ml-2">@{{ user.username }}</span>
              <p class="text-xs text-slate-400 mt-0.5">{{ user.email }} • Student ID: {{ user.student_id || 'N/A' }}</p>
            </div>
            <div class="flex space-x-2">
              <button @click="approveUser(user.id)" class="btn-neon-cyan text-xs py-1.5 px-4">Approve</button>
              <button @click="suspendUser(user.id)" class="btn-ghost text-xs py-1.5 px-3 text-red-400">Reject</button>
            </div>
          </div>
          <div v-if="pendingUsers.length === 0" class="text-center py-6 text-slate-500 text-xs font-mono">
            No pending registration requests at this time.
          </div>
        </div>
      </div>

      <!-- Audit Logs Table -->
      <div class="glass-panel p-6 space-y-4">
        <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3">System Audit Log</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs font-mono">
            <thead class="bg-slate-900 text-slate-400 uppercase">
              <tr>
                <th class="p-3">Timestamp</th>
                <th class="p-3">Actor</th>
                <th class="p-3">Role</th>
                <th class="p-3">Action</th>
                <th class="p-3">Target</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800 text-slate-300">
              <tr v-for="log in auditLogs" :key="log.id" class="hover:bg-slate-800/40">
                <td class="p-3 text-slate-500">{{ new Date(log.timestamp).toLocaleString() }}</td>
                <td class="p-3 font-bold text-white">{{ log.actor_name }}</td>
                <td class="p-3 text-cyan-400">{{ log.actor_role }}</td>
                <td class="p-3 text-amber-400 font-bold">{{ log.action }}</td>
                <td class="p-3 text-slate-400">{{ log.target_type }} #{{ log.target_id }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const users = ref([])
const auditLogs = ref([])

const pendingUsers = computed(() => users.value.filter(u => u.status === 'pending'))

const fetchData = async () => {
  try {
    const resUsers = await axios.get('/api/admin/users')
    users.value = resUsers.data.users
    const resLogs = await axios.get('/api/admin/audit-logs')
    auditLogs.value = resLogs.data.audit_logs
  } catch (err) {
    console.error('Failed to load admin data', err)
  }
}

onMounted(fetchData)

const approveUser = async (id) => {
  try {
    await axios.post(`/api/admin/users/${id}/approve`)
    await fetchData()
  } catch (err) {
    alert('Approve failed')
  }
}

const suspendUser = async (id) => {
  try {
    await axios.post(`/api/admin/users/${id}/suspend`)
    await fetchData()
  } catch (err) {
    alert(err.response?.data?.error || 'Suspend failed')
  }
}
</script>
