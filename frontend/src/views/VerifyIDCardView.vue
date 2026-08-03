<template>
  <div class="min-h-screen flex flex-col justify-between bg-[#0b0e14]">
    <!-- Minimal standalone header - this is a public trust page reachable by
         anyone who scans a badge QR (including non-members), so it must never
         show the internal authenticated app navigation, even if the person
         viewing it happens to be logged in on this browser. -->
    <header class="border-b border-[#1f293d] bg-[#0c1117]/95 backdrop-blur-md">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
        <router-link to="/" class="flex items-center gap-3">
          <img src="/logo.png" alt="HackerXploit" class="w-11 h-11 object-contain" />
          <span class="font-extrabold text-white font-mono text-xl">Hacker<span class="text-red-500">Xploit</span></span>
        </router-link>
        <span class="text-sm font-mono text-slate-400 uppercase tracking-widest hidden sm:inline">Official Badge Verification</span>
      </div>
    </header>

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

        <!-- Verification Success Card - accent color reflects the verified
             person's role, matching the theme already used on the Dashboard
             badge and the full physical ID Card (red=admin, amber=teacher,
             green/amber-gold/cyan for member specializations). -->
        <div v-else-if="verification" class="glass-panel p-6 border bg-[#111927] space-y-6" :class="theme.border">

          <!-- Verified Badge Header -->
          <div class="flex items-center justify-between border-b border-[#1f293d] pb-4">
            <div class="flex items-center space-x-3">
              <img src="/logo.png" alt="HackerXploit" class="w-9 h-9 object-contain flex-shrink-0" />
              <div>
                <h3 class="font-mono font-bold text-sm text-white">VERIFIED {{ theme.label }}</h3>
                <span class="text-[10px] font-mono text-slate-400">HACKERXPLOIT OFFICIAL IDENTITY</span>
              </div>
            </div>
            <span class="text-xs font-mono font-bold px-2.5 py-0.5 rounded" :class="theme.solidBg">VALID</span>
          </div>

          <!-- Member Details -->
          <div class="flex items-center space-x-4">
            <img
              :src="verification.member.avatar_url || '/uploads/avatars/default.png'"
              @error="$event.target.src='/uploads/avatars/default.png'"
              alt="Member photo"
              class="w-16 h-16 rounded-xl object-cover border-2 shadow-lg flex-shrink-0"
              :class="theme.avatarBorder"
            />
            <div class="min-w-0">
              <h3 class="font-mono font-bold text-lg text-white truncate">{{ verification.member.full_name }}</h3>
              <p class="text-xs font-mono text-slate-500 truncate">@{{ verification.member.username }}</p>
              <span class="text-[10px] font-mono font-bold uppercase bg-[#151f30] px-2 py-0.5 rounded border inline-block mt-1" :class="[theme.textAccent, theme.badgeBorder]">
                {{ verification.member.role }}
              </span>
            </div>
          </div>

          <!-- Status Info -->
          <div class="p-3 bg-[#090d16] border border-[#1f293d] rounded-lg space-y-2 text-xs font-mono">
            <div class="flex justify-between">
              <span class="text-slate-400">BADGE ID:</span>
              <span class="text-white font-bold">{{ verification.member.member_id }}</span>
            </div>
            <div v-if="verification.member.registration_number" class="flex justify-between">
              <span class="text-slate-400">REGISTRATION NO:</span>
              <span class="text-white font-bold">{{ verification.member.registration_number }}</span>
            </div>
            <div v-if="verification.member.specialization_role" class="flex justify-between">
              <span class="text-slate-400">SPECIALIZATION:</span>
              <span class="text-white">{{ verification.member.specialization_role }}</span>
            </div>
            <div v-if="verification.member.department" class="flex justify-between">
              <span class="text-slate-400">DEPARTMENT:</span>
              <span class="text-white">{{ verification.member.department }}<template v-if="verification.member.academic_year"> &middot; Year {{ verification.member.academic_year }}</template></span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">MEMBER SINCE:</span>
              <span class="text-white">{{ verification.member.member_since }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">LIVE PARTICIPATION:</span>
              <span :class="verification.live_status.is_actively_participating ? [theme.textAccent, 'font-bold'] : 'text-slate-500'">
                {{ verification.live_status.is_actively_participating ? 'ACTIVE EVENT' : 'INACTIVE' }}
              </span>
            </div>
          </div>

          <div v-if="verification.live_status.is_actively_participating" class="p-3 rounded-lg text-xs font-mono border" :class="theme.calloutBg">
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
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import axios from 'axios'
import Footer from '../components/Footer.vue'

const route = useRoute()
const loading = ref(true)
const error = ref(null)
const verification = ref(null)

// Mirrors the role/specialization color theme already used on the Dashboard
// ID badge and the full physical ID Card - red for admins, amber for
// teachers, and per-specialization colors for members (green/amber-gold/cyan).
const THEMES = {
  admin: { label: 'ADMIN', border: 'border-red-500/50', solidBg: 'bg-red-500 text-white', avatarBorder: 'border-red-500/60', textAccent: 'text-red-400', badgeBorder: 'border-red-500/30', calloutBg: 'bg-red-500/10 border-red-500/40 text-red-300' },
  teacher: { label: 'FACULTY', border: 'border-amber-400/50', solidBg: 'bg-amber-400 text-black', avatarBorder: 'border-amber-400/60', textAccent: 'text-amber-400', badgeBorder: 'border-amber-400/30', calloutBg: 'bg-amber-400/10 border-amber-400/40 text-amber-300' },
  engineer: { label: 'CLUB MEMBER', border: 'border-[#ffb700]/50', solidBg: 'bg-[#ffb700] text-black', avatarBorder: 'border-[#ffb700]/60', textAccent: 'text-[#ffb700]', badgeBorder: 'border-[#ffb700]/30', calloutBg: 'bg-[#ffb700]/10 border-[#ffb700]/40 text-[#ffb700]' },
  pentester: { label: 'CLUB MEMBER', border: 'border-[#9fef00]/40', solidBg: 'bg-[#9fef00] text-black', avatarBorder: 'border-[#9fef00]/60', textAccent: 'text-[#9fef00]', badgeBorder: 'border-[#9fef00]/30', calloutBg: 'bg-[#9fef00]/10 border-[#9fef00]/40 text-[#9fef00]' },
  analyst: { label: 'CLUB MEMBER', border: 'border-[#00f0ff]/40', solidBg: 'bg-[#00f0ff] text-black', avatarBorder: 'border-[#00f0ff]/60', textAccent: 'text-[#00f0ff]', badgeBorder: 'border-[#00f0ff]/30', calloutBg: 'bg-[#00f0ff]/10 border-[#00f0ff]/40 text-[#00f0ff]' }
}

const theme = computed(() => {
  const member = verification.value?.member
  if (!member) return THEMES.analyst
  if (member.role === 'root_admin' || member.role === 'admin') return THEMES.admin
  if (member.role === 'teacher' || member.role === 'teacher_admin') return THEMES.teacher
  if (member.specialization_role === 'Security Engineer') return THEMES.engineer
  if (member.specialization_role === 'Penetration Tester') return THEMES.pentester
  return THEMES.analyst
})

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
