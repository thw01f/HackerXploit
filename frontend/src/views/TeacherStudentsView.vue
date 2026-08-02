<template>
  <div class="space-y-8">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 class="text-3xl font-extrabold text-white flex items-center gap-3">
            <span class="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </span>
            Students & Profiles
          </h1>
          <p class="text-slate-400 text-sm mt-1">Search, monitor activity levels, review student progress, and edit details.</p>
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
          <input v-model="searchQuery" @input="fetchStudents" type="text" placeholder="Search by name, student ID, email, or username..." class="w-full bg-slate-900 border border-slate-700/80 rounded-xl pr-4 !pl-11 py-2.5 text-sm text-white focus:border-cyan-500 focus:outline-none" />
          <svg class="w-5 h-5 text-slate-500 absolute left-3.5 top-3 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      <!-- Roster Grid -->
      <div v-if="loading" class="text-center py-12 text-slate-500 font-mono text-sm">
        Loading student directory...
      </div>

      <div v-else-if="students.length === 0" class="glass-panel p-12 text-center text-slate-400">
        No student profiles match your search criteria.
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="student in students" :key="student.id" class="glass-panel p-6 space-y-4 hover:border-cyan-500/40 transition-all flex flex-col justify-between">
          <div class="space-y-4">
            <div class="flex items-center space-x-4">
              <img :src="student.avatar_url || defaultAvatarSvg" @error="(e) => e.target.src = defaultAvatarSvg" class="w-14 h-14 rounded-2xl object-cover border border-cyan-500/30" />
              <div class="min-w-0 flex-1">
                <h3 class="font-bold text-white text-base truncate">{{ student.full_name || student.username }}</h3>
                <p class="text-xs font-mono text-cyan-400">@{{ student.username }}</p>
                <p v-if="student.student_id" class="text-xs font-mono text-slate-400">ID: {{ student.student_id }}</p>
              </div>
            </div>

            <!-- Badges & Activity Pill -->
            <div class="flex flex-wrap gap-2 pt-2 border-t border-slate-800">
              <span :class="getActivityBadgeClass(student.activity_level)" class="text-[11px] font-mono px-2 py-0.5 rounded border uppercase">
                {{ student.total_activity_hours }}h Active
              </span>
              <span class="text-[11px] font-mono px-2 py-0.5 rounded border border-purple-500/30 bg-purple-950/30 text-purple-400">
                {{ student.enrollments_count }} Courses
              </span>
              <span class="text-[11px] font-mono px-2 py-0.5 rounded border border-amber-500/30 bg-amber-950/30 text-amber-400">
                {{ student.competitions_count }} Comps
              </span>
            </div>
          </div>

          <div class="pt-4 border-t border-slate-800/80 flex items-center justify-between gap-2">
            <button @click="openEditStudentModal(student)" class="btn-ghost text-xs py-1.5 px-3 text-[#00f0ff] border border-[#00f0ff]/40 hover:bg-[#00f0ff]/10 font-mono font-bold">
              ✏️ Edit Details
            </button>
            <router-link :to="`/teacher/students/${student.id}`" class="btn-neon-cyan text-xs py-1.5 px-4 font-mono font-bold">
              View Profile →
            </router-link>
          </div>
        </div>
      </div>

      <!-- Edit Student Details Modal -->
      <div v-if="showEditModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm font-mono">
        <div class="w-full max-w-md glass-panel p-6 rounded-2xl border border-slate-800 bg-[#0d1420] space-y-4">
          <h3 class="text-lg font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
            <span class="text-[#00f0ff]">✏️ Edit Student Details</span>
          </h3>

          <form @submit.prevent="saveStudentDetails" class="space-y-3 text-xs">
            <div>
              <label class="block text-slate-400 uppercase mb-1">Full Name</label>
              <input v-model="editForm.full_name" type="text" class="input-field w-full py-2" required />
            </div>

            <div>
              <label class="block text-slate-400 uppercase mb-1">Email Address</label>
              <input v-model="editForm.email" type="email" class="input-field w-full py-2" required />
            </div>

            <div>
              <label class="block text-slate-400 uppercase mb-1">Student / Member ID</label>
              <input v-model="editForm.student_id" type="text" placeholder="e.g. STU-2026-042" class="input-field w-full py-2" />
            </div>

            <div>
              <label class="block text-slate-400 uppercase mb-1">Specialization Track</label>
              <select v-model="editForm.specialization_role" class="input-field w-full py-2 bg-[#0b0e14]">
                <option value="Penetration Tester">Penetration Tester</option>
                <option value="Security Analyst">Security Analyst</option>
                <option value="Malware Analyst">Malware Analyst</option>
                <option value="Red Teamer">Red Teamer</option>
                <option value="Digital Forensics Specialist">Digital Forensics Specialist</option>
              </select>
            </div>

            <div v-if="authStore.isAdmin">
              <label class="block text-slate-400 uppercase mb-1">Account Role</label>
              <select v-model="editForm.role" class="input-field w-full py-2 bg-[#0b0e14]">
                <option value="member">Student / Member</option>
                <option value="teacher">Teacher / Faculty</option>
                <option value="admin">Platform Admin</option>
              </select>
            </div>

            <div class="flex justify-end space-x-3 pt-3 border-t border-slate-800">
              <button type="button" @click="showEditModal = false" class="btn-ghost py-1.5 px-4">Cancel</button>
              <button type="submit" :disabled="saving" class="btn-htb py-1.5 px-5 font-bold uppercase">
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
      </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const searchQuery = ref('')
const activeLevel = ref('all')
const students = ref([])
const loading = ref(true)

const showEditModal = ref(false)
const saving = ref(false)
const editingStudentId = ref(null)
const editForm = ref({ full_name: '', email: '', student_id: '', specialization_role: 'Penetration Tester', role: 'member' })

const defaultAvatarSvg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'><rect width='100' height='100' fill='%230b0e14'/><circle cx='50' cy='38' r='20' fill='%231f293d' stroke='%239fef00' stroke-width='2'/><path d='M20,85 C20,62 35,55 50,55 C65,55 80,62 80,85 Z' fill='%231f293d' stroke='%239fef00' stroke-width='2'/></svg>"

const openEditStudentModal = (student) => {
  editingStudentId.value = student.id
  editForm.value = {
    full_name: student.full_name || '',
    email: student.email || '',
    student_id: student.student_id || '',
    specialization_role: student.specialization_role || 'Penetration Tester',
    role: student.role || 'member'
  }
  showEditModal.value = true
}

const saveStudentDetails = async () => {
  saving.value = true
  try {
    await axios.put(`/api/admin/users/${editingStudentId.value}/update`, editForm.value, { withCredentials: true })
    showEditModal.value = false
    await fetchStudents()
  } catch (err) {
    alert('Failed to update student details: ' + (err.response?.data?.error || err.message))
  } finally {
    saving.value = false
  }
}

const fetchStudents = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) params.q = searchQuery.value
    if (activeLevel.value !== 'all') params.activity_level = activeLevel.value

    const res = await axios.get('/api/teacher/students', { params })
    let raw = res.data.students || []
    
    // Strict filter for teachers: only display real student accounts
    if (!authStore.isAdmin) {
      raw = raw.filter(s => 
        s.role !== 'admin' && 
        s.role !== 'root_admin' && 
        s.role !== 'teacher' && 
        s.role !== 'teacher_admin' && 
        !s.is_root_admin
      )
    }
    students.value = raw
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
