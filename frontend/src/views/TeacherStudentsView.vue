<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full space-y-8">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 class="text-3xl font-extrabold text-white flex items-center gap-3">
            <span class="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </span>
            Student Roster & Profiles
          </h1>
          <p class="text-slate-400 text-sm mt-1">Search, monitor activity levels, and review student progress across Academy and Competitions.</p>
        </div>

        <div class="flex items-center gap-2 font-mono text-xs">
          <span class="text-slate-400">Filter Activity:</span>
          <button v-for="level in ['all', 'high', 'medium', 'low']" :key="level" @click="setActivityFilter(level)" :class="activeLevel === level ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/50' : 'bg-slate-900 text-slate-400 border-slate-800'" class="px-3 py-1.5 rounded-lg border uppercase transition-colors">
            {{ level }}
          </button>
        </div>
      </div>

      <!-- Search Bar -->
      <div class="glass-panel p-4 flex flex-col sm:flex-row gap-4 items-center">
        <div class="relative flex-1 w-full">
          <input v-model="searchQuery" @input="fetchStudents" type="text" placeholder="Search by name, student ID, email, or username..." class="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm text-white focus:border-cyan-500 focus:outline-none pl-10" />
          <svg class="w-5 h-5 text-slate-500 absolute left-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      <!-- Roster Grid -->
      <div v-if="loading" class="text-center py-12 text-slate-500 font-mono text-sm">
        Loading student roster...
      </div>

      <div v-else-if="students.length === 0" class="glass-panel p-12 text-center text-slate-400">
        No student profiles match your search criteria.
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="student in students" :key="student.id" class="glass-panel p-6 space-y-4 hover:border-cyan-500/40 transition-all flex flex-col justify-between">
          <div class="space-y-4">
            <div class="flex items-center space-x-4">
              <img :src="student.avatar_url || '/uploads/avatars/default.png'" class="w-14 h-14 rounded-2xl object-cover border border-cyan-500/30" />
              <div class="min-w-0 flex-1">
                <h3 class="font-bold text-white text-base truncate">{{ student.full_name || student.username }}</h3>
                <p class="text-xs font-mono text-cyan-400">@{{ student.username }}</p>
                <p v-if="student.student_id" class="text-[11px] font-mono text-slate-400">ID: {{ student.student_id }}</p>
              </div>
            </div>

            <!-- Badges & Activity Pill -->
            <div class="flex flex-wrap gap-2 pt-2 border-t border-slate-800">
              <span :class="getActivityBadgeClass(student.activity_level)" class="text-[10px] font-mono px-2 py-0.5 rounded border uppercase">
                ⚡ {{ student.total_activity_hours }}h Active
              </span>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded border border-purple-500/30 bg-purple-950/30 text-purple-400">
                📚 {{ student.enrollments_count }} Courses
              </span>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded border border-amber-500/30 bg-amber-950/30 text-amber-400">
                🏆 {{ student.competitions_count }} Comps
              </span>
            </div>
          </div>

          <div class="pt-4 border-t border-slate-800/80 flex items-center justify-between">
            <span class="text-[10px] text-slate-500 font-mono">
              Last seen: {{ student.last_seen_at ? new Date(student.last_seen_at).toLocaleDateString() : 'Never' }}
            </span>
            <router-link :to="`/teacher/students/${student.id}`" class="btn-neon-cyan text-xs py-1.5 px-4 font-mono font-bold">
              View Profile →
            </router-link>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

const searchQuery = ref('')
const activeLevel = ref('all')
const students = ref([])
const loading = ref(true)

const fetchStudents = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) params.q = searchQuery.value
    if (activeLevel.value !== 'all') params.activity_level = activeLevel.value

    const res = await axios.get('/api/teacher/students', { params })
    students.value = res.data.students
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const setActivityFilter = (level) => {
  activeLevel.value = level
  fetchStudents()
}

const getActivityBadgeClass = (level) => {
  if (level === 'high') return 'border-emerald-500/40 bg-emerald-950/30 text-emerald-400'
  if (level === 'medium') return 'border-cyan-500/40 bg-cyan-950/30 text-cyan-400'
  return 'border-slate-700 bg-slate-900 text-slate-400'
}

onMounted(() => {
  fetchStudents()
})
</script>
