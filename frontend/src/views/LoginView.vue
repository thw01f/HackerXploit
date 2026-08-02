<template>
  <div class="min-h-screen flex flex-col justify-between bg-[#0b0e14]">
    <Navbar />

    <main class="flex-1 flex items-center justify-center p-4">
      <div class="w-full max-w-md glass-panel p-8 rounded-xl shadow-2xl relative border border-[#1f293d]">
        
        <!-- Header -->
        <div class="text-center mb-6">
          <img src="/logo.png" class="w-24 h-24 object-contain mx-auto mb-3" alt="HackerXploit Logo" />
          <h2 class="text-2xl font-bold text-white font-mono">Sign In</h2>
          <p class="text-xs text-slate-400 font-mono mt-1">hackerxploit.org // Unified Auth Service</p>
        </div>


        <!-- Error Message Alert -->
        <div v-if="errorMessage" class="mb-5 p-3 rounded-lg bg-red-950/80 border border-red-500/50 text-red-300 text-xs font-mono">
          {{ errorMessage }}
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-xs font-mono text-slate-400 uppercase mb-1.5">Username or Email</label>
            <input 
              v-model="emailOrUsername" 
              type="text" 
              required 
              placeholder="operator or user@hackerxploit.org"
              class="w-full"
            />
          </div>

          <div>
            <div class="flex justify-between items-center mb-1.5">
              <label class="block text-xs font-mono text-slate-400 uppercase">Password</label>
              <router-link to="/forgot-password" class="text-xs font-mono text-[#9fef00] hover:underline">Forgot?</router-link>
            </div>
            <input 
              v-model="password" 
              type="password" 
              required 
              placeholder="••••••••••••"
              class="w-full"
            />
          </div>

          <button 
            type="submit" 
            :disabled="loading"
            class="w-full btn-htb py-3 text-sm flex items-center justify-center space-x-2 mt-2"
          >
            <span v-if="loading" class="animate-spin rounded-full h-4 w-4 border-2 border-black border-t-transparent"></span>
            <span>{{ loading ? 'AUTHENTICATING...' : 'AUTHENTICATE &rarr;' }}</span>
          </button>
        </form>

        <div class="mt-6 pt-4 border-t border-[#1f293d] text-center text-xs font-mono text-slate-400">
          Need an account? 
          <router-link to="/register" class="text-[#9fef00] font-semibold hover:underline">Register here</router-link>
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
    if (authStore.user?.is_root_admin && authStore.user?.is_first_login) {
      router.push('/setup-admin')
    } else if (authStore.user?.status === 'approved' && !authStore.user?.onboarding_completed) {
      router.push('/onboarding')
    } else {
      const redirectPath = route.query.redirect || '/dashboard'
      router.push(redirectPath)
    }
  } catch (err) {
    errorMessage.value = err.message || 'Login failed.'
  } finally {
    loading.value = false
  }
}
</script>
