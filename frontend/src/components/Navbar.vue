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
      <nav v-if="authStore.isAuthenticated" class="hidden lg:flex items-center space-x-5">
        <router-link to="/dashboard" class="text-xs font-medium text-slate-300 hover:text-cyan-400 transition-colors" active-class="text-cyan-400 font-semibold">Dashboard</router-link>
        <router-link to="/academy" class="text-xs font-medium text-slate-300 hover:text-cyan-400 transition-colors" active-class="text-cyan-400 font-semibold">Academy</router-link>
        <router-link to="/competitions" class="text-xs font-medium text-slate-300 hover:text-cyan-400 transition-colors" active-class="text-cyan-400 font-semibold">Competitions</router-link>
        <router-link to="/opportunities" class="text-xs font-medium text-slate-300 hover:text-cyan-400 transition-colors" active-class="text-cyan-400 font-semibold">Opportunities</router-link>
        <router-link to="/leaderboard" class="text-xs font-medium text-amber-400 hover:text-amber-300 transition-colors" active-class="text-amber-300 font-semibold">🏆 Ranks</router-link>
        <router-link to="/inbox" class="text-xs font-medium text-slate-300 hover:text-cyan-400 transition-colors" active-class="text-cyan-400 font-semibold">Inbox</router-link>
        <router-link to="/chat" class="text-xs font-medium text-slate-300 hover:text-cyan-400 transition-colors" active-class="text-cyan-400 font-semibold">Chat</router-link>
        <router-link v-if="authStore.isTeacher" to="/teacher/students" class="text-xs font-medium text-slate-300 hover:text-cyan-400 transition-colors" active-class="text-cyan-400 font-semibold">Roster</router-link>
        <router-link v-if="authStore.isTeacher" to="/admin" class="text-xs font-medium text-amber-400 hover:text-amber-300" active-class="text-amber-300 font-semibold">Control Center</router-link>
      </nav>

      <!-- Auth & Notification Actions -->
      <div class="flex items-center space-x-3">
        <template v-if="authStore.isAuthenticated">
          <!-- Notification Bell -->
          <div class="relative">
            <button @click="toggleNotifications" class="relative p-2 rounded-lg text-slate-400 hover:text-cyan-400 hover:bg-slate-800/60 transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span v-if="unreadCount > 0" class="absolute top-1 right-1 w-4 h-4 bg-cyan-500 text-black text-[10px] font-bold rounded-full flex items-center justify-center animate-pulse">
                {{ unreadCount > 9 ? '9+' : unreadCount }}
              </span>
            </button>

            <!-- Notifications Dropdown -->
            <div v-if="showNotifications" class="absolute right-0 mt-2 w-80 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl z-50 overflow-hidden">
              <div class="px-4 py-3 border-b border-slate-800 flex justify-between items-center bg-slate-950">
                <span class="text-xs font-bold text-white uppercase tracking-wider">Notifications</span>
                <button @click="markAllRead" class="text-[11px] text-cyan-400 hover:underline">Mark all read</button>
              </div>
              <div class="max-h-80 overflow-y-auto divide-y divide-slate-800/60">
                <div v-if="notifications.length === 0" class="p-4 text-center text-xs text-slate-500">
                  No notifications yet
                </div>
                <div v-for="n in notifications" :key="n.id" :class="['p-3 transition-colors', n.is_read ? 'bg-slate-900/50' : 'bg-slate-800/40 border-l-2 border-cyan-400']">
                  <div class="flex justify-between items-start">
                    <h4 class="text-xs font-semibold text-white">{{ n.title }}</h4>
                    <span class="text-[10px] text-slate-500">{{ formatDate(n.created_at) }}</span>
                  </div>
                  <p class="text-xs text-slate-300 mt-1">{{ n.message }}</p>
                  <router-link v-if="n.link" :to="n.link" @click="showNotifications = false" class="inline-block mt-1 text-[11px] text-cyan-400 hover:underline">
                    View details &rarr;
                  </router-link>
                </div>
              </div>
            </div>
          </div>

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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const authStore = useAuthStore()
const router = useRouter()

const showNotifications = ref(false)
const notifications = ref([])
const unreadCount = ref(0)

const roleBadgeClass = computed(() => {
  const role = authStore.user?.role
  if (role === 'root_admin') return 'text-red-400'
  if (role === 'admin') return 'text-purple-400'
  if (role === 'teacher') return 'text-cyan-400'
  return 'text-slate-400'
})

const fetchNotifications = async () => {
  if (!authStore.isAuthenticated) return
  try {
    const res = await axios.get('/api/notifications')
    notifications.value = res.data.notifications || []
    unreadCount.value = res.data.unread_count || 0
  } catch (err) {
    console.error('Failed to load notifications', err)
  }
}

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
  if (showNotifications.value) {
    fetchNotifications()
  }
}

const markAllRead = async () => {
  try {
    await axios.post('/api/notifications/read-all')
    notifications.value.forEach(n => n.is_read = true)
    unreadCount.value = 0
  } catch (err) {
    console.error('Failed to mark notifications read', err)
  }
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchNotifications()
  }
})
</script>
