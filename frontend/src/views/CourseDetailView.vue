<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full space-y-8">
      <div v-if="course" class="space-y-8">
        <!-- Header -->
        <div class="glass-panel p-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <span class="text-xs font-mono text-cyan-400 font-bold uppercase">{{ course.category }}</span>
            <h1 class="text-3xl font-extrabold text-white mt-1">{{ course.title }}</h1>
            <p class="text-slate-300 text-sm mt-2 max-w-2xl">{{ course.description }}</p>
          </div>

          <div v-if="enrollment" class="w-full md:w-auto glass-panel p-4 text-center">
            <span class="block text-xs text-slate-400 font-mono">PROGRESS</span>
            <span class="block text-2xl font-bold text-cyan-400 font-mono">{{ progressPercentage }}%</span>
            <a v-if="enrollment.is_completed" :href="enrollment.certificate_url" target="_blank" class="mt-2 inline-block btn-neon-violet text-xs py-1 px-3">
              Download Certificate
            </a>
          </div>
          <button v-else @click="handleEnroll" class="btn-neon-cyan text-sm py-2 px-6">
            Enroll In Course
          </button>
        </div>

        <!-- Modules & Lesson Player Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Sidebar: Module & Lesson List -->
          <div class="space-y-4">
            <div v-for="module in course.modules" :key="module.id" class="glass-panel p-4">
              <h4 class="font-bold text-white text-sm mb-3 border-b border-slate-800 pb-2">{{ module.title }}</h4>
              <div class="space-y-2">
                <button 
                  v-for="lesson in module.lessons" 
                  :key="lesson.id" 
                  @click="selectedLesson = lesson"
                  class="w-full text-left p-2.5 rounded-lg text-xs flex items-center justify-between transition-colors"
                  :class="selectedLesson?.id === lesson.id ? 'bg-cyan-950 text-cyan-300 border border-cyan-500/40 font-semibold' : 'text-slate-300 hover:bg-slate-800/60'"
                >
                  <span class="truncate">{{ lesson.title }}</span>
                  <span v-if="isLessonCompleted(lesson.id)" class="text-emerald-400 font-bold">✓</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Main Content: Active Lesson Reader -->
          <div class="lg:col-span-2 glass-panel p-8 space-y-6">
            <template v-if="selectedLesson">
              <div class="flex justify-between items-center border-b border-slate-800 pb-4">
                <h2 class="text-2xl font-bold text-white">{{ selectedLesson.title }}</h2>
                <button @click="markCompleted(selectedLesson.id)" class="btn-neon-cyan text-xs py-1.5 px-4">
                  {{ isLessonCompleted(selectedLesson.id) ? 'Completed ✓' : 'Mark as Complete' }}
                </button>
              </div>

              <!-- Lesson Body -->
              <div class="prose prose-invert max-w-none text-slate-300 text-sm whitespace-pre-line leading-relaxed font-sans">
                {{ selectedLesson.content_markdown }}
              </div>
            </template>
            <template v-else>
              <div class="text-center py-20 text-slate-500">
                Select a lesson from the module sidebar to begin learning.
              </div>
            </template>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

const route = useRoute()
const course = ref(null)
const enrollment = ref(null)
const selectedLesson = ref(null)

const courseId = route.params.id

const fetchCourse = async () => {
  try {
    const res = await axios.get(`/api/academy/courses/${courseId}`)
    course.value = res.data
    enrollment.value = res.data.enrollment
    if (res.data.modules?.length && res.data.modules[0].lessons?.length) {
      selectedLesson.value = res.data.modules[0].lessons[0]
    }
  } catch (err) {
    console.error('Failed to load course details', err)
  }
}

onMounted(fetchCourse)

const handleEnroll = async () => {
  try {
    const res = await axios.post(`/api/academy/courses/${courseId}/enroll`)
    enrollment.value = res.data
  } catch (err) {
    alert(err.response?.data?.error || 'Enrollment failed')
  }
}

const isLessonCompleted = (lessonId) => {
  return enrollment.value?.completed_lessons?.includes(lessonId) || false
}

const markCompleted = async (lessonId) => {
  try {
    const res = await axios.post(`/api/academy/lessons/${lessonId}/complete`)
    enrollment.value = res.data
  } catch (err) {
    alert('Failed to update progress')
  }
}

const progressPercentage = computed(() => {
  if (!course.value || !enrollment.value) return 0
  let total = 0
  course.value.modules?.forEach(m => total += m.lessons?.length || 0)
  if (total === 0) return 0
  return Math.round(((enrollment.value.completed_lessons?.length || 0) / total) * 100)
})
</script>
