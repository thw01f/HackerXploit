<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="flex-1 flex items-center justify-center p-4">
      <div class="w-full max-w-md glass-panel p-8 rounded-2xl shadow-2xl relative border border-cyan-500/20">
        <div class="text-center mb-6">
          <h2 class="text-2xl font-bold text-white">Enter Password Reset Code</h2>
          <p class="text-xs text-slate-400 font-mono mt-1">Enter your 8-character admin-issued code and new password.</p>
        </div>

        <div v-if="successMessage" class="mb-6 p-4 rounded-lg bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 text-sm">
          {{ successMessage }}
          <div class="mt-3">
            <router-link to="/login" class="btn-neon-cyan text-xs py-1.5 px-3">Sign In Now &rarr;</router-link>
          </div>
        </div>

        <div v-if="errorMessage" class="mb-6 p-4 rounded-lg bg-red-950/80 border border-red-500/50 text-red-300 text-sm">
          {{ errorMessage }}
        </div>

        <form v-if="!successMessage" @submit.prevent="handleReset" class="space-y-4">
          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-1">8-Character Reset Code</label>
            <input v-model="code" type="text" maxlength="8" required placeholder="A1B2C3D4" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white text-center font-mono text-lg tracking-widest uppercase focus:outline-none focus:border-cyan-500" />
          </div>

          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-1">New Password</label>
            <input v-model="password" type="password" required placeholder="••••••••••••" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-cyan-500" />
          </div>

          <button type="submit" :disabled="loading" class="w-full btn-neon-cyan py-3 text-sm flex items-center justify-center space-x-2">
            <span v-if="loading" class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
            <span>{{ loading ? 'Updating Password...' : 'Reset Password' }}</span>
          </button>
        </form>
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

const code = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const handleReset = async () => {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const res = await axios.post('/api/auth/reset-password', {
      code: code.value,
      password: password.value
    })
    successMessage.value = res.data.message
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Invalid or expired code'
  } finally {
    loading.value = false
  }
}
</script>
