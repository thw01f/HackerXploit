<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="flex-1 flex items-center justify-center p-4">
      <div class="w-full max-w-md glass-panel p-8 rounded-2xl shadow-2xl relative border border-cyan-500/20">
        <div class="text-center mb-8">
          <h2 class="text-2xl font-bold text-white">Sign In to Club Portal</h2>
          <p class="text-xs text-slate-400 font-mono mt-1">hackerxploit.org Unified Auth Service</p>
        </div>

        <div v-if="errorMessage" class="mb-6 p-4 rounded-lg bg-red-950/80 border border-red-500/50 text-red-300 text-sm">
          {{ errorMessage }}
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-2">Username or Email</label>
            <input 
              v-model="emailOrUsername" 
              type="text" 
              required 
              placeholder="operator@hackerxploit.org"
              class="w-full bg-slate-900/90 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-2">Password</label>
            <input 
              v-model="password" 
              type="password" 
              required 
              placeholder="••••••••••••"
              class="w-full bg-slate-900/90 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          <button 
            type="submit" 
            :disabled="loading"
            class="w-full btn-neon-cyan py-3 text-sm flex items-center justify-center space-x-2"
          >
            <span v-if="loading" class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
            <span>{{ loading ? 'Authenticating...' : 'Sign In' }}</span>
          </button>
        </form>

        <div class="mt-6 text-center text-xs text-slate-400">
          Need an account? 
          <router-link to="/register" class="text-cyan-400 font-semibold hover:underline">Register here</router-link>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const emailOrUsername = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    await authStore.login(emailOrUsername.value, password.value)
    const redirectPath = route.query.redirect || '/dashboard'
    router.push(redirectPath)
  } catch (err) {
    errorMessage.value = err.message
  } finally {
    loading.value = false
  }
}
</script>
