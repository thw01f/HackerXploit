<template>
  <header class="sticky top-0 z-50 glass-panel border-b border-slate-800 backdrop-blur-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <!-- Logo -->
      <router-link to="/" class="flex items-center space-x-3 group">
        <div class="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
          <span class="font-mono font-bold text-black text-lg">HX</span>
        </div>
        <div>
          <span class="font-bold text-lg text-white tracking-tight group-hover:text-cyan-400 transition-colors">HackerXploit</span>
          <span class="block text-[10px] text-cyan-400 font-mono -mt-1 tracking-widest uppercase">Club Platform</span>
        </div>
      </router-link>

      <!-- Navigation Links -->
      <nav v-if="authStore.isAuthenticated" class="hidden md:flex items-center space-x-6">
        <router-link to="/dashboard" class="text-sm font-medium text-slate-300 hover:text-cyan-400 transition-colors" active-class="text-cyan-400 font-semibold">Dashboard</router-link>
        <router-link to="/academy" class="text-sm font-medium text-slate-300 hover:text-cyan-400 transition-colors" active-class="text-cyan-400 font-semibold">Academy</router-link>
        <router-link to="/competitions" class="text-sm font-medium text-slate-300 hover:text-cyan-400 transition-colors" active-class="text-cyan-400 font-semibold">Competitions</router-link>
        <router-link to="/opportunities" class="text-sm font-medium text-slate-300 hover:text-cyan-400 transition-colors" active-class="text-cyan-400 font-semibold">Opportunities</router-link>
        <a href="http://ctf.hackerxploit.org" target="_blank" class="text-sm font-medium text-purple-400 hover:text-purple-300 flex items-center space-x-1">
          <span>CTF Platform</span>
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
        </a>
        <router-link v-if="authStore.isTeacher" to="/admin" class="text-sm font-medium text-amber-400 hover:text-amber-300" active-class="text-amber-300 font-semibold">Control Center</router-link>
      </nav>

      <!-- Auth Actions -->
      <div class="flex items-center space-x-4">
        <template v-if="authStore.isAuthenticated">
          <router-link to="/profile" class="flex items-center space-x-2 p-1.5 rounded-lg hover:bg-slate-800/60 transition-colors">
            <img :src="authStore.user?.avatar_url || '/uploads/avatars/default.png'" class="w-8 h-8 rounded-full border border-cyan-500/40 object-cover" />
            <div class="hidden sm:block text-left">
              <span class="block text-xs font-semibold text-white leading-tight">{{ authStore.user?.username }}</span>
              <span :class="roleBadgeClass" class="text-[9px] uppercase font-bold">{{ authStore.user?.role }}</span>
            </div>
          </router-link>
          <button @click="handleLogout" class="btn-ghost text-xs py-1.5 px-3">Logout</button>
        </template>
        <template v-else>
          <router-link to="/login" class="btn-ghost text-xs py-1.5 px-4">Sign In</router-link>
          <router-link to="/register" class="btn-neon-cyan text-xs py-1.5 px-4">Join Club</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const roleBadgeClass = computed(() => {
  const role = authStore.user?.role
  if (role === 'root_admin') return 'text-red-400'
  if (role === 'admin') return 'text-purple-400'
  if (role === 'teacher') return 'text-cyan-400'
  return 'text-slate-400'
})

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>
