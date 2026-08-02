<template>
  <div class="max-w-5xl mx-auto space-y-8 pb-12">
    
    <!-- Page Title Header -->
    <div class="glass-panel p-8 relative overflow-hidden bg-gradient-to-r from-[#0d1525] via-[#111927] to-[#090d16] border-l-4 border-l-[#00f0ff]">
      <div class="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <span class="px-3 py-1 rounded bg-[#00f0ff]/10 border border-[#00f0ff]/30 text-[#00f0ff] font-mono text-xs font-bold uppercase tracking-wider">
            HELP CENTER & PLATFORM FEEDBACK
          </span>
          <h1 class="text-3xl font-extrabold text-white mt-2 font-mono flex items-center gap-3">
            <span>Contact Support & Bug Reporting</span>
          </h1>
          <p class="text-slate-300 text-sm mt-1.5 max-w-2xl leading-relaxed">
            Have questions for the HackerXploit leadership team, or encountered a system glitch? Submit a message below or log a structured bug report for our engineering staff.
          </p>
        </div>
        
        <div class="flex items-center space-x-2 bg-slate-900/90 p-3 rounded-xl border border-slate-800 font-mono text-xs text-slate-300">
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Response SLA: &lt; 12 Hours</span>
        </div>
      </div>
    </div>

    <!-- Tab Switcher -->
    <div class="flex space-x-3 border-b border-slate-800 pb-3">
      <button 
        @click="activeTab = 'contact'"
        :class="[
          'px-5 py-2.5 rounded-xl font-mono text-xs font-bold transition-all flex items-center space-x-2',
          activeTab === 'contact' 
            ? 'bg-[#00f0ff] text-black shadow-lg shadow-[#00f0ff]/20' 
            : 'bg-[#111927] text-slate-300 hover:bg-slate-800 border border-slate-800'
        ]"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
        <span>General Contact & Support</span>
      </button>

      <button 
        @click="activeTab = 'bug_report'"
        :class="[
          'px-5 py-2.5 rounded-xl font-mono text-xs font-bold transition-all flex items-center space-x-2',
          activeTab === 'bug_report' 
            ? 'bg-amber-400 text-black shadow-lg shadow-amber-400/20' 
            : 'bg-[#111927] text-slate-300 hover:bg-slate-800 border border-slate-800'
        ]"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        <span>Submit Bug / Vulnerability Report</span>
      </button>
    </div>

    <!-- Alert Banner -->
    <div v-if="feedbackMsg" class="p-4 rounded-xl bg-emerald-950/70 border border-emerald-500/50 text-emerald-300 text-xs font-mono flex justify-between items-center shadow-lg">
      <div class="flex items-center space-x-2">
        <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
        </svg>
        <span>{{ feedbackMsg }}</span>
      </div>
      <button @click="feedbackMsg = ''" class="text-emerald-400 hover:text-white">&times;</button>
    </div>

    <!-- TAB 1: GENERAL CONTACT FORM -->
    <div v-if="activeTab === 'contact'" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <div class="lg:col-span-2 glass-panel p-6 space-y-6">
        <h2 class="text-xl font-bold text-white font-mono border-b border-slate-800 pb-3">Send Support Message</h2>
        
        <form @submit.prevent="submitContact" class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Your Full Name *</label>
              <input v-model="contactForm.name" type="text" required class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-[#00f0ff] focus:outline-none" />
            </div>
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Email Address *</label>
              <input v-model="contactForm.email" type="email" required class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-[#00f0ff] focus:outline-none" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Subject / Inquiry Title *</label>
            <input v-model="contactForm.subject" type="text" required placeholder="e.g. Question regarding CTF registration or Academy access" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-[#00f0ff] focus:outline-none" />
          </div>

          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Message Body *</label>
            <textarea v-model="contactForm.message" rows="5" required placeholder="Provide full details of your inquiry or feedback..." class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-[#00f0ff] focus:outline-none"></textarea>
          </div>

          <div class="flex justify-end">
            <button type="submit" :disabled="loading" class="btn-htb text-xs py-2.5 px-6 font-mono font-bold uppercase tracking-wider flex items-center space-x-2">
              <span>Send Message</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
              </svg>
            </button>
          </div>
        </form>
      </div>

      <!-- Contact Info Sidebar -->
      <div class="space-y-6">
        <div class="glass-panel p-6 space-y-4 border-l-4 border-l-purple-500">
          <h3 class="text-sm font-bold text-white font-mono uppercase">Official Communications</h3>
          <div class="space-y-3 text-xs font-mono text-slate-300">
            <div>
              <span class="block text-slate-500 uppercase text-[10px]">Support Inbox</span>
              <a href="mailto:support@hackerxploit.org" class="text-[#00f0ff] hover:underline">support@hackerxploit.org</a>
            </div>
            <div>
              <span class="block text-slate-500 uppercase text-[10px]">Academic Faculty Desk</span>
              <a href="mailto:faculty@hackerxploit.org" class="text-[#00f0ff] hover:underline">faculty@hackerxploit.org</a>
            </div>
            <div>
              <span class="block text-slate-500 uppercase text-[10px]">Security Incident Response</span>
              <a href="mailto:security@hackerxploit.org" class="text-red-400 hover:underline">security@hackerxploit.org</a>
            </div>
          </div>
        </div>

        <div class="glass-panel p-6 bg-[#0c131e]">
          <h3 class="text-xs font-bold text-amber-400 font-mono uppercase mb-2">Urgent Support?</h3>
          <p class="text-xs text-slate-400 leading-relaxed font-mono">
            For urgent event questions during live competition rounds, ping the leadership team on the live <router-link to="/chat" class="text-[#9fef00] underline">General Chat channel</router-link>.
          </p>
        </div>
      </div>

    </div>

    <!-- TAB 2: BUG REPORTING FORM -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <div class="lg:col-span-2 glass-panel p-6 space-y-6 border-t-2 border-t-amber-400">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <h2 class="text-xl font-bold text-white font-mono">Report a Bug / Vulnerability</h2>
          <span class="text-[11px] font-mono px-2.5 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-500/30">BUG DISCOVERY</span>
        </div>

        <form @submit.prevent="submitBugReport" class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Issue Category *</label>
              <select v-model="bugForm.category" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-amber-400 focus:outline-none">
                <option value="UI/UX">UI / Layout / Responsiveness</option>
                <option value="Backend API">Backend API / Error Message</option>
                <option value="CTFd Sync">CTFd Account / Scoreboard Sync</option>
                <option value="ID Card/QR">Operator ID Badge & QR Verification</option>
                <option value="Security Vulnerability">Security Vulnerability (VDP)</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Severity Level *</label>
              <select v-model="bugForm.severity" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-amber-400 focus:outline-none">
                <option value="Low">Low - Minor visual tweak</option>
                <option value="Medium">Medium - Feature non-functional</option>
                <option value="High">High - Major workflow broken</option>
                <option value="Critical">Critical - System vulnerability / Crash</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Bug Title / Brief Summary *</label>
            <input v-model="bugForm.title" type="text" required placeholder="e.g. ID card QR verification fails when scanned in dark mode" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-amber-400 focus:outline-none" />
          </div>

          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Detailed Description *</label>
            <textarea v-model="bugForm.description" rows="4" required placeholder="Describe what happened, expected behavior vs actual behavior..." class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-amber-400 focus:outline-none"></textarea>
          </div>

          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Steps to Reproduce (Optional)</label>
            <textarea v-model="bugForm.steps_to_reproduce" rows="3" placeholder="1. Go to '/id-card'&#10;2. Click on 'Generate Pass'&#10;3. See error code" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-amber-400 focus:outline-none"></textarea>
          </div>

          <div class="flex justify-end">
            <button type="submit" :disabled="loading" class="px-6 py-2.5 rounded-xl bg-amber-400 text-black hover:bg-amber-300 font-mono text-xs font-extrabold uppercase shadow-lg shadow-amber-400/20 flex items-center space-x-2">
              <span>Submit Bug Report</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
              </svg>
            </button>
          </div>
        </form>
      </div>

      <!-- User's Submitted Bug History -->
      <div class="space-y-4">
        <div class="glass-panel p-6 space-y-4">
          <h3 class="text-sm font-bold text-white font-mono uppercase flex justify-between items-center border-b border-slate-800 pb-2">
            <span>Your Submitted Bug Reports</span>
            <span class="text-xs font-normal text-amber-400">{{ myReports.length }} Reports</span>
          </h3>

          <div v-if="myReports.length === 0" class="text-center py-6 text-slate-500 font-mono text-xs">
            No bug reports logged yet.
          </div>

          <div v-else class="space-y-3 max-h-[450px] overflow-y-auto pr-1">
            <div v-for="b in myReports" :key="b.id" class="p-3 bg-slate-900/90 rounded-lg border border-slate-800 space-y-1.5">
              <div class="flex justify-between items-start">
                <span class="font-bold text-xs text-white font-mono line-clamp-1">{{ b.title }}</span>
                <span :class="[
                  'text-[9px] font-mono font-bold px-2 py-0.5 rounded uppercase',
                  b.status === 'resolved' ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30' : 
                  (b.status === 'in_review' ? 'bg-amber-950 text-amber-400 border border-amber-500/30' : 'bg-slate-800 text-slate-300')
                ]">
                  {{ b.status }}
                </span>
              </div>
              <div class="flex items-center space-x-2 text-[10px] font-mono text-slate-400">
                <span>Cat: {{ b.category }}</span>
                <span>•</span>
                <span :class="b.severity === 'Critical' ? 'text-red-400 font-bold' : ''">Sev: {{ b.severity }}</span>
              </div>
            </div>
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
const activeTab = ref('contact')
const loading = ref(false)
const feedbackMsg = ref('')

const contactForm = ref({
  name: authStore.user?.full_name || authStore.user?.username || '',
  email: authStore.user?.email || '',
  subject: '',
  message: ''
})

const bugForm = ref({
  category: 'UI/UX',
  severity: 'Low',
  title: '',
  description: '',
  steps_to_reproduce: ''
})

const myReports = ref([])

const fetchMyReports = async () => {
  try {
    const res = await axios.get('/api/support/my-reports')
    myReports.value = res.data.bug_reports || []
  } catch (err) {
    console.error('Failed to load my bug reports', err)
  }
}

const submitContact = async () => {
  loading.value = true
  try {
    const res = await axios.post('/api/support/contact', contactForm.value)
    feedbackMsg.value = res.data.message
    contactForm.value.subject = ''
    contactForm.value.message = ''
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to submit contact inquiry')
  } finally {
    loading.value = false
  }
}

const submitBugReport = async () => {
  loading.value = true
  try {
    const res = await axios.post('/api/support/bug-report', bugForm.value)
    feedbackMsg.value = res.data.message
    bugForm.value.title = ''
    bugForm.value.description = ''
    bugForm.value.steps_to_reproduce = ''
    await fetchMyReports()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to submit bug report')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchMyReports()
})
</script>
