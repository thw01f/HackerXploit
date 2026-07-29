<template>
  <div class="space-y-8">
      <div v-if="loading" class="text-center py-16 text-slate-500 font-mono text-sm">
        Loading student structured profile...
      </div>

      <div v-else-if="!profile" class="glass-panel p-12 text-center text-slate-400">
        Student profile not found.
      </div>

      <div v-else class="space-y-8">
        <!-- Header Banner -->
        <div class="glass-panel p-8 flex flex-col md:flex-row items-center justify-between gap-6 border-l-4 border-cyan-500">
          <div class="flex items-center space-x-6">
            <img :src="profile.overview.avatar_url || '/uploads/avatars/default.png'" class="w-24 h-24 rounded-2xl object-cover border-2 border-cyan-500/40 shadow-lg shadow-cyan-500/10" />
            <div>
              <div class="flex items-center gap-3">
                <h1 class="text-2xl font-bold text-white">{{ profile.overview.full_name || profile.overview.username }}</h1>
                <span class="text-xs font-mono px-2.5 py-0.5 rounded uppercase border bg-cyan-950/40 border-cyan-500/30 text-cyan-400">
                  {{ profile.overview.role }}
                </span>
              </div>
              <p class="text-xs font-mono text-cyan-400 mt-0.5">@{{ profile.overview.username }} | {{ profile.overview.email }}</p>
              <p v-if="profile.overview.student_id" class="text-xs font-mono text-slate-400 mt-1">Student ID: {{ profile.overview.student_id }}</p>
            </div>
          </div>

          <div class="flex flex-wrap gap-4 text-center">
            <div class="bg-slate-900/80 px-4 py-2.5 rounded-xl border border-slate-800">
              <p class="text-[10px] font-mono text-slate-400 uppercase">Active Hours</p>
              <p class="text-lg font-mono font-bold text-cyan-400">⚡ {{ profile.activity.total_hours }}h</p>
            </div>
            <div class="bg-slate-900/80 px-4 py-2.5 rounded-xl border border-slate-800">
              <p class="text-[10px] font-mono text-slate-400 uppercase">Leaderboard Score</p>
              <p class="text-lg font-mono font-bold text-amber-400">⭐ {{ profile.overview.leaderboard_score || 0 }}</p>
            </div>
          </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="flex border-b border-slate-800 space-x-6 text-sm font-mono">
          <button v-for="tab in ['overview', 'activity', 'academy', 'trophy_case']" :key="tab" @click="activeTab = tab" :class="activeTab === tab ? 'text-cyan-400 border-b-2 border-cyan-400 font-bold pb-3' : 'text-slate-400 hover:text-slate-200 pb-3'" class="uppercase transition-colors flex items-center gap-2">
            <span v-if="tab === 'overview'">👤 Overview</span>
            <span v-else-if="tab === 'activity'">📊 Activity</span>
            <span v-else-if="tab === 'academy'">📚 Academy</span>
            <span v-else-if="tab === 'trophy_case'">🏆 Trophy Case</span>
          </button>
        </div>

        <!-- TAB 1: OVERVIEW -->
        <div v-if="activeTab === 'overview'" class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="md:col-span-2 glass-panel p-6 space-y-6">
            <h3 class="text-sm font-mono font-bold uppercase text-white border-b border-slate-800 pb-2">Bio & Focus Areas</h3>
            <p class="text-slate-300 text-sm leading-relaxed whitespace-pre-line">{{ profile.overview.bio || 'No bio specified.' }}</p>

            <div class="pt-4 border-t border-slate-800 space-y-3">
              <h4 class="text-xs font-mono uppercase text-slate-400">Skills Taxonomy</h4>
              <div v-if="profile.overview.skills && profile.overview.skills.length" class="flex flex-wrap gap-2">
                <span v-for="skill in profile.overview.skills" :key="skill" class="px-2.5 py-1 text-xs font-mono rounded-lg bg-cyan-950/40 text-cyan-400 border border-cyan-500/30">
                  #{{ skill }}
                </span>
              </div>
              <p v-else class="text-xs text-slate-500 font-mono">No skill tags listed.</p>
            </div>
          </div>

          <div class="glass-panel p-6 space-y-4">
            <h3 class="text-sm font-mono font-bold uppercase text-white border-b border-slate-800 pb-2">Academic & Contact Info</h3>
            <div class="space-y-3 text-xs font-mono">
              <div>
                <span class="text-slate-500 block">Academic Year:</span>
                <span class="text-cyan-400 font-bold">Year {{ profile.overview.academic_year || 'N/A' }}</span>
              </div>
              <div>
                <span class="text-slate-500 block">Department:</span>
                <span class="text-white">{{ profile.overview.department || 'Cyber Security' }}</span>
              </div>
              <div class="pt-2 border-t border-slate-800/80">
                <span class="text-amber-400 font-bold block mb-1">🔒 Private Contact Info (Admins/Teachers)</span>
                <p class="text-slate-300">📧 Gmail: <span class="text-white font-semibold">{{ profile.overview.gmail || profile.overview.email }}</span></p>
                <p class="text-slate-300 mt-1">📱 Phone: <span class="text-white font-semibold">{{ profile.overview.phone_number || 'Not provided' }}</span></p>
              </div>
              <div class="pt-2 border-t border-slate-800/80">
                <span class="text-slate-500 block">Status:</span>
                <span class="text-emerald-400 font-bold uppercase">{{ profile.overview.status }}</span>
              </div>
              <div>
                <span class="text-slate-500 block">Joined:</span>
                <span class="text-white">{{ new Date(profile.overview.created_at).toLocaleDateString() }}</span>
              </div>
              <div>
                <span class="text-slate-500 block">Last Seen:</span>
                <span class="text-cyan-400">{{ profile.overview.last_seen_at ? new Date(profile.overview.last_seen_at).toLocaleString() : 'Never' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 2: ACTIVITY CHART -->
        <div v-if="activeTab === 'activity'" class="glass-panel p-8 space-y-8">
          <div class="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h3 class="text-lg font-bold text-white">30-Day Activity Matrix</h3>
              <p class="text-xs text-slate-400">Active hours accrued across HackerXploit subdomains.</p>
            </div>

            <div class="flex gap-4 font-mono text-xs">
              <span class="text-cyan-400">Club: {{ profile.activity.subdomain_breakdown.club }}h</span>
              <span class="text-purple-400">CTF: {{ profile.activity.subdomain_breakdown.ctf }}h</span>
              <span class="text-emerald-400">Intro: {{ profile.activity.subdomain_breakdown.intro }}h</span>
            </div>
          </div>

          <!-- CSS Bar Chart Visualization -->
          <div class="h-48 flex items-end gap-1 sm:gap-2 pt-8 pb-2 px-2 border-b border-slate-800">
            <div v-for="point in profile.activity.chart_data" :key="point.date" class="flex-1 flex flex-col items-center group relative">
              <div class="w-full bg-cyan-500/30 group-hover:bg-cyan-400 rounded-t transition-all" :style="{ height: Math.min(point.hours * 25 + 4, 180) + 'px' }"></div>
              <div class="absolute -top-8 hidden group-hover:block bg-slate-900 text-cyan-400 text-[10px] font-mono px-2 py-0.5 rounded border border-cyan-500/40 z-10 whitespace-nowrap shadow-lg">
                {{ point.date }}: {{ point.hours }}h
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 3: ACADEMY PROGRESS -->
        <div v-if="activeTab === 'academy'" class="space-y-4">
          <div v-if="profile.academy.length === 0" class="glass-panel p-8 text-center text-slate-400">
            No enrolled courses yet.
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div v-for="course in profile.academy" :key="course.course_id" class="glass-panel p-6 space-y-4 flex flex-col justify-between">
              <div class="space-y-3">
                <div class="flex justify-between items-start">
                  <h4 class="font-bold text-white text-base">{{ course.title }}</h4>
                  <span v-if="course.completed_at" class="text-[10px] font-mono px-2 py-0.5 rounded border border-emerald-500/40 bg-emerald-950/30 text-emerald-400">COMPLETED</span>
                </div>

                <div class="space-y-1">
                  <div class="flex justify-between text-xs font-mono text-slate-400">
                    <span>Progress</span>
                    <span>{{ course.progress_percent }}%</span>
                  </div>
                  <div class="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
                    <div class="bg-cyan-400 h-full rounded-full transition-all" :style="{ width: course.progress_percent + '%' }"></div>
                  </div>
                </div>
              </div>

              <div v-if="course.certificate" class="pt-3 border-t border-slate-800 flex justify-between items-center text-xs font-mono">
                <span class="text-slate-400">📜 Course Certificate</span>
                <a :href="course.certificate.file_path" target="_blank" class="text-cyan-400 hover:underline">Download PDF →</a>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 4: TROPHY CASE -->
        <div v-if="activeTab === 'trophy_case'" class="space-y-6">
          <div v-if="profile.trophy_case.length === 0" class="glass-panel p-12 text-center text-slate-400">
            No competition records or trophies found.
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div v-for="item in profile.trophy_case" :key="item.participation_id" class="glass-panel p-6 space-y-4 border-l-4" :class="getTrophyBorderClass(item.result)">
              <div class="flex justify-between items-start">
                <div>
                  <span class="text-[10px] font-mono uppercase px-2 py-0.5 rounded border border-slate-700 bg-slate-900 text-slate-300">
                    {{ item.category }}
                  </span>
                  <h4 class="font-bold text-white text-lg mt-1">{{ item.competition_title }}</h4>
                </div>

                <span :class="getResultBadgeClass(item.result)" class="text-xs font-mono px-3 py-1 rounded-lg border font-bold uppercase">
                  🏆 {{ item.result }}
                </span>
              </div>

              <div v-if="item.application_screenshot" class="pt-2">
                <p class="text-[11px] font-mono text-slate-400 mb-1">Verification Screenshot:</p>
                <img :src="item.application_screenshot" class="w-full h-36 object-cover rounded-xl border border-slate-800" />
              </div>

              <p v-if="item.summary_notes" class="text-xs text-slate-300 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                "{{ item.summary_notes }}"
              </p>

              <div v-if="item.certificate" class="pt-3 border-t border-slate-800/80 flex justify-between items-center text-xs font-mono">
                <span class="text-amber-400 font-bold">📜 Winner Certificate</span>
                <a :href="item.certificate.file_path" target="_blank" class="btn-neon-cyan text-[11px] px-3 py-1">Download PDF</a>
              </div>
            </div>
          </div>
        </div>
      </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import axios from 'axios'

const route = useRoute()
const activeTab = ref('overview')
const profile = ref(null)
const loading = ref(true)

const fetchProfile = async () => {
  loading.value = true
  const userId = route.params.id
  try {
    const res = await axios.get(`/api/teacher/students/${userId}`)
    profile.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const getResultBadgeClass = (res) => {
  if (res === 'winner') return 'border-amber-500/50 bg-amber-950/40 text-amber-300'
  if (res === 'runner_up') return 'border-slate-400/50 bg-slate-900 text-slate-200'
  return 'border-cyan-500/40 bg-cyan-950/30 text-cyan-400'
}

const getTrophyBorderClass = (res) => {
  if (res === 'winner') return 'border-amber-500'
  if (res === 'runner_up') return 'border-slate-400'
  return 'border-cyan-500'
}

onMounted(() => {
  fetchProfile()
})
</script>
