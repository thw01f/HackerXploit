<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="flex-1 flex items-center justify-center p-4">
      <div class="w-full max-w-md glass-panel p-8 rounded-2xl shadow-2xl relative border border-cyan-500/30">
        <div class="text-center mb-6">
          <span class="px-2.5 py-1 rounded bg-amber-950 text-amber-400 font-mono text-xs font-bold uppercase">INITIAL SETUP REQUIRED</span>
          <h2 class="text-2xl font-bold text-white mt-2">Configure Root Admin Credentials</h2>
          <p class="text-xs text-slate-400 font-mono mt-1">Please update your default username, email, and password before proceeding.</p>
        </div>

        <div v-if="errorMessage" class="mb-6 p-4 rounded-lg bg-red-950/80 border border-red-500/50 text-red-300 text-sm">
          {{ errorMessage }}
        </div>

        <form @submit.prevent="handleSetup" class="space-y-4">
          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-1">New Username</label>
            <input v-model="form.username" type="text" required placeholder="superadmin" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-cyan-500" />
          </div>

          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Admin Email</label>
            <input v-model="form.email" type="email" required placeholder="admin@college.edu" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-cyan-500" />
          </div>

          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-1">New Password</label>
            <input v-model="form.password" type="password" required placeholder="••••••••••••" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-cyan-500" />
          </div>

          <button type="submit" :disabled="loading" class="w-full btn-neon-cyan py-3 text-sm flex items-center justify-center space-x-2">
            <span v-if="loading" class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
            <span>{{ loading ? 'Updating...' : 'Save & Continue to Dashboard' }}</span>
          </button>
        </form>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const form = ref({
  username: authStore.user?.username || '',
  email: authStore.user?.email || '',
  password: ''
})

const loading = ref(false)
const errorMessage = ref('')

const handleSetup = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await axios.post('/api/auth/setup-admin', form.value)
    await authStore.fetchMe()
    // `redirect` can point at a backend-only path (e.g. /oauth/authorize,
    // when CTFd's SSO button sent an un-setup root admin here) that this
    // SPA's router doesn't know about - router.push() on that silently does
    // nothing, so it needs a real full-page navigation instead.
    const redirectPath = route.query.redirect
    if (typeof redirectPath === 'string' && redirectPath.startsWith('/oauth/')) {
      window.location.href = redirectPath
    } else {
      router.push(redirectPath || '/dashboard')
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Setup failed'
  } finally {
    loading.value = false
  }
}
</script>
