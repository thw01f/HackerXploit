<template>
  <!-- Sidebar Overlay for mobile -->
  <div
    v-if="mobileOpen"
    class="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
    @click="$emit('close')"
  />

  <!-- Sidebar -->
  <aside
    :class="[
      'fixed top-0 left-0 h-screen z-50 flex flex-col bg-[#0c1117] border-r border-[#1a2332]',
      'transition-all duration-300 ease-in-out shadow-2xl',
      collapsed && !mobileOpen ? 'w-[76px]' : 'w-72',
      mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
    ]"
  >
    <!-- Logo Section -->
    <div class="flex items-center h-20 px-5 border-b border-[#1a2332] flex-shrink-0">
      <router-link to="/" class="flex items-center gap-4 min-w-0">
        <img src="/logo.png" class="w-14 h-14 object-contain flex-shrink-0" alt="HackerXploit" />
        <div v-if="!collapsed || mobileOpen" class="min-w-0">
          <div class="font-extrabold text-lg text-white font-mono leading-tight tracking-tight">
            Hacker<span class="text-red-500">Xploit</span>
          </div>
          <div class="text-xs text-[#9fef00] font-mono font-extrabold tracking-widest uppercase mt-0.5">Cyber Platform</div>
        </div>
      </router-link>
    </div>

    <!-- Nav Items -->
    <nav class="flex-1 overflow-y-auto py-5 px-3 space-y-1">

      <!-- Main Section -->
      <div v-if="!collapsed || mobileOpen" class="px-2 mb-2 mt-1">
        <span class="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest">Main</span>
      </div>

      <NavItem to="/dashboard" :collapsed="collapsed && !mobileOpen" icon="dashboard">
        Dashboard
      </NavItem>

      <NavItem to="/academy" :collapsed="collapsed && !mobileOpen" icon="academy">
        Academy
      </NavItem>

      <NavItem to="/competitions" :collapsed="collapsed && !mobileOpen" icon="competitions">
        Competitions
      </NavItem>

      <NavItem to="/opportunities" :collapsed="collapsed && !mobileOpen" icon="opportunities">
        Opportunities
      </NavItem>

      <NavItem to="/leaderboard" :collapsed="collapsed && !mobileOpen" icon="leaderboard" accent="amber">
        Leaderboard
      </NavItem>

      <!-- Comms Section -->
      <div v-if="!collapsed || mobileOpen" class="px-2 mt-5 mb-2">
        <span class="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest">Comms</span>
      </div>
      <div v-else class="my-3 mx-2 border-t border-[#1a2332]"></div>

      <NavItem to="/inbox" :collapsed="collapsed && !mobileOpen" icon="inbox" :badge="0">
        Inbox
      </NavItem>

      <NavItem v-if="authStore.publicSettings?.general_chat_enabled !== false" to="/chat" :collapsed="collapsed && !mobileOpen" icon="chat">
        General Chat
      </NavItem>


      <!-- Account Section -->
      <div v-if="!collapsed || mobileOpen" class="px-2 mt-5 mb-2">
        <span class="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest">Account</span>
      </div>
      <div v-else class="my-3 mx-2 border-t border-[#1a2332]"></div>

      <NavItem to="/id-card" :collapsed="collapsed && !mobileOpen" icon="idcard" accent="cyan">
        Digital ID Card
      </NavItem>

      <!-- Faculty / Staff Section for Teachers -->
      <template v-if="authStore.isTeacher && !authStore.isAdmin">
        <div v-if="!collapsed || mobileOpen" class="px-2 mt-5 mb-2">
          <span class="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest">Faculty Hub</span>
        </div>
        <div v-else class="my-3 mx-2 border-t border-[#1a2332]"></div>

        <NavItem to="/teacher/students" :collapsed="collapsed && !mobileOpen" icon="roster" accent="cyan">
          Students
        </NavItem>
      </template>

      <!-- Full System Control Section for Admins Only -->
      <template v-if="authStore.isAdmin">
        <div v-if="!collapsed || mobileOpen" class="px-2 mt-5 mb-2">
          <span class="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest">System Admin</span>
        </div>
        <div v-else class="my-3 mx-2 border-t border-[#1a2332]"></div>

        <NavItem to="/teacher/students" :collapsed="collapsed && !mobileOpen" icon="roster">
          Students
        </NavItem>

        <NavItem to="/admin" :collapsed="collapsed && !mobileOpen" icon="control" accent="amber">
          Control Center
        </NavItem>
      </template>

    </nav>

    <!-- Collapse Toggle (desktop) -->
    <button
      @click="$emit('toggle-collapse')"
      class="hidden lg:flex absolute -right-3 top-20 w-6 h-6 rounded-full bg-[#1a2332] border border-[#283548] items-center justify-center text-slate-400 hover:text-[#9fef00] hover:border-[#9fef00]/50 transition-all z-10"
    >
      <svg class="w-3 h-3 transition-transform" :class="collapsed ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/>
      </svg>
    </button>
  </aside>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import NavItem from './NavItem.vue'

defineProps({
  collapsed: { type: Boolean, default: false },
  mobileOpen: { type: Boolean, default: false }
})

defineEmits(['toggle-collapse', 'close'])

const authStore = useAuthStore()
const router = useRouter()

onMounted(() => {
  authStore.fetchPublicSettings()
})

const roleBadgeClass = computed(() => {
  const role = authStore.user?.role
  if (role === 'root_admin') return 'text-red-400'
  if (role === 'admin') return 'text-purple-400'
  if (role === 'teacher') return 'text-[#00f0ff]'
  return 'text-[#9fef00]'
})

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>
