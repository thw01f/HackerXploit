<template>
  <div class="min-h-screen bg-[#0b0e14] text-slate-100 font-sans pb-20 selection:bg-[#00f0ff] selection:text-black">
    
    <!-- Top Reading Progress Bar -->
    <div 
      class="fixed top-0 left-0 h-1 bg-gradient-to-r from-[#00f0ff] via-[#9fef00] to-[#00f0ff] z-50 transition-all duration-150"
      :style="{ width: `${scrollProgress}%` }"
    ></div>

    <!-- Main Container -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-8">
      
      <!-- Loading Skeleton -->
      <div v-if="loading" class="animate-pulse space-y-8">
        <div class="h-48 bg-[#151f30] rounded-3xl border border-[#1f293d]"></div>
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div class="lg:col-span-3 h-96 bg-[#151f30] rounded-2xl"></div>
          <div class="lg:col-span-9 h-[600px] bg-[#151f30] rounded-3xl"></div>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-rose-500/10 border border-rose-500/30 text-rose-400 p-6 rounded-2xl text-center font-mono">
        {{ error }}
      </div>

      <div v-else class="space-y-8">

        <!-- Course Top Banner Header -->
        <div class="glass-panel border border-[#1f293d] p-6 md:p-8 rounded-3xl bg-[#0d1420]/90 shadow-2xl relative overflow-hidden">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10 font-mono">
            
            <div class="space-y-2">
              <div class="flex items-center space-x-2 text-xs">
                <router-link to="/academy" class="text-[#00f0ff] hover:underline font-bold">&larr; Modules</router-link>
                <span class="text-slate-600">•</span>
                <span class="text-slate-400 uppercase tracking-wider font-semibold">MkDocs Documentation</span>
              </div>
              <h1 class="text-3xl md:text-4xl font-extrabold text-white tracking-tight font-serif">
                {{ course.title }}
              </h1>
              <p class="text-slate-300 text-xs md:text-sm max-w-3xl leading-relaxed font-sans">
                {{ course.description }}
              </p>
              <div class="flex items-center gap-4 text-[11px] text-slate-400 pt-2 font-mono">
                <span>Author: <strong class="text-[#00f0ff]">{{ course.author_name || 'HackerXploit Staff' }}</strong></span>
                <span>Chapters: <strong class="text-white">{{ course.chapters?.length || 0 }}</strong></span>
              </div>
            </div>

            <!-- Enrollment Card -->
            <div class="w-full md:w-64 bg-[#0b0e14] p-4 rounded-2xl border border-[#1f293d] space-y-3 flex-shrink-0">
              <div class="flex items-center justify-between text-xs font-mono">
                <span class="font-bold text-slate-300">Module Progress</span>
                <span class="text-[#9fef00] font-bold">{{ enrollment?.progress_percent || 0 }}%</span>
              </div>
              <div class="w-full bg-[#1f293d] h-2 rounded-full overflow-hidden">
                <div 
                  class="bg-gradient-to-r from-[#00f0ff] to-[#9fef00] h-full transition-all duration-500" 
                  :style="{ width: `${enrollment?.progress_percent || 0}%` }"
                ></div>
              </div>

              <button 
                v-if="!enrollment" 
                @click="enrollCourse" 
                class="btn-htb w-full py-2 text-xs font-bold uppercase tracking-wider"
              >
                Enroll in Module
              </button>
              <div v-else-if="enrollment.progress_percent >= 100" class="text-center text-xs text-[#9fef00] font-bold font-mono py-1">
                ✓ Module Completed!
              </div>
            </div>

          </div>
        </div>

        <!-- MkDocs Layout: Left Chapters Tree + Main Reader + Right TOC -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          <!-- Left Navigation Sidebar: Chapters List -->
          <div class="lg:col-span-3 glass-panel p-4 rounded-2xl border border-[#1f293d] bg-[#0d1420] space-y-3 sticky top-6 font-mono">
            <div class="flex items-center justify-between px-2">
              <h3 class="text-xs font-extrabold text-[#00f0ff] uppercase tracking-wider">Module Navigation</h3>
              <span class="text-[10px] text-slate-500">({{ course.chapters?.length || 0 }})</span>
            </div>
            
            <div class="space-y-1.5 max-h-[70vh] overflow-y-auto pr-1">
              <div 
                v-for="(ch, idx) in course.chapters" 
                :key="ch.id" 
                @click="activeChapterIndex = idx"
                :class="[
                  activeChapterIndex === idx ? 'bg-[#00f0ff]/15 border-[#00f0ff]/40 text-[#00f0ff] font-bold shadow-[0_0_10px_rgba(0,240,255,0.1)]' : 'bg-[#0b0e14] border-[#1f293d] text-slate-400 hover:text-white'
                ]"
                class="w-full text-left p-3 rounded-xl border transition-all flex items-center justify-between text-xs group cursor-pointer"
              >
                <div class="flex items-center space-x-2.5 truncate">
                  <span class="w-5 h-5 rounded bg-[#151f30] text-slate-300 flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                    {{ idx + 1 }}
                  </span>
                  <span class="truncate font-sans text-xs">{{ ch.title }}</span>
                </div>

                <div class="flex items-center space-x-1.5">
                  <span v-if="isChapterCompleted(ch.id)" class="text-[#9fef00] text-xs font-bold flex-shrink-0">✓</span>
                  
                  <!-- Teacher & Admin Note Reordering Controls -->
                  <div v-if="authStore.isTeacher" class="opacity-0 group-hover:opacity-100 flex items-center space-x-0.5 transition-opacity">
                    <button @click.stop="moveChapterUp(idx)" title="Move Note Up" class="hover:text-[#00f0ff] text-[10px] px-1 font-bold">▲</button>
                    <button @click.stop="moveChapterDown(idx)" title="Move Note Down" class="hover:text-[#00f0ff] text-[10px] px-1 font-bold">▼</button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Main MkDocs Article Reader -->
          <div v-if="activeChapter" class="lg:col-span-6 space-y-8">
            
            <article class="glass-panel p-6 md:p-10 rounded-3xl border border-[#1f293d] bg-[#0d1420] shadow-2xl space-y-8">
              
              <!-- Chapter Header -->
              <header class="space-y-4 border-b border-[#1f293d] pb-6">
                <div class="flex items-center justify-between font-mono text-xs text-[#00f0ff]">
                  <span>CHAPTER {{ activeChapterIndex + 1 }} OF {{ course.chapters?.length }}</span>
                  <span class="bg-[#151f30] px-3 py-1 rounded-full border border-[#1f293d] text-slate-300 flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span>{{ activeChapter.read_time_minutes }} min read</span>
                  </span>
                </div>

                <h1 class="text-3xl md:text-4xl font-extrabold text-white font-serif tracking-tight leading-tight">
                  {{ activeChapter.title }}
                </h1>
              </header>

              <!-- Markdown Body Output -->
              <main 
                class="mkdocs-content prose prose-invert max-w-none text-slate-200 leading-relaxed space-y-5 font-sans text-base border-b border-[#1f293d] pb-8"
                v-html="processedHtml"
              ></main>

              <!-- Gated Attachments -->
              <div v-if="activeChapter.attachments?.length" class="space-y-3 font-mono">
                <div class="flex items-center space-x-2 text-[#00f0ff]">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                  </svg>
                  <h4 class="text-xs font-bold uppercase tracking-wider">Lab Attachments & Resources</h4>
                </div>
                <div class="flex flex-wrap gap-3">
                  <a 
                    v-for="att in activeChapter.attachments" 
                    :key="att.name" 
                    :href="`/api/academy/attachments/${activeChapter.id}/${att.name}`" 
                    target="_blank" 
                    class="bg-[#0b0e14] hover:bg-[#151f30] border border-[#1f293d] hover:border-[#00f0ff] px-4 py-2.5 rounded-xl text-xs font-bold text-[#00f0ff] flex items-center space-x-2 transition-all shadow-md"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                    </svg>
                    <span>Download</span>
                    <span>{{ att.name }}</span>
                    <span class="text-[10px] text-slate-400 font-normal">({{ (att.size / 1024).toFixed(1) }} KB)</span>
                  </a>
                </div>
              </div>

              <!-- Chapter Navigation & Mark Complete -->
              <footer class="flex items-center justify-between pt-4 font-mono text-xs">
                <button 
                  @click="activeChapterIndex = Math.max(0, activeChapterIndex - 1)" 
                  :disabled="activeChapterIndex === 0" 
                  class="text-slate-400 hover:text-white disabled:opacity-30 disabled:hover:text-slate-400 flex items-center space-x-1"
                >
                  <span>&larr; Previous Chapter</span>
                </button>

                <button 
                  @click="markComplete(activeChapter.id)" 
                  :disabled="completing || isChapterCompleted(activeChapter.id)" 
                  class="btn-htb py-2 px-5 font-bold uppercase tracking-wider flex items-center gap-1.5"
                >
                  <span v-if="isChapterCompleted(activeChapter.id)" class="flex items-center gap-1">
                    <svg class="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                    </svg>
                    <span>Completed</span>
                  </span>
                  <span v-else>{{ completing ? 'Updating...' : 'Mark Chapter Complete' }}</span>
                </button>

                <button 
                  @click="activeChapterIndex = Math.min(course.chapters.length - 1, activeChapterIndex + 1)" 
                  :disabled="activeChapterIndex >= course.chapters.length - 1" 
                  class="text-slate-400 hover:text-white disabled:opacity-30 disabled:hover:text-slate-400 flex items-center space-x-1"
                >
                  <span>Next Chapter &rarr;</span>
                </button>
              </footer>

            </article>

            <!-- Comments & Discussion Area -->
            <section class="glass-panel p-6 rounded-3xl border border-[#1f293d] bg-[#0d1420] space-y-6">
              <h3 class="text-sm font-extrabold text-white font-mono uppercase tracking-wider flex items-center space-x-2">
                <svg class="w-4 h-4 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
                </svg>
                <span>Discussion & Help</span>
                <span class="text-xs text-slate-500">({{ comments.length }})</span>
              </h3>

              <!-- Comment Input Box -->
              <div class="space-y-3 font-mono">
                <textarea 
                  v-model="newComment" 
                  rows="3" 
                  placeholder="Ask a question or share notes about this chapter..." 
                  class="input-field text-xs w-full bg-[#0b0e14] p-3 border-[#1f293d] resize-none"
                ></textarea>
                <div class="flex justify-end">
                  <button 
                    @click="postComment" 
                    :disabled="!newComment.trim()" 
                    class="btn-htb text-xs py-1.5 px-4 font-bold uppercase tracking-wider disabled:opacity-50"
                  >
                    Post Comment
                  </button>
                </div>
              </div>

              <!-- Comments List -->
              <div class="space-y-4 pt-2">
                <div 
                  v-for="c in comments" 
                  :key="c.id" 
                  class="bg-[#0b0e14] border border-[#1f293d] p-4 rounded-2xl space-y-2 font-mono text-xs"
                >
                  <div class="flex items-center justify-between text-slate-400 text-[11px]">
                    <div class="flex items-center space-x-2">
                      <strong class="text-[#00f0ff] font-bold">{{ c.user_name || 'User' }}</strong>
                      <span class="text-slate-600">•</span>
                      <span>{{ formatDate(c.created_at) }}</span>
                    </div>
                    <button @click="reportComment(c.id)" class="text-slate-500 hover:text-rose-400 text-[10px] flex items-center gap-1">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"/>
                      </svg>
                      <span>Report</span>
                    </button>
                  </div>
                  <p class="text-slate-200 leading-relaxed font-sans text-sm">{{ c.body }}</p>
                </div>
              </div>
            </section>

          </div>

          <!-- Right Sidebar: MkDocs On-This-Page TOC -->
          <div class="lg:col-span-3 glass-panel p-4 rounded-2xl border border-[#1f293d] bg-[#0d1420] space-y-3 sticky top-6 font-mono text-xs hidden lg:block">
            <h3 class="text-xs font-extrabold text-slate-400 uppercase tracking-wider px-1">On This Page</h3>

            <nav class="space-y-1 max-h-[70vh] overflow-y-auto pr-1">
              <a 
                v-for="h in chapterHeadings" 
                :key="h.id" 
                :href="`#${h.id}`" 
                :class="[
                  'block py-1 hover:text-[#00f0ff] transition-colors truncate',
                  h.level === 1 ? 'font-bold text-white' : (h.level === 2 ? 'pl-3 text-slate-300' : 'pl-5 text-slate-400')
                ]"
              >
                {{ h.text }}
              </a>
            </nav>
            <div v-if="!chapterHeadings.length" class="text-xs text-slate-500 italic">No section headings found</div>
          </div>

        </div>

      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const route = useRoute()
const authStore = useAuthStore()
const course = ref({})
const enrollment = ref(null)
const activeChapterIndex = ref(0)
const comments = ref([])
const newComment = ref('')
const loading = ref(true)
const completing = ref(false)
const error = ref('')
const scrollProgress = ref(0)

const activeChapter = computed(() => {
  return course.value.chapters?.[activeChapterIndex.value] || null
})

// Move chapter UP in ordering
const moveChapterUp = async (idx) => {
  if (idx <= 0 || !course.value?.chapters) return
  const chapters = course.value.chapters
  const temp = chapters[idx]
  chapters[idx] = chapters[idx - 1]
  chapters[idx - 1] = temp

  chapters.forEach((ch, i) => ch.order_index = i + 1)
  activeChapterIndex.value = idx - 1

  try {
    const chapterIds = chapters.map(ch => ch.id)
    await axios.put(`/api/academy/courses/${course.value.id}/reorder-chapters`, { chapter_ids: chapterIds }, { withCredentials: true })
  } catch (e) {
    console.error('Failed to save chapter order', e)
  }
}

// Move chapter DOWN in ordering
const moveChapterDown = async (idx) => {
  if (!course.value?.chapters || idx >= course.value.chapters.length - 1) return
  const chapters = course.value.chapters
  const temp = chapters[idx]
  chapters[idx] = chapters[idx + 1]
  chapters[idx + 1] = temp

  chapters.forEach((ch, i) => ch.order_index = i + 1)
  activeChapterIndex.value = idx + 1

  try {
    const chapterIds = chapters.map(ch => ch.id)
    await axios.put(`/api/academy/courses/${course.value.id}/reorder-chapters`, { chapter_ids: chapterIds }, { withCredentials: true })
  } catch (e) {
    console.error('Failed to save chapter order', e)
  }
}

// Enhance HTML output with clickable target="_blank" links, images, and callouts
const processedHtml = computed(() => {
  let html = activeChapter.value?.sanitized_html || ''
  
  // Transform Markdown Callouts if present
  html = html.replace(/&gt;\s*\[!NOTE\]/gi, '<div class="my-4 p-4 rounded-xl bg-cyan-950/60 border-l-4 border-[#00f0ff] text-cyan-200 text-xs font-mono"><strong class="text-[#00f0ff] uppercase block mb-1">ℹ️ Note</strong>')
  html = html.replace(/&gt;\s*\[!TIP\]/gi, '<div class="my-4 p-4 rounded-xl bg-emerald-950/60 border-l-4 border-[#9fef00] text-emerald-200 text-xs font-mono"><strong class="text-[#9fef00] uppercase block mb-1">💡 Tip</strong>')
  html = html.replace(/&gt;\s*\[!WARNING\]/gi, '<div class="my-4 p-4 rounded-xl bg-amber-950/60 border-l-4 border-amber-400 text-amber-200 text-xs font-mono"><strong class="text-amber-400 uppercase block mb-1">⚠️ Warning</strong>')

  // Transform <a> tags to open in target="_blank" with neon styling
  html = html.replace(/<a /gi, '<a target="_blank" rel="noopener noreferrer" class="text-[#00f0ff] font-bold underline hover:text-[#9fef00] transition-colors" ')
  
  // Transform <img> tags to responsive rounded images
  html = html.replace(/<img /gi, '<img class="my-4 rounded-xl border border-[#1f293d] max-h-96 w-full object-cover shadow-lg" ')

  return html
})

// TOC headings extraction from HTML
const chapterHeadings = computed(() => {
  const html = activeChapter.value?.sanitized_html || ''
  const regex = /<h([1-3])\s*[^>]*>(.*?)<\/h[1-3]>/gi
  const headings = []
  let match

  while ((match = regex.exec(html)) !== null) {
    const level = parseInt(match[1])
    const rawText = match[2].replace(/<[^>]+>/g, '').trim()
    const id = rawText.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
    headings.push({ level, text: rawText, id })
  }

  return headings
})

const updateScrollProgress = () => {
  const winScroll = document.documentElement.scrollTop || document.body.scrollTop
  const height = document.documentElement.scrollHeight - document.documentElement.clientHeight
  scrollProgress.value = height > 0 ? (winScroll / height) * 100 : 0
}

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
    error.value = err.response?.data?.error || 'Failed to load module details.'
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
  window.addEventListener('scroll', updateScrollProgress)
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateScrollProgress)
})
</script>
