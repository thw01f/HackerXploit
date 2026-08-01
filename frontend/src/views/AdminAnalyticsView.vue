<template>
  <div class="space-y-8">
      <div class="flex items-center justify-between border-b border-slate-800 pb-6">
        <div>
          <h1 class="text-3xl font-extrabold text-white flex items-center gap-3">
            <span class="p-2 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
            </span>
            System Analytics & Intelligence
          </h1>
          <p class="text-slate-400 text-sm mt-1">Real-time metrics on member growth, weekly active retention, top academy courses, and competition participation.</p>
        </div>

        <button @click="fetchAnalytics" class="btn-ghost text-xs py-2 px-4 font-mono flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          <span>Refresh Analytics</span>
        </button>
      </div>

      <div v-if="loading" class="text-center py-16 text-slate-500 font-mono text-sm">
        Computing system analytics...
      </div>

      <div v-else-if="!data" class="glass-panel p-12 text-center text-slate-400">
        Analytics data unavailable.
      </div>

      <div v-else class="space-y-8">
        <!-- Metric Cards: Registration Trends -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div class="glass-panel p-6 space-y-2 border-l-4 border-emerald-500">
            <p class="text-xs font-mono text-slate-400 uppercase">Approved Members</p>
            <p class="text-3xl font-mono font-extrabold text-white">{{ data.registration_trend.total_approved }}</p>
            <p class="text-[11px] font-mono text-emerald-400">+{{ data.registration_trend.recent_30_day_signups }} new in last 30d</p>
          </div>

          <div class="glass-panel p-6 space-y-2 border-l-4 border-amber-500">
            <p class="text-xs font-mono text-slate-400 uppercase">Pending Approvals</p>
            <p class="text-3xl font-mono font-extrabold text-amber-400">{{ data.registration_trend.total_pending }}</p>
            <p class="text-[11px] font-mono text-slate-400">Awaiting admin review</p>
          </div>

          <div class="glass-panel p-6 space-y-2 border-l-4 border-rose-500">
            <p class="text-xs font-mono text-slate-400 uppercase">Rejected Signups</p>
            <p class="text-3xl font-mono font-extrabold text-rose-400">{{ data.registration_trend.total_rejected }}</p>
            <p class="text-[11px] font-mono text-slate-400">Access denied</p>
          </div>

          <div class="glass-panel p-6 space-y-2 border-l-4 border-purple-500">
            <p class="text-xs font-mono text-slate-400 uppercase">Suspended Accounts</p>
            <p class="text-3xl font-mono font-extrabold text-purple-400">{{ data.registration_trend.total_suspended }}</p>
            <p class="text-[11px] font-mono text-slate-400">Sessions invalidated</p>
          </div>
        </div>

        <!-- Weekly Active Members Chart -->
        <div class="glass-panel p-8 space-y-6">
          <div class="flex justify-between items-center border-b border-slate-800 pb-4">
            <div>
              <h3 class="text-lg font-bold text-white">Weekly Active Members (WAM)</h3>
              <p class="text-xs text-slate-400">Unique active user heartbeats per 7-day window over the last 8 weeks.</p>
            </div>
          </div>

          <div class="h-44 flex items-end gap-4 pt-6 pb-2 px-4 border-b border-slate-800">
            <div v-for="w in data.weekly_active_members" :key="w.week" class="flex-1 flex flex-col items-center group relative">
              <div class="w-full bg-purple-500/40 group-hover:bg-purple-400 rounded-t transition-all" :style="{ height: Math.max(w.active_members * 18, 12) + 'px' }"></div>
              <p class="text-[10px] font-mono text-slate-400 mt-2">{{ w.label }}</p>
              <div class="absolute -top-8 hidden group-hover:block bg-slate-900 text-purple-400 text-[10px] font-mono px-2 py-0.5 rounded border border-purple-500/40 z-10 whitespace-nowrap shadow-lg">
                {{ w.label }}: {{ w.active_members }} active
              </div>
            </div>
          </div>
        </div>

        <!-- Top Courses & Top Competitions Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <!-- Top Courses -->
          <div class="glass-panel p-6 space-y-4">
            <h3 class="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
              </svg>
              <span>Top 5 Academy Courses by Enrollment</span>
            </h3>

            <div v-if="data.top_courses.length === 0" class="text-xs text-slate-500 font-mono py-4">No course enrollment metrics.</div>

            <div v-else class="space-y-3">
              <div v-for="(course, idx) in data.top_courses" :key="course.id" class="flex justify-between items-center p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                <div class="flex items-center space-x-3">
                  <span class="font-mono text-xs font-bold text-purple-400">#{{ idx + 1 }}</span>
                  <span class="font-bold text-white text-sm truncate max-w-[200px]">{{ course.title }}</span>
                </div>
                <span class="text-xs font-mono px-2.5 py-1 rounded bg-purple-950/40 text-purple-300 border border-purple-500/30">
                  {{ course.enrollment_count }} enrolled
                </span>
              </div>
            </div>
          </div>

          <!-- Top Competitions -->
          <div class="glass-panel p-6 space-y-4">
            <h3 class="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/>
              </svg>
              <span>Top 5 Competitions by Participation</span>
            </h3>

            <div v-if="data.top_competitions.length === 0" class="text-xs text-slate-500 font-mono py-4">No competition participation metrics.</div>

            <div v-else class="space-y-3">
              <div v-for="(comp, idx) in data.top_competitions" :key="comp.id" class="flex justify-between items-center p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                <div class="flex items-center space-x-3">
                  <span class="font-mono text-xs font-bold text-amber-400">#{{ idx + 1 }}</span>
                  <div>
                    <p class="font-bold text-white text-sm truncate max-w-[200px]">{{ comp.title }}</p>
                    <p class="text-[10px] font-mono text-slate-500 uppercase">{{ comp.category }}</p>
                  </div>
                </div>
                <span class="text-xs font-mono px-2.5 py-1 rounded bg-amber-950/40 text-amber-300 border border-amber-500/30">
                  {{ comp.participant_count }} participants
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const data = ref(null)
const loading = ref(true)

const fetchAnalytics = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/admin/analytics')
    data.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchAnalytics()
})
</script>
