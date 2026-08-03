<template>
  <div class="space-y-8">

      <!-- Announcements -->
      <div
        v-for="ann in visibleAnnouncements"
        :key="ann.id"
        class="glass-panel p-4 flex flex-col sm:flex-row items-center justify-between gap-4 border-l-4 border-l-[#9fef00] relative"
      >
        <div class="flex items-center space-x-3">
          <span class="px-2.5 py-0.5 rounded bg-[#151f30] border border-[#9fef00]/30 text-[#9fef00] font-mono text-xs font-bold uppercase shrink-0">ANNOUNCEMENT</span>
          <p class="text-sm text-slate-200 font-medium">{{ ann.message }}</p>
        </div>
        <div class="flex items-center space-x-3 w-full sm:w-auto justify-between sm:justify-end">
          <a v-if="ann.link && ann.button_label" :href="ann.link" target="_blank" class="btn-htb text-xs py-1.5 px-4 whitespace-nowrap font-mono">
            {{ ann.button_label }} &rarr;
          </a>
          <button @click="dismissedAnnouncementIds.add(ann.id)" class="px-2 py-0.5 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors font-mono text-base font-bold" title="Close Banner">
            &times;
          </button>
        </div>
      </div>

      <!-- Main Dashboard Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

        <!-- Left 2 Columns: role-specific content -->
        <div class="lg:col-span-2 space-y-8">

          <!-- Welcome Banner (role-aware) -->
          <div class="glass-panel-htb p-8 relative overflow-hidden bg-[#111927]">
            <div class="relative z-10">
              <span class="text-xs font-mono text-[#9fef00] font-bold uppercase tracking-widest">{{ banner.label }}</span>
              <h2 class="text-2xl sm:text-3xl font-extrabold text-white mt-1 font-mono">Welcome back, {{ authStore.user?.full_name || authStore.user?.username }}!</h2>
              <p class="text-slate-300 text-sm mt-2 max-w-xl leading-relaxed">
                {{ banner.description }}
              </p>

              <div class="flex flex-wrap items-center gap-4 mt-6">
                <router-link :to="banner.primaryCta.to" class="btn-htb text-xs py-2.5 px-5 font-mono">{{ banner.primaryCta.label }}</router-link>
                <a v-if="dashboardRole === 'member'" :href="ctfdUrl" target="_blank" class="btn-ghost text-xs py-2.5 px-5 font-mono text-[#9fef00] border-[#9fef00]/30">CTF Arena</a>
                <router-link
                  v-for="cta in banner.secondaryCtas"
                  :key="cta.label"
                  :to="cta.to"
                  class="btn-ghost text-xs py-2.5 px-5 font-mono"
                  :class="cta.class || ''"
                >
                  {{ cta.label }}
                </router-link>
              </div>
            </div>
          </div>

          <!-- Quick Stats Cards (role-aware) -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div v-for="stat in quickStats" :key="stat.label" class="glass-panel p-5 text-center">
              <span class="block text-2xl font-extrabold font-mono" :class="stat.color">{{ stat.value }}</span>
              <span class="text-[11px] text-slate-400 uppercase font-mono mt-1 block">{{ stat.label }}</span>
            </div>
          </div>

          <!-- Member: Featured Academy Modules -->
          <div v-if="dashboardRole === 'member'" class="glass-panel p-6 space-y-4">
            <div class="flex justify-between items-center border-b border-[#1f293d] pb-3">
              <h3 class="text-base font-bold text-white font-mono uppercase">Featured Academy Modules</h3>
              <router-link to="/academy" class="text-xs text-[#9fef00] hover:underline font-mono">View Catalog &rarr;</router-link>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div v-for="course in clubStore.courses.slice(0, 2)" :key="course.id" class="p-4 rounded-xl bg-[#090d16] border border-[#1f293d] hover:border-[#9fef00]/40 transition-all flex flex-col justify-between">
                <div>
                  <div class="flex justify-between items-center mb-2">
                    <span class="text-[10px] font-mono uppercase bg-[#151f30] text-[#9fef00] border border-[#9fef00]/30 px-2 py-0.5 rounded">{{ course.difficulty || 'Intermediate' }}</span>
                    <span class="text-[10px] font-mono text-slate-400">{{ course.modules_count || 0 }} Modules</span>
                  </div>
                  <h4 class="font-bold text-white text-sm font-mono">{{ course.title }}</h4>
                  <p class="text-slate-400 text-xs mt-1.5 line-clamp-2 leading-relaxed">{{ course.description }}</p>
                </div>
                <router-link :to="`/academy/course/${course.slug}`" class="inline-block mt-4 text-xs text-[#9fef00] font-mono font-semibold hover:underline">
                  Start Course &rarr;
                </router-link>
              </div>
            </div>
          </div>

          <!-- Teacher: My Learning Paths -->
          <div v-if="dashboardRole === 'teacher'" class="glass-panel p-6 space-y-4">
            <div class="flex justify-between items-center border-b border-[#1f293d] pb-3">
              <h3 class="text-base font-bold text-white font-mono uppercase">My Learning Paths</h3>
              <router-link to="/academy/write" class="text-xs text-[#9fef00] hover:underline font-mono">Content Studio &rarr;</router-link>
            </div>
            <div v-if="myCourses.length" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div v-for="course in myCourses.slice(0, 4)" :key="course.id" class="p-4 rounded-xl bg-[#090d16] border border-[#1f293d] hover:border-[#9fef00]/40 transition-all flex flex-col justify-between">
                <div>
                  <div class="flex justify-between items-center mb-2">
                    <span class="text-[10px] font-mono uppercase bg-[#151f30] text-[#9fef00] border border-[#9fef00]/30 px-2 py-0.5 rounded">{{ course.difficulty || 'Intermediate' }}</span>
                    <span class="text-[10px] font-mono text-slate-400">{{ course.modules_count || 0 }} Modules</span>
                  </div>
                  <h4 class="font-bold text-white text-sm font-mono">{{ course.title }}</h4>
                  <p class="text-slate-400 text-xs mt-1.5 line-clamp-2 leading-relaxed">{{ course.description }}</p>
                </div>
                <router-link :to="`/academy/course/${course.slug}`" class="inline-block mt-4 text-xs text-[#9fef00] font-mono font-semibold hover:underline">
                  Manage Path &rarr;
                </router-link>
              </div>
            </div>
            <p v-else class="text-xs text-slate-500 text-center py-6">
              You haven't authored any Learning Paths yet.
              <router-link to="/academy/write" class="text-[#9fef00] hover:underline">Create one in the Content Studio &rarr;</router-link>
            </p>
          </div>

          <!-- Teacher + Admin: Pending Approvals -->
          <div v-if="dashboardRole !== 'member'" class="glass-panel p-6 space-y-4">
            <div class="flex justify-between items-center border-b border-[#1f293d] pb-3">
              <h3 class="text-base font-bold text-white font-mono uppercase">Pending Approvals</h3>
              <span v-if="pendingUsers.length" class="text-[11px] font-mono text-amber-400 bg-amber-400/10 px-2.5 py-0.5 rounded border border-amber-400/20">{{ pendingUsers.length }} waiting</span>
            </div>
            <div v-if="pendingUsers.length" class="space-y-3">
              <div v-for="u in pendingUsers.slice(0, 5)" :key="u.id" class="flex items-center justify-between p-3 rounded-xl bg-[#090d16] border border-[#1f293d] gap-3">
                <div class="flex items-center space-x-3 min-w-0">
                  <img :src="u.avatar_url || '/uploads/avatars/default.png'" @error="$event.target.src='/uploads/avatars/default.png'" class="w-9 h-9 rounded-lg object-cover border border-slate-700 flex-shrink-0" />
                  <div class="min-w-0">
                    <span class="block text-xs font-bold text-white font-mono truncate">{{ u.full_name || u.username }}</span>
                    <span class="block text-[10px] text-slate-400 font-mono truncate">{{ u.email }}</span>
                  </div>
                </div>
                <div class="flex items-center gap-2 flex-shrink-0">
                  <button @click="approvePendingUser(u.id)" class="btn-neon-cyan text-[11px] py-1.5 px-3 font-mono font-extrabold">Approve</button>
                  <button @click="rejectPendingUser(u.id)" class="btn-ghost text-[11px] py-1.5 px-3 text-red-400 font-mono font-bold hover:bg-red-500/15">Reject</button>
                </div>
              </div>
              <router-link v-if="dashboardRole === 'admin'" to="/admin" class="block text-center text-xs text-[#9fef00] hover:underline font-mono pt-1">View All in Admin Panel &rarr;</router-link>
            </div>
            <p v-else class="text-xs text-slate-500 text-center py-6">All caught up - no pending approvals.</p>
          </div>

          <!-- Admin: Recent Platform Activity -->
          <div v-if="dashboardRole === 'admin'" class="glass-panel p-6 space-y-4">
            <div class="flex justify-between items-center border-b border-[#1f293d] pb-3">
              <h3 class="text-base font-bold text-white font-mono uppercase">Recent Platform Activity</h3>
              <router-link to="/admin/audit-logs" class="text-xs text-[#9fef00] hover:underline font-mono">Full Log &rarr;</router-link>
            </div>
            <div v-if="recentAuditLogs.length" class="space-y-2.5">
              <div v-for="log in recentAuditLogs" :key="log.id" class="flex items-start justify-between gap-3 p-2.5 rounded-lg bg-[#090d16] border border-[#1f293d]">
                <div class="min-w-0">
                  <p class="text-xs text-slate-200 font-mono"><span class="font-bold text-[#00f0ff]">{{ log.actor_name }}</span> {{ formatAuditAction(log.action) }}</p>
                  <p v-if="log.notes" class="text-[10px] text-slate-500 mt-0.5 truncate">{{ log.notes }}</p>
                </div>
                <span class="text-[10px] text-slate-500 font-mono flex-shrink-0 whitespace-nowrap">{{ timeAgo(log.created_at) }}</span>
              </div>
            </div>
            <p v-else class="text-xs text-slate-500 text-center py-6">No recent activity.</p>
          </div>

        </div>

        <!-- Right Column: Digital ID Card & Online Roster (same for all roles) -->
        <div class="space-y-8">

          <div class="glass-panel p-6 flex flex-col items-center">
            <h3 class="text-xs font-mono uppercase text-slate-400 mb-4 self-start border-b border-[#1f293d] w-full pb-2">OPERATOR ID BADGE</h3>
            <DigitalIDCard :user="authStore.user" />
          </div>

          <div class="glass-panel p-6 space-y-4">
            <h3 class="text-xs font-mono font-bold text-white uppercase flex items-center justify-between border-b border-[#1f293d] pb-3">
              <div class="flex items-center space-x-2">
                <span class="w-2 h-2 rounded-full bg-[#9fef00]"></span>
                <span>Active Hunters</span>
              </div>
              <span class="text-[11px] font-mono text-[#9fef00] bg-[#9fef00]/10 px-2.5 py-0.5 rounded border border-[#9fef00]/20 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-[#9fef00]"></span>
                {{ chatStore.onlineCount || 1 }} Online
              </span>
            </h3>
            <div class="space-y-3">
              <div v-for="member in chatStore.onlineUsers.slice(0, 8)" :key="member.id" class="flex items-center justify-between p-2.5 rounded-lg bg-[#090d16] border border-[#1f293d] hover:border-slate-700 transition-colors">
                <div class="flex items-center space-x-3">
                  <div class="relative flex-shrink-0">
                    <img :src="member.avatar_url || '/uploads/avatars/default.png'" @error="$event.target.src='/uploads/avatars/default.png'" class="w-8 h-8 rounded-lg object-cover border border-[#9fef00]/40" />
                    <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[#9fef00] border-2 border-[#090d16]"></span>
                  </div>
                  <div>
                    <span class="block text-xs font-bold text-white font-mono">{{ member.full_name || member.username }}</span>
                    <span class="block text-[10px] text-slate-400 font-mono">@{{ member.username }}</span>
                  </div>
                </div>
                <span class="text-[9px] font-mono px-2 py-0.5 rounded uppercase font-bold" :class="member.role === 'root_admin' ? 'bg-red-950 text-red-400' : 'bg-[#151f30] text-slate-300 border border-slate-700'">
                  {{ member.role }}
                </span>
              </div>
              <p v-if="chatStore.onlineUsers.length > 8" class="text-[10px] text-slate-500 font-mono text-center pt-1">+{{ chatStore.onlineUsers.length - 8 }} more online</p>
              <p v-if="!chatStore.onlineUsers.length" class="text-xs text-slate-500 text-center py-4 font-mono">No one else is online right now.</p>
            </div>
          </div>

        </div>

      </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import DigitalIDCard from '../components/DigitalIDCard.vue'
import { useAuthStore } from '../stores/auth'
import { useClubStore } from '../stores/club'
import { useChatStore } from '../stores/chat'

const authStore = useAuthStore()
const clubStore = useClubStore()
const chatStore = useChatStore()

const announcements = ref([])
const dismissedAnnouncementIds = ref(new Set())
const visibleAnnouncements = computed(() => announcements.value.filter(a => !dismissedAnnouncementIds.value.has(a.id)))

const pendingUsers = ref([])
const recentAuditLogs = ref([])
const liveClasses = ref([])

// isAdmin/isTeacher on the auth store are cumulative (isTeacher is also true
// for admins), so checking isAdmin first and falling through gives exactly
// one of 'admin' | 'teacher' | 'member'.
const dashboardRole = computed(() => {
  if (authStore.isAdmin) return 'admin'
  if (authStore.isTeacher) return 'teacher'
  return 'member'
})

const myCourses = computed(() => clubStore.courses.filter(c => c.author_id === authStore.user?.id))
const myModulesCount = computed(() => myCourses.value.reduce((sum, c) => sum + (c.modules_count || 0), 0))
const upcomingLiveClasses = computed(() => {
  const now = Date.now()
  return liveClasses.value.filter(c => c.scheduled_at && new Date(c.scheduled_at).getTime() >= now)
})

const banner = computed(() => {
  if (dashboardRole.value === 'admin') {
    return {
      label: 'ADMIN COMMAND DASHBOARD',
      description: 'Oversee the platform: review pending member approvals, monitor recent activity, and keep the club running smoothly.',
      primaryCta: { to: '/admin', label: 'Admin Panel' },
      secondaryCtas: [
        { to: '/academy/write', label: 'Content Studio' },
        { to: '/competitions', label: 'View Competitions' },
        { to: '/id-card', label: 'Digital ID', class: 'text-[#00f0ff] border-[#00f0ff]/30' }
      ]
    }
  }
  if (dashboardRole.value === 'teacher') {
    return {
      label: 'FACULTY OPERATOR DASHBOARD',
      description: 'Manage your Learning Paths, review pending student approvals, and keep your Live Classes on schedule.',
      primaryCta: { to: '/academy/write', label: 'Content Studio' },
      secondaryCtas: [
        { to: '/academy/roadmap-studio', label: 'Roadmap Studio' },
        { to: '/competitions', label: 'View Competitions' },
        { to: '/id-card', label: 'Digital ID', class: 'text-[#00f0ff] border-[#00f0ff]/30' }
      ]
    }
  }
  return {
    label: 'MEMBER OPERATOR DASHBOARD',
    description: 'Ready to level up your offensive security skills today? Complete active Academy modules, register for collegiate CTF matches, or hop into the practice arena.',
    primaryCta: { to: '/academy', label: 'Explore Academy' },
    secondaryCtas: [
      { to: '/competitions', label: 'View Competitions' },
      { to: '/id-card', label: 'Digital ID', class: 'text-[#00f0ff] border-[#00f0ff]/30' }
    ]
  }
})

const quickStats = computed(() => {
  if (dashboardRole.value === 'admin') {
    return [
      { label: 'Total Members', value: clubStore.stats?.total_members || 0, color: 'text-[#9fef00]' },
      { label: 'Pending Approvals', value: pendingUsers.value.length, color: 'text-amber-400' },
      { label: 'Total Paths', value: clubStore.courses.length, color: 'text-[#00f0ff]' },
      { label: 'Total Competitions', value: clubStore.competitions.length, color: 'text-purple-400' }
    ]
  }
  if (dashboardRole.value === 'teacher') {
    return [
      { label: 'My Paths', value: myCourses.value.length, color: 'text-[#9fef00]' },
      { label: 'My Modules', value: myModulesCount.value, color: 'text-[#00f0ff]' },
      { label: 'Pending Approvals', value: pendingUsers.value.length, color: 'text-amber-400' },
      { label: 'Live Classes Upcoming', value: upcomingLiveClasses.value.length, color: 'text-purple-400' }
    ]
  }
  return [
    { label: 'Active Members', value: clubStore.stats?.total_members || 0, color: 'text-[#9fef00]' },
    { label: 'Active Enrollees', value: clubStore.stats?.active_courses || 0, color: 'text-[#00f0ff]' },
    { label: 'Certs Awarded', value: clubStore.stats?.completed_courses || 0, color: 'text-purple-400' },
    { label: 'CTF Rank', value: `#${clubStore.stats?.ctf_rank || 1}`, color: 'text-amber-400' }
  ]
})

const fetchAnnouncements = async () => {
  try {
    const res = await axios.get('/api/announcements/active')
    announcements.value = res.data.announcements || []
  } catch (err) {
    console.error('Failed to load announcements', err)
  }
}

const fetchPendingUsers = async () => {
  try {
    const res = await axios.get('/api/admin/users', { params: { status: 'pending' } })
    pendingUsers.value = res.data.users || []
  } catch (err) {
    console.error('Failed to load pending users', err)
  }
}

const fetchRecentAuditLogs = async () => {
  try {
    const res = await axios.get('/api/admin/audit-log')
    recentAuditLogs.value = (res.data.audit_logs || []).slice(0, 5)
  } catch (err) {
    console.error('Failed to load audit log', err)
  }
}

const fetchLiveClasses = async () => {
  try {
    const res = await axios.get('/api/academy/live-classes')
    liveClasses.value = res.data.live_classes || []
  } catch (err) {
    console.error('Failed to load live classes', err)
  }
}

const approvePendingUser = async (userId) => {
  try {
    await axios.post(`/api/admin/users/${userId}/approve`, dashboardRole.value === 'admin' ? { assigned_role: 'member' } : {})
    pendingUsers.value = pendingUsers.value.filter(u => u.id !== userId)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to approve user')
  }
}

const rejectPendingUser = async (userId) => {
  if (!confirm('Reject this pending registration?')) return
  try {
    await axios.post(`/api/admin/users/${userId}/reject`)
    pendingUsers.value = pendingUsers.value.filter(u => u.id !== userId)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to reject user')
  }
}

const formatAuditAction = (action) => (action || '').replace(/_/g, ' ').toLowerCase()

const timeAgo = (isoString) => {
  if (!isoString) return ''
  const diffMs = Date.now() - new Date(isoString).getTime()
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return 'just now'
  if (diffMin < 60) return `${diffMin}m ago`
  const diffHr = Math.floor(diffMin / 60)
  if (diffHr < 24) return `${diffHr}h ago`
  const diffDay = Math.floor(diffHr / 24)
  return `${diffDay}d ago`
}

const ctfdUrl = computed(() => {
  if (window.location.hostname.includes('hackerxploit.org')) {
    return 'https://arena.hackerxploit.org'
  }
  return `${window.location.protocol}//${window.location.hostname}:8000`
})

onMounted(() => {
  clubStore.fetchStats()
  clubStore.fetchCourses()
  chatStore.initSocket()
  fetchAnnouncements()

  if (dashboardRole.value !== 'member') {
    fetchPendingUsers()
  }
  if (dashboardRole.value === 'admin') {
    clubStore.fetchCompetitions()
    fetchRecentAuditLogs()
  }
  if (dashboardRole.value === 'teacher') {
    fetchLiveClasses()
  }
})
</script>
