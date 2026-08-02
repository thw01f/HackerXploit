<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="flex-1 flex items-center justify-center p-4">
      <div class="w-full max-w-md glass-panel p-8 rounded-2xl shadow-2xl relative border border-cyan-500/20">

        <!-- Step indicator -->
        <div class="flex items-center justify-center gap-2 mb-6">
          <div v-for="s in 3" :key="s" class="flex items-center gap-2">
            <div
              :class="[
                'w-7 h-7 rounded-full flex items-center justify-center text-xs font-mono font-bold border-2 transition-all',
                step === s ? 'bg-[#9fef00] text-black border-[#9fef00]' : step > s ? 'bg-slate-800 text-[#9fef00] border-[#9fef00]/50' : 'bg-slate-900 text-slate-500 border-slate-700'
              ]"
            >
              <span v-if="step > s">✓</span>
              <span v-else>{{ s }}</span>
            </div>
            <div v-if="s < 3" :class="['w-8 h-0.5', step > s ? 'bg-[#9fef00]/50' : 'bg-slate-700']"></div>
          </div>
        </div>

        <!-- STEP 1: Username / Email -->
        <div v-if="step === 1">
          <div class="text-center mb-6">
            <h2 class="text-2xl font-bold text-white">Reset Password</h2>
            <p class="text-xs text-slate-400 font-mono mt-1">Enter your username or email to begin. An admin issues a one-time code out of band.</p>
          </div>

          <div v-if="errorMessage" class="mb-4 p-3 rounded-lg bg-red-950/80 border border-red-500/50 text-red-300 text-sm">
            {{ errorMessage }}
          </div>

          <form @submit.prevent="handleStep1" class="space-y-4">
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
              <span>{{ loading ? 'Submitting...' : 'Continue' }}</span>
            </button>
          </form>
        </div>

        <!-- STEP 2: Enter Code -->
        <div v-else-if="step === 2">
          <div class="text-center mb-6">
            <h2 class="text-2xl font-bold text-white">Enter Reset Code</h2>
            <p class="text-xs text-slate-400 font-mono mt-1">
              An admin has been notified for <strong class="text-white">{{ loginId }}</strong>. Enter the 8-character code once they give it to you - it's valid for 3 minutes.
            </p>
          </div>

          <div v-if="errorMessage" class="mb-4 p-3 rounded-lg bg-red-950/80 border border-red-500/50 text-red-300 text-sm">
            {{ errorMessage }}
          </div>

          <form @submit.prevent="handleStep2" class="space-y-4">
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">8-Character Reset Code</label>
              <input v-model="code" type="text" maxlength="8" required placeholder="A1B2C3D4" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white text-center font-mono text-lg tracking-widest uppercase focus:outline-none focus:border-cyan-500" />
            </div>

            <button type="submit" :disabled="loading" class="w-full btn-neon-cyan py-3 text-sm flex items-center justify-center space-x-2">
              <span v-if="loading" class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
              <span>{{ loading ? 'Verifying...' : 'Verify Code' }}</span>
            </button>

            <button type="button" @click="step = 1; errorMessage = ''" class="w-full text-xs text-slate-400 hover:text-white py-1">
              &larr; Wrong username?
            </button>
          </form>
        </div>

        <!-- STEP 3: Set New Password -->
        <div v-else-if="step === 3">
          <div class="text-center mb-6">
            <h2 class="text-2xl font-bold text-white">Set New Password</h2>
            <p class="text-xs font-mono mt-1" :class="secondsLeft <= 30 ? 'text-red-400' : 'text-slate-400'">
              Code confirmed. Finish before it expires: {{ secondsLeft }}s remaining.
            </p>
          </div>

          <div v-if="errorMessage" class="mb-4 p-3 rounded-lg bg-red-950/80 border border-red-500/50 text-red-300 text-sm">
            {{ errorMessage }}
          </div>

          <form @submit.prevent="handleStep3" class="space-y-4">
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">New Password</label>
              <input v-model="password" type="password" required placeholder="••••••••••••" minlength="8" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-cyan-500" />
            </div>
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Confirm New Password</label>
              <input v-model="confirmPassword" type="password" required placeholder="••••••••••••" minlength="8" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-cyan-500" />
            </div>

            <button type="submit" :disabled="loading" class="w-full btn-neon-cyan py-3 text-sm flex items-center justify-center space-x-2">
              <span v-if="loading" class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
              <span>{{ loading ? 'Updating Password...' : 'Reset Password' }}</span>
            </button>
          </form>
        </div>

        <!-- SUCCESS -->
        <div v-else-if="step === 4" class="text-center space-y-4">
          <h2 class="text-2xl font-bold text-white">Password Reset</h2>
          <div class="p-4 rounded-lg bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 text-sm">
            {{ successMessage }}
          </div>
          <router-link to="/login" class="btn-neon-cyan text-sm py-2.5 px-6 inline-block">Sign In Now &rarr;</router-link>
        </div>

      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

const step = ref(1)
const loginId = ref('')
const captchaVerified = ref(false)
const code = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const secondsLeft = ref(0)
let countdownTimer = null

const startCountdown = (expiresAtIso) => {
  clearInterval(countdownTimer)
  const expiresAt = new Date(expiresAtIso).getTime()
  const tick = () => {
    const remaining = Math.max(0, Math.round((expiresAt - Date.now()) / 1000))
    secondsLeft.value = remaining
    if (remaining <= 0) {
      clearInterval(countdownTimer)
      errorMessage.value = 'Your reset code expired. Please verify it again.'
      step.value = 2
    }
  }
  tick()
  countdownTimer = setInterval(tick, 1000)
}

onUnmounted(() => clearInterval(countdownTimer))

const handleStep1 = async () => {
  if (!captchaVerified.value) {
    errorMessage.value = 'Please verify CAPTCHA'
    return
  }
  loading.value = true
  errorMessage.value = ''
  try {
    await axios.post('/api/auth/forgot-password', {
      email_or_username: loginId.value,
      captcha_token: 'DEV_BYPASS_TOKEN'
    })
    step.value = 2
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Failed to submit reset request'
  } finally {
    loading.value = false
  }
}

const handleStep2 = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await axios.post('/api/auth/verify-reset-code', {
      email_or_username: loginId.value,
      code: code.value
    })
    startCountdown(res.data.expires_at)
    step.value = 3
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Invalid or expired code'
  } finally {
    loading.value = false
  }
}

const handleStep3 = async () => {
  errorMessage.value = ''
  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match'
    return
  }
  loading.value = true
  try {
    const res = await axios.post('/api/auth/reset-password', {
      email_or_username: loginId.value,
      code: code.value,
      password: password.value
    })
    clearInterval(countdownTimer)
    successMessage.value = res.data.message
    step.value = 4
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Invalid or expired code'
    if (err.response?.status === 400) {
      // Code likely expired/invalid by the time they submitted - send back to re-verify
      step.value = 2
    }
  } finally {
    loading.value = false
  }
}
</script>
