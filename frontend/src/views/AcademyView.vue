<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full space-y-8">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-3xl font-extrabold text-white">HackerXploit Academy</h1>
          <p class="text-slate-400 text-sm mt-1">Enterprise cybersecurity learning paths & hands-on laboratory modules.</p>
        </div>
        <button v-if="authStore.isTeacher" @click="showCreateModal = true" class="btn-neon-violet text-xs py-2.5 px-5 flex items-center space-x-2">
          <span>+ Create New Course</span>
        </button>
      </div>

      <!-- Course Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div v-for="course in clubStore.courses" :key="course.id" class="glass-panel p-6 flex flex-col justify-between hover:border-cyan-500/40 transition-all">
          <div>
            <div class="flex items-center justify-between mb-3">
              <span class="text-[10px] font-mono uppercase bg-cyan-950 text-cyan-300 px-2.5 py-0.5 rounded border border-cyan-500/30">
                {{ course.category }}
              </span>
              <span class="text-xs text-slate-400 font-mono">{{ course.difficulty }}</span>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">{{ course.title }}</h3>
            <p class="text-slate-300 text-sm line-clamp-3 mb-6">{{ course.description }}</p>
          </div>

          <div class="pt-4 border-t border-slate-800 flex items-center justify-between">
            <span class="text-xs text-slate-400 font-mono">{{ course.modules_count || 0 }} Modules</span>
            <router-link :to="`/academy/course/${course.id}`" class="btn-neon-cyan text-xs py-1.5 px-4">
              Open Course
            </router-link>
          </div>
        </div>
      </div>

      <!-- Create Course Modal for Teachers -->
      <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
        <div class="w-full max-w-lg glass-panel p-6 rounded-2xl border border-cyan-500/30">
          <h3 class="text-xl font-bold text-white mb-4">Create Academy Course</h3>
          <form @submit.prevent="handleCreateCourse" class="space-y-4">
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Course Title</label>
              <input v-model="newCourse.title" type="text" required class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" />
            </div>
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Category</label>
              <input v-model="newCourse.category" type="text" placeholder="Web Security, Reverse Engineering" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" />
            </div>
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Difficulty</label>
              <select v-model="newCourse.difficulty" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm">
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Description</label>
              <textarea v-model="newCourse.description" rows="3" required class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm"></textarea>
            </div>
            <div class="flex justify-end space-x-3 pt-4">
              <button type="button" @click="showCreateModal = false" class="btn-ghost text-xs py-2 px-4">Cancel</button>
              <button type="submit" class="btn-neon-cyan text-xs py-2 px-4">Publish Course</button>
            </div>
          </form>
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
import { useAuthStore } from '../stores/auth'
import { useClubStore } from '../stores/club'

const authStore = useAuthStore()
const clubStore = useClubStore()

const showCreateModal = ref(false)
const newCourse = ref({
  title: '',
  category: 'Web Security',
  difficulty: 'Beginner',
  description: '',
  is_published: true
})

onMounted(() => {
  clubStore.fetchCourses()
})

const handleCreateCourse = async () => {
  try {
    await axios.post('/api/academy/courses', newCourse.value)
    showCreateModal.value = false
    newCourse.value = { title: '', category: 'Web Security', difficulty: 'Beginner', description: '', is_published: true }
    await clubStore.fetchCourses()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to create course')
  }
}
</script>
