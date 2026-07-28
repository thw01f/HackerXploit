<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full space-y-8">
      <div>
        <h1 class="text-3xl font-extrabold text-white">Account Settings & Security</h1>
        <p class="text-slate-400 text-sm mt-1">Manage your identity, digital credentials, and active device sessions.</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left: Avatar Upload & Profile Details -->
        <div class="lg:col-span-2 glass-panel p-8 space-y-6">
          <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3">Personal Profile</h3>

          <div class="flex items-center space-x-6">
            <div class="relative">
              <img :src="authStore.user?.avatar_url || '/uploads/avatars/default.png'" class="w-20 h-20 rounded-2xl object-cover border-2 border-cyan-500/40" />
            </div>
            <div>
              <label class="btn-ghost text-xs py-2 px-4 cursor-pointer inline-block">
                <span>Upload New Avatar</span>
                <input type="file" @change="uploadAvatar" class="hidden" accept="image/*" />
              </label>
              <p class="text-[11px] text-slate-400 mt-1">Files are scanned with ClamAV and compressed to WebP.</p>
            </div>
          </div>

          <form @submit.prevent="updateProfile" class="space-y-4 pt-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Full Name</label>
                <input v-model="form.full_name" type="text" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" />
              </div>
              <div>
                <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Student ID</label>
                <input v-model="form.student_id" type="text" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" />
              </div>
            </div>

            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Bio / Research Focus</label>
              <textarea v-model="form.bio" rows="3" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm"></textarea>
            </div>

            <button type="submit" class="btn-neon-cyan text-xs py-2.5 px-6">Save Changes</button>
          </form>
        </div>

        <!-- Right: Active Device Sessions (Kill Switch) -->
        <div class="glass-panel p-6 space-y-4">
          <h3 class="text-sm font-mono font-bold text-white uppercase border-b border-slate-800 pb-3 flex items-center justify-between">
            <span>Active Device Sessions</span>
            <span class="text-xs text-cyan-400">KILL-SWITCH ACTIVE</span>
          </h3>

          <div class="space-y-3">
            <div v-for="s in authStore.sessions" :key="s.id" class="p-3 bg-slate-900/80 rounded-lg border border-slate-800 space-y-1">
              <div class="flex justify-between items-start">
                <span class="text-xs font-bold text-white truncate max-w-[160px]">{{ s.device_name }}</span>
                <button @click="revokeSession(s.id)" class="text-[10px] text-red-400 hover:underline font-mono font-bold">
                  REVOKE
                </button>
              </div>
              <p class="text-[11px] font-mono text-cyan-400">IP: {{ s.ip_address }}</p>
              <p class="text-[10px] text-slate-500 font-mono">Last active: {{ new Date(s.last_active).toLocaleTimeString() }}</p>
            </div>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const form = ref({
  full_name: authStore.user?.full_name || '',
  student_id: authStore.user?.student_id || '',
  bio: authStore.user?.bio || ''
})

onMounted(() => {
  authStore.fetchSessions()
})

const uploadAvatar = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  formData.append('feature', 'avatars')

  try {
    const res = await axios.post('/api/uploads', formData)
    await axios.put('/api/club/profile', { avatar_url: res.data.url })
    await authStore.fetchMe()
    alert('Avatar uploaded & processed through security pipeline successfully!')
  } catch (err) {
    alert(err.response?.data?.error || 'Avatar upload failed')
  }
}

const updateProfile = async () => {
  try {
    await axios.put('/api/club/profile', form.value)
    await authStore.fetchMe()
    alert('Profile updated successfully!')
  } catch (err) {
    alert('Failed to update profile')
  }
}

const revokeSession = async (id) => {
  if (confirm('Revoke this device session server-side immediately?')) {
    try {
      await authStore.revokeSession(id)
    } catch (err) {
      alert(err.message)
    }
  }
}
</script>
