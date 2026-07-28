<template>
  <div class="max-w-6xl mx-auto px-4 py-8 text-slate-100">
    <div class="mb-8">
      <h1 class="text-3xl font-bold tracking-tight bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
        My Enrolled Courses & Certificates
      </h1>
      <p class="text-slate-400 text-sm mt-1">Track learning progress across enrolled cybersecurity courses and download official completion certificates</p>
    </div>

    <div v-if="loading" class="text-center py-20 text-slate-400 animate-pulse">
      Loading your enrollments...
    </div>

    <div v-else-if="!enrollments.length" class="bg-slate-900/60 p-12 rounded-3xl border border-slate-800 text-center space-y-4">
      <BookOpen class="w-12 h-12 text-slate-600 mx-auto" />
      <h3 class="text-lg font-bold text-slate-200">No Enrolled Courses Found</h3>
      <p class="text-slate-400 text-sm">Explore the HackerXploit Academy catalog to start your learning journey!</p>
      <router-link to="/academy" class="inline-block px-6 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs uppercase tracking-wider rounded-xl transition-all">
        Browse Courses
      </router-link>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div 
        v-for="item in enrollments" 
        :key="item.id" 
        class="bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-md flex flex-col justify-between space-y-6">
        <div>
          <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>Enrolled {{ formatDate(item.created_at) }}</span>
            <span class="text-cyan-400 font-bold">{{ item.progress_percent }}% Complete</span>
          </div>
          <h2 class="text-xl font-bold text-slate-100">{{ item.course?.title || 'Academy Course' }}</h2>
          <p class="text-slate-400 text-sm line-clamp-2 mt-1">{{ item.course?.description }}</p>
        </div>

        <!-- Progress Bar -->
        <div class="space-y-2">
          <div class="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-slate-800">
            <div 
              class="bg-gradient-to-r from-cyan-400 to-indigo-500 h-full transition-all duration-500" 
              :style="{ width: `${item.progress_percent}%` }"></div>
          </div>
        </div>

        <!-- Actions: Resume Course & Download Certificate PDF -->
        <div class="flex items-center justify-between pt-2 border-t border-slate-800/80">
          <router-link 
            :to="`/academy/course/${item.course?.slug}`" 
            class="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1">
            Resume Learning <ArrowRight class="w-4 h-4" />
          </router-link>

          <a 
            v-if="item.certificate?.file_path" 
            :href="item.certificate.file_path" 
            target="_blank" 
            class="px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20 text-xs font-bold rounded-xl transition-all flex items-center gap-1.5">
            <Award class="w-4 h-4" /> Download Certificate (PDF)
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { BookOpen, ArrowRight, Award } from 'lucide-vue-next'

const enrollments = ref([])
const loading = ref(true)

const fetchMyCourses = async () => {
  try {
    const res = await axios.get('/api/academy/my-courses', { withCredentials: true })
    enrollments.value = res.data.enrollments || []
  } catch (err) {
    console.error('Failed to load my courses:', err)
  } finally {
    loading.value = false
  }
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

onMounted(() => {
  fetchMyCourses()
})
</script>
