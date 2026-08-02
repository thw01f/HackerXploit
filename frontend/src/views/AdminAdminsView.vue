<template>
  <div class="space-y-8">
    <AdminSubNav />

    <div>
      <span class="px-2.5 py-1 rounded bg-red-950 text-red-400 font-mono text-xs font-bold uppercase">ADMINISTRATOR CONTROL</span>
      <h1 class="text-3xl font-extrabold text-white mt-2">Manage Admins & Privilege Transfer</h1>
      <p class="text-slate-400 text-sm mt-1">Promote members to Faculty/Teacher status with teacher details, manage non-root admin quotas (max 5), or transfer root admin privileges.</p>
    </div>

      <!-- Success Notification Banner -->
      <div v-if="successMsg" class="p-4 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-400 text-xs font-mono flex items-center justify-between">
        <span>{{ successMsg }}</span>
        <button @click="successMsg = ''" class="text-emerald-400 hover:text-white">&times;</button>
      </div>

      <!-- Current Active Admins List -->
      <div class="glass-panel p-6 space-y-4">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <div>
            <h3 class="text-lg font-bold text-white">Current Administrators</h3>
            <p class="text-xs text-slate-400 font-mono">System-wide control & audit privileges.</p>
          </div>
          <span class="text-xs font-mono text-purple-400 font-bold px-3 py-1 bg-purple-950/40 border border-purple-500/30 rounded-lg">
            {{ currentAdmins.length }} / 5 ADMIN QUOTA ACTIVE
          </span>
        </div>

        <div class="space-y-3">
          <div v-for="user in adminUsers" :key="user.id" class="p-4 bg-slate-900/80 rounded-xl border border-slate-800 flex justify-between items-center">
            <div>
              <span class="font-bold text-white">{{ user.full_name || user.username }}</span>
              <span class="text-xs text-slate-400 font-mono ml-2">@{{ user.username }}</span>
              <span :class="roleBadge(user.role)" class="text-[10px] ml-2 px-2 py-0.5 rounded font-bold uppercase border">
                {{ user.is_root_admin ? 'ROOT ADMIN' : user.role }}
              </span>
            </div>

            <div v-if="!user.is_root_admin" class="flex items-center space-x-2">
              <button 
                @click="openTeacherModal(user)" 
                class="btn-ghost text-xs py-1 px-3 text-cyan-400"
              >
                Convert to Teacher
              </button>
              <button 
                @click="changeRole(user.id, 'member')" 
                class="btn-ghost text-xs py-1 px-3 text-amber-400"
              >
                Demote to Member
              </button>
              <button 
                @click="transferRoot(user.id)" 
                class="btn-ghost text-xs py-1 px-3 text-red-400 font-bold"
              >
                Transfer Root Status
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Member Promotion to Teacher Section -->
      <div class="glass-panel p-6 space-y-4">
        <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-b border-slate-800 pb-3">
          <div>
            <h3 class="text-lg font-bold text-white">Promote Members to Faculty / Teacher</h3>
            <p class="text-xs text-slate-400 font-mono mt-0.5">Select a member to grant teacher privileges & enter faculty details.</p>
          </div>

          <div class="flex items-center gap-3">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search member by name, username..." 
              class="input-field text-xs py-1.5 px-3 w-48 sm:w-64"
            />
            <select v-model="filterRole" class="input-field text-xs py-1.5 px-3">
              <option value="all">All Roles</option>
              <option value="member">Members Only</option>
              <option value="teacher">Teachers Only</option>
            </select>
          </div>
        </div>

        <div class="space-y-3">
          <div v-for="user in filteredUsers" :key="user.id" class="p-4 bg-slate-900/60 rounded-xl border border-slate-800 flex flex-col sm:flex-row justify-between sm:items-center gap-3 hover:border-cyan-500/30 transition-all">
            <div>
              <div class="flex items-center space-x-2">
                <span class="font-bold text-white">{{ user.full_name || user.username }}</span>
                <span class="text-xs text-cyan-400 font-mono">@{{ user.username }}</span>
                <span :class="roleBadge(user.role)" class="text-[10px] px-2 py-0.5 rounded font-bold uppercase border">
                  {{ user.role }}
                </span>
              </div>
              <p class="text-xs text-slate-400 font-mono mt-1">Email: {{ user.email }} | {{ user.bio || 'No profile bio provided.' }}</p>
            </div>

            <div class="flex items-center space-x-2 self-end sm:self-center">
              <button 
                v-if="user.role === 'member'" 
                @click="openTeacherModal(user)" 
                class="btn-neon-cyan text-xs py-1.5 px-4 font-mono font-bold"
              >
                Promote to Teacher
              </button>
              <button 
                v-if="user.role !== 'admin' && !user.is_root_admin" 
                @click="changeRole(user.id, 'admin')" 
                class="btn-neon-violet text-xs py-1.5 px-3 font-mono"
              >
                Make Admin
              </button>
            </div>
          </div>

          <div v-if="filteredUsers.length === 0" class="p-8 text-center text-slate-500 font-mono text-xs">
            No member accounts found matching your filter criteria.
          </div>
        </div>
      </div>

      <!-- Modal Dialog: Promote Member to Teacher -->
      <div v-if="showTeacherModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="glass-panel max-w-lg w-full p-6 space-y-5 border border-cyan-500/40 shadow-2xl relative">
          <button @click="closeTeacherModal" class="absolute top-4 right-4 text-slate-400 hover:text-white text-lg">&times;</button>
          
          <div>
            <span class="px-2.5 py-1 rounded bg-cyan-950 text-cyan-400 font-mono text-[10px] font-bold uppercase border border-cyan-500/30">FACULTY PROMOTION</span>
            <h3 class="text-xl font-extrabold text-white mt-2">Promote to Teacher / Faculty</h3>
            <p class="text-xs text-slate-300 mt-1">Assigning faculty status to <strong class="text-cyan-400 font-mono">@{{ selectedUser?.username }}</strong> ({{ selectedUser?.email }}).</p>
          </div>

          <form @submit.prevent="submitTeacherPromotion" class="space-y-4">
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Department / Faculty Specialization *</label>
              <input v-model="teacherForm.department" type="text" required placeholder="e.g. Department of Cybersecurity & Defense" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-cyan-500 focus:outline-none" />
            </div>

            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Official Designation</label>
              <input v-model="teacherForm.designation" type="text" placeholder="e.g. Senior Instructor / Assistant Professor" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-cyan-500 focus:outline-none" />
            </div>

            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Staff / Faculty ID Number</label>
              <input v-model="teacherForm.staff_id" type="text" placeholder="e.g. FAC-2026-8812" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-cyan-500 focus:outline-none" />
            </div>

            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Notes / Welcome Instructions</label>
              <textarea v-model="teacherForm.notes" rows="2" placeholder="e.g. Granted full student roster access, course publication, and CTF score monitoring privileges." class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs focus:border-cyan-500 focus:outline-none"></textarea>
            </div>

            <div class="flex items-center justify-end space-x-3 pt-2">
              <button type="button" @click="closeTeacherModal" class="btn-ghost text-xs py-2 px-4">Cancel</button>
              <button type="submit" class="btn-neon-cyan text-xs py-2 px-6 font-bold">Confirm & Assign Faculty Role</button>
            </div>
          </form>
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import AdminSubNav from '../components/AdminSubNav.vue'

const users = ref([])
const searchQuery = ref('')
const filterRole = ref('all')
const successMsg = ref('')

const showTeacherModal = ref(false)
const selectedUser = ref(null)
const teacherForm = ref({
  department: '',
  designation: '',
  staff_id: '',
  notes: ''
})

const currentAdmins = computed(() => users.value.filter(u => u.role === 'admin' || u.is_root_admin))
const adminUsers = computed(() => users.value.filter(u => u.role === 'admin' || u.is_root_admin))

const filteredUsers = computed(() => {
  return users.value.filter(u => {
    if (filterRole.value !== 'all' && u.role !== filterRole.value) return false
    if (!searchQuery.value) return true
    const q = searchQuery.value.toLowerCase()
    return (u.username && u.username.toLowerCase().includes(q)) ||
           (u.full_name && u.full_name.toLowerCase().includes(q)) ||
           (u.email && u.email.toLowerCase().includes(q))
  })
})

const fetchUsers = async () => {
  try {
    const res = await axios.get('/api/admin/users')
    users.value = res.data.users
  } catch (err) {
    console.error(err)
  }
}

onMounted(fetchUsers)

const roleBadge = (role) => {
  if (role === 'root_admin') return 'bg-red-950/80 text-red-400 border-red-500/40'
  if (role === 'admin') return 'bg-purple-950/80 text-purple-400 border-purple-500/40'
  if (role === 'teacher') return 'bg-cyan-950/80 text-cyan-400 border-cyan-500/40'
  return 'bg-slate-800 text-slate-400 border-slate-700'
}

const openTeacherModal = (user) => {
  selectedUser.value = user
  teacherForm.value = {
    department: 'Department of Cybersecurity',
    designation: 'Faculty Member',
    staff_id: user.student_id || '',
    notes: ''
  }
  showTeacherModal.value = true
}

const closeTeacherModal = () => {
  showTeacherModal.value = false
  selectedUser.value = null
}

const submitTeacherPromotion = async () => {
  if (!selectedUser.value) return
  try {
    const res = await axios.post(`/api/admin/users/${selectedUser.value.id}/promote-teacher`, teacherForm.value)
    successMsg.value = `User @${selectedUser.value.username} successfully promoted to Teacher/Faculty!`
    closeTeacherModal()
    await fetchUsers()
  } catch (err) {
    alert(err.response?.data?.error || 'Promotion failed')
  }
}

const changeRole = async (userId, newRole) => {
  try {
    await axios.post(`/api/admin/users/${userId}/role`, { role: newRole })
    successMsg.value = `User role updated to ${newRole.toUpperCase()}.`
    await fetchUsers()
  } catch (err) {
    alert(err.response?.data?.error || 'Role change failed')
  }
}

const transferRoot = async (userId) => {
  if (confirm('Are you sure you want to transfer ROOT ADMIN status? This will convert your role to Admin and cannot be undone.')) {
    try {
      await axios.post('/api/admin/transfer-root', { target_user_id: userId })
      alert('Root admin status transferred successfully!')
      window.location.reload()
    } catch (err) {
      alert(err.response?.data?.error || 'Transfer failed')
    }
  }
}
</script>
