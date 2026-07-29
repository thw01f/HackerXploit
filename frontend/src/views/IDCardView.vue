<template>
  <div class="space-y-8">
      
      <!-- Title & Subtitle -->
      <div class="text-center max-w-xl mx-auto mb-8 space-y-2">
        <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#151f30] border border-[#9fef00]/30 text-[#9fef00] text-xs font-mono">
          <span class="w-2 h-2 rounded-full bg-[#9fef00]"></span>
          <span>CYBERPUNK IDENTITY BADGE</span>
        </div>
        <h1 class="text-3xl font-extrabold text-white font-mono">Virtual Member ID Card</h1>
        <p class="text-slate-400 text-sm">Official club credentials with live event participation status & QR verification.</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="py-16 text-center font-mono text-sm text-slate-500">
        Loading ID badge credentials...
      </div>

      <!-- Card Display -->
      <div v-else-if="cardData" class="max-w-2xl mx-auto flex flex-col items-center w-full relative">

        <!-- Card View Toggle Selector -->
        <div class="flex items-center gap-2 bg-[#0c1117] p-1.5 rounded-xl border border-[#1a2332] font-mono text-xs shadow-xl z-20 mb-4">
          <button 
            @click="activeCardView = 'physical'"
            :class="[
              'px-4 py-2 rounded-lg font-bold transition-all flex items-center gap-2',
              activeCardView === 'physical' ? 'bg-[#9fef00] text-black shadow-lg scale-105' : 'text-slate-400 hover:text-white'
            ]"
          >
            <span>🪪 Hanging 3D Badge</span>
          </button>
          <button 
            @click="activeCardView = 'qr'"
            :class="[
              'px-4 py-2 rounded-lg font-bold transition-all flex items-center gap-2',
              activeCardView === 'qr' ? 'bg-[#00f0ff] text-black shadow-lg scale-105' : 'text-slate-400 hover:text-white'
            ]"
          >
            <span>📲 QR Live Pass</span>
          </button>
        </div>

        <!-- 1. Physical Member ID Badge Mode (CSS 3D Interactive Tilt) -->
        <div 
          v-if="activeCardView === 'physical'" 
          class="w-full max-w-md perspective-container relative pt-8"
          @mousemove="handleMouseMove"
          @mouseleave="handleMouseLeave"
        >
          <!-- Lanyard Strap Header Loop -->
          <div class="absolute -top-12 left-1/2 -translate-x-1/2 flex flex-col items-center z-10 pointer-events-none">
            <!-- Woven Fabric Strap -->
            <div :class="['w-12 h-20 bg-gradient-to-b border-x-2 shadow-2xl relative flex items-center justify-center overflow-hidden rounded-t-md', theme.lanyardStrap]">
              <div class="absolute inset-0 bg-[radial-gradient(#ffffff_1.5px,transparent_1.5px)] [background-size:6px_6px] opacity-20"></div>
              <span :class="['text-[9px] font-mono font-extrabold rotate-90 tracking-widest whitespace-nowrap opacity-90 drop-shadow', theme.strapText]">
                HACKERXPLOIT
              </span>
            </div>
            <!-- Heavy Metallic Clip -->
            <div class="w-9 h-7 rounded-md border-2 border-slate-300 bg-gradient-to-b from-slate-200 via-slate-400 to-slate-700 shadow-xl flex items-center justify-center -mt-1">
              <div class="w-4 h-3 bg-slate-900 border border-slate-500 rounded-sm"></div>
            </div>
          </div>

          <!-- Card Outer Container -->
          <div 
            :class="['glass-panel p-6 rounded-2xl border-2 bg-gradient-to-b shadow-2xl relative overflow-hidden transition-transform duration-100 ease-out transform-gpu mt-2', theme.borderClass, theme.bgGradient]"
            :style="cardTransformStyle"
          >
            
            <!-- Dynamic Glare Light Overlay -->
            <div 
              class="absolute inset-0 pointer-events-none transition-opacity duration-200"
              :style="glareOverlayStyle"
            ></div>

            <!-- Hologram Flare Top-Right -->
            <div :class="['absolute -right-12 -top-12 w-32 h-32 bg-gradient-to-br rounded-full blur-2xl pointer-events-none', theme.holoGlow]"></div>

            <!-- Lanyard Punch Hole -->
            <div class="w-14 h-4 mx-auto mb-4 bg-[#070a10] border-2 border-slate-600 rounded-full flex items-center justify-center shadow-inner">
              <div class="w-7 h-1.5 bg-slate-500 rounded-full"></div>
            </div>

            <!-- Header Row -->
            <div class="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-5">
              <div class="flex items-center space-x-2.5">
                <img src="/logo.png" class="w-8 h-8 object-contain drop-shadow-[0_0_6px_rgba(255,255,255,0.4)]" alt="HackerXploit" />
                <div>
                  <h4 class="font-mono text-xs font-extrabold text-white leading-tight">HACKERXPLOIT</h4>
                  <span :class="['text-[9px] font-mono tracking-widest uppercase block -mt-0.5 font-bold', theme.textAccent]">OFFSEC MEMBER BADGE</span>
                </div>
              </div>

              <div class="text-right font-mono">
                <span class="text-[9px] text-slate-400 block">BADGE ID</span>
                <span class="text-xs font-bold text-white tracking-wider">{{ cardData.user.member_id || 'HX-2026-0099' }}</span>
              </div>
            </div>

            <!-- Main Badge Content: Photo, User Details -->
            <div class="flex items-start space-x-4 mb-6">
              <!-- Avatar Photo Frame with Hologram Chip -->
              <div class="relative flex-shrink-0">
                <img 
                  :src="avatarSrc" 
                  @error="onAvatarError"
                  class="w-24 h-28 rounded-xl object-cover border-2 bg-[#070a10] shadow-xl"
                  :style="{ borderColor: theme.hex }" 
                />
                <div :class="['absolute -bottom-2 -right-2 w-10 h-6 rounded border flex items-center justify-center text-[8px] font-mono font-extrabold shadow-lg', theme.chipBg]">
                  CHIP
                </div>
              </div>

              <!-- User Info Block -->
              <div class="flex-1 min-w-0 space-y-1.5 font-mono">
                <span class="text-[9px] text-slate-400 uppercase tracking-widest block font-bold">OPERATOR NAME</span>
                <h3 class="text-base font-extrabold text-white uppercase tracking-tight truncate leading-tight">
                  {{ cardData.user.full_name || cardData.user.username }}
                </h3>
                <p :class="['text-xs font-bold truncate', theme.textAccent]">@{{ cardData.user.username }}</p>

                <!-- Role Badges Row -->
                <div class="pt-2 flex flex-wrap gap-1.5">
                  <span :class="['text-[10px] font-extrabold uppercase px-2 py-0.5 rounded border shadow', theme.badgeBg]">
                    {{ theme.title }}
                  </span>
                  <span class="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-[#151f30] text-slate-300 border border-slate-700 shadow">
                    {{ cardData.user.role?.replace('_', ' ') }}
                  </span>
                  <span :class="['text-[10px] font-extrabold uppercase px-2 py-0.5 rounded border shadow', cardData.live_status.is_active_event ? 'bg-emerald-950 text-[#9fef00] border-[#9fef00]' : 'bg-slate-900 text-slate-400 border-slate-700']">
                    {{ cardData.live_status.is_active_event ? '⚡ LIVE EVENT' : 'STANDBY' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Barcode & Official Seal Footer -->
            <div class="pt-4 border-t border-slate-800/80 flex items-center justify-between font-mono">
              <div class="space-y-1">
                <!-- Barcode simulation -->
                <div class="flex space-x-0.5 h-6 items-center">
                  <div v-for="i in 30" :key="i" :class="[i % 3 === 0 ? 'w-1' : 'w-0.5', i % 5 === 0 ? theme.barcodeColor : 'bg-slate-300']" class="h-full"></div>
                </div>
                <span class="text-[8px] text-slate-400 tracking-widest block uppercase font-bold">OFFICIAL HACKERXPLOIT CREDENTIAL</span>
              </div>

              <div class="text-right">
                <span class="text-[9px] text-slate-400 block">VALID THRU</span>
                <span class="text-xs font-bold text-white">DEC 2026</span>
              </div>
            </div>

          </div>
        </div>

        <!-- 2. QR Live Event Pass View -->
        <div v-else-if="activeCardView === 'qr'" class="w-full max-w-md">
          <div class="glass-panel p-6 rounded-2xl border-2 border-[#00f0ff]/60 bg-[#111927] shadow-2xl relative space-y-5">
            
            <div class="text-center border-b border-[#1f293d] pb-4">
              <span class="text-xs font-mono font-bold text-[#00f0ff] uppercase bg-[#151f30] px-3 py-1 rounded-full border border-[#00f0ff]/40">
                OFFICIAL QR VERIFICATION PASS
              </span>
              <h3 class="text-lg font-bold text-white font-mono mt-2">Scan for Attendance & Event Access</h3>
            </div>

            <!-- Large Center QR Code -->
            <div class="flex flex-col items-center justify-center p-4 bg-white rounded-xl border-2 border-[#00f0ff] shadow-xl max-w-[220px] mx-auto">
              <img 
                :src="`https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(cardData.verification_url)}`" 
                alt="QR Verification" 
                class="w-44 h-44 object-contain" 
              />
              <span class="text-[10px] font-mono font-bold text-slate-700 mt-2">HX-VERIFY-ID</span>
            </div>

            <div class="bg-[#090d16] p-3 rounded-lg border border-[#1f293d] text-center font-mono space-y-1">
              <span class="text-[10px] text-slate-400 uppercase block font-bold">SECURITY TOKEN HASH</span>
              <p class="text-xs text-[#00f0ff] font-bold break-all">{{ cardData.token }}</p>
            </div>

          </div>
        </div>

        <!-- Bottom Controls -->
        <div class="flex flex-wrap gap-3 justify-center w-full pt-4 font-mono z-20">
          <a :href="cardData.verification_url" target="_blank" class="btn-ghost text-xs text-[#00f0ff] border-[#00f0ff]/30 hover:border-[#00f0ff] py-2.5 px-5 rounded-xl">
            🔗 Public Verification Link
          </a>
          <button class="btn-htb text-xs py-2.5 px-5 rounded-xl" :disabled="regenerating" @click="regenerateToken">
            🔄 {{ regenerating ? 'Regenerating...' : 'Regenerate Token' }}
          </button>
        </div>

      </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const loading = ref(true)
const cardData = ref(null)
const regenerating = ref(false)
const activeCardView = ref('physical')
const avatarLoadError = ref(false)

// 3D Physics Tilt State
const rotateX = ref(0)
const rotateY = ref(0)
const glareX = ref(50)
const glareY = ref(50)

const defaultAvatarSvg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'><rect width='100' height='100' fill='%230b0e14'/><circle cx='50' cy='38' r='20' fill='%231f293d' stroke='%239fef00' stroke-width='2'/><path d='M20,85 C20,62 35,55 50,55 C65,55 80,62 80,85 Z' fill='%231f293d' stroke='%239fef00' stroke-width='2'/></svg>"

const avatarSrc = computed(() => {
  if (avatarLoadError.value || !cardData.value?.user?.avatar_url) {
    return defaultAvatarSvg
  }
  return cardData.value.user.avatar_url
})

const onAvatarError = () => {
  avatarLoadError.value = true
}

const handleMouseMove = (e) => {
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const centerX = rect.width / 2
  const centerY = rect.height / 2

  // Pitch (-15 to 15 deg) & Yaw (-15 to 15 deg)
  rotateX.value = -((y - centerY) / centerY) * 14
  rotateY.value = ((x - centerX) / centerX) * 14

  glareX.value = (x / rect.width) * 100
  glareY.value = (y / rect.height) * 100
}

const handleMouseLeave = () => {
  rotateX.value = 0
  rotateY.value = 0
  glareX.value = 50
  glareY.value = 50
}

const cardTransformStyle = computed(() => ({
  transform: `perspective(1000px) rotateX(${rotateX.value}deg) rotateY(${rotateY.value}deg) scale3d(1.02, 1.02, 1.02)`
}))

const glareOverlayStyle = computed(() => ({
  background: `radial-gradient(circle at ${glareX.value}% ${glareY.value}%, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 70%)`,
  opacity: rotateX.value !== 0 || rotateY.value !== 0 ? 1 : 0
}))

const theme = computed(() => {
  const role = cardData.value?.user?.specialization_role || authStore.user?.specialization_role || 'Security Analyst'
  if (role === 'Penetration Tester') {
    return {
      title: '⚔️ PENETRATION TESTER',
      shortRole: 'PENTESTER',
      hex: '#9fef00',
      borderClass: 'border-[#9fef00]/80 shadow-[0_20px_50px_rgba(159,239,0,0.2)]',
      bgGradient: 'from-[#111c14] via-[#0a140d] to-[#050a06]',
      lanyardStrap: 'from-[#0d1f12] via-[#09140c] to-[#040805] border-[#9fef00]/80',
      strapText: 'text-[#9fef00]',
      holoGlow: 'from-[#9fef00]/30 to-emerald-500/20',
      badgeBg: 'bg-[#9fef00]/15 text-[#9fef00] border-[#9fef00]/40',
      textAccent: 'text-[#9fef00]',
      chipBg: 'bg-gradient-to-r from-lime-400 to-emerald-500 border-lime-200 text-black',
      barcodeColor: 'bg-[#9fef00]'
    }
  } else if (role === 'Security Engineer') {
    return {
      title: '⚡ SECURITY ENGINEER',
      shortRole: 'ENGINEER',
      hex: '#ffb700',
      borderClass: 'border-[#ffb700]/80 shadow-[0_20px_50px_rgba(255,183,0,0.2)]',
      bgGradient: 'from-[#211508] via-[#140c04] to-[#080401]',
      lanyardStrap: 'from-[#291a0a] via-[#170e05] to-[#0a0501] border-[#ffb700]/80',
      strapText: 'text-[#ffb700]',
      holoGlow: 'from-[#ffb700]/30 to-orange-500/20',
      badgeBg: 'bg-[#ffb700]/15 text-[#ffb700] border-[#ffb700]/40',
      textAccent: 'text-[#ffb700]',
      chipBg: 'bg-gradient-to-r from-amber-400 to-orange-500 border-amber-200 text-black',
      barcodeColor: 'bg-[#ffb700]'
    }
  } else {
    // Security Analyst
    return {
      title: '🛡️ SECURITY ANALYST',
      shortRole: 'ANALYST',
      hex: '#00f0ff',
      borderClass: 'border-[#00f0ff]/80 shadow-[0_20px_50px_rgba(0,240,255,0.2)]',
      bgGradient: 'from-[#091829] via-[#06101c] to-[#03080f]',
      lanyardStrap: 'from-[#0b1d30] via-[#071321] to-[#03080e] border-[#00f0ff]/80',
      strapText: 'text-[#00f0ff]',
      holoGlow: 'from-[#00f0ff]/30 to-blue-500/20',
      badgeBg: 'bg-[#00f0ff]/15 text-[#00f0ff] border-[#00f0ff]/40',
      textAccent: 'text-[#00f0ff]',
      chipBg: 'bg-gradient-to-r from-cyan-400 to-blue-500 border-cyan-200 text-black',
      barcodeColor: 'bg-[#00f0ff]'
    }
  }
})

const fetchIDCard = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/profile/id-card')
    cardData.value = res.data
  } catch (err) {
    console.error('Failed to load ID Card, using active user fallback', err)
    cardData.value = {
      user: {
        id: 1,
        username: 'admin',
        full_name: 'System Admin',
        member_id: 'HX-2026-0001',
        role: 'root_admin',
        created_at: new Date().toISOString(),
        avatar_url: null
      },
      token: 'hx_sec_token_9948184818481848',
      verification_url: 'https://club.hackerxploit.org/verify/hx_sec_token_9948184818481848',
      live_status: {
        is_active_event: false,
        active_event_name: null
      }
    }
  } finally {
    loading.value = false
  }
}

const regenerateToken = async () => {
  regenerating.value = true
  try {
    const res = await axios.post('/api/profile/id-card/regenerate')
    if (cardData.value) {
      cardData.value.token = res.data.token
      cardData.value.verification_url = res.data.verification_url
    }
  } catch (err) {
    alert(err.response?.data?.error || 'Token regeneration failed')
  } finally {
    regenerating.value = false
  }
}

onMounted(() => {
  fetchIDCard()
})
</script>
