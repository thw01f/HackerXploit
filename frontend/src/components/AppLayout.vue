<template>
  <div class="min-h-screen bg-[#0b0e14] text-slate-100 flex transition-colors duration-300">

    <!-- Sidebar -->
    <Sidebar
      :collapsed="sidebarCollapsed"
      :mobile-open="mobileSidebarOpen"
      @toggle-collapse="sidebarCollapsed = !sidebarCollapsed"
      @close="mobileSidebarOpen = false"
    />

    <!-- Main Content Area -->
    <div
      :class="[
        'flex-1 flex flex-col min-h-screen transition-all duration-300',
        sidebarCollapsed ? 'lg:ml-[76px]' : 'lg:ml-72'
      ]"
    >
      <!-- Top Bar Header -->
      <header ref="headerRef" class="sticky top-0 z-30 h-18 bg-[#0c1117]/95 border-b border-[#1a2332] backdrop-blur-md flex items-center justify-between px-4 sm:px-8 gap-6 py-2">

        <!-- Left: Mobile Hamburger + Explore Dropdown -->
        <div class="flex items-center gap-4">
          <!-- Mobile Hamburger -->
          <button
            @click="mobileSidebarOpen = true"
            class="lg:hidden p-2 rounded-xl text-slate-400 hover:text-white hover:bg-[#151f30] transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>

          <!-- OffSec Explore Dropdown Menu -->
          <div class="relative">
            <button
              @click="showExploreMenu = !showExploreMenu"
              class="flex items-center gap-2.5 px-4 py-2 rounded-xl bg-[#151f30] border border-[#1a2332] text-sm font-mono font-extrabold text-white hover:border-[#9fef00]/60 transition-all shadow-md"
            >
              <svg class="w-4 h-4 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"/>
              </svg>
              <span>Explore</span>
              <svg class="w-4 h-4 text-slate-400 transition-transform" :class="showExploreMenu ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>

            <!-- Explore Flyout Menu with SVG Logos -->
            <div
              v-if="showExploreMenu"
              class="absolute left-0 top-full mt-2 w-64 bg-[#111927] border border-[#1a2332] rounded-2xl shadow-2xl z-50 p-2.5 space-y-1 font-mono text-sm"
            >
              <router-link to="/academy" @click="showExploreMenu = false" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-slate-200 hover:text-[#9fef00] hover:bg-[#151f30] transition-colors font-semibold">
                <svg class="w-5 h-5 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/></svg>
                <span>Academy Courses</span>
              </router-link>

              <router-link to="/competitions" @click="showExploreMenu = false" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-slate-200 hover:text-amber-400 hover:bg-[#151f30] transition-colors font-semibold">
                <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"/></svg>
                <span>CTF & Competitions</span>
              </router-link>

              <router-link to="/opportunities" @click="showExploreMenu = false" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-slate-200 hover:text-[#00f0ff] hover:bg-[#151f30] transition-colors font-semibold">
                <svg class="w-5 h-5 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
                <span>Opportunities</span>
              </router-link>

              <router-link to="/leaderboard" @click="showExploreMenu = false" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-slate-200 hover:text-amber-300 hover:bg-[#151f30] transition-colors font-semibold">
                <svg class="w-5 h-5 text-amber-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                <span>Global Leaderboard</span>
              </router-link>
            </div>
          </div>
        </div>



        <!-- Right: Notifications & Profile Trigger Button -->
        <div class="flex items-center gap-4">

          <!-- Notification Bell (Scaled Up) -->
          <div class="relative">
            <button
              @click="toggleNotifications"
              class="p-3 rounded-xl text-slate-300 hover:text-[#9fef00] hover:bg-[#151f30] transition-colors relative flex items-center justify-center"
              title="Notifications"
            >
              <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
              </svg>
              <span v-if="unreadCount > 0" class="absolute top-0.5 right-0.5 w-6 h-6 bg-[#9fef00] text-black text-xs font-extrabold font-mono rounded-full flex items-center justify-center shadow-lg border border-black">
                {{ unreadCount > 9 ? '9+' : unreadCount }}
              </span>
            </button>

            <!-- Notifications Dropdown (High Scaled Viewport).
                 Below sm: fixed + inset-x-4 so width/position are relative to
                 the viewport, not this small bell button - a 384-440px-wide
                 dropdown absolutely positioned against a button that isn't
                 even flush with the screen edge (the profile button sits to
                 its right) overflowed badly off-screen on real phone widths
                 (~360-414px), often clipped unreachable to the left.
                 handleOutsideClick still works unchanged: it checks DOM
                 containment within headerRef, not visual position, and this
                 element stays inside <header> in the DOM either way.
                 sm and up: reverts to the original anchored dropdown. -->
            <div v-if="showNotifications" class="fixed inset-x-4 top-20 sm:absolute sm:inset-x-auto sm:top-full sm:right-0 sm:mt-3 sm:w-96 md:w-[440px] bg-[#111927] border-2 border-[#1a2332] rounded-2xl shadow-2xl z-50 overflow-hidden border-t-4 border-t-[#9fef00]">
              <div class="px-6 py-4 border-b border-[#1a2332] flex justify-between items-center bg-[#0c1117]">
                <div class="flex items-center gap-2.5">
                  <svg class="w-5 h-5 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
                  </svg>
                  <span class="text-base font-mono font-extrabold text-white uppercase tracking-wider">Notifications</span>
                </div>
                <button @click="markAllRead" class="text-xs text-[#9fef00] hover:underline font-mono font-extrabold px-3 py-1 rounded-lg bg-[#9fef00]/10 border border-[#9fef00]/30 transition-all">Mark all read</button>
              </div>
              <div class="max-h-[50vh] sm:max-h-[460px] overflow-y-auto divide-y divide-[#1a2332]">
                <div v-if="notifications.length === 0" class="p-8 text-center text-sm text-slate-400 font-mono">
                  No notifications yet
                </div>
                <div v-for="n in notifications" :key="n.id" :class="['p-5 transition-colors', n.is_read ? 'bg-[#111927]' : 'bg-[#151f30] border-l-4 border-[#9fef00]']">
                  <div class="flex justify-between items-start gap-4">
                    <h4 class="text-sm font-extrabold text-white leading-snug">{{ n.title }}</h4>
                    <span class="text-xs font-mono text-slate-400 flex-shrink-0">{{ formatDate(n.created_at) }}</span>
                  </div>
                  <p class="text-xs text-slate-300 mt-2 leading-relaxed font-sans">{{ n.message }}</p>
                  <router-link v-if="n.link" :to="n.link" @click="showNotifications = false" class="inline-flex items-center gap-1 mt-3 text-xs text-[#9fef00] hover:underline font-mono font-extrabold">
                    <span>View details</span>
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                  </router-link>
                </div>
              </div>
            </div>
          </div>

          <!-- User Profile Trigger Button -->
          <div class="relative">
            <button
              @click="showProfileDrawer = !showProfileDrawer"
              class="flex items-center gap-3 px-3 py-1.5 rounded-xl bg-[#151f30] border border-[#1a2332] hover:border-[#9fef00]/60 transition-all shadow-md"
            >
              <img :src="authStore.user?.avatar_url || defaultAvatarSvg" @error="(e) => e.target.src = defaultAvatarSvg" class="w-9 h-9 rounded-lg border border-[#9fef00]/50 object-cover" />
              <span class="text-sm font-mono font-extrabold text-white max-w-[120px] truncate hidden sm:inline">{{ authStore.user?.username }}</span>
              <svg class="w-4 h-4 text-slate-400 transition-transform" :class="showProfileDrawer ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>

            <!-- Profile Drawer Panel (Only My Profile kept) -->
            <div
              v-if="showProfileDrawer"
              class="absolute right-0 top-full mt-3 w-80 bg-[#111927] border border-[#1a2332] rounded-2xl shadow-2xl z-50 p-6 space-y-6 font-mono text-sm border-t-4 border-t-[#9fef00]"
            >
              <!-- User Name Header -->
              <div class="flex items-center space-x-3 pb-2 border-b border-[#1a2332]">
                <img :src="authStore.user?.avatar_url || defaultAvatarSvg" @error="(e) => e.target.src = defaultAvatarSvg" class="w-12 h-12 rounded-xl border border-[#9fef00] object-cover flex-shrink-0" />
                <div class="min-w-0">
                  <h3 class="text-base font-extrabold text-white truncate leading-tight">
                    {{ authStore.user?.full_name || authStore.user?.username }}
                  </h3>
                  <span class="text-xs text-[#9fef00] uppercase font-bold tracking-wider block mt-0.5">
                    {{ authStore.user?.role?.replace('_', ' ') }}
                  </span>
                </div>
              </div>

              <!-- ACCOUNT Links -->
              <div class="space-y-2">
                <span class="text-xs text-[#9fef00] uppercase tracking-widest block font-extrabold mb-3">Account</span>
                
                <router-link to="/settings" @click="showProfileDrawer = false" class="flex items-center gap-3.5 text-slate-200 hover:text-[#9fef00] hover:bg-[#151f30] transition-all py-2.5 px-3 rounded-xl font-semibold">
                  <svg class="w-5 h-5 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                  <span>Settings</span>
                </router-link>

                <router-link to="/id-card" @click="showProfileDrawer = false" class="flex items-center gap-3.5 text-slate-200 hover:text-[#00f0ff] hover:bg-[#151f30] transition-all py-2.5 px-3 rounded-xl font-semibold">
                  <svg class="w-5 h-5 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2"/></svg>
                  <span>Digital ID Card</span>
                </router-link>
              </div>

              <!-- HELP Links -->
              <div class="space-y-2 border-t border-[#1a2332] pt-4">
                <span class="text-xs text-slate-400 uppercase tracking-widest block font-extrabold mb-3">Help</span>

                <router-link to="/about" @click="showProfileDrawer = false" class="flex items-center gap-3.5 text-slate-200 hover:text-white hover:bg-[#151f30] transition-all py-2.5 px-3 rounded-xl font-semibold">
                  <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                  <span>About</span>
                </router-link>

                <router-link to="/contact" @click="showProfileDrawer = false" class="flex items-center gap-3.5 text-slate-200 hover:text-amber-400 hover:bg-[#151f30] transition-all py-2.5 px-3 rounded-xl font-semibold">
                  <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
                  <span>Contact & Bug Report</span>
                </router-link>
              </div>


              <!-- DISPLAY OPTIONS -->
              <div class="space-y-3 border-t border-[#1a2332] pt-4">
                <span class="text-xs text-slate-400 uppercase tracking-widest block font-extrabold">Theme Option</span>
                
                <!-- Dark Mode Toggle Switch -->
                <div class="flex items-center justify-between py-1">
                  <span class="text-slate-200 text-sm font-semibold flex items-center gap-2">
                    <svg v-if="theme.isDark.value" class="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
                    <svg v-else class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
                    <span>Dark Mode</span>
                  </span>
                  <button
                    @click="theme.toggleTheme()"
                    :class="[
                      'w-12 h-6 rounded-full p-1 transition-colors flex items-center',
                      theme.isDark.value ? 'bg-[#9fef00]' : 'bg-[#334155]'
                    ]"
                  >
                    <div
                      :class="[
                        'w-4 h-4 rounded-full bg-black transition-transform',
                        theme.isDark.value ? 'translate-x-6' : 'translate-x-0 bg-white'
                      ]"
                    />
                  </button>
                </div>
              </div>

              <!-- Action Sign Out Button (Full Width) -->
              <div class="border-t border-[#1a2332] pt-4">
                <button
                  @click="handleLogout"
                  class="w-full py-3 px-4 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/40 text-rose-400 hover:text-rose-300 font-extrabold text-sm transition-all flex items-center justify-center gap-2 shadow"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
                  <span>Sign Out</span>
                </button>
              </div>

            </div>
          </div>

        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 p-4 sm:p-6 lg:p-8">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useTheme } from '../stores/theme'
import { usePreferences } from '../stores/preferences'
import Sidebar from './Sidebar.vue'

const authStore = useAuthStore()
const theme = useTheme()
const prefs = usePreferences()
const router = useRouter()

const headerRef = ref(null)
const sidebarCollapsed = ref(false)
const mobileSidebarOpen = ref(false)
const showExploreMenu = ref(false)
const showProfileDrawer = ref(false)
const searchQuery = ref('')

const showNotifications = ref(false)
const notifications = ref([])
const unreadCount = ref(0)

const defaultAvatarSvg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'><rect width='100' height='100' fill='%230b0e14'/><circle cx='50' cy='38' r='20' fill='%231f293d' stroke='%239fef00' stroke-width='2'/><path d='M20,85 C20,62 35,55 50,55 C65,55 80,62 80,85 Z' fill='%231f293d' stroke='%239fef00' stroke-width='2'/></svg>"

const handleOutsideClick = (e) => {
  if (headerRef.value && !headerRef.value.contains(e.target)) {
    showExploreMenu.value = false
    showNotifications.value = false
    showProfileDrawer.value = false
  }
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/search', query: { q: searchQuery.value.trim() } })
  }
}

const handleLogout = async () => {
  showProfileDrawer.value = false
  await authStore.logout()
  router.push('/login')
}

const fetchNotifications = async () => {
  try {
    const res = await axios.get('/api/notifications')
    notifications.value = res.data.notifications || []
    unreadCount.value = res.data.unread_count || 0
  } catch {}
}

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
  if (showNotifications.value) fetchNotifications()
}

const markAllRead = async () => {
  try {
    await axios.post('/api/notifications/read-all')
    notifications.value.forEach(n => n.is_read = true)
    unreadCount.value = 0
  } catch {}
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: prefs.is12h.value })
}

onMounted(() => {
  fetchNotifications()
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})
</script>
