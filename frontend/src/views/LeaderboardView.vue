<template>
  <div class="space-y-8 font-mono">
    
    <!-- Leaderboard Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1f293d] pb-6">
      <div>
        <h1 class="text-3xl font-extrabold text-white flex items-center gap-3">
          <span class="p-2 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400">
            🏆
          </span>
          CTFd Official Leaderboard
        </h1>
        <p class="text-slate-400 text-xs mt-1">Rankings are strictly determined by CTFd challenge scores. Event participations and badges are displayed below.</p>
      </div>

      <div class="relative w-full md:w-72">
        <input v-model="searchQuery" type="text" placeholder="Search members..." class="input-field w-full text-xs pl-9" />
        <svg class="w-4 h-4 text-slate-500 absolute left-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
    </div>

    <!-- Top 3 Champions Podium -->
    <div v-if="filteredRankings.length >= 3 && !searchQuery" class="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
      
      <!-- #2 Silver -->
      <div class="glass-panel p-6 border-slate-400/40 text-center space-y-3 order-2 md:order-1 mt-4 bg-[#0d1420]">
        <span class="inline-block px-3 py-1 rounded-full text-xs font-bold bg-slate-400/20 text-slate-300 border border-slate-400/40">🥈 RANK #2</span>
        <img :src="filteredRankings[1].avatar_url || '/uploads/avatars/default.png'" @error="$event.target.src='/uploads/avatars/default.png'" class="w-20 h-20 mx-auto rounded-full object-cover border-2 border-slate-400" />
        <div>
          <h3 class="font-bold text-white text-base">{{ filteredRankings[1].full_name }}</h3>
          <p class="text-xs text-[#00f0ff]">@{{ filteredRankings[1].username }}</p>
        </div>
        <p class="text-xl font-bold text-[#9fef00]">⚔️ {{ filteredRankings[1].ctfd_score }} pts</p>
        <div class="text-[11px] text-slate-400 pt-1 border-t border-[#1f293d]">
          Events: {{ filteredRankings[1].events_attended }} | Wins: {{ filteredRankings[1].competition_wins }}
        </div>
      </div>

      <!-- #1 Gold -->
      <div class="glass-panel p-8 border-amber-500/60 text-center space-y-4 order-1 md:order-2 shadow-2xl shadow-amber-500/10 scale-105 bg-[#0d1420]">
        <span class="inline-block px-4 py-1.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/50">👑 RANK #1 (CHAMPION)</span>
        <img :src="filteredRankings[0].avatar_url || '/uploads/avatars/default.png'" @error="$event.target.src='/uploads/avatars/default.png'" class="w-24 h-24 mx-auto rounded-full object-cover border-4 border-amber-400 shadow-lg shadow-amber-500/30" />
        <div>
          <h3 class="font-bold text-white text-lg">{{ filteredRankings[0].full_name }}</h3>
          <p class="text-xs text-[#00f0ff]">@{{ filteredRankings[0].username }}</p>
        </div>
        <p class="text-2xl font-bold text-[#9fef00]">⚔️ {{ filteredRankings[0].ctfd_score }} pts</p>
        <div class="text-xs text-slate-300 pt-1 border-t border-[#1f293d] flex justify-center space-x-3">
          <span>🎯 {{ filteredRankings[0].ctfd_solves }} Solves</span>
          <span>🏆 {{ filteredRankings[0].competition_wins }} Wins</span>
        </div>
      </div>

      <!-- #3 Bronze -->
      <div class="glass-panel p-6 border-amber-700/40 text-center space-y-3 order-3 mt-8 bg-[#0d1420]">
        <span class="inline-block px-3 py-1 rounded-full text-xs font-bold bg-amber-800/20 text-amber-500 border border-amber-700/40">🥉 RANK #3</span>
        <img :src="filteredRankings[2].avatar_url || '/uploads/avatars/default.png'" @error="$event.target.src='/uploads/avatars/default.png'" class="w-20 h-20 mx-auto rounded-full object-cover border-2 border-amber-600" />
        <div>
          <h3 class="font-bold text-white text-base">{{ filteredRankings[2].full_name }}</h3>
          <p class="text-xs text-[#00f0ff]">@{{ filteredRankings[2].username }}</p>
        </div>
        <p class="text-xl font-bold text-[#9fef00]">⚔️ {{ filteredRankings[2].ctfd_score }} pts</p>
        <div class="text-[11px] text-slate-400 pt-1 border-t border-[#1f293d]">
          Events: {{ filteredRankings[2].events_attended }} | Wins: {{ filteredRankings[2].competition_wins }}
        </div>
      </div>

    </div>

    <!-- Leaderboard Table -->
    <div class="glass-panel overflow-hidden bg-[#0d1420] border border-[#1f293d] rounded-2xl shadow-2xl">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs font-mono">
          <thead class="bg-[#0b0e14] text-slate-400 border-b border-[#1f293d]">
            <tr>
              <th class="px-6 py-4">RANK</th>
              <th class="px-6 py-4">MEMBER</th>
              <th class="px-6 py-4 text-center">EVENTS ATTENDED & BADGES</th>
              <th class="px-6 py-4 text-center">CTFd SOLVES</th>
              <th class="px-6 py-4 text-right">CTFd SCORE (RANKING)</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[#1f293d] text-slate-200">
            <tr v-for="user in filteredRankings" :key="user.user_id" class="hover:bg-[#151f30] transition-colors">
              <td class="px-6 py-4 font-bold">
                <span v-if="user.rank === 1" class="text-amber-400">👑 #1</span>
                <span v-else-if="user.rank === 2" class="text-slate-300">🥈 #2</span>
                <span v-else-if="user.rank === 3" class="text-amber-600">🥉 #3</span>
                <span v-else class="text-slate-500">#{{ user.rank }}</span>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center space-x-3">
                  <img :src="user.avatar_url || '/uploads/avatars/default.png'" @error="$event.target.src='/uploads/avatars/default.png'" class="w-8 h-8 rounded-full object-cover border border-[#1f293d]" />
                  <div>
                    <div class="flex items-center gap-2">
                      <p class="font-bold text-white text-xs leading-tight">{{ user.full_name }}</p>
                      <span v-if="user.academic_year" class="text-[10px] px-1.5 py-0.2 rounded bg-cyan-950 text-[#00f0ff] border border-[#00f0ff]/30">Yr {{ user.academic_year }}</span>
                    </div>
                    <p class="text-[11px] text-[#00f0ff]">@{{ user.username }} &bull; {{ user.specialization_role || 'Operator' }}</p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 text-center">
                <div class="flex items-center justify-center space-x-2 text-[11px]">
                  <span class="bg-[#151f30] px-2 py-0.5 rounded border border-[#1f293d] text-slate-300">
                    🎟️ {{ user.events_attended }} Events
                  </span>
                  <span v-if="user.competition_wins > 0" class="bg-amber-500/20 border border-amber-500/40 text-amber-300 px-2 py-0.5 rounded">
                    🥇 {{ user.competition_wins }} Win
                  </span>
                  <span v-if="user.competition_runner_ups > 0" class="bg-slate-400/20 border border-slate-400/40 text-slate-300 px-2 py-0.5 rounded">
                    🥈 {{ user.competition_runner_ups }} Runner-Up
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 text-center text-slate-300">
                🎯 {{ user.ctfd_solves || 0 }} Solves
              </td>
              <td class="px-6 py-4 text-right font-bold text-sm text-[#9fef00]">
                ⚔️ {{ user.ctfd_score }} pts
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const rankings = ref([])
const searchQuery = ref('')

const fetchLeaderboard = async () => {
  try {
    const res = await axios.get('/api/leaderboard', { withCredentials: true })
    rankings.value = res.data.leaderboard || []
  } catch (err) {
    console.error('Failed to fetch leaderboard:', err)
  }
}

const filteredRankings = computed(() => {
  if (!searchQuery.value.trim()) return rankings.value
  const q = searchQuery.value.toLowerCase()
  return rankings.value.filter(u => 
    u.full_name.toLowerCase().includes(q) || 
    u.username.toLowerCase().includes(q) ||
    (u.specialization_role && u.specialization_role.toLowerCase().includes(q))
  )
})

onMounted(() => {
  fetchLeaderboard()
})
</script>
