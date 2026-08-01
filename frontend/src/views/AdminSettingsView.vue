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
          <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/>
          </svg>
          <span>Registration Domain Allowance</span>
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
          <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
          </svg>
          <span>CTFd Password Security Policy</span>
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

      <!-- Section 3: Global Broadcast Announcement Banner -->
      <div class="glass-panel p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 class="text-lg font-bold text-white flex items-center gap-2">
            <svg class="w-5 h-5 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"/>
            </svg>
            <span>Global Dashboard Announcement Banner</span>
          </h3>

          <!-- Toggle Switch for Announcement Banner -->
          <div class="flex items-center space-x-2">
            <span class="text-xs font-mono text-slate-300 font-bold uppercase">{{ settings.announcement_enabled ? 'ENABLED' : 'DISABLED' }}</span>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="settings.announcement_enabled" class="sr-only peer">
              <div class="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#9fef00]"></div>
            </label>
          </div>
        </div>

        <div v-if="settings.announcement_enabled">
          <label class="block text-xs font-mono text-slate-300 uppercase mb-1">
            Broadcast Notice Text (Appears on Member Dashboard)
          </label>
          <textarea 
            v-model="settings.announcement_banner" 
            rows="2"
            placeholder="Welcome to HackerXploit Club Platform! Next CTF competition is scheduled for Saturday." 
            class="w-full bg-slate-900 border border-[#9fef00]/40 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-[#9fef00] focus:outline-none"
          ></textarea>
          <p class="text-[11px] text-slate-400 mt-1 font-mono">
            This message will be broadcast live at the top of every member's dashboard banner.
          </p>
        </div>
        <div v-else class="p-3 bg-slate-900/60 rounded-lg border border-slate-800 text-xs font-mono text-slate-500">
          Announcement banner is currently disabled and hidden site-wide.
        </div>
      </div>

      <!-- Section 4: Site Feature Toggles -->
      <div class="glass-panel p-6 space-y-4">
        <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3 flex items-center gap-2">
          <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
          </svg>
          <span>Site Feature Toggles</span>
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
        <button type="submit" class="btn-neon-cyan py-2.5 px-6 text-xs font-bold font-mono uppercase tracking-wider flex items-center gap-2">
          <svg class="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
          <span>Save Policy & Security Settings</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import AdminSubNav from '../components/AdminSubNav.vue'
import { useClubStore } from '../stores/club'

const clubStore = useClubStore()

const successMsg = ref('')
const settings = ref({
  general_chat_enabled: true,
  allowed_email_domains: 'gmail.com, srm.edu.in, hackerxploit.org',
  password_min_length: 8,
  announcement_enabled: true,
  announcement_banner: 'Welcome to HackerXploit Club Platform! Next CTF competition is scheduled for Saturday.'
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
    await clubStore.fetchStats()
    successMsg.value = 'Platform security and registration policy settings updated successfully!'
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to update settings')
  }
}

onMounted(() => {
  fetchSettings()
})
</script>
