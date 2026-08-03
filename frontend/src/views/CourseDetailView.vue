<template>
  <div class="min-h-screen bg-[#0b0e14] text-slate-100 font-sans pb-20 selection:bg-[#00f0ff] selection:text-black">

    <!-- Top Reading Progress Bar -->
    <div
      class="fixed top-0 left-0 h-1 bg-gradient-to-r from-[#00f0ff] via-[#9fef00] to-[#00f0ff] z-50 transition-all duration-150"
      :style="{ width: `${scrollProgress}%` }"
    ></div>

    <!-- Main Container (Full width responsive layout) -->
    <div class="w-full px-4 sm:px-6 lg:px-8 pt-4 space-y-8">

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

        <!-- Module Top Banner Header -->
        <div class="glass-panel border border-[#1f293d] p-6 md:p-8 rounded-3xl bg-[#0d1420]/90 shadow-2xl relative overflow-hidden">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10 font-mono">

            <div class="space-y-2">
              <div class="flex items-center space-x-2 text-lg">
                <router-link :to="`/academy/course/${route.params.slug}/module/${route.params.moduleId}`" class="text-[#00f0ff] hover:underline font-bold">&larr; Overview</router-link>
                <span class="text-slate-600 text-sm">•</span>
                <span class="text-slate-400 uppercase tracking-wider font-semibold text-sm">Interactive Module</span>
              </div>
              <h1 class="text-3xl md:text-4xl font-extrabold text-white tracking-tight font-serif">
                {{ moduleData.title }}
              </h1>
              <p class="text-slate-300 text-xs md:text-sm max-w-3xl leading-relaxed font-sans">
                {{ moduleData.description }}
              </p>
              <div class="flex items-center gap-4 text-[11px] text-slate-400 pt-2 font-mono">
                <span>Path: <strong class="text-[#00f0ff]">{{ moduleData.course?.title }}</strong></span>
                <span>Notes: <strong class="text-white">{{ moduleData.notes?.length || 0 }}</strong></span>
              </div>
            </div>

            <!-- Enrollment Card -->
            <div class="w-full md:w-64 bg-[#0b0e14] p-4 rounded-2xl border border-[#1f293d] space-y-3 flex-shrink-0">
              <div class="flex items-center justify-between text-xs font-mono">
                <span class="font-bold text-slate-300">Path Progress</span>
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
                Enroll in Path
              </button>
              <div v-else-if="enrollment.progress_percent >= 100" class="text-center text-xs text-[#9fef00] font-bold font-mono py-1">
                ✓ Path Completed!
              </div>
            </div>

          </div>
        </div>

        <!-- MkDocs Layout: Compact Left Navigation + Extended Content Reader -->
        <div class="flex flex-col lg:flex-row gap-6 items-start">

          <!-- Left Navigation Sidebar: Compact Note List -->
          <div class="w-full lg:w-64 xl:w-72 shrink-0 glass-panel p-3.5 rounded-2xl border border-[#1f293d] bg-[#0d1420] space-y-3 sticky top-6 font-mono">
            <div class="flex items-center justify-between px-1">
              <h3 class="text-[11px] font-extrabold text-[#00f0ff] uppercase tracking-wider">Note Navigation</h3>
              <span class="text-[10px] text-slate-500 font-bold">({{ moduleData.notes?.length || 0 }})</span>
            </div>

            <div class="space-y-1.5 max-h-[70vh] overflow-y-auto pr-1">
              <div
                v-for="(note, idx) in moduleData.notes"
                :key="note.id"
                @click="activeNoteIndex = idx"
                :class="[
                  activeNoteIndex === idx ? 'bg-[#00f0ff]/15 border-[#00f0ff]/40 text-[#00f0ff] font-bold shadow-[0_0_10px_rgba(0,240,255,0.1)]' : isNoteCompleted(note.id) ? 'bg-[#9fef00]/5 border-[#9fef00]/25 text-slate-300 hover:text-white' : 'bg-[#0b0e14] border-[#1f293d] text-slate-400 hover:text-white'
                ]"
                class="w-full text-left p-2.5 rounded-xl border transition-all flex items-center justify-between text-xs group cursor-pointer"
              >
                <div class="flex items-center space-x-2 truncate">
                  <span
                    class="w-5 h-5 rounded flex items-center justify-center text-[10px] font-bold flex-shrink-0"
                    :class="isNoteCompleted(note.id) ? 'bg-[#9fef00]/20 text-[#9fef00]' : 'bg-[#151f30] text-slate-300'"
                  >
                    <svg v-if="isNoteCompleted(note.id)" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
                    <template v-else>{{ idx + 1 }}</template>
                  </span>
                  <span class="truncate font-sans text-xs font-semibold">{{ note.title }}</span>
                </div>

                <div class="flex items-center space-x-1">
                  <!-- Teacher & Admin Note Reordering Controls -->
                  <div v-if="authStore.isTeacher" class="opacity-0 group-hover:opacity-100 flex items-center space-x-0.5 transition-opacity">
                    <button @click.stop="moveNoteUp(idx)" title="Move Note Up" class="hover:text-[#00f0ff] text-[10px] px-0.5 font-bold">▲</button>
                    <button @click.stop="moveNoteDown(idx)" title="Move Note Down" class="hover:text-[#00f0ff] text-[10px] px-0.5 font-bold">▼</button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Main MkDocs Article Reader (Extended full width content field) -->
          <div v-if="activeNote" class="flex-1 min-w-0 w-full space-y-8">

            <article class="glass-panel p-6 md:p-10 lg:p-12 rounded-3xl border border-[#1f293d] bg-[#0d1420] shadow-2xl space-y-8">

              <!-- Note Header -->
              <header class="space-y-4 border-b border-[#1f293d] pb-6">
                <div class="flex items-center justify-between font-mono text-xs text-[#00f0ff]">
                  <span>NOTE {{ activeNoteIndex + 1 }} OF {{ moduleData.notes?.length }}</span>
                  <span class="bg-[#151f30] px-3 py-1 rounded-full border border-[#1f293d] text-slate-300 flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span>{{ activeNote.read_time_minutes }} min read</span>
                  </span>
                </div>

                <h1 class="text-3xl md:text-5xl font-extrabold text-white font-serif tracking-tight leading-tight">
                  {{ activeNote.title }}
                </h1>

                <!-- Interactive Quick Table of Contents Bar -->
                <div v-if="noteHeadings && noteHeadings.length" class="p-3.5 bg-[#0b0e14]/90 rounded-2xl border border-[#1f293d] font-mono text-xs space-y-2">
                  <div class="flex items-center justify-between text-slate-400">
                    <span class="font-bold text-[#00f0ff] uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"/>
                      </svg>
                      Quick Note Outline
                    </span>
                    <span class="text-[10px] text-slate-500">({{ noteHeadings.length }} sections)</span>
                  </div>
                  <div class="flex flex-wrap gap-2 pt-1">
                    <a
                      v-for="h in noteHeadings"
                      :key="h.id"
                      :href="`#${h.id}`"
                      class="px-2.5 py-1 bg-[#151f30] hover:bg-[#00f0ff]/20 hover:text-[#00f0ff] border border-[#1f293d] rounded-lg text-[11px] text-slate-300 transition-all font-sans font-medium"
                    >
                      {{ h.text }}
                    </a>
                  </div>
                </div>
              </header>

              <!-- Markdown Body Output (Expanded spacious text) -->
              <main
                class="mkdocs-content prose prose-invert prose-lg max-w-none text-slate-200 leading-relaxed space-y-6 font-sans border-b border-[#1f293d] pb-8 w-full"
                v-html="processedHtml"
              ></main>

              <!-- Gated Attachments -->
              <div v-if="activeNote.attachments?.length" class="space-y-3 font-mono">
                <div class="flex items-center space-x-2 text-[#00f0ff]">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                  </svg>
                  <h4 class="text-xs font-bold uppercase tracking-wider">Lab Attachments & Resources</h4>
                </div>
                <div class="flex flex-wrap gap-3">
                  <a
                    v-for="att in activeNote.attachments"
                    :key="att.name"
                    :href="`/api/academy/attachments/${activeNote.id}/${att.name}`"
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

              <!-- Note Navigation & Mark Complete -->
              <footer class="flex items-center justify-between pt-4 font-mono text-xs">
                <button
                  @click="activeNoteIndex = Math.max(0, activeNoteIndex - 1)"
                  :disabled="activeNoteIndex === 0"
                  class="text-slate-400 hover:text-white disabled:opacity-30 disabled:hover:text-slate-400 flex items-center space-x-1"
                >
                  <span>&larr; Previous Note</span>
                </button>

                <button
                  @click="markComplete(activeNote.id)"
                  :disabled="completing || isNoteCompleted(activeNote.id)"
                  class="btn-htb py-2 px-5 font-bold uppercase tracking-wider flex items-center gap-1.5"
                >
                  <span v-if="isNoteCompleted(activeNote.id)" class="flex items-center gap-1">
                    <svg class="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                    </svg>
                    <span>Completed</span>
                  </span>
                  <span v-else>{{ completing ? 'Updating...' : 'Mark Note Complete' }}</span>
                </button>

                <button
                  @click="activeNoteIndex = Math.min(moduleData.notes.length - 1, activeNoteIndex + 1)"
                  :disabled="activeNoteIndex >= moduleData.notes.length - 1"
                  class="text-slate-400 hover:text-white disabled:opacity-30 disabled:hover:text-slate-400 flex items-center space-x-1"
                >
                  <span>Next Note &rarr;</span>
                </button>
              </footer>

            </article>

            <!-- Review Area (rating + one shared discussion thread per Module) -->
            <section class="glass-panel p-6 rounded-3xl border border-[#1f293d] bg-[#0d1420] space-y-6">
              <h3 class="text-sm font-extrabold text-white font-mono uppercase tracking-wider flex items-center space-x-2">
                <svg class="w-4 h-4 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
                </svg>
                <span>Review</span>
                <span class="text-xs text-slate-500">({{ comments.length }})</span>
              </h3>

              <!-- Rate this Note - given after reading it, alongside the comment -->
              <div class="flex items-center justify-between font-mono text-xs">
                <div class="flex items-center gap-2.5">
                  <span class="text-slate-400">Rate this note:</span>
                  <div class="flex items-center gap-0.5">
                    <button
                      v-for="star in 5"
                      :key="star"
                      @click="rateNote(star)"
                      :disabled="ratingSubmitting"
                      class="text-xl leading-none transition-colors disabled:cursor-wait"
                      :class="star <= (noteRating.my_rating || 0) ? 'text-amber-400' : 'text-slate-700 hover:text-amber-400/60'"
                    >
                      &#9733;
                    </button>
                  </div>
                </div>
                <span v-if="noteRating.total_ratings" class="text-slate-500">
                  {{ noteRating.average_rating }} avg &middot; {{ noteRating.total_ratings }} rating{{ noteRating.total_ratings === 1 ? '' : 's' }}
                </span>
              </div>

              <!-- Review Input Box - one review per note; posting again edits your existing one -->
              <div class="space-y-3 font-mono">
                <textarea
                  v-model="newComment"
                  rows="3"
                  placeholder="Share your thoughts on this note..."
                  class="input-field text-xs w-full bg-[#0b0e14] p-3 border-[#1f293d] resize-none"
                ></textarea>
                <div class="flex items-center justify-between">
                  <span v-if="myReview" class="text-[10px] text-slate-500">You've already reviewed this note - posting again updates it.</span>
                  <span v-else></span>
                  <button
                    @click="postComment"
                    :disabled="!newComment.trim()"
                    class="btn-htb text-xs py-1.5 px-4 font-bold uppercase tracking-wider disabled:opacity-50"
                  >
                    {{ myReview ? 'Update Review' : 'Post Review' }}
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
                      <strong class="text-[#00f0ff] font-bold">{{ c.full_name || c.username || 'User' }}</strong>
                      <span class="text-slate-600">•</span>
                      <span>{{ formatDate(c.created_at) }}</span>
                    </div>
                    <div class="flex items-center gap-3">
                      <button @click="reportComment(c.id)" class="text-slate-500 hover:text-rose-400 text-[10px] flex items-center gap-1">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"/>
                        </svg>
                        <span>Report</span>
                      </button>
                      <button v-if="authStore.isTeacher" @click="deleteComment(c.id)" class="text-slate-500 hover:text-rose-400 text-[10px] flex items-center gap-1">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                        </svg>
                        <span>Delete</span>
                      </button>
                    </div>
                  </div>
                  <p class="text-slate-200 leading-relaxed font-sans text-sm">{{ c.body }}</p>
                </div>
              </div>
            </section>

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
import { usePreferences } from '../stores/preferences'
import axios from 'axios'

const route = useRoute()
const authStore = useAuthStore()
const prefs = usePreferences()
const moduleData = ref({})
const enrollment = ref(null)
const activeNoteIndex = ref(0)
const comments = ref([])
const newComment = ref('')
const loading = ref(true)
const completing = ref(false)
const error = ref('')
const scrollProgress = ref(0)

// Rating is per-Note (given after reading it), distinct from the
// module-wide Discussion & Help thread below.
const noteRating = ref({ average_rating: 0, total_ratings: 0, my_rating: null })
const ratingSubmitting = ref(false)

const activeNote = computed(() => {
  return moduleData.value.notes?.[activeNoteIndex.value] || null
})

const myReview = computed(() => comments.value.find(c => c.user_id === authStore.user?.id) || null)

// Move note UP in ordering
const moveNoteUp = async (idx) => {
  if (idx <= 0 || !moduleData.value?.notes) return
  const notes = moduleData.value.notes
  const temp = notes[idx]
  notes[idx] = notes[idx - 1]
  notes[idx - 1] = temp

  notes.forEach((n, i) => n.order_index = i + 1)
  activeNoteIndex.value = idx - 1

  try {
    const noteIds = notes.map(n => n.id)
    await axios.put(`/api/academy/modules/${route.params.moduleId}/reorder-notes`, { note_ids: noteIds }, { withCredentials: true })
  } catch (e) {
    console.error('Failed to save note order', e)
  }
}

// Move note DOWN in ordering
const moveNoteDown = async (idx) => {
  if (!moduleData.value?.notes || idx >= moduleData.value.notes.length - 1) return
  const notes = moduleData.value.notes
  const temp = notes[idx]
  notes[idx] = notes[idx + 1]
  notes[idx + 1] = temp

  notes.forEach((n, i) => n.order_index = i + 1)
  activeNoteIndex.value = idx + 1

  try {
    const noteIds = notes.map(n => n.id)
    await axios.put(`/api/academy/modules/${route.params.moduleId}/reorder-notes`, { note_ids: noteIds }, { withCredentials: true })
  } catch (e) {
    console.error('Failed to save note order', e)
  }
}

// Enhance HTML output with clickable target="_blank" links, images, and callouts
const processedHtml = computed(() => {
  let html = activeNote.value?.sanitized_html || ''

  // Transform Markdown Callouts if present
  html = html.replace(/&gt;\s*\[!NOTE\]/gi, '<div class="my-4 p-4 rounded-xl bg-cyan-950/60 border-l-4 border-[#00f0ff] text-cyan-200 text-xs font-mono"><strong class="text-[#00f0ff] uppercase block mb-1">ℹ️ Note</strong>')
  html = html.replace(/&gt;\s*\[!TIP\]/gi, '<div class="my-4 p-4 rounded-xl bg-emerald-950/60 border-l-4 border-[#9fef00] text-emerald-200 text-xs font-mono"><strong class="text-[#9fef00] uppercase block mb-1">Tip</strong>')
  html = html.replace(/&gt;\s*\[!WARNING\]/gi, '<div class="my-4 p-4 rounded-xl bg-amber-950/60 border-l-4 border-amber-400 text-amber-200 text-xs font-mono"><strong class="text-amber-400 uppercase block mb-1">Warning</strong>')

  // Transform <a> tags to open in target="_blank" with neon styling
  html = html.replace(/<a /gi, '<a target="_blank" rel="noopener noreferrer" class="text-[#00f0ff] font-bold underline hover:text-[#9fef00] transition-colors" ')

  // Transform <img> tags to responsive rounded images
  html = html.replace(/<img /gi, '<img class="my-4 rounded-xl border border-[#1f293d] max-h-96 w-full object-cover shadow-lg" ')

  return html
})

// TOC headings extraction from HTML
const noteHeadings = computed(() => {
  const html = activeNote.value?.sanitized_html || ''
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

const fetchModule = async () => {
  loading.value = true
  try {
    const res = await axios.get(`/api/academy/modules/${route.params.moduleId}/read`, { withCredentials: true })
    moduleData.value = res.data
    enrollment.value = res.data.enrollment

    // Deep-link from the module overview page's Notes outline (?noteId=N)
    const requestedId = Number(route.query.noteId)
    if (requestedId) {
      const idx = (moduleData.value.notes || []).findIndex(n => n.id === requestedId)
      if (idx !== -1) activeNoteIndex.value = idx
    }
    // fetchComments/fetchNoteRating run via the activeNote watcher below,
    // once moduleData/activeNoteIndex have both settled.
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load module details.'
  } finally {
    loading.value = false
  }
}

// Review is per-Note: one CourseComment (with note_id set) per user per
// note, paired with the star rating - re-posting edits your existing
// review instead of creating a second one.
const fetchComments = async () => {
  if (!activeNote.value) return
  try {
    const res = await axios.get(`/api/academy/notes/${activeNote.value.id}/reviews`, { withCredentials: true })
    comments.value = res.data.comments || []
    const mine = comments.value.find(c => c.user_id === authStore.user?.id)
    newComment.value = mine ? mine.body : ''
  } catch (err) {
    console.error('Failed to load comments:', err)
  }
}

const enrollCourse = async () => {
  try {
    const res = await axios.post(`/api/academy/courses/${moduleData.value.course.id}/enroll`, {}, { withCredentials: true })
    enrollment.value = res.data
  } catch (err) {
    console.error('Enrollment failed:', err)
  }
}

const isNoteCompleted = (noteId) => {
  return enrollment.value?.completed_chapters?.includes(noteId)
}

const markComplete = async (noteId) => {
  completing.value = true
  try {
    const res = await axios.post(`/api/academy/notes/${noteId}/complete`, {}, { withCredentials: true })
    enrollment.value = res.data
  } catch (err) {
    console.error('Failed to complete note:', err)
  } finally {
    completing.value = false
  }
}

const postComment = async () => {
  if (!newComment.value.trim() || !activeNote.value) return
  try {
    await axios.post(`/api/academy/notes/${activeNote.value.id}/reviews`, { body: newComment.value }, { withCredentials: true })
    await fetchComments()
  } catch (err) {
    console.error('Failed to post review:', err)
  }
}

const reportComment = async (commentId) => {
  try {
    await axios.post(`/api/academy/comments/${commentId}/report`, {}, { withCredentials: true })
    await fetchComments()
  } catch (err) {
    console.error('Failed to report comment:', err)
  }
}

const deleteComment = async (commentId) => {
  if (!confirm('Delete this comment? This cannot be undone.')) return
  try {
    await axios.delete(`/api/academy/comments/${commentId}`, { withCredentials: true })
    comments.value = comments.value.filter(c => c.id !== commentId)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete comment')
  }
}

const fetchNoteRating = async () => {
  if (!activeNote.value) return
  try {
    const res = await axios.get(`/api/academy/notes/${activeNote.value.id}/rating`, { withCredentials: true })
    noteRating.value = res.data
  } catch (err) {
    console.error('Failed to load note rating:', err)
  }
}

const rateNote = async (star) => {
  if (!activeNote.value || ratingSubmitting.value) return
  ratingSubmitting.value = true
  try {
    const res = await axios.post(`/api/academy/notes/${activeNote.value.id}/rating`, { rating: star }, { withCredentials: true })
    noteRating.value = res.data
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to submit rating')
  } finally {
    ratingSubmitting.value = false
  }
}

watch(activeNote, (note) => {
  if (note) {
    fetchNoteRating()
    fetchComments()
  }
})

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: prefs.is12h.value })
}

onMounted(() => {
  fetchModule()
  window.addEventListener('scroll', updateScrollProgress)
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateScrollProgress)
})
</script>
