<template>
  <div class="space-y-8">
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
                <input v-model="form.full_name" type="text" placeholder="e.g. GOWTHAMAN GS" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" />
              </div>
              <div>
                <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Student ID</label>
                <input v-model="form.student_id" type="text" placeholder="e.g. RA2311030050008" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" />
              </div>
              <div>
                <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Academic Year</label>
                <select v-model="form.academic_year" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm">
                  <option value="I">1st Year (I)</option>
                  <option value="II">2nd Year (II)</option>
                  <option value="III">3rd Year (III)</option>
                  <option value="IV">4th Year (IV)</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Department</label>
                <input v-model="form.department" type="text" placeholder="Cyber Security" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" />
              </div>
            </div>

            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Bio / Research Focus</label>
              <textarea v-model="form.bio" rows="2" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm"></textarea>
            </div>

            <!-- Private Contact Info (Confidential) -->
            <div class="pt-4 border-t border-slate-800 space-y-4">
              <div class="flex items-center justify-between">
                <h4 class="text-xs font-mono font-bold uppercase text-cyan-400 tracking-wider flex items-center gap-1.5">
                  <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                  </svg>
                  <span>Private Contact Information</span>
                </h4>
                <span class="text-[10px] text-slate-400 font-mono">Visible ONLY to Teachers & Platform Admins</span>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Personal Gmail Address</label>
                  <input v-model="form.gmail" type="email" placeholder="yourname@gmail.com" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono" />
                </div>
                <div>
                  <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Phone Number / WhatsApp</label>
                  <input v-model="form.phone_number" type="tel" placeholder="e.g. 6379855124" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono" />
                </div>
              </div>
            </div>

            <!-- Social & Portfolio Connections -->
            <div class="pt-4 border-t border-slate-800 space-y-4">
              <h4 class="text-xs font-mono font-bold uppercase text-[#9fef00] tracking-wider">Cyber Portfolios & Social Links (Synced to CTFd)</h4>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Portfolio Website URL</label>
                  <input v-model="form.website_url" type="url" placeholder="https://yourname.dev" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono" />
                </div>
                <div>
                  <label class="block text-xs font-mono text-slate-300 uppercase mb-1">GitHub Profile URL</label>
                  <input v-model="form.github_url" type="url" placeholder="https://github.com/username" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono" />
                </div>
                <div>
                  <label class="block text-xs font-mono text-slate-300 uppercase mb-1">LinkedIn Profile URL</label>
                  <input v-model="form.linkedin_url" type="url" placeholder="https://linkedin.com/in/username" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono" />
                </div>
                <div>
                  <label class="block text-xs font-mono text-slate-300 uppercase mb-1">TryHackMe Profile URL</label>
                  <input v-model="form.tryhackme_url" type="url" placeholder="https://tryhackme.com/p/username" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono" />
                </div>
                <div class="sm:col-span-2">
                  <label class="block text-xs font-mono text-slate-300 uppercase mb-1">HackTheBox Profile URL</label>
                  <input v-model="form.htb_url" type="url" placeholder="https://app.hackthebox.com/profile/12345" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono" />
                </div>
              </div>
            </div>

            <button type="submit" class="btn-neon-cyan text-xs py-2.5 px-6 font-bold uppercase tracking-wider flex items-center gap-2">
              <svg class="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
              <span>Save & Sync Settings</span>
            </button>
          </form>
        </div>

        <!-- Right: Active Device Sessions (Kill Switch) -->
        <div class="glass-panel p-6 space-y-4">
          <div class="border-b border-slate-800 pb-3 flex items-center justify-between">
            <h3 class="text-sm font-mono font-bold text-white uppercase">Active Device Sessions</h3>
          </div>

          <div class="space-y-3">
            <div v-for="s in devices" :key="s.id" :class="s.is_current_device ? 'border-cyan-500/60 bg-cyan-950/20' : 'border-slate-800 bg-slate-900/80'" class="p-3 rounded-lg border space-y-1">
              <div class="flex justify-between items-start">
                <span class="text-xs font-bold text-white truncate max-w-[160px]">
                  {{ s.device_label || s.device_name }}
                  <span v-if="s.is_current_device" class="ml-1 text-[9px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 font-mono border border-cyan-500/30">THIS DEVICE</span>
                </span>
                <button v-if="!s.is_current_device" @click="revokeDevice(s.id)" class="text-[10px] text-red-400 hover:underline font-mono font-bold">
                  REVOKE
                </button>
              </div>
              <p class="text-[11px] font-mono text-cyan-400">IP: {{ s.ip_address }}</p>
              <p class="text-[10px] text-slate-500 font-mono">Last active: {{ new Date(s.last_active_at || s.created_at).toLocaleString() }}</p>
            </div>
          </div>
        </div>
      </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const form = ref({
  full_name: authStore.user?.full_name || '',
  student_id: authStore.user?.student_id || '',
  academic_year: authStore.user?.academic_year || 'I',
  department: authStore.user?.department || '',
  bio: authStore.user?.bio || '',
  gmail: authStore.user?.gmail || '',
  phone_number: authStore.user?.phone_number || '',
  website_url: authStore.user?.website_url || '',
  github_url: authStore.user?.github_url || '',
  linkedin_url: authStore.user?.linkedin_url || '',
  tryhackme_url: authStore.user?.tryhackme_url || '',
  htb_url: authStore.user?.htb_url || ''
})

const devices = ref([])

const fetchDevices = async () => {
  try {
    const res = await axios.get('/api/club/profile/devices')
    devices.value = res.data.devices
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  fetchDevices()
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

const revokeDevice = async (id) => {
  if (confirm('Revoke this device session server-side immediately?')) {
    try {
      await axios.delete(`/api/club/profile/devices/${id}`)
      await fetchDevices()
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to revoke device')
    }
  }
}

const logoutAllOthers = async () => {
  if (confirm('Log out all other active devices except this one?')) {
    try {
      await axios.delete('/api/club/profile/devices/others')
      await fetchDevices()
    } catch (err) {
      alert('Failed to revoke other devices')
    }
  }
}
</script>
