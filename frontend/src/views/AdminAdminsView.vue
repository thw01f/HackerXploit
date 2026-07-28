<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full space-y-8">
      <div>
        <span class="px-2.5 py-1 rounded bg-red-950 text-red-400 font-mono text-xs font-bold uppercase">ROOT ADMIN ONLY</span>
        <h1 class="text-3xl font-extrabold text-white mt-2">Manage Admins & Privilege Transfer</h1>
        <p class="text-slate-400 text-sm mt-1">Approve/demote admins (hard cap of 5 concurrent admins enforced) or transfer root status.</p>
      </div>

      <!-- Current Admins List -->
      <div class="glass-panel p-6 space-y-4">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <h3 class="text-lg font-bold text-white">Current Admins</h3>
          <span class="text-xs font-mono text-purple-400 font-bold">{{ currentAdmins.length }} / 5 ADMINS ACTIVE</span>
        </div>

        <div class="space-y-3">
          <div v-for="user in users" :key="user.id" class="p-4 bg-slate-900/80 rounded-xl border border-slate-800 flex justify-between items-center">
            <div>
              <span class="font-bold text-white">{{ user.full_name }}</span>
              <span class="text-xs text-slate-400 font-mono ml-2">@{{ user.username }}</span>
              <span :class="roleBadge(user.role)" class="text-[10px] ml-2 px-2 py-0.5 rounded font-bold uppercase">
                {{ user.role }}
              </span>
            </div>

            <div v-if="user.role !== 'root_admin'" class="flex items-center space-x-2">
              <button 
                v-if="user.role !== 'admin'" 
                @click="changeRole(user.id, 'admin')" 
                class="btn-neon-violet text-xs py-1 px-3"
              >
                Promote to Admin
              </button>
              <button 
                v-if="user.role === 'admin'" 
                @click="changeRole(user.id, 'teacher')" 
                class="btn-ghost text-xs py-1 px-3"
              >
                Demote to Teacher
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
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

const users = ref([])

const currentAdmins = computed(() => users.value.filter(u => u.role === 'admin'))

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
  if (role === 'root_admin') return 'bg-red-950 text-red-400'
  if (role === 'admin') return 'bg-purple-950 text-purple-400'
  if (role === 'teacher') return 'bg-cyan-950 text-cyan-400'
  return 'bg-slate-800 text-slate-400'
}

const changeRole = async (userId, newRole) => {
  try {
    await axios.post(`/api/admin/users/${userId}/role`, { role: newRole })
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
