<template>
  <div 
    :class="[
      'relative w-full max-w-sm rounded-xl p-5 text-white overflow-hidden shadow-2xl transition-all duration-300 transform cursor-pointer select-none bg-gradient-to-br',
      theme.borderClass,
      theme.bgGradient
    ]"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
    :style="cardStyle"
  >
    <!-- Background Watermark & Cyber Lines -->
    <div class="absolute inset-0 bg-[radial-gradient(#ffffff_1px,transparent_1px)] [background-size:16px_16px] opacity-10 pointer-events-none"></div>
    
    <!-- Top Lanyard Hole & Header Bar -->
    <div class="relative z-10 flex justify-between items-center mb-4 border-b border-slate-800/80 pb-3">
      <div class="flex items-center space-x-2">
        <div :class="['w-2.5 h-2.5 rounded-full', theme.pingBg]"></div>
        <span :class="['font-mono text-xs tracking-widest font-extrabold uppercase', theme.textAccent]">HACKERXPLOIT</span>
      </div>
      <span :class="['font-mono text-[10px] px-2 py-0.5 rounded border font-bold uppercase', theme.badgeBg]">
        {{ theme.shortRole }} {{ user?.role === 'root_admin' || user?.role === 'admin' || user?.is_root_admin ? 'CREDENTIAL' : (user?.role === 'teacher' ? 'FACULTY' : 'OPERATOR') }}
      </span>
    </div>

    <!-- Main Card Body -->
    <div class="relative z-10 flex items-center space-x-4">
      <!-- User Avatar -->
      <div class="relative flex-shrink-0">
        <img 
          :src="user?.avatar_url || '/uploads/avatars/default.png'" 
          alt="Avatar" 
          :class="['w-16 h-16 rounded-xl object-cover border-2 shadow-lg', 'border-' + theme.hex]"
          :style="{ borderColor: theme.hex }"
          @error="$event.target.src='https://api.dicebear.com/7.x/bottts/svg?seed=' + (user?.username || 'member')"
        />
        <div :class="['absolute -bottom-1 -right-1 text-black text-[9px] font-mono font-bold px-1.5 py-0.2 rounded uppercase shadow', theme.chipBg]">
          {{ user?.is_root_admin || user?.role === 'root_admin' ? 'ROOT' : (user?.role === 'admin' ? 'ADMIN' : user?.role) }}
        </div>
      </div>

      <!-- Info Details -->
      <div class="flex-1 min-w-0">
        <h4 class="font-bold text-base font-mono text-white truncate leading-snug">{{ user?.full_name || user?.username || 'Cyber Member' }}</h4>
        <p :class="['font-mono text-xs font-bold truncate', theme.textAccent]">@{{ user?.username || 'cyber_user' }}</p>
        <p class="font-mono text-[11px] text-slate-400 mt-0.5">BADGE ID: <span class="text-white font-bold">{{ formattedBadgeId }}</span></p>
        
        <!-- Role Badge Display -->
        <div class="mt-1.5 inline-flex items-center space-x-1.5 px-2 py-0.5 rounded border text-[10px] font-mono font-extrabold uppercase shadow" :class="theme.badgeBg">
          <span>{{ theme.title }}</span>
        </div>
      </div>
    </div>

    <!-- Bottom Footer / Holographic QR Code -->
    <div class="relative z-10 mt-4 pt-3 flex justify-between items-end border-t border-slate-800/80">
      <div>
        <span class="block text-[9px] text-slate-400 font-mono uppercase">Status</span>
        <span :class="['inline-flex items-center text-xs font-bold font-mono', theme.textAccent]">
          {{ user?.role === 'root_admin' || user?.role === 'admin' || user?.is_root_admin ? 'SYSTEM GOVERNANCE' : (user?.role === 'teacher' ? 'FACULTY MEMBER' : 'ACTIVELY PARTICIPATING') }}
        </span>
      </div>
      <div class="flex items-center space-x-2">
        <div class="text-right">
          <span class="block text-[9px] text-slate-500 font-mono">CYCLE</span>
          <span class="text-[10px] text-slate-300 font-mono">2026-2027</span>
        </div>
        <!-- QR Code Graphic -->
        <div class="w-9 h-9 bg-white p-1 rounded border shadow" :style="{ borderColor: theme.hex }">
          <svg viewBox="0 0 24 24" class="w-full h-full text-black fill-current">
            <path d="M2,2H10V10H2V2M4,4V8H8V4H4M14,2H22V10H14V2M16,4V8H20V4H16M2,14H10V22H2V14M4,16V20H8V16H4M14,14H17V17H14V14M19,14H22V17H19V14M14,19H17V22H14V19M19,19H22V22H19V19Z" />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  user: Object
})

const formattedBadgeId = computed(() => {
  const u = props.user
  if (!u) return 'HX-STU-0001'
  if (u.badge_id && (u.badge_id.startsWith('HX-ROOT-') || u.badge_id.startsWith('HX-ADM-') || u.badge_id.startsWith('HX-FAC-') || u.badge_id.startsWith('HX-STU-'))) {
    return u.badge_id
  }
  const numStr = String(u.id || 1).padStart(4, '0')
  if (u.is_root_admin || u.role === 'root_admin') return `HX-ROOT-${numStr}`
  if (u.role === 'admin') return `HX-ADM-${numStr}`
  if (u.role === 'teacher' || u.role === 'teacher_admin') return `HX-FAC-${numStr}`
  return `HX-STU-${u.student_id || numStr}`
})

const rotateX = ref(0)
const rotateY = ref(0)

const handleMouseMove = (e) => {
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX - rect.left - rect.width / 2
  const y = e.clientY - rect.top - rect.height / 2
  rotateX.value = -y / 12
  rotateY.value = x / 12
}

const handleMouseLeave = () => {
  rotateX.value = 0
  rotateY.value = 0
}

const cardStyle = computed(() => ({
  transform: `perspective(1000px) rotateX(${rotateX.value}deg) rotateY(${rotateY.value}deg)`
}))

const theme = computed(() => {
  if (props.user?.role === 'root_admin' || props.user?.role === 'admin' || props.user?.is_root_admin) {
    return {
      title: props.user?.is_root_admin || props.user?.role === 'root_admin' ? 'ROOT ADMINISTRATOR' : 'PLATFORM ADMIN',
      shortRole: 'ADMIN',
      hex: '#ff003c',
      borderClass: 'border-red-600/90 shadow-[0_0_20px_rgba(255,0,60,0.3)]',
      bgGradient: 'from-[#2b040a] via-[#1a0206] to-[#0d0103]',
      badgeBg: 'bg-red-950/80 text-red-400 border-red-600/50',
      textAccent: 'text-red-500',
      pingBg: 'bg-red-600',
      chipBg: 'bg-red-600 text-white'
    }
  }

  if (props.user?.role === 'teacher' || props.user?.role === 'teacher_admin') {
    return {
      title: 'FACULTY / TEACHER',
      shortRole: 'TEACHER',
      hex: '#fbbf24',
      borderClass: 'border-amber-400/80 shadow-[0_0_20px_rgba(251,191,36,0.25)]',
      bgGradient: 'from-[#1c1404] via-[#120d02] to-[#050301]',
      badgeBg: 'bg-amber-400/20 text-amber-300 border-amber-400/40',
      textAccent: 'text-amber-400',
      pingBg: 'bg-amber-400',
      chipBg: 'bg-amber-400 text-black'
    }
  }

  const role = props.user?.specialization_role || 'Penetration Tester'
  if (role === 'Penetration Tester') {
    return {
      title: 'PENETRATION TESTER',
      shortRole: 'PENTESTER',
      hex: '#9fef00',
      borderClass: 'border-[#9fef00]/80 shadow-[0_0_20px_rgba(159,239,0,0.25)]',
      bgGradient: 'from-[#0d170f] via-[#09120b] to-[#040805]',
      badgeBg: 'bg-[#9fef00]/15 text-[#9fef00] border-[#9fef00]/40',
      textAccent: 'text-[#9fef00]',
      pingBg: 'bg-[#9fef00]',
      chipBg: 'bg-[#9fef00] text-black'
    }
  } else if (role === 'Security Engineer') {
    return {
      title: 'SECURITY ENGINEER',
      shortRole: 'ENGINEER',
      hex: '#ffb700',
      borderClass: 'border-[#ffb700]/80 shadow-[0_0_20px_rgba(255,183,0,0.25)]',
      bgGradient: 'from-[#211508] via-[#140c04] to-[#070401]',
      badgeBg: 'bg-[#ffb700]/15 text-[#ffb700] border-[#ffb700]/40',
      textAccent: 'text-[#ffb700]',
      pingBg: 'bg-[#ffb700]',
      chipBg: 'bg-[#ffb700] text-black'
    }
  } else {
    // Security Analyst
    return {
      title: 'SECURITY ANALYST',
      shortRole: 'ANALYST',
      hex: '#00f0ff',
      borderClass: 'border-[#00f0ff]/80 shadow-[0_0_20px_rgba(0,240,255,0.25)]',
      bgGradient: 'from-[#09192b] via-[#05111d] to-[#02080f]',
      badgeBg: 'bg-[#00f0ff]/15 text-[#00f0ff] border-[#00f0ff]/40',
      textAccent: 'text-[#00f0ff]',
      pingBg: 'bg-[#00f0ff]',
      chipBg: 'bg-[#00f0ff] text-black'
    }
  }
})
</script>
