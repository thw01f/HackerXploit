<template>
  <div class="space-y-8 max-w-full">
    <AdminSubNav />

    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">Club Control Center</h1>
        <p class="text-slate-400 text-base mt-1.5">User approvals, custom fields, security oversight, and administrative activity monitoring.</p>
      </div>
    </div>

    <!-- User Approvals Section -->
    <div class="glass-panel p-6 sm:p-8 space-y-6">
      <h3 class="text-xl font-bold text-white border-b border-slate-800 pb-4 flex items-center justify-between">
        <span>Registration Approvals Queue</span>
        <span class="text-sm font-mono font-extrabold px-3 py-1 bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 rounded-lg">{{ pendingUsers.length }} PENDING</span>
      </h3>

      <div class="space-y-4">
        <div v-for="user in pendingUsers" :key="user.id" class="p-5 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:border-slate-700 transition-all">
          <div>
            <span class="font-extrabold text-white text-base">{{ user.full_name }}</span>
            <span class="text-sm text-cyan-400 font-mono font-bold ml-3">@{{ user.username }}</span>
            <p class="text-xs text-slate-400 mt-1 font-mono">{{ user.email }} • Student ID: {{ user.student_id || 'N/A' }}</p>
          </div>
          <div class="flex items-center space-x-3">
            <button @click="approveUser(user.id, 'member')" class="btn-neon-cyan text-xs py-2.5 px-4 font-mono font-extrabold shadow-lg">
              Approve Member
            </button>
            <button @click="approveUser(user.id, 'teacher')" class="btn-ghost text-xs py-2.5 px-4 font-mono font-extrabold text-purple-400 border-purple-500/40 hover:bg-purple-500/15">
              Approve Teacher
            </button>
            <button @click="rejectUser(user.id)" class="btn-ghost text-xs py-2.5 px-3.5 text-red-400 font-mono font-bold hover:bg-red-500/15">Reject</button>
          </div>
        </div>
        <div v-if="pendingUsers.length === 0" class="text-center py-8 text-slate-400 text-sm font-mono">
          No pending registration requests at this time.
        </div>
      </div>
    </div>

    <!-- User Directory & Account Management -->
    <div class="glass-panel p-6 sm:p-8 space-y-6">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h3 class="text-xl font-bold text-white">All Accounts & Member Directory</h3>
          <p class="text-sm text-slate-400 font-mono mt-1">Manage user roles, reset passwords, suspend or permanently delete accounts.</p>
        </div>

        <div class="flex items-center gap-3 w-full sm:w-auto">
          <input 
            v-model="userSearchQuery" 
            type="text" 
            placeholder="Search user by name, @username, email..." 
            class="input-field text-sm py-2.5 px-4 w-full sm:w-80 font-mono"
          />
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm font-mono">
          <thead class="bg-slate-900/90 text-slate-300 uppercase tracking-wider text-xs border-b border-slate-800">
            <tr>
              <th class="p-4">User</th>
              <th class="p-4">Email</th>
              <th class="p-4">Role</th>
              <th class="p-4">Status</th>
              <th class="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800 text-slate-200">
            <tr v-for="user in filteredAllUsers" :key="user.id" class="hover:bg-slate-800/50 transition-colors">
              <td class="p-4 font-bold text-white">
                <div class="flex items-center space-x-2">
                  <span class="text-sm font-extrabold text-white">{{ user.full_name || user.username }}</span>
                  <span class="text-xs text-cyan-400 font-bold font-mono">@{{ user.username }}</span>
                </div>
              </td>
              <td class="p-4 text-slate-300 text-xs">{{ user.email }}</td>
              <td class="p-4">
                <span :class="user.role === 'root_admin' ? 'text-rose-400 font-extrabold' : user.role === 'admin' ? 'text-amber-400 font-extrabold' : user.role === 'teacher' ? 'text-purple-400 font-extrabold' : 'text-slate-300 font-bold'">
                  {{ user.role.toUpperCase() }}
                </span>
              </td>
              <td class="p-4">
                <span :class="[
                  'px-3 py-1 rounded-md text-xs font-extrabold uppercase border',
                  user.status === 'approved' ? 'bg-emerald-950/50 text-[#9fef00] border-[#9fef00]/40' :
                  user.status === 'pending' ? 'bg-amber-950/50 text-amber-400 border-amber-500/40' :
                  'bg-red-950/50 text-red-400 border-red-500/40'
                ]">
                  {{ user.status }}
                </span>
              </td>
              <td class="p-4 text-right space-x-2">
                <button @click="openEditUserModal(user)" class="btn-ghost text-xs py-1.5 px-3 text-[#9fef00] font-bold border border-[#9fef00]/30 hover:bg-[#9fef00]/10">
                  Edit Details
                </button>
                <button @click="openResetPasswordModal(user)" class="btn-ghost text-xs py-1.5 px-3 text-cyan-400 font-bold border border-cyan-500/30 hover:bg-cyan-500/10">
                  Reset Pass
                </button>
                <button v-if="user.status === 'approved'" @click="suspendUser(user.id)" class="btn-ghost text-xs py-1.5 px-3 text-amber-400 font-bold border border-amber-500/30 hover:bg-amber-500/10">
                  Suspend
                </button>
                <button v-else-if="user.status === 'suspended'" @click="reinstateUser(user.id)" class="btn-ghost text-xs py-1.5 px-3 text-emerald-400 font-bold border border-emerald-500/30 hover:bg-emerald-500/10">
                  Reinstate
                </button>
                <button 
                  v-if="!user.is_root_admin" 
                  @click="confirmDeleteUser(user)" 
                  title="Delete User Account"
                  class="btn-ghost text-xs p-2 text-red-400 hover:text-red-300 font-bold border border-red-500/40 hover:bg-red-500/20 hover:border-red-500/60 inline-flex items-center justify-center rounded-lg transition-all"
                >
                  <svg class="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </td>
            </tr>
            <tr v-if="filteredAllUsers.length === 0">
              <td colspan="5" class="p-6 text-center text-slate-400 text-sm font-mono">No matching accounts found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Audit Logs Table -->
    <div class="glass-panel p-6 sm:p-8 space-y-6">
      <div class="flex items-center justify-between border-b border-slate-800 pb-4">
        <h3 class="text-xl font-bold text-white">System Audit Log</h3>
        <button @click="fetchData" class="text-xs font-mono font-extrabold text-[#9fef00] hover:underline flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#9fef00]/10 border border-[#9fef00]/30">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          <span>Refresh Logs</span>
        </button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm font-mono">
          <thead class="bg-slate-900/90 text-slate-300 uppercase tracking-wider text-xs border-b border-slate-800">
            <tr>
              <th class="p-4">Timestamp</th>
              <th class="p-4">Actor</th>
              <th class="p-4">Role</th>
              <th class="p-4">Action</th>
              <th class="p-4">Target</th>
              <th class="p-4">Notes & Reason</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800 text-slate-200">
            <tr v-for="log in auditLogs" :key="log.id" class="hover:bg-slate-800/50 transition-colors">
              <td class="p-4 text-slate-400 text-xs font-mono">{{ formatDate(log.created_at || log.timestamp) }}</td>
              <td class="p-4 font-bold text-white text-sm">{{ log.actor_username || log.actor_name || 'System' }}</td>
              <td class="p-4 text-cyan-400 text-xs font-bold">{{ log.actor_role || 'N/A' }}</td>
              <td class="p-4 text-amber-400 font-bold text-sm">{{ log.action }}</td>
              <td class="p-4 text-slate-300 text-xs">{{ log.target_type }} #{{ log.target_id }}</td>
              <td class="p-4 text-slate-300 font-mono text-xs max-w-sm break-words" :title="log.notes">
                {{ log.notes || '-' }}
              </td>
            </tr>
            <tr v-if="auditLogs.length === 0">
              <td colspan="6" class="p-6 text-center text-slate-400 text-sm font-mono">No audit log entries recorded.</td>
            </tr>
          </tbody>
          </table>
        </div>
      </div>

    <!-- Admin Edit User Details Modal -->
    <div v-if="showEditUserModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="glass-panel max-w-md w-full p-6 space-y-4 border border-[#9fef00]/30 shadow-2xl">
        <h3 class="text-lg font-bold text-white font-mono flex items-center justify-between border-b border-slate-800 pb-3">
          <span>Edit Account: @{{ targetUser?.username }}</span>
          <button @click="showEditUserModal = false" class="text-slate-400 hover:text-white">✕</button>
        </h3>
        <form @submit.prevent="submitUserUpdate" class="space-y-3 font-mono text-xs">
          <div>
            <label class="block text-slate-400 uppercase mb-1">Username</label>
            <input v-model="editUserForm.username" type="text" class="input-field w-full py-2" required />
          </div>

          <div>
            <label class="block text-slate-400 uppercase mb-1">Full Name</label>
            <input v-model="editUserForm.full_name" type="text" class="input-field w-full py-2" required />
          </div>

          <div>
            <label class="block text-slate-400 uppercase mb-1">SRM Email Address</label>
            <input v-model="editUserForm.email" type="email" class="input-field w-full py-2" required />
          </div>

          <div>
            <label class="block text-slate-400 uppercase mb-1">Registration Number</label>
            <input v-model="editUserForm.registration_number" type="text" placeholder="e.g. RA2311030050008" class="input-field w-full py-2" />
          </div>

          <div>
            <label class="block text-slate-400 uppercase mb-1">Student / Member ID</label>
            <input v-model="editUserForm.student_id" type="text" placeholder="e.g. STU-2026-042" class="input-field w-full py-2" />
          </div>

          <div>
            <label class="block text-slate-400 uppercase mb-1">Specialization Track</label>
            <select v-model="editUserForm.specialization_role" class="input-field w-full py-2 bg-[#0b0e14]">
              <option value="Penetration Tester">Penetration Tester</option>
              <option value="Security Analyst">Security Analyst</option>
              <option value="Malware Analyst">Malware Analyst</option>
              <option value="Red Teamer">Red Teamer</option>
              <option value="Digital Forensics Specialist">Digital Forensics Specialist</option>
            </select>
          </div>

          <div>
            <label class="block text-slate-400 uppercase mb-1">Role</label>
            <select v-model="editUserForm.role" class="input-field w-full py-2 bg-[#0b0e14]">
              <option value="member">Student / Member</option>
              <option value="teacher">Teacher / Faculty</option>
              <option value="admin">Platform Admin</option>
            </select>
          </div>

          <div>
            <label class="block text-slate-400 uppercase mb-1">Status</label>
            <select v-model="editUserForm.status" class="input-field w-full py-2 bg-[#0b0e14]">
              <option value="approved">Approved</option>
              <option value="pending">Pending</option>
              <option value="suspended">Suspended</option>
            </select>
          </div>

          <div class="flex justify-end space-x-3 pt-3 border-t border-slate-800">
            <button type="button" @click="showEditUserModal = false" class="btn-ghost py-1.5 px-4">Cancel</button>
            <button type="submit" :disabled="savingUser" class="btn-htb py-1.5 px-5 font-bold uppercase">
              {{ savingUser ? 'Saving...' : 'Save User Details' }}
            </button>
          </div>
        </form>
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
          <div class="flex justify-end space-x-3 pt-3">
            <button @click="showPasswordModal = false" class="btn-ghost text-xs py-1.5 px-4">Cancel</button>
            <button @click="submitAdminPasswordReset" class="btn-htb text-xs py-1.5 px-4 font-bold uppercase">Set New Password</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { usePreferences } from '../stores/preferences'
import AdminSubNav from '../components/AdminSubNav.vue'

const prefs = usePreferences()
const formatDate = (isoStr) => {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleString(undefined, { hour12: prefs.is12h.value })
}

const authStore = useAuthStore()
const users = ref([])
const auditLogs = ref([])
const userSearchQuery = ref('')

const showPasswordModal = ref(false)
const showEditUserModal = ref(false)
const savingUser = ref(false)
const targetUser = ref(null)
const newPasswordInput = ref('')
const editUserForm = ref({ username: '', full_name: '', email: '', registration_number: '', student_id: '', specialization_role: 'Penetration Tester', role: 'member', status: 'approved' })

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

const openEditUserModal = (user) => {
  targetUser.value = user
  editUserForm.value = {
    username: user.username || '',
    full_name: user.full_name || '',
    email: user.email || '',
    registration_number: user.registration_number || '',
    student_id: user.student_id || '',
    specialization_role: user.specialization_role || 'Penetration Tester',
    role: user.role || 'member',
    status: user.status || 'approved'
  }
  showEditUserModal.value = true
}

const submitUserUpdate = async () => {
  savingUser.value = true
  try {
    await axios.put(`/api/admin/users/${targetUser.value.id}/update`, editUserForm.value)
    showEditUserModal.value = false
    await fetchData()
  } catch (err) {
    alert(err.response?.data?.error || 'Update failed')
  } finally {
    savingUser.value = false
  }
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
