<template>
  <div 
    class="relative w-full max-w-sm h-56 rounded-2xl p-6 text-white overflow-hidden shadow-2xl transition-all duration-500 transform hover:scale-105 hover:rotate-1 border border-cyan-500/30 glass-panel-cyan cursor-pointer select-none"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
    :style="cardStyle"
  >
    <!-- Background Watermark & Cyber Lines -->
    <div class="absolute inset-0 bg-gradient-to-br from-cyan-900/20 via-slate-900/80 to-purple-900/30 pointer-events-none"></div>
    <div class="absolute -right-8 -bottom-8 w-32 h-32 bg-cyan-500/10 rounded-full blur-2xl pointer-events-none"></div>
    
    <!-- Top Header Bar -->
    <div class="relative z-10 flex justify-between items-center mb-4 border-b border-cyan-500/20 pb-3">
      <div class="flex items-center space-x-2">
        <div class="w-3 h-3 rounded-full bg-cyan-400 animate-pulse"></div>
        <span class="font-mono text-xs tracking-widest text-cyan-400 font-bold uppercase">HACKERXPLOIT CLUB</span>
      </div>
      <span class="font-mono text-[10px] bg-cyan-950 text-cyan-300 px-2 py-0.5 rounded border border-cyan-500/40">VERIFIED MEMBER</span>
    </div>

    <!-- Main Card Body -->
    <div class="relative z-10 flex items-center space-x-4">
      <!-- User Avatar -->
      <div class="relative">
        <img 
          :src="user?.avatar_url || '/uploads/avatars/default.png'" 
          alt="Avatar" 
          class="w-16 h-16 rounded-xl object-cover border-2 border-cyan-400/60 shadow-lg"
          @error="$event.target.src='https://api.dicebear.com/7.x/bottts/svg?seed=' + (user?.username || 'member')"
        />
        <div class="absolute -bottom-1 -right-1 bg-cyan-500 text-black text-[9px] font-bold px-1.5 py-0.2 rounded-full uppercase">
          {{ user?.role === 'root_admin' ? 'ROOT' : user?.role }}
        </div>
      </div>

      <!-- Info Details -->
      <div class="flex-1 min-w-0">
        <h4 class="font-bold text-lg text-white truncate leading-snug">{{ user?.full_name || 'Cyber Member' }}</h4>
        <p class="font-mono text-xs text-cyan-300/80 truncate">@{{ user?.username || 'cyber_user' }}</p>
        <p class="font-mono text-[11px] text-slate-400 mt-1">ID: <span class="text-cyan-400 font-medium">{{ user?.student_id || 'HX-2026-904' }}</span></p>
      </div>
    </div>

    <!-- Bottom Footer / Holographic QR Code -->
    <div class="relative z-10 mt-4 pt-3 flex justify-between items-end border-t border-slate-800">
      <div>
        <span class="block text-[10px] text-slate-400 font-mono">STATUS</span>
        <span class="inline-flex items-center text-xs font-semibold text-emerald-400 font-mono">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-ping"></span>
          ACTIVE
        </span>
      </div>
      <div class="flex items-center space-x-2">
        <div class="text-right">
          <span class="block text-[9px] text-slate-500 font-mono">ISSUED</span>
          <span class="text-[10px] text-slate-300 font-mono">FALL 2026</span>
        </div>
        <!-- Simulated QR Code SVG -->
        <div class="w-9 h-9 bg-white/90 p-1 rounded border border-cyan-400/50">
          <svg viewBox="0 0 24 24" class="w-full h-full text-slate-900 fill-current">
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

const rotateX = ref(0)
const rotateY = ref(0)

const handleMouseMove = (e) => {
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX - rect.left - rect.width / 2
  const y = e.clientY - rect.top - rect.height / 2
  rotateX.value = -y / 10
  rotateY.value = x / 10
}

const handleMouseLeave = () => {
  rotateX.value = 0
  rotateY.value = 0
}

const cardStyle = computed(() => ({
  transform: `perspective(1000px) rotateX(${rotateX.value}deg) rotateY(${rotateY.value}deg)`
}))
</script>
