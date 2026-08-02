<template>
  <div class="min-h-screen flex flex-col justify-between bg-[#0b0e14]">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex-1 w-full flex flex-col items-center justify-center">
      <div class="w-full max-w-md">

        <!-- Loading State -->
        <div v-if="loading" class="py-12 text-center font-mono text-sm text-slate-500">
          <span class="inline-block animate-spin mr-2">⚡</span> Verifying ID Card Credentials...
        </div>

        <!-- Verification Error Card -->
        <div v-else-if="error" class="glass-panel p-8 text-center space-y-4 border border-red-500/50 bg-[#111927]">
          <div class="text-4xl">🚨</div>
          <h4 class="font-mono font-bold text-xl text-white">Verification Failed</h4>
          <p class="text-xs font-mono text-red-400">{{ error }}</p>
          <router-link to="/" class="btn-ghost text-xs font-mono py-2 px-4 inline-block mt-2">Return to Home</router-link>
        </div>

        <!-- Verification Success Card -->
        <div v-else-if="verification" class="glass-panel p-6 border border-[#9fef00]/40 bg-[#111927] space-y-6">
          
          <!-- Shield Badge Header -->
          <div class="flex items-center justify-between border-b border-[#1f293d] pb-4">
            <div class="flex items-center space-x-3">
              <span class="text-2xl">🛡️</span>
              <div>
                <h3 class="font-mono font-bold text-sm text-white">VERIFIED CLUB MEMBER</h3>
                <span class="text-[10px] font-mono text-slate-400">HACKERXPLOIT OFFICIAL IDENTITY</span>
              </div>
            </div>
            <span class="text-xs font-mono font-bold bg-[#9fef00] text-black px-2.5 py-0.5 rounded">VALID</span>
          </div>

          <!-- Member Details -->
          <div class="flex items-center space-x-4">
            <img
              :src="verification.member.avatar_url || '/uploads/avatars/default.png'"
              @error="$event.target.src='/uploads/avatars/default.png'"
              alt="Member photo"
              class="w-16 h-16 rounded-xl object-cover border-2 border-[#9fef00]/60 shadow-lg"
            />
            <div>
              <h3 class="font-mono font-bold text-lg text-white uppercase">{{ verification.member.username }}</h3>
              <span class="text-[10px] font-mono font-bold uppercase bg-[#151f30] text-[#00f0ff] px-2 py-0.5 rounded border border-[#00f0ff]/30">
                {{ verification.member.role }}
              </span>
              <p class="text-[11px] font-mono text-slate-400 mt-1">ID: {{ verification.member.member_id }}</p>
            </div>
          </div>

          <!-- Status Info -->
          <div class="p-3 bg-[#090d16] border border-[#1f293d] rounded-lg space-y-2 text-xs font-mono">
            <div class="flex justify-between">
              <span class="text-slate-400">MEMBER SINCE:</span>
              <span class="text-white">{{ verification.member.member_since }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">LIVE PARTICIPATION:</span>
              <span :class="verification.live_status.is_actively_participating ? 'text-[#9fef00] font-bold' : 'text-slate-500'">
                {{ verification.live_status.is_actively_participating ? 'ACTIVE EVENT' : 'INACTIVE' }}
              </span>
            </div>
          </div>

          <div v-if="verification.live_status.is_actively_participating" class="p-3 bg-[#9fef00]/10 border border-[#9fef00]/40 rounded-lg text-xs font-mono text-[#9fef00]">
            Currently in: <strong>{{ verification.live_status.active_event_name }}</strong>
          </div>

          <div class="text-[10px] font-mono text-center text-slate-500 border-t border-[#1f293d] pt-3">
            Verified at {{ new Date(verification.verified_at).toLocaleString() }}
          </div>

        </div>

      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

const route = useRoute()
const loading = ref(true)
const error = ref(null)
const verification = ref(null)

const verifyToken = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await axios.get(`/api/verify/${route.params.token}`)
    verification.value = res.data
  } catch (err) {
    error.value = err.response?.data?.error || 'Invalid or revoked ID card token.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  verifyToken()
})
</script>
