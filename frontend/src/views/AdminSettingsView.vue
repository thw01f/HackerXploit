<template>
  <div class="space-y-8">
    <AdminSubNav />

    <div>
      <span class="px-2.5 py-1 rounded bg-purple-950 text-purple-400 font-mono text-xs font-bold uppercase">PLATFORM SECURITY & POLICY</span>
      <h1 class="text-3xl font-extrabold text-white mt-2">Registration, Security & Feature Toggles</h1>
      <p class="text-slate-400 text-sm mt-1">Configure email domain allowance, password complexity rules, and global feature toggles.</p>
    </div>

    <!-- Success Banner -->
    <div v-if="successMsg" class="p-4 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-400 text-xs font-mono flex items-center justify-between">
      <span>✅ {{ successMsg }}</span>
      <button @click="successMsg = ''" class="text-emerald-400 hover:text-white">&times;</button>
    </div>

    <form @submit.prevent="saveSettings" class="space-y-6">
      <!-- Section 1: Registration Domain Allowance -->
      <div class="glass-panel p-6 space-y-4">
        <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3 flex items-center space-x-2">
          <span>🌐 Registration Domain Allowance</span>
        </h3>

        <div>
          <label class="block text-xs font-mono text-slate-300 uppercase mb-1">
            Allowed Email Domains (Comma-Separated)
          </label>
          <input 
            v-model="settings.allowed_email_domains" 
            type="text" 
            placeholder="gmail.com, srm.edu.in, hackerxploit.org" 
            class="w-full bg-slate-900 border border-cyan-500/40 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-cyan-500 focus:outline-none"
          />
          <p class="text-[11px] text-slate-400 mt-1 font-mono">
            Enter authorized domains separated by commas (e.g. <code>gmail.com, srm.edu.in, hackerxploit.org</code>). Use <code>*</code> to permit all domains.
          </p>
        </div>
      </div>

      <!-- Section 2: CTFd-Aligned Password Security Policy -->
      <div class="glass-panel p-6 space-y-4">
        <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3 flex items-center space-x-2">
          <span>🔒 CTFd Password Security Policy</span>
        </h3>

        <div>
          <label class="block text-xs font-mono text-slate-300 uppercase mb-1">
            Minimum Password Length
          </label>
          <input 
            v-model.number="settings.password_min_length" 
            type="number" 
            min="6" 
            max="64"
            class="w-full max-w-xs bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono"
          />
          <p class="text-[11px] text-slate-400 mt-1.5 font-mono">
            Aligned with CTFd security standard (minimum {{ settings.password_min_length || 8 }} characters). No forced arbitrary symbol restrictions.
          </p>
        </div>
      </div>

      <!-- Section 3: Site Feature Toggles -->
      <div class="glass-panel p-6 space-y-4">
        <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3">
          💬 Site Feature Toggles
        </h3>

        <div class="p-4 bg-slate-900/80 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <h4 class="text-sm font-bold text-white">General Text Chat Channel</h4>
            <p class="text-xs text-slate-400 mt-0.5">Enable or disable real-time text chat at <code>/chat</code> site-wide.</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="settings.general_chat_enabled" class="sr-only peer">
            <div class="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-500"></div>
          </label>
        </div>
      </div>

      <div class="flex justify-end">
        <button type="submit" class="btn-neon-cyan py-2.5 px-6 text-xs font-bold font-mono">
          💾 Save Policy & Security Settings
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import AdminSubNav from '../components/AdminSubNav.vue'

const successMsg = ref('')
const settings = ref({
  general_chat_enabled: true,
  allowed_email_domains: 'gmail.com, srm.edu.in, hackerxploit.org',
  password_min_length: 8
})

const fetchSettings = async () => {
  try {
    const res = await axios.get('/api/admin/settings')
    settings.value = { ...settings.value, ...res.data }
  } catch (err) {
    console.error('Failed to load settings', err)
  }
}

const saveSettings = async () => {
  try {
    await axios.post('/api/admin/settings', settings.value)
    successMsg.value = 'Platform security and registration policy settings updated successfully!'
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to update settings')
  }
}

onMounted(() => {
  fetchSettings()
})
</script>
