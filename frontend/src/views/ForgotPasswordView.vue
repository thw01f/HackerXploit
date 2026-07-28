<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="flex-1 flex items-center justify-center p-4">
      <div class="w-full max-w-md glass-panel p-8 rounded-2xl shadow-2xl relative border border-cyan-500/20">
        <div class="text-center mb-6">
          <h2 class="text-2xl font-bold text-white">Reset Password Request</h2>
          <p class="text-xs text-slate-400 font-mono mt-1">Submit your account email or username to request an admin reset code.</p>
        </div>

        <div v-if="successMessage" class="mb-6 p-4 rounded-lg bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 text-sm">
          {{ successMessage }}
          <div class="mt-3">
            <router-link to="/reset-password" class="btn-neon-cyan text-xs py-1.5 px-3">Enter Reset Code &rarr;</router-link>
          </div>
        </div>

        <div v-if="errorMessage" class="mb-6 p-4 rounded-lg bg-red-950/80 border border-red-500/50 text-red-300 text-sm">
          {{ errorMessage }}
        </div>

        <form v-if="!successMessage" @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Username or Email</label>
            <input v-model="loginId" type="text" required placeholder="operator@hackerxploit.org" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-cyan-500" />
          </div>

          <div class="p-3 bg-slate-900/80 border border-slate-700/70 rounded-lg flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <input type="checkbox" id="captcha" v-model="captchaVerified" required class="w-4 h-4 text-cyan-500 rounded" />
              <label for="captcha" class="text-xs text-slate-300">Verify CAPTCHA Security</label>
            </div>
            <span class="text-[10px] font-mono text-slate-500">PROTECTED</span>
          </div>

          <button type="submit" :disabled="loading" class="w-full btn-neon-cyan py-3 text-sm flex items-center justify-center space-x-2">
            <span v-if="loading" class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
            <span>{{ loading ? 'Submitting Request...' : 'Submit Reset Request' }}</span>
          </button>
        </form>

        <div class="mt-6 text-center text-xs text-slate-400">
          Already have a 8-character reset code? 
          <router-link to="/reset-password" class="text-cyan-400 font-semibold hover:underline">Reset password here</router-link>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

const loginId = ref('')
const captchaVerified = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const handleSubmit = async () => {
  if (!captchaVerified.value) {
    errorMessage.value = 'Please verify CAPTCHA'
    return
  }

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const res = await axios.post('/api/auth/forgot-password', {
      email_or_username: loginId.value,
      captcha_token: 'DEV_BYPASS_TOKEN'
    })
    successMessage.value = res.data.message
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Failed to submit reset request'
  } finally {
    loading.value = false
  }
}
</script>
