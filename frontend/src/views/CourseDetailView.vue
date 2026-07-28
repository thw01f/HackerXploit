<template>
  <div class="max-w-7xl mx-auto px-4 py-8 text-slate-100">
    <div v-if="loading" class="text-center py-20 text-slate-400 animate-pulse">
      Loading course contents...
    </div>

    <div v-else-if="error" class="bg-rose-500/10 border border-rose-500/30 text-rose-400 p-6 rounded-2xl text-center">
      {{ error }}
    </div>

    <div v-else class="space-y-8">
      <!-- Course Header Banner -->
      <div class="bg-slate-900/80 p-8 rounded-3xl border border-slate-800 backdrop-blur-md relative overflow-hidden">
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
          <div class="space-y-2">
            <span class="text-xs font-semibold text-cyan-400 uppercase tracking-wider">HackerXploit Academy</span>
            <h1 class="text-3xl md:text-4xl font-extrabold text-slate-100 tracking-tight">{{ course.title }}</h1>
            <p class="text-slate-400 text-sm max-w-2xl">{{ course.description }}</p>
            <div class="flex items-center gap-4 text-xs text-slate-500 pt-2">
              <span>Author: <strong class="text-slate-300">{{ course.author_name }}</strong></span>
              <span>Chapters: <strong class="text-slate-300">{{ course.chapters?.length || 0 }}</strong></span>
            </div>
          </div>

          <!-- Progress Bar & Enroll Button -->
          <div class="w-full md:w-72 bg-slate-950 p-5 rounded-2xl border border-slate-800 space-y-3">
            <div class="flex items-center justify-between text-xs">
              <span class="font-semibold text-slate-300">Course Progress</span>
              <span class="text-cyan-400 font-bold">{{ enrollment?.progress_percent || 0 }}%</span>
            </div>
            <div class="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
              <div 
                class="bg-gradient-to-r from-cyan-400 to-indigo-500 h-full transition-all duration-500" 
                :style="{ width: `${enrollment?.progress_percent || 0}%` }"></div>
            </div>

            <button 
              v-if="!enrollment" 
              @click="enrollCourse" 
              class="w-full py-2.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs uppercase tracking-wider rounded-xl transition-all">
              Enroll in Course
            </button>
            <div v-else-if="enrollment.progress_percent >= 100" class="text-center text-xs text-emerald-400 font-semibold flex items-center justify-center gap-1">
              <CheckCircle class="w-4 h-4" /> Course Completed!
            </div>
          </div>
        </div>
      </div>

      <!-- Main Reader Layout: Sidebar + Chapter Content -->
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <!-- Sidebar Chapter Navigation -->
        <div class="lg:col-span-1 space-y-3">
          <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider px-2">Table of Contents</h3>
          <div class="space-y-1.5">
            <button 
              v-for="(ch, idx) in course.chapters" 
              :key="ch.id" 
              @click="activeChapterIndex = idx"
              :class="[activeChapterIndex === idx ? 'bg-cyan-500/10 border-cyan-500/40 text-cyan-300' : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:text-slate-200']"
              class="w-full text-left p-3.5 rounded-xl border transition-all flex items-center justify-between group">
              <div class="flex items-center gap-3">
                <span class="w-6 h-6 rounded-lg bg-slate-800 text-slate-300 flex items-center justify-center text-xs font-bold">{{ ch.order_index }}</span>
                <span class="text-sm font-medium truncate max-w-[150px]">{{ ch.title }}</span>
              </div>
              <CheckCircle v-if="isChapterCompleted(ch.id)" class="w-4 h-4 text-emerald-400 flex-shrink-0" />
            </button>
          </div>
        </div>

        <!-- Chapter Reader Body -->
        <div v-if="activeChapter" class="lg:col-span-3 space-y-8">
          <div class="bg-slate-950 p-8 md:p-12 rounded-3xl border border-slate-800 shadow-2xl space-y-6">
            <!-- Chapter Title & Reading Info -->
            <div class="flex items-center justify-between border-b border-slate-800 pb-6">
              <div>
                <span class="text-xs font-semibold text-cyan-400 uppercase">Chapter {{ activeChapter.order_index }}</span>
                <h2 class="text-2xl md:text-3xl font-bold text-slate-100 tracking-tight mt-1">{{ activeChapter.title }}</h2>
              </div>
              <div class="flex items-center gap-2 text-xs text-slate-400 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800">
                <Clock class="w-3.5 h-3.5 text-cyan-400" />
                <span>{{ activeChapter.read_time_minutes }} min read</span>
              </div>
            </div>

            <!-- Sanitized Medium-style Content HTML -->
            <div 
              class="prose prose-invert max-w-none text-slate-300 leading-relaxed space-y-4 font-sans text-base"
              v-html="activeChapter.sanitized_html"></div>

            <!-- Attachments Section (Nginx X-Accel-Redirect Gated) -->
            <div v-if="activeChapter.attachments?.length" class="pt-6 border-t border-slate-800 space-y-3">
              <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Chapter Attachments</h4>
              <div class="flex flex-wrap gap-3">
                <a 
                  v-for="att in activeChapter.attachments" 
                  :key="att.name" 
                  :href="`/api/academy/attachments/${activeChapter.id}/${att.name}`" 
                  target="_blank" 
                  class="bg-slate-900 hover:bg-slate-800 border border-slate-800 px-4 py-2 rounded-xl text-xs font-medium text-cyan-400 hover:text-cyan-300 flex items-center gap-2 transition-all">
                  <Download class="w-4 h-4" /> {{ att.name }}
                </a>
              </div>
            </div>

            <!-- Mark Chapter Complete Action -->
            <div class="pt-8 border-t border-slate-800 flex items-center justify-between">
              <span class="text-xs text-slate-500">Read through the chapter content before marking complete</span>
              <button 
                @click="markComplete(activeChapter.id)" 
                :disabled="completing"
                :class="[isChapterCompleted(activeChapter.id) ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white']"
                class="px-6 py-3 rounded-xl font-semibold text-sm transition-all flex items-center gap-2 border">
                <CheckCircle class="w-4 h-4" /> 
                {{ isChapterCompleted(activeChapter.id) ? 'Completed' : (completing ? 'Updating...' : 'Mark Chapter Complete') }}
              </button>
            </div>
          </div>

          <!-- Chapter Comments Section -->
          <div class="bg-slate-900/60 p-8 rounded-3xl border border-slate-800 backdrop-blur-md space-y-6">
            <h3 class="text-lg font-bold text-slate-100 flex items-center gap-2">
              <MessageSquare class="w-5 h-5 text-cyan-400" /> Discussion & Comments
            </h3>

            <!-- Add Comment Form -->
            <div class="flex items-start gap-3">
              <textarea 
                v-model="newComment" 
                rows="2" 
                placeholder="Ask a question or share thoughts about this chapter..." 
                class="flex-1 bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-slate-200 placeholder-slate-600 text-sm focus:outline-none focus:border-cyan-500"></textarea>
              <button 
                @click="postComment" 
                :disabled="!newComment.trim()" 
                class="px-5 py-3 bg-cyan-500 hover:bg-cyan-400 disabled:opacity-40 text-slate-950 font-bold text-xs uppercase tracking-wider rounded-xl transition-all">
                Post
              </button>
            </div>

            <!-- Comments List -->
            <div class="space-y-4 pt-4 border-t border-slate-800/80">
              <div 
                v-for="cmt in comments" 
                :key="cmt.id" 
                class="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 flex items-start justify-between gap-4">
                <div class="space-y-1">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-bold text-slate-200">{{ cmt.username }}</span>
                    <span class="text-[10px] text-slate-500">{{ formatDate(cmt.created_at) }}</span>
                  </div>
                  <p class="text-slate-300 text-sm leading-relaxed">{{ cmt.body }}</p>
                </div>
                <button 
                  @click="reportComment(cmt.id)" 
                  :disabled="cmt.is_reported"
                  title="Report inappropriate comment"
                  class="text-slate-500 hover:text-rose-400 transition-colors p-1">
                  <Flag class="w-4 h-4" :class="{'text-rose-400': cmt.is_reported}" />
                </button>
              </div>
              <div v-if="!comments.length" class="text-center py-6 text-slate-500 text-sm">
                No comments yet. Be the first to start the discussion!
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { CheckCircle, Clock, Download, MessageSquare, Flag } from 'lucide-vue-next'

const route = useRoute()
const course = ref({})
const enrollment = ref(null)
const activeChapterIndex = ref(0)
const comments = ref([])
const newComment = ref('')
const loading = ref(true)
const completing = ref(false)
const error = ref('')

const activeChapter = computed(() => {
  return course.value.chapters?.[activeChapterIndex.value] || null
})

const fetchCourse = async () => {
  loading.value = true
  try {
    const res = await axios.get(`/api/academy/course/${route.params.slug}`, { withCredentials: true })
    course.value = res.data
    enrollment.value = res.data.enrollment
    if (activeChapter.value) {
      await fetchComments(activeChapter.value.id)
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load course details.'
  } finally {
    loading.value = false
  }
}

const fetchComments = async (chapterId) => {
  try {
    const res = await axios.get(`/api/academy/chapters/${chapterId}/comments`, { withCredentials: true })
    comments.value = res.data.comments || []
  } catch (err) {
    console.error('Failed to load comments:', err)
  }
}

const enrollCourse = async () => {
  try {
    const res = await axios.post(`/api/academy/courses/${course.value.id}/enroll`, {}, { withCredentials: true })
    enrollment.value = res.data
  } catch (err) {
    console.error('Enrollment failed:', err)
  }
}

const isChapterCompleted = (chapterId) => {
  return enrollment.value?.completed_chapters?.includes(chapterId)
}

const markComplete = async (chapterId) => {
  completing.value = true
  try {
    const res = await axios.post(`/api/academy/chapters/${chapterId}/complete`, {}, { withCredentials: true })
    enrollment.value = res.data
  } catch (err) {
    console.error('Failed to complete chapter:', err)
  } finally {
    completing.value = false
  }
}

const postComment = async () => {
  if (!newComment.value.trim() || !activeChapter.value) return
  try {
    await axios.post(`/api/academy/chapters/${activeChapter.value.id}/comments`, { body: newComment.value }, { withCredentials: true })
    newComment.value = ''
    await fetchComments(activeChapter.value.id)
  } catch (err) {
    console.error('Failed to post comment:', err)
  }
}

const reportComment = async (commentId) => {
  try {
    await axios.post(`/api/academy/comments/${commentId}/report`, {}, { withCredentials: true })
    await fetchComments(activeChapter.value.id)
  } catch (err) {
    console.error('Failed to report comment:', err)
  }
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

watch(activeChapterIndex, async (newIdx) => {
  const ch = course.value.chapters?.[newIdx]
  if (ch) {
    await fetchComments(ch.id)
  }
})

onMounted(() => {
  fetchCourse()
})
</script>
