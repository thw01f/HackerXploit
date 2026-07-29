<template>
  <div class="space-y-8">
    <AdminSubNav />

    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-extrabold text-white">Club Control Center</h1>
        <p class="text-slate-400 text-sm mt-1">User approvals, custom fields, audit logging, and member activity oversight.</p>
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
            <div class="flex items-center space-x-2">
              <button @click="approveUser(user.id, 'member')" class="btn-neon-cyan text-xs py-1.5 px-3 font-mono font-bold">
                ✓ Approve Member
              </button>
              <button @click="approveUser(user.id, 'teacher')" class="btn-ghost text-xs py-1.5 px-3 font-mono font-bold text-purple-400 border-purple-500/30 hover:bg-purple-500/10">
                Approve Teacher
              </button>
              <button @click="rejectUser(user.id)" class="btn-ghost text-xs py-1.5 px-2.5 text-red-400 font-mono">Reject</button>
            </div>
          </div>
          <div v-if="pendingUsers.length === 0" class="text-center py-6 text-slate-500 text-xs font-mono">
            No pending registration requests at this time.
          </div>
        </div>
      </div>

      <!-- User Directory & Account Management -->
      <div class="glass-panel p-6 space-y-4">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-3">
          <div>
            <h3 class="text-lg font-bold text-white">All Accounts & Member Directory</h3>
            <p class="text-xs text-slate-400 font-mono mt-0.5">Manage user roles, reset passwords, suspend or permanently delete accounts.</p>
          </div>

          <div class="flex items-center gap-3 w-full sm:w-auto">
            <input 
              v-model="userSearchQuery" 
              type="text" 
              placeholder="Search user by name, @username, email..." 
              class="input-field text-xs py-1.5 px-3 w-full sm:w-64"
            />
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs font-mono">
            <thead class="bg-slate-900 text-slate-400 uppercase">
              <tr>
                <th class="p-3">User</th>
                <th class="p-3">Email</th>
                <th class="p-3">Role</th>
                <th class="p-3">Status</th>
                <th class="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800 text-slate-300">
              <tr v-for="user in filteredAllUsers" :key="user.id" class="hover:bg-slate-800/40">
                <td class="p-3 font-bold text-white">
                  <div class="flex items-center space-x-2">
                    <span>{{ user.full_name || user.username }}</span>
                    <span class="text-xs text-cyan-400 font-normal">@{{ user.username }}</span>
                  </div>
                </td>
                <td class="p-3 text-slate-400">{{ user.email }}</td>
                <td class="p-3">
                  <span :class="user.role === 'admin' ? 'text-amber-400 font-bold' : user.role === 'teacher' ? 'text-purple-400 font-bold' : 'text-slate-400'">
                    {{ user.role.toUpperCase() }}
                  </span>
                </td>
                <td class="p-3">
                  <span :class="[
                    'px-2 py-0.5 rounded text-[10px] font-bold uppercase border',
                    user.status === 'approved' ? 'bg-emerald-950/40 text-[#9fef00] border-[#9fef00]/40' :
                    user.status === 'pending' ? 'bg-amber-950/40 text-amber-400 border-amber-500/40' :
                    'bg-red-950/40 text-red-400 border-red-500/40'
                  ]">
                    {{ user.status }}
                  </span>
                </td>
                <td class="p-3 text-right space-x-2">
                  <button @click="openResetPasswordModal(user)" class="btn-ghost text-[11px] py-1 px-2.5 text-cyan-400">
                    🔑 Reset Pass
                  </button>
                  <button v-if="user.status === 'approved'" @click="suspendUser(user.id)" class="btn-ghost text-[11px] py-1 px-2.5 text-amber-400">
                    Suspend
                  </button>
                  <button v-else-if="user.status === 'suspended'" @click="reinstateUser(user.id)" class="btn-ghost text-[11px] py-1 px-2.5 text-emerald-400">
                    Reinstate
                  </button>
                  <button v-if="!user.is_root_admin" @click="confirmDeleteUser(user)" class="btn-ghost text-[11px] py-1 px-2.5 text-red-400">
                    🗑️ Delete
                  </button>
                </td>
              </tr>
              <tr v-if="filteredAllUsers.length === 0">
                <td colspan="5" class="p-4 text-center text-slate-500 text-xs font-mono">No matching accounts found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Audit Logs Table -->
      <div class="glass-panel p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 class="text-lg font-bold text-white">System Audit Log</h3>
          <button @click="fetchData" class="text-xs font-mono text-[#9fef00] hover:underline">
            🔄 Refresh
          </button>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs font-mono">
            <thead class="bg-slate-900 text-slate-400 uppercase">
              <tr>
                <th class="p-3">Timestamp</th>
                <th class="p-3">Actor</th>
                <th class="p-3">Role</th>
                <th class="p-3">Action</th>
                <th class="p-3">Target</th>
                <th class="p-3">Notes & Reason</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800 text-slate-300">
              <tr v-for="log in auditLogs" :key="log.id" class="hover:bg-slate-800/40">
                <td class="p-3 text-slate-500">{{ new Date(log.created_at || log.timestamp).toLocaleString() }}</td>
                <td class="p-3 font-bold text-white">{{ log.actor_username || log.actor_name || 'System' }}</td>
                <td class="p-3 text-cyan-400">{{ log.actor_role || 'N/A' }}</td>
                <td class="p-3 text-amber-400 font-bold">{{ log.action }}</td>
                <td class="p-3 text-slate-400">{{ log.target_type }} #{{ log.target_id }}</td>
                <td class="p-3 text-amber-300/90 font-mono text-[11px] max-w-xs break-words" :title="log.notes">
                  {{ log.notes || '-' }}
                </td>
              </tr>
              <tr v-if="auditLogs.length === 0">
                <td colspan="6" class="p-4 text-center text-slate-500 text-xs font-mono">No audit log entries recorded.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    <!-- Admin Reset Password Modal -->
    <div v-if="showPasswordModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="glass-panel max-w-md w-full p-6 space-y-4 border border-[#00f0ff]/30 shadow-2xl">
        <h3 class="text-lg font-bold text-white font-mono flex items-center justify-between">
          <span>Reset Password for @{{ targetUser?.username }}</span>
          <button @click="showPasswordModal = false" class="text-slate-400 hover:text-white">✕</button>
        </h3>
        <p class="text-xs text-slate-400">Enter a new password for <strong>{{ targetUser?.full_name || targetUser?.username }}</strong>. Existing user sessions will be invalidated immediately.</p>
        <div>
          <label class="block text-xs font-mono text-slate-400 mb-1">New Password</label>
          <input v-model="newPasswordInput" type="password" placeholder="Enter new password (min 6 chars)" class="input-field text-xs py-2" />
        </div>
        <div class="flex justify-end space-x-3 pt-2">
          <button @click="showPasswordModal = false" class="btn-ghost text-xs py-2 px-4">Cancel</button>
          <button @click="submitAdminPasswordReset" class="btn-neon-cyan text-xs py-2 px-4 font-mono font-bold">Set Password</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import AdminSubNav from '../components/AdminSubNav.vue'

const authStore = useAuthStore()
const users = ref([])
const auditLogs = ref([])
const userSearchQuery = ref('')

const showPasswordModal = ref(false)
const targetUser = ref(null)
const newPasswordInput = ref('')

const pendingUsers = computed(() => users.value.filter(u => u.status === 'pending'))

const filteredAllUsers = computed(() => {
  if (!userSearchQuery.value) return users.value
  const q = userSearchQuery.value.toLowerCase()
  return users.value.filter(u => 
    u.username.toLowerCase().includes(q) || 
    (u.email && u.email.toLowerCase().includes(q)) ||
    (u.full_name && u.full_name.toLowerCase().includes(q))
  )
})

const fetchData = async () => {
  try {
    const resUsers = await axios.get('/api/admin/users')
    users.value = resUsers.data.users || []
  } catch (err) {
    console.error('Failed to load admin users', err)
  }

  try {
    const resLogs = await axios.get('/api/admin/audit-log')
    auditLogs.value = resLogs.data.audit_logs || []
  } catch (err) {
    console.error('Failed to load audit logs', err)
  }
}

onMounted(fetchData)

const approveUser = async (id, role = 'member') => {
  try {
    await axios.post(`/api/admin/users/${id}/approve`, { assigned_role: role })
    await fetchData()
  } catch (err) {
    alert('Approve failed: ' + (err.response?.data?.error || err.message))
  }
}

const rejectUser = async (id) => {
  try {
    await axios.post(`/api/admin/users/${id}/reject`)
    await fetchData()
  } catch (err) {
    alert('Reject failed: ' + (err.response?.data?.error || err.message))
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

const reinstateUser = async (id) => {
  try {
    await axios.post(`/api/admin/users/${id}/reinstate`)
    await fetchData()
  } catch (err) {
    alert(err.response?.data?.error || 'Reinstate failed')
  }
}

const confirmDeleteUser = async (user) => {
  if (!confirm(`Are you sure you want to PERMANENTLY delete user @${user.username}? This action cannot be undone.`)) return
  try {
    await axios.delete(`/api/admin/users/${user.id}`)
    await fetchData()
  } catch (err) {
    alert(err.response?.data?.error || 'Delete failed')
  }
}

const openResetPasswordModal = (user) => {
  targetUser.value = user
  newPasswordInput.value = ''
  showPasswordModal.value = true
}

const submitAdminPasswordReset = async () => {
  if (!newPasswordInput.value || newPasswordInput.value.length < 6) {
    alert('Password must be at least 6 characters long')
    return
  }
  try {
    await axios.post(`/api/admin/users/${targetUser.value.id}/reset-password`, {
      new_password: newPasswordInput.value
    })
    alert(`Password for @${targetUser.value.username} updated successfully!`)
    showPasswordModal.value = false
    await fetchData()
  } catch (err) {
    alert(err.response?.data?.error || 'Reset failed')
  }
}
</script>
