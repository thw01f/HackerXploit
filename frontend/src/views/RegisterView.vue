<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="flex-1 flex items-center justify-center p-4">
      <div class="w-full max-w-lg glass-panel p-8 rounded-2xl shadow-2xl relative border border-cyan-500/20">
        <div class="text-center mb-6">
          <h2 class="text-2xl font-bold text-white">Join HackerXploit Club</h2>
          <p class="text-xs text-slate-400 font-mono mt-1">College Cybersecurity Club Registration</p>
        </div>

        <div v-if="successMessage" class="mb-6 p-4 rounded-lg bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 text-sm">
          {{ successMessage }}
        </div>

        <div v-if="errorMessage" class="mb-6 p-4 rounded-lg bg-red-950/80 border border-red-500/50 text-red-300 text-sm">
          {{ errorMessage }}
        </div>

        <form @submit.prevent="handleRegister" class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Full Name</label>
              <input v-model="form.full_name" type="text" required placeholder="Alex Mercer" class="w-full bg-slate-900/90 border border-slate-700 rounded-lg px-3.5 py-2 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500" />
            </div>
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Username</label>
              <input v-model="form.username" type="text" required placeholder="amercer" class="w-full bg-slate-900/90 border border-slate-700 rounded-lg px-3.5 py-2 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-1">College Email</label>
            <input v-model="form.email" type="email" required placeholder="alex@college.edu" class="w-full bg-slate-900/90 border border-slate-700 rounded-lg px-3.5 py-2 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500" />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Student ID</label>
              <input v-model="form.student_id" type="text" placeholder="CS-2026-88" class="w-full bg-slate-900/90 border border-slate-700 rounded-lg px-3.5 py-2 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500" />
            </div>
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Graduation Year</label>
              <input v-model.number="form.graduation_year" type="number" placeholder="2027" class="w-full bg-slate-900/90 border border-slate-700 rounded-lg px-3.5 py-2 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Password</label>
            <input v-model="form.password" type="password" required placeholder="••••••••••••" class="w-full bg-slate-900/90 border border-slate-700 rounded-lg px-3.5 py-2 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500" />
          </div>

          <!-- Turnstile CAPTCHA widget mockup -->
          <div class="p-3 bg-slate-900/80 border border-slate-700/70 rounded-lg flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <input type="checkbox" id="turnstile" v-model="captchaVerified" required class="w-4 h-4 text-cyan-500 rounded focus:ring-0" />
              <label for="turnstile" class="text-xs text-slate-300">Verify Cloudflare Turnstile Security</label>
            </div>
            <span class="text-[10px] font-mono text-slate-500">PROTECTED</span>
          </div>

          <button type="submit" :disabled="loading" class="w-full btn-neon-cyan py-3 text-sm flex items-center justify-center space-x-2">
            <span v-if="loading" class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
            <span>{{ loading ? 'Submitting Application...' : 'Create Account' }}</span>
          </button>
        </form>

        <div class="mt-6 text-center text-xs text-slate-400">
          Already registered? 
          <router-link to="/login" class="text-cyan-400 font-semibold hover:underline">Sign In</router-link>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const form = ref({
  full_name: '',
  username: '',
  email: '',
  student_id: '',
  graduation_year: 2027,
  password: ''
})

const captchaVerified = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const handleRegister = async () => {
  if (!captchaVerified.value) {
    errorMessage.value = 'Please complete CAPTCHA verification'
    return
  }

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const res = await authStore.register({
      ...form.value,
      captcha_token: 'DEV_BYPASS_TOKEN'
    })
    successMessage.value = res.message
  } catch (err) {
    errorMessage.value = err.message
  } finally {
    loading.value = false
  }
}
</script>
