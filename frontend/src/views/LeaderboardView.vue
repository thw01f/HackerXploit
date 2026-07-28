<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full space-y-8">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 class="text-3xl font-extrabold text-white flex items-center gap-3">
            <span class="p-2 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400">
              🏆
            </span>
            Cybersecurity Club Leaderboard
          </h1>
          <p class="text-slate-400 text-sm mt-1">Combined weighted rankings across CTF points, competition wins, and completed academy modules.</p>
        </div>

        <div class="relative w-full md:w-72">
          <input v-model="searchQuery" type="text" placeholder="Search members..." class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-sm text-white focus:border-amber-500 focus:outline-none pl-9" />
          <svg class="w-4 h-4 text-slate-500 absolute left-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      <!-- Podium Top 3 -->
      <div v-if="filteredRankings.length >= 3 && !searchQuery" class="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
        <!-- #2 Silver -->
        <div class="glass-panel p-6 border-slate-400/40 text-center space-y-3 order-2 md:order-1 mt-4">
          <span class="inline-block px-3 py-1 rounded-full text-xs font-mono font-bold bg-slate-400/20 text-slate-300 border border-slate-400/40">🥈 RANK #2</span>
          <img :src="filteredRankings[1].avatar_url || '/uploads/avatars/default.png'" class="w-20 h-20 mx-auto rounded-full object-cover border-2 border-slate-400" />
          <div>
            <h3 class="font-bold text-white text-base">{{ filteredRankings[1].full_name }}</h3>
            <p class="text-xs font-mono text-cyan-400">@{{ filteredRankings[1].username }}</p>
          </div>
          <p class="text-xl font-mono font-bold text-amber-400">⭐ {{ filteredRankings[1].leaderboard_score }} pts</p>
        </div>

        <!-- #1 Gold -->
        <div class="glass-panel p-8 border-amber-500/60 text-center space-y-4 order-1 md:order-2 shadow-xl shadow-amber-500/10 scale-105">
          <span class="inline-block px-4 py-1.5 rounded-full text-xs font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/50">👑 RANK #1 (CHAMPION)</span>
          <img :src="filteredRankings[0].avatar_url || '/uploads/avatars/default.png'" class="w-24 h-24 mx-auto rounded-full object-cover border-4 border-amber-400 shadow-lg shadow-amber-500/30" />
          <div>
            <h3 class="font-bold text-white text-lg">{{ filteredRankings[0].full_name }}</h3>
            <p class="text-xs font-mono text-cyan-400">@{{ filteredRankings[0].username }}</p>
          </div>
          <p class="text-2xl font-mono font-bold text-amber-400">⭐ {{ filteredRankings[0].leaderboard_score }} pts</p>
        </div>

        <!-- #3 Bronze -->
        <div class="glass-panel p-6 border-amber-700/40 text-center space-y-3 order-3 mt-8">
          <span class="inline-block px-3 py-1 rounded-full text-xs font-mono font-bold bg-amber-800/20 text-amber-500 border border-amber-700/40">🥉 RANK #3</span>
          <img :src="filteredRankings[2].avatar_url || '/uploads/avatars/default.png'" class="w-20 h-20 mx-auto rounded-full object-cover border-2 border-amber-600" />
          <div>
            <h3 class="font-bold text-white text-base">{{ filteredRankings[2].full_name }}</h3>
            <p class="text-xs font-mono text-cyan-400">@{{ filteredRankings[2].username }}</p>
          </div>
          <p class="text-xl font-mono font-bold text-amber-400">⭐ {{ filteredRankings[2].leaderboard_score }} pts</p>
        </div>
      </div>

      <!-- Leaderboard Table -->
      <div class="glass-panel overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm font-mono">
            <thead class="bg-slate-900/80 text-xs text-slate-400 border-b border-slate-800">
              <tr>
                <th class="px-6 py-4">RANK</th>
                <th class="px-6 py-4">MEMBER</th>
                <th class="px-6 py-4 text-center">COMPETITION WINS</th>
                <th class="px-6 py-4 text-center">RUNNER-UPS</th>
                <th class="px-6 py-4 text-center">COURSES PASSED</th>
                <th class="px-6 py-4 text-right">TOTAL SCORE</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60 text-slate-200">
              <tr v-for="user in filteredRankings" :key="user.user_id" class="hover:bg-slate-900/50 transition-colors">
                <td class="px-6 py-4 font-bold">
                  <span v-if="user.rank === 1" class="text-amber-400">👑 #1</span>
                  <span v-else-if="user.rank === 2" class="text-slate-300">🥈 #2</span>
                  <span v-else-if="user.rank === 3" class="text-amber-600">🥉 #3</span>
                  <span v-else class="text-slate-500">#{{ user.rank }}</span>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center space-x-3">
                    <img :src="user.avatar_url || '/uploads/avatars/default.png'" class="w-8 h-8 rounded-full object-cover border border-slate-700" />
                    <div>
                      <p class="font-bold text-white text-sm leading-tight">{{ user.full_name }}</p>
                      <p class="text-[11px] text-cyan-400">@{{ user.username }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 text-center text-amber-400 font-bold">🥇 {{ user.competition_wins }}</td>
                <td class="px-6 py-4 text-center text-slate-300">🥈 {{ user.competition_runner_ups }}</td>
                <td class="px-6 py-4 text-center text-purple-400">📚 {{ user.courses_completed }}</td>
                <td class="px-6 py-4 text-right font-bold text-base text-amber-400">⭐ {{ user.leaderboard_score }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

const searchQuery = ref('')
const rankings = ref([])

const fetchLeaderboard = async () => {
  try {
    const res = await axios.get('/api/leaderboard')
    rankings.value = res.data.leaderboard
  } catch (err) {
    console.error(err)
  }
}

const filteredRankings = computed(() => {
  if (!searchQuery.value) return rankings.value
  const q = searchQuery.value.toLowerCase()
  return rankings.value.filter(u =>
    u.username.toLowerCase().includes(q) ||
    u.full_name.toLowerCase().includes(q)
  )
})

onMounted(() => {
  fetchLeaderboard()
})
</script>
