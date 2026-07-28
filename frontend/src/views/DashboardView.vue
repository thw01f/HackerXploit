<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full space-y-8">
      <!-- Announcement Header -->
      <div v-if="clubStore.stats?.announcement" class="glass-panel p-4 flex items-center justify-between border-l-4 border-l-cyan-400">
        <div class="flex items-center space-x-3">
          <span class="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 font-mono text-xs font-bold uppercase">ANNOUNCEMENT</span>
          <p class="text-sm text-slate-200 font-medium">{{ clubStore.stats.announcement }}</p>
        </div>
        <a href="http://ctf.hackerxploit.org" target="_blank" class="btn-neon-cyan text-xs py-1.5 px-3 whitespace-nowrap">Join CTF Arena</a>
      </div>

      <!-- Main Dashboard Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left 2 Columns: Welcome Banner, Quick Stats & Academy Spotlight -->
        <div class="lg:col-span-2 space-y-8">
          <div class="glass-panel-cyan p-8 relative overflow-hidden">
            <div class="relative z-10">
              <span class="text-xs font-mono text-cyan-400 font-semibold uppercase tracking-wider">MEMBER DASHBOARD</span>
              <h2 class="text-3xl font-extrabold text-white mt-1">Welcome back, {{ authStore.user?.full_name }}!</h2>
              <p class="text-slate-300 text-sm mt-2 max-w-xl">
                Ready to level up your skills today? Check out active Academy courses, apply for collegiate CTFs, or hop into the CTF arena.
              </p>

              <div class="flex items-center space-x-4 mt-6">
                <router-link to="/academy" class="btn-neon-cyan text-xs py-2 px-5">Explore Academy</router-link>
                <router-link to="/competitions" class="btn-ghost text-xs py-2 px-5">View Competitions</router-link>
              </div>
            </div>
          </div>

          <!-- Quick Stats Cards -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div class="glass-panel p-5 text-center">
              <span class="block text-2xl font-extrabold text-cyan-400 font-mono">{{ clubStore.stats?.total_members || 0 }}</span>
              <span class="text-xs text-slate-400 uppercase font-mono mt-1 block">Active Members</span>
            </div>
            <div class="glass-panel p-5 text-center">
              <span class="block text-2xl font-extrabold text-purple-400 font-mono">{{ clubStore.stats?.active_courses || 0 }}</span>
              <span class="text-xs text-slate-400 uppercase font-mono mt-1 block">Active Enrollees</span>
            </div>
            <div class="glass-panel p-5 text-center">
              <span class="block text-2xl font-extrabold text-emerald-400 font-mono">{{ clubStore.stats?.completed_courses || 0 }}</span>
              <span class="text-xs text-slate-400 uppercase font-mono mt-1 block">Certs Awarded</span>
            </div>
            <div class="glass-panel p-5 text-center">
              <span class="block text-2xl font-extrabold text-amber-400 font-mono">#{{ clubStore.stats?.ctf_rank || 12 }}</span>
              <span class="text-xs text-slate-400 uppercase font-mono mt-1 block">CTF Rank</span>
            </div>
          </div>

          <!-- Course Catalog Quick Access -->
          <div class="glass-panel p-6">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-bold text-white">Recommended Courses</h3>
              <router-link to="/academy" class="text-xs text-cyan-400 hover:underline font-mono">View All &rarr;</router-link>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div v-for="course in clubStore.courses.slice(0, 2)" :key="course.id" class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-cyan-500/30 transition-all">
                <span class="text-[10px] font-mono uppercase bg-cyan-950 text-cyan-400 px-2 py-0.5 rounded">{{ course.difficulty }}</span>
                <h4 class="font-bold text-white text-base mt-2">{{ course.title }}</h4>
                <p class="text-slate-400 text-xs mt-1 line-clamp-2">{{ course.description }}</p>
                <router-link :to="`/academy/course/${course.id}`" class="inline-block mt-3 text-xs text-cyan-400 font-semibold hover:underline">
                  Start Course &rarr;
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Digital ID Card & Online Members -->
        <div class="space-y-8">
          <div class="flex flex-col items-center">
            <h3 class="text-xs font-mono uppercase text-slate-400 mb-3 self-start">DIGITAL MEMBERSHIP ID</h3>
            <DigitalIDCard :user="authStore.user" />
          </div>

          <div class="glass-panel p-6">
            <h3 class="text-sm font-mono font-bold text-white uppercase mb-4 flex items-center space-x-2">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              <span>Active Club Roster</span>
            </h3>
            <div class="space-y-3">
              <div v-for="member in clubStore.members.slice(0, 5)" :key="member.id" class="flex items-center justify-between p-2 rounded-lg hover:bg-slate-800/40 transition-colors">
                <div class="flex items-center space-x-3">
                  <img :src="member.avatar_url || '/uploads/avatars/default.png'" class="w-8 h-8 rounded-full object-cover border border-slate-700" />
                  <div>
                    <span class="block text-xs font-semibold text-white">{{ member.full_name }}</span>
                    <span class="block text-[10px] text-slate-400 font-mono">@{{ member.username }}</span>
                  </div>
                </div>
                <span class="text-[10px] px-2 py-0.5 rounded uppercase font-bold" :class="member.role === 'root_admin' ? 'bg-red-950 text-red-400' : 'bg-slate-800 text-slate-300'">
                  {{ member.role }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import DigitalIDCard from '../components/DigitalIDCard.vue'
import { useAuthStore } from '../stores/auth'
import { useClubStore } from '../stores/club'

const authStore = useAuthStore()
const clubStore = useClubStore()

onMounted(() => {
  clubStore.fetchStats()
  clubStore.fetchCourses()
  clubStore.fetchMembers()
})
</script>
