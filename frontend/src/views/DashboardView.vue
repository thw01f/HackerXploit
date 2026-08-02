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
        
        <!-- Left 2 Columns: Welcome Banner, Quick Stats & Academy Spotlight -->
        <div class="lg:col-span-2 space-y-8">
          
          <div class="glass-panel-htb p-8 relative overflow-hidden bg-[#111927]">
            <div class="relative z-10">
              <span class="text-xs font-mono text-[#9fef00] font-bold uppercase tracking-widest">MEMBER OPERATOR DASHBOARD</span>
              <h2 class="text-2xl sm:text-3xl font-extrabold text-white mt-1 font-mono">Welcome back, {{ authStore.user?.full_name || authStore.user?.username }}!</h2>
              <p class="text-slate-300 text-sm mt-2 max-w-xl leading-relaxed">
                Ready to level up your offensive security skills today? Complete active Academy modules, register for collegiate CTF matches, or hop into the practice arena.
              </p>

              <div class="flex flex-wrap items-center gap-4 mt-6">
                <router-link to="/academy" class="btn-htb text-xs py-2.5 px-5 font-mono">Explore Academy</router-link>
                <a :href="ctfdUrl" target="_blank" class="btn-ghost text-xs py-2.5 px-5 font-mono text-[#9fef00] border-[#9fef00]/30">⚔️ CTF Arena</a>
                <router-link to="/competitions" class="btn-ghost text-xs py-2.5 px-5 font-mono">View Competitions</router-link>
                <router-link to="/id-card" class="btn-ghost text-xs py-2.5 px-5 font-mono text-[#00f0ff] border-[#00f0ff]/30">🪪 Digital ID</router-link>
              </div>
            </div>
          </div>

          <!-- Quick Stats Cards (Symmetric Grid) -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div class="glass-panel p-5 text-center">
              <span class="block text-2xl font-extrabold text-[#9fef00] font-mono">{{ clubStore.stats?.total_members || 0 }}</span>
              <span class="text-[11px] text-slate-400 uppercase font-mono mt-1 block">Active Members</span>
            </div>
            <div class="glass-panel p-5 text-center">
              <span class="block text-2xl font-extrabold text-[#00f0ff] font-mono">{{ clubStore.stats?.active_courses || 0 }}</span>
              <span class="text-[11px] text-slate-400 uppercase font-mono mt-1 block">Active Enrollees</span>
            </div>
            <div class="glass-panel p-5 text-center">
              <span class="block text-2xl font-extrabold text-purple-400 font-mono">{{ clubStore.stats?.completed_courses || 0 }}</span>
              <span class="text-[11px] text-slate-400 uppercase font-mono mt-1 block">Certs Awarded</span>
            </div>
            <div class="glass-panel p-5 text-center">
              <span class="block text-2xl font-extrabold text-amber-400 font-mono">#{{ clubStore.stats?.ctf_rank || 1 }}</span>
              <span class="text-[11px] text-slate-400 uppercase font-mono mt-1 block">CTF Rank</span>
            </div>
          </div>

          <!-- Course Catalog Quick Access -->
          <div class="glass-panel p-6 space-y-4">
            <div class="flex justify-between items-center border-b border-[#1f293d] pb-3">
              <h3 class="text-base font-bold text-white font-mono uppercase">Featured Academy Modules</h3>
              <router-link to="/academy" class="text-xs text-[#9fef00] hover:underline font-mono">View Catalog &rarr;</router-link>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div v-for="course in clubStore.courses.slice(0, 2)" :key="course.id" class="p-4 rounded-xl bg-[#090d16] border border-[#1f293d] hover:border-[#9fef00]/40 transition-all flex flex-col justify-between">
                <div>
                  <div class="flex justify-between items-center mb-2">
                    <span class="text-[10px] font-mono uppercase bg-[#151f30] text-[#9fef00] border border-[#9fef00]/30 px-2 py-0.5 rounded">{{ course.difficulty || 'Intermediate' }}</span>
                    <span class="text-[10px] font-mono text-slate-400">{{ course.chapters_count || 5 }} Modules</span>
                  </div>
                  <h4 class="font-bold text-white text-sm font-mono">{{ course.title }}</h4>
                  <p class="text-slate-400 text-xs mt-1.5 line-clamp-2 leading-relaxed">{{ course.description }}</p>
                </div>
                <router-link :to="`/academy/course/${course.id}`" class="inline-block mt-4 text-xs text-[#9fef00] font-mono font-semibold hover:underline">
                  Start Course &rarr;
                </router-link>
              </div>
            </div>
          </div>

        </div>

        <!-- Right Column: Digital ID Card & Online Roster -->
        <div class="space-y-8">
          
          <div class="glass-panel p-6 flex flex-col items-center">
            <h3 class="text-xs font-mono uppercase text-slate-400 mb-4 self-start border-b border-[#1f293d] w-full pb-2">OPERATOR ID BADGE</h3>
            <DigitalIDCard :user="authStore.user" />
          </div>

          <div class="glass-panel p-6 space-y-4">
            <h3 class="text-xs font-mono font-bold text-white uppercase flex items-center justify-between border-b border-[#1f293d] pb-3">
              <div class="flex items-center space-x-2">
                <span class="w-2 h-2 rounded-full bg-[#9fef00]"></span>
                <span>Active Club Roster</span>
              </div>
              <span class="text-[11px] font-mono text-[#9fef00] bg-[#9fef00]/10 px-2.5 py-0.5 rounded border border-[#9fef00]/20 flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-[#9fef00]"></span>
                {{ chatStore.onlineCount || 1 }} Online
              </span>
            </h3>
            <div class="space-y-3">
              <div v-for="member in clubStore.members.slice(0, 5)" :key="member.id" class="flex items-center justify-between p-2.5 rounded-lg bg-[#090d16] border border-[#1f293d] hover:border-slate-700 transition-colors">
                <div class="flex items-center space-x-3">
                  <img :src="member.avatar_url || '/uploads/avatars/default.png'" @error="$event.target.src='/uploads/avatars/default.png'" class="w-8 h-8 rounded-lg object-cover border border-[#9fef00]/40" />
                  <div>
                    <span class="block text-xs font-bold text-white font-mono">{{ member.full_name || member.username }}</span>
                    <span class="block text-[10px] text-slate-400 font-mono">@{{ member.username }}</span>
                  </div>
                </div>
                <span class="text-[9px] font-mono px-2 py-0.5 rounded uppercase font-bold" :class="member.role === 'root_admin' ? 'bg-red-950 text-red-400' : 'bg-[#151f30] text-slate-300 border border-slate-700'">
                  {{ member.role }}
                </span>
              </div>
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

const fetchAnnouncements = async () => {
  try {
    const res = await axios.get('/api/announcements/active')
    announcements.value = res.data.announcements || []
  } catch (err) {
    console.error('Failed to load announcements', err)
  }
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
  clubStore.fetchMembers()
  chatStore.initSocket()
  fetchAnnouncements()
})
</script>
