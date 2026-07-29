<template>
  <header class="sticky top-0 z-50 bg-[#0b0e14]/90 border-b border-[#1f293d] backdrop-blur-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      
      <!-- Brand Logo -->
      <router-link to="/" class="flex items-center gap-3.5 min-w-0 group">
        <img src="/logo.png" class="w-14 h-14 object-contain flex-shrink-0 group-hover:scale-105 transition-transform" alt="HackerXploit" />
        <div class="min-w-0">
          <div class="font-extrabold text-base text-white font-mono leading-tight tracking-tight group-hover:text-[#9fef00] transition-colors">
            Hacker<span class="text-red-500">Xploit</span>
          </div>
          <div class="text-[11px] text-[#9fef00] font-mono font-bold tracking-widest uppercase mt-0.5">Cyber Platform</div>
        </div>
      </router-link>


      <!-- Desktop Navigation Links -->
      <nav v-if="authStore.isAuthenticated" class="hidden xl:flex items-center space-x-1">
        <router-link to="/dashboard" class="nav-link" active-class="nav-link-active">Dashboard</router-link>
        <router-link to="/academy" class="nav-link" active-class="nav-link-active">Academy</router-link>
        <router-link to="/competitions" class="nav-link" active-class="nav-link-active">Competitions</router-link>
        <router-link to="/opportunities" class="nav-link" active-class="nav-link-active">Opportunities</router-link>
        <router-link to="/leaderboard" class="nav-link text-amber-400" active-class="nav-link-active">🏆 Ranks</router-link>
        <router-link to="/inbox" class="nav-link" active-class="nav-link-active">Inbox</router-link>
        <router-link to="/chat" class="nav-link" active-class="nav-link-active">Chat</router-link>
        <router-link to="/id-card" class="nav-link text-[#00f0ff]" active-class="nav-link-active">🪪 ID Card</router-link>
        <router-link to="/profile/privacy" class="nav-link" active-class="nav-link-active">Privacy</router-link>
        <router-link v-if="authStore.isTeacher" to="/teacher/students" class="nav-link" active-class="nav-link-active">Roster</router-link>
        <router-link v-if="authStore.isAdmin" to="/admin/backups" class="nav-link" active-class="nav-link-active">Backups</router-link>
        <router-link v-if="authStore.isTeacher" to="/admin" class="nav-link text-amber-400 font-bold" active-class="nav-link-active">Control Center</router-link>
      </nav>

      <!-- Right Header Actions (Notifications, User Profile, Mobile Menu Toggle) -->
      <div class="flex items-center space-x-3">
        <template v-if="authStore.isAuthenticated">
          
          <!-- Notification Bell Dropdown -->
          <div class="relative">
            <button @click="toggleNotifications" class="relative p-2 rounded-lg text-slate-400 hover:text-[#9fef00] hover:bg-[#151f30] transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span v-if="unreadCount > 0" class="absolute top-1 right-1 w-4 h-4 bg-[#9fef00] text-black text-[10px] font-mono font-bold rounded-full flex items-center justify-center animate-pulse">
                {{ unreadCount > 9 ? '9+' : unreadCount }}
              </span>
            </button>

            <!-- Notifications Drawer (Scalable, Large Font for High Visibility) -->
            <div v-if="showNotifications" class="absolute right-0 mt-3 w-96 md:w-[440px] bg-[#0d1420] border-2 border-[#1f293d] rounded-2xl shadow-2xl z-50 overflow-hidden backdrop-blur-xl">
              <div class="px-5 py-4 border-b border-[#1f293d] flex justify-between items-center bg-[#0b0e14]">
                <div class="flex items-center space-x-2">
                  <span class="text-base">🔔</span>
                  <span class="text-sm font-mono font-extrabold text-white uppercase tracking-wider">Notifications</span>
                  <span v-if="unreadCount > 0" class="text-xs font-mono font-bold text-black bg-[#9fef00] px-2 py-0.5 rounded-full">
                    {{ unreadCount }} new
                  </span>
                </div>
                <button @click.stop="markAllRead" class="text-xs font-mono font-bold text-[#9fef00] hover:bg-[#9fef00]/15 bg-[#9fef00]/10 px-3 py-1.5 rounded-lg border border-[#9fef00]/30 transition-all">
                  Mark all read
                </button>
              </div>
              <div class="max-h-96 overflow-y-auto divide-y divide-[#1f293d]">
                <div v-if="notifications.length === 0" class="p-6 text-center text-sm text-slate-400 font-mono">
                  No notifications yet
                </div>
                <div 
                  v-for="n in notifications" 
                  :key="n.id" 
                  @click="handleNotificationClick(n)" 
                  :class="['p-4 transition-all cursor-pointer hover:bg-[#151f30]', n.is_read ? 'bg-[#0d1420]' : 'bg-[#152338] border-l-4 border-[#00f0ff]']"
                >
                  <div class="flex justify-between items-start space-x-2">
                    <h4 class="text-sm font-bold text-white leading-snug">{{ n.title }}</h4>
                    <span class="text-xs font-mono text-slate-400 flex-shrink-0 bg-[#0b0e14] px-2 py-0.5 rounded border border-[#1f293d]">{{ formatDate(n.created_at) }}</span>
                  </div>
                  <p class="text-xs md:text-sm text-slate-300 mt-1.5 leading-relaxed font-sans line-clamp-3">{{ n.message }}</p>
                  <div class="mt-2.5 flex items-center justify-between">
                    <span class="text-xs text-[#00f0ff] font-bold font-mono hover:underline flex items-center space-x-1">
                      <span>View details</span>
                      <span>&rarr;</span>
                    </span>
                    <span v-if="!n.is_read" class="w-2.5 h-2.5 bg-[#00f0ff] rounded-full animate-pulse"></span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- User Profile & Avatar -->
          <router-link to="/profile" class="flex items-center space-x-2.5 p-1.5 rounded-lg hover:bg-[#151f30] transition-colors border border-transparent hover:border-[#1f293d]">
            <img :src="authStore.user?.avatar_url || '/uploads/avatars/default.png'" class="w-8 h-8 rounded-lg border border-[#9fef00]/50 object-cover" />
            <div class="hidden sm:block text-left">
              <span class="block text-xs font-bold text-white leading-tight font-mono">{{ authStore.user?.username }}</span>
              <span :class="roleBadgeClass" class="text-[9px] uppercase font-mono font-bold">{{ authStore.user?.role }}</span>
            </div>
          </router-link>

          <!-- Logout Button -->
          <button @click="handleLogout" class="btn-ghost text-xs py-1.5 px-3 font-mono">Logout</button>
        </template>
        
        <template v-else>
          <router-link to="/login" class="btn-ghost text-xs py-1.5 px-4 font-mono">Sign In</router-link>
          <router-link to="/register" class="btn-htb text-xs py-1.5 px-4 font-mono">Join Club</router-link>
        </template>

        <!-- Mobile Menu Toggle Button -->
        <button v-if="authStore.isAuthenticated" @click="mobileMenuOpen = !mobileMenuOpen" class="xl:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-[#151f30]">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

      </div>
    </div>

    <!-- Mobile Navigation Drawer -->
    <div v-if="mobileMenuOpen && authStore.isAuthenticated" class="xl:hidden border-t border-[#1f293d] bg-[#0b0e14] px-4 pt-3 pb-4 space-y-1">
      <router-link to="/dashboard" @click="mobileMenuOpen = false" class="mobile-nav-link">Dashboard</router-link>
      <router-link to="/academy" @click="mobileMenuOpen = false" class="mobile-nav-link">Academy</router-link>
      <router-link to="/competitions" @click="mobileMenuOpen = false" class="mobile-nav-link">Competitions</router-link>
      <router-link to="/opportunities" @click="mobileMenuOpen = false" class="mobile-nav-link">Opportunities</router-link>
      <router-link to="/leaderboard" @click="mobileMenuOpen = false" class="mobile-nav-link text-amber-400">🏆 Leaderboard</router-link>
      <router-link to="/inbox" @click="mobileMenuOpen = false" class="mobile-nav-link">Inbox</router-link>
      <router-link to="/chat" @click="mobileMenuOpen = false" class="mobile-nav-link">Chat</router-link>
      <router-link to="/id-card" @click="mobileMenuOpen = false" class="mobile-nav-link text-[#00f0ff]">🪪 ID Card</router-link>
      <router-link to="/profile/privacy" @click="mobileMenuOpen = false" class="mobile-nav-link">Privacy</router-link>
      <router-link v-if="authStore.isTeacher" to="/teacher/students" @click="mobileMenuOpen = false" class="mobile-nav-link">Student Roster</router-link>
      <router-link v-if="authStore.isAdmin" to="/admin/backups" @click="mobileMenuOpen = false" class="mobile-nav-link">Backups</router-link>
      <router-link v-if="authStore.isTeacher" to="/admin" @click="mobileMenuOpen = false" class="mobile-nav-link text-amber-400">Control Center</router-link>
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

const mobileMenuOpen = ref(false)
const showNotifications = ref(false)
const notifications = ref([])
const unreadCount = ref(0)

const roleBadgeClass = computed(() => {
  const role = authStore.user?.role
  if (role === 'root_admin') return 'text-red-400'
  if (role === 'admin') return 'text-purple-400'
  if (role === 'teacher') return 'text-[#00f0ff]'
  return 'text-[#9fef00]'
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

const handleNotificationClick = async (n) => {
  if (!n.is_read) {
    n.is_read = true
    if (unreadCount.value > 0) unreadCount.value--
    try {
      await axios.put(`/api/notifications/${n.id}/read`)
    } catch (err) {
      console.error('Failed to mark notification read', err)
    }
  }
  showNotifications.value = false
  if (n.link) {
    router.push(n.link)
  } else {
    router.push('/inbox')
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

<style scoped>
.nav-link {
  font-family: 'Fira Code', monospace;
  font-size: 0.75rem;
  font-weight: 500;
  color: #94a3b8;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: #9fef00;
  background-color: rgba(159, 239, 0, 0.05);
}

.nav-link-active {
  color: #9fef00 !important;
  font-weight: 700 !important;
  background-color: rgba(159, 239, 0, 0.1) !important;
  border: 1px solid rgba(159, 239, 0, 0.3);
}

.mobile-nav-link {
  display: block;
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
  color: #cbd5e1;
  padding: 0.625rem 0.75rem;
  border-radius: 0.375rem;
}

.mobile-nav-link:hover {
  background-color: #151f30;
  color: #9fef00;
}
</style>
