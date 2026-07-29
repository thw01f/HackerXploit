<template>
  <div class="space-y-8 font-sans selection:bg-[#00f0ff] selection:text-black">
      
      <!-- TryHackMe-Style Hero Header Banner -->
      <div class="glass-panel p-8 md:p-10 rounded-3xl bg-[#0d1420]/90 border border-[#1f293d] shadow-2xl relative overflow-hidden">
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-8 relative z-10">
          <div class="space-y-3 max-w-2xl">
            <span class="text-xs font-mono font-bold text-[#00f0ff] uppercase tracking-wider bg-[#00f0ff]/10 px-3 py-1 rounded-full border border-[#00f0ff]/30">
              LEARN & HACK
            </span>
            <h1 class="text-3xl md:text-5xl font-extrabold text-white tracking-tight font-serif leading-tight">
              Cyber Security Learning Paths
            </h1>
            <p class="text-slate-300 text-sm md:text-base leading-relaxed">
              Discover real-world offensive & defensive cybersecurity modules, live classes, and structured roadmaps.
            </p>
            <div class="flex items-center gap-6 pt-2 font-mono text-xs md:text-sm">
              <div class="flex items-center space-x-2">
                <span class="text-lg font-bold text-white">{{ clubStore.courses?.length || 0 }}</span>
                <span class="text-slate-400">Active Paths & Modules</span>
              </div>
              <span class="text-slate-600">•</span>
              <div class="flex items-center space-x-2">
                <span class="text-lg font-bold text-white">{{ liveClasses?.length || 0 }}</span>
                <span class="text-slate-400">Scheduled Live Sessions</span>
              </div>
            </div>
          </div>

          <!-- Studio Authoring & Management Actions -->
          <div class="flex flex-wrap items-center gap-3 font-mono">
            <button 
              v-if="authStore.isTeacher" 
              @click="openCreatePathModal" 
              class="btn-htb text-xs py-3 px-5 font-bold uppercase tracking-wider shadow-lg flex items-center justify-center space-x-2"
            >
              <span>📁 + Create Path / Module</span>
            </button>

            <router-link 
              to="/academy/write" 
              class="bg-[#161b22] hover:bg-[#21262d] text-slate-200 border border-[#30363d] text-xs py-3 px-5 font-bold rounded-xl transition-all flex items-center justify-center space-x-2"
            >
              <span>✍️ Modules Studio</span>
            </router-link>

            <button 
              v-if="authStore.isTeacher" 
              @click="showLiveModal = true" 
              class="btn-neon-cyan text-xs py-3 px-5 font-bold uppercase tracking-wider flex items-center justify-center space-x-2"
            >
              <span>🎥 Live Class</span>
            </button>
          </div>
        </div>
      </div>

      <!-- TryHackMe Sub-Navigation Tabs Bar -->
      <div class="flex items-center space-x-2 border-b border-[#1f293d] pb-3 overflow-x-auto font-mono">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 whitespace-nowrap',
            activeTab === tab.id 
              ? 'bg-[#9fef00]/15 text-[#9fef00] border border-[#9fef00]/40 shadow-[0_0_12px_rgba(159,239,0,0.15)]' 
              : 'text-slate-400 hover:text-white hover:bg-[#151f30]'
          ]"
        >
          <span>{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- TAB: PATHS -->
      <div v-if="activeTab === 'paths'" class="space-y-6">
        
        <!-- Search & Filter Controls -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 font-mono">
          <div class="md:col-span-2 relative flex items-center">
            <div class="absolute left-3.5 pointer-events-none text-slate-400 flex items-center justify-center">
              <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
            </div>
            <input 
              v-model="pathSearch" 
              type="text" 
              placeholder="Search learning paths & modules..." 
              class="input-field w-full text-xs !pl-11 py-3 bg-[#0d1420]" 
            />
          </div>

          <div>
            <select v-model="difficultyFilter" class="input-field w-full text-xs py-3 bg-[#0d1420] text-slate-300">
              <option value="All">Difficulty: All</option>
              <option value="Easy">Easy</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
          </div>

          <div>
            <select v-model="statusFilter" class="input-field w-full text-xs py-3 bg-[#0d1420] text-slate-300">
              <option value="All">Status: All</option>
              <option value="published">Published</option>
              <option value="draft">Draft</option>
            </select>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="filteredPaths.length === 0" class="glass-panel p-16 text-center text-slate-400 space-y-4 rounded-3xl bg-[#0d1420]">
          <div class="text-4xl">🛣️</div>
          <h3 class="text-lg font-bold text-white font-serif">No Learning Paths Found</h3>
          <p class="text-xs text-slate-400 max-w-md mx-auto font-mono">
            There are currently no matching learning paths. Teachers and Admins can create new paths or write notes using the studio.
          </p>
          <button v-if="authStore.isTeacher" @click="openCreatePathModal" class="btn-htb text-xs py-2 px-5 font-mono uppercase font-bold">
            + Create First Path
          </button>
        </div>

        <!-- Learning Path Cards Grid -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div 
            v-for="path in filteredPaths" 
            :key="path.id"
            class="glass-panel rounded-2xl bg-[#0d1420] border border-[#1f293d] hover:border-[#00f0ff] transition-all duration-300 flex flex-col justify-between overflow-hidden group hover:scale-[1.02]"
          >
            <!-- Card Image Artwork & Badges -->
            <div class="relative h-48 bg-[#0b0e14] overflow-hidden cursor-pointer" @click="navigateToCourse(path.slug)">
              <img 
                :src="path.cover_image || '/uploads/courses/default_cover.png'" 
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
              />
              <div class="absolute inset-0 bg-gradient-to-t from-[#0d1420] via-transparent to-black/30"></div>

              <!-- Top Left Badge Tag -->
              <span v-if="path.is_new" class="absolute top-3 left-3 bg-[#9fef00] text-black text-[10px] font-mono font-extrabold px-2.5 py-0.5 rounded uppercase tracking-wider shadow-md">
                NEW 2026
              </span>

              <!-- Top Right Management Actions for Admins & Teachers -->
              <div v-if="authStore.isTeacher" class="absolute top-3 right-3 flex items-center space-x-1.5 bg-[#0b0e14]/90 p-1 rounded-lg border border-[#1f293d] backdrop-blur-sm">
                <button @click.stop="openEditPathModal(path)" title="Edit Path" class="text-xs px-2 py-1 bg-[#151f30] hover:bg-[#1f293d] text-[#00f0ff] rounded font-mono font-bold">✏️ Edit</button>
                <button @click.stop="deletePath(path.id)" title="Delete Path" class="text-xs px-2 py-1 bg-rose-950/80 hover:bg-rose-900 text-rose-300 rounded font-mono font-bold">🗑️</button>
              </div>
            </div>

            <!-- Card Content Body -->
            <div class="p-5 space-y-4 flex-1 flex flex-col justify-between cursor-pointer" @click="navigateToCourse(path.slug)">
              <div class="space-y-2">
                <div class="flex items-center justify-between font-mono text-[10px]">
                  <span class="text-[#00f0ff] uppercase font-bold tracking-wider">{{ path.difficulty || 'Easy' }}</span>
                  <span class="text-slate-500 font-bold">{{ path.chapters_count || 0 }} Chapters</span>
                </div>
                <h3 class="text-lg font-bold text-white group-hover:text-[#00f0ff] transition-colors leading-snug">
                  {{ path.title }}
                </h3>
                <p class="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                  {{ path.description }}
                </p>
              </div>

              <div class="pt-3 border-t border-[#1f293d] flex items-center justify-between font-mono text-xs">
                <span class="text-slate-400 text-[11px]">Author: {{ path.author_name || 'HackerXploit Staff' }}</span>
                <span class="text-[#9fef00] font-bold group-hover:underline">Start Path &rarr;</span>
              </div>
            </div>

          </div>
        </div>

      </div>

      <!-- TAB: ROADMAP -->
      <div v-if="activeTab === 'roadmap'" class="space-y-6 font-mono">
        <div class="glass-panel p-6 bg-[#0d1420] border border-[#1f293d] rounded-2xl space-y-4">
          <h3 class="text-lg font-bold text-white mb-2">🗺️ Cybersecurity Learning Roadmap</h3>
          <p class="text-xs text-slate-400">Structured pathways generated dynamically from published academy courses.</p>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
            <div 
              v-for="(course, idx) in clubStore.courses" 
              :key="course.id" 
              class="p-5 rounded-xl bg-[#0b0e14] border border-[#1f293d] space-y-3 cursor-pointer hover:border-[#00f0ff] transition-all"
              @click="navigateToCourse(course.slug)"
            >
              <span class="text-xs font-bold text-[#00f0ff] uppercase bg-[#00f0ff]/10 px-2.5 py-1 rounded border border-[#00f0ff]/30">Phase {{ idx + 1 }}</span>
              <h4 class="font-bold text-white text-sm">{{ course.title }}</h4>
              <p class="text-xs text-slate-400 line-clamp-2">{{ course.description }}</p>
              <div class="text-xs text-[#00f0ff]">{{ course.chapters_count || 1 }} Chapters &bull; {{ course.difficulty || 'Easy' }}</div>
            </div>

            <div v-if="!clubStore.courses?.length" class="col-span-3 text-center py-8 text-slate-500 text-xs">
              No active courses in roadmap yet.
            </div>
          </div>
        </div>
      </div>

      <!-- TAB: MODULES (Course Catalog) -->
      <div v-if="activeTab === 'modules'" class="space-y-6 font-mono">
        <div v-if="!clubStore.courses?.length" class="glass-panel p-12 text-center text-slate-500 text-xs rounded-2xl">
          No modules available.
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="course in clubStore.courses" :key="course.id" class="glass-panel p-6 flex flex-col justify-between hover:border-[#9fef00]/50 transition-all bg-[#0d1420] border border-[#1f293d] rounded-2xl">
            <div>
              <div class="flex items-center justify-between mb-3">
                <span class="text-[10px] uppercase bg-[#151f30] text-[#9fef00] px-2.5 py-0.5 rounded border border-[#9fef00]/30">
                  {{ course.difficulty || 'Easy' }}
                </span>
                <span class="text-xs text-slate-400">{{ course.chapters_count || 0 }} Chapters</span>
              </div>
              <h3 class="text-lg font-bold text-white mb-2">{{ course.title }}</h3>
              <p class="text-slate-300 text-xs line-clamp-3 mb-6 leading-relaxed">{{ course.description }}</p>
            </div>

            <div class="pt-4 border-t border-[#1f293d] flex items-center justify-between">
              <span class="text-xs text-slate-400">{{ course.status }}</span>
              <router-link :to="`/academy/course/${course.slug}`" class="btn-htb text-xs py-1.5 px-4">
                Start Module &rarr;
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB: LIVE CLASSES -->
      <div v-if="activeTab === 'live'" class="space-y-6 font-mono">
        <div v-if="liveClasses.length === 0" class="glass-panel p-12 text-center text-slate-500 text-xs rounded-2xl">
          No live classes currently scheduled.
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-for="lc in liveClasses" :key="lc.id" class="glass-panel p-6 bg-[#0d1420] border border-[#1f293d] rounded-2xl flex flex-col justify-between space-y-4">
            <div class="space-y-3">
              <div class="flex justify-between items-start">
                <span class="text-xs font-bold text-[#9fef00] bg-[#9fef00]/10 px-2.5 py-0.5 rounded border border-[#9fef00]/30 uppercase flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-[#9fef00]"></span> Scheduled Live
                </span>
                <span class="text-xs text-slate-400">{{ formatDate(lc.scheduled_at) }}</span>
              </div>

              <!-- Thumbnail artwork -->
              <img :src="lc.thumbnail_url || '/uploads/courses/default_cover.png'" class="w-full h-40 object-cover rounded-xl border border-[#1f293d]" />

              <h3 class="text-lg font-bold text-white">{{ lc.title }}</h3>
              <p class="text-xs text-slate-300 leading-relaxed">{{ lc.description }}</p>
            </div>

            <div class="pt-4 border-t border-[#1f293d] flex justify-between items-center">
              <div v-if="authStore.isTeacher" class="flex items-center space-x-2">
                <button @click="openEditLiveModal(lc)" class="text-xs text-[#00f0ff] hover:underline font-bold">Edit</button>
                <button @click="deleteLiveClass(lc.id)" class="text-xs text-rose-400 hover:underline font-bold">Cancel</button>
              </div>
              <a :href="lc.meeting_link" target="_blank" class="btn-neon-cyan text-xs py-2 px-5 font-bold ml-auto flex items-center gap-2">
                <span>🚀 Join Live Class</span>
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Create / Edit Path Modal for Admins & Teachers -->
      <div v-if="showPathModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm font-mono">
        <div class="w-full max-w-lg glass-panel p-6 rounded-2xl border border-[#1f293d] bg-[#0d1420]">
          <h3 class="text-xl font-bold text-white mb-4">{{ isEditingPath ? '✏️ Edit Path / Module' : '📁 Create Path / Module' }}</h3>
          <form @submit.prevent="handleSavePath" class="space-y-4">
            <div>
              <label class="block text-xs text-slate-400 uppercase mb-1">Path Title <span class="text-rose-400">*</span></label>
              <input v-model="pathForm.title" type="text" placeholder="e.g. Web Application Security" required class="input-field text-xs w-full py-2" />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-slate-400 uppercase mb-1">Difficulty</label>
                <select v-model="pathForm.difficulty" class="input-field text-xs w-full py-2 bg-[#0b0e14] text-slate-300">
                  <option value="Easy">Easy</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                </select>
              </div>

              <div>
                <label class="block text-xs text-slate-400 uppercase mb-1">Status</label>
                <select v-model="pathForm.status" class="input-field text-xs w-full py-2 bg-[#0b0e14] text-slate-300">
                  <option value="published">Published</option>
                  <option value="draft">Draft</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-xs text-slate-400 uppercase mb-1">Cover Image / Thumbnail URL</label>
              <input v-model="pathForm.cover_image" type="text" placeholder="/uploads/courses/cover.png or https://..." class="input-field text-xs w-full py-2" />
            </div>

            <div>
              <label class="block text-xs text-slate-400 uppercase mb-1">Description</label>
              <textarea v-model="pathForm.description" rows="3" placeholder="Overview of learning path..." class="input-field text-xs w-full py-2"></textarea>
            </div>

            <div class="flex items-center space-x-2">
              <input v-model="pathForm.is_new" type="checkbox" id="is_new_chk" class="rounded border-[#1f293d]" />
              <label for="is_new_chk" class="text-xs text-slate-300">Highlight with NEW 2026 Badge</label>
            </div>

            <div class="flex justify-end space-x-3 pt-4 border-t border-[#1f293d]">
              <button type="button" @click="showPathModal = false" class="btn-ghost text-xs py-2 px-4">Cancel</button>
              <button type="submit" class="btn-htb text-xs py-2 px-5 font-bold uppercase">{{ isEditingPath ? 'Update Path' : 'Publish Path' }}</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Schedule / Edit Live Class Modal for Teachers -->
      <div v-if="showLiveModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm font-mono">
        <div class="w-full max-w-lg glass-panel p-6 rounded-2xl border border-[#1f293d] bg-[#0d1420]">
          <h3 class="text-xl font-bold text-white mb-4">{{ isEditingLive ? '✏️ Edit Live Class' : '🎥 Schedule Live Class' }}</h3>
          <form @submit.prevent="handleScheduleLive" class="space-y-4">
            <div>
              <label class="block text-xs text-slate-400 uppercase mb-1">Session Title <span class="text-rose-400">*</span></label>
              <input v-model="newLive.title" type="text" placeholder="e.g. Kerberoasting Deep Dive" required class="input-field text-xs w-full py-2" />
            </div>

            <div>
              <label class="block text-xs text-slate-400 uppercase mb-1">Meeting Link <span class="text-rose-400">*</span></label>
              <input v-model="newLive.meeting_link" type="url" placeholder="https://meet.google.com/xyz" required class="input-field text-xs w-full py-2" />
            </div>

            <div>
              <label class="block text-xs text-slate-400 uppercase mb-1">Thumbnail Artwork URL</label>
              <input v-model="newLive.thumbnail_url" type="text" placeholder="/uploads/courses/cover.png" class="input-field text-xs w-full py-2" />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-slate-400 uppercase mb-1">Date & Time</label>
                <input v-model="newLive.scheduled_at" type="datetime-local" required class="input-field text-xs w-full py-2 bg-[#0b0e14]" />
              </div>
              <div>
                <label class="block text-xs text-slate-400 uppercase mb-1">Duration (Minutes)</label>
                <input v-model="newLive.duration_minutes" type="number" placeholder="60" class="input-field text-xs w-full py-2" />
              </div>
            </div>

            <div>
              <label class="block text-xs text-slate-400 uppercase mb-1">Description / Agenda</label>
              <textarea v-model="newLive.description" rows="3" placeholder="Session details..." class="input-field text-xs w-full py-2"></textarea>
            </div>

            <div class="flex justify-end space-x-3 pt-4 border-t border-[#1f293d]">
              <button type="button" @click="showLiveModal = false" class="btn-ghost text-xs py-2 px-4">Cancel</button>
              <button type="submit" class="btn-neon-cyan text-xs py-2 px-5 font-bold">{{ isEditingLive ? 'Update Live Class' : 'Publish Live Class' }}</button>
            </div>
          </form>
        </div>
      </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useClubStore } from '../stores/club'

const router = useRouter()
const authStore = useAuthStore()
const clubStore = useClubStore()

const activeTab = ref('paths')
const pathSearch = ref('')
const difficultyFilter = ref('All')
const statusFilter = ref('All')

const tabs = [
  { id: 'paths', label: 'Paths', icon: '🛣️' },
  { id: 'roadmap', label: 'Roadmap', icon: '🗺️' },
  { id: 'modules', label: 'Modules', icon: '📦' },
  { id: 'live', label: 'Live Classes', icon: '🎥' }
]

const liveClasses = ref([])
const showLiveModal = ref(false)
const isEditingLive = ref(false)
const editingLiveId = ref(null)
const newLive = ref({ title: '', meeting_link: '', thumbnail_url: '', scheduled_at: '', duration_minutes: 60, description: '' })

const showPathModal = ref(false)
const isEditingPath = ref(false)
const editingPathId = ref(null)
const pathForm = ref({ title: '', description: '', difficulty: 'Easy', cover_image: '', is_new: true, status: 'published' })

const filteredPaths = computed(() => {
  let list = clubStore.courses || []
  if (pathSearch.value.trim()) {
    const q = pathSearch.value.toLowerCase()
    list = list.filter(p => p.title.toLowerCase().includes(q) || (p.description && p.description.toLowerCase().includes(q)))
  }
  if (difficultyFilter.value !== 'All') {
    list = list.filter(p => (p.difficulty || 'Easy').toLowerCase() === difficultyFilter.value.toLowerCase())
  }
  if (statusFilter.value !== 'All') {
    list = list.filter(p => p.status === statusFilter.value)
  }
  return list
})

const navigateToCourse = (slug) => {
  if (slug) router.push(`/academy/course/${slug}`)
}

const openCreatePathModal = () => {
  isEditingPath.value = false
  editingPathId.value = null
  pathForm.value = { title: '', description: '', difficulty: 'Easy', cover_image: '', is_new: true, status: 'published' }
  showPathModal.value = true
}

const openEditPathModal = (path) => {
  isEditingPath.value = true
  editingPathId.value = path.id
  pathForm.value = {
    title: path.title,
    description: path.description,
    difficulty: path.difficulty || 'Easy',
    cover_image: path.cover_image || '',
    is_new: path.is_new !== false,
    status: path.status || 'published'
  }
  showPathModal.value = true
}

const handleSavePath = async () => {
  if (!pathForm.value.title.trim()) return
  try {
    if (isEditingPath.value && editingPathId.value) {
      await axios.put(`/api/academy/courses/${editingPathId.value}`, pathForm.value, { withCredentials: true })
    } else {
      await axios.post('/api/academy/courses', pathForm.value, { withCredentials: true })
    }
    showPathModal.value = false
    await clubStore.fetchCourses()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to save path')
  }
}

const deletePath = async (courseId) => {
  if (!confirm('Delete this path and all associated chapters?')) return
  try {
    await axios.delete(`/api/academy/courses/${courseId}`, { withCredentials: true })
    await clubStore.fetchCourses()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete path')
  }
}

const fetchLiveClasses = async () => {
  try {
    const res = await axios.get('/api/academy/live-classes', { withCredentials: true })
    liveClasses.value = res.data.live_classes || []
  } catch (err) {
    console.error('Failed to fetch live classes', err)
  }
}

const openEditLiveModal = (lc) => {
  isEditingLive.value = true
  editingLiveId.value = lc.id
  newLive.value = {
    title: lc.title,
    meeting_link: lc.meeting_link,
    thumbnail_url: lc.thumbnail_url || '',
    scheduled_at: lc.scheduled_at ? lc.scheduled_at.slice(0, 16) : '',
    duration_minutes: lc.duration_minutes || 60,
    description: lc.description || ''
  }
  showLiveModal.value = true
}

const handleScheduleLive = async () => {
  if (!newLive.value.title.trim() || !newLive.value.meeting_link.trim()) return
  try {
    if (isEditingLive.value && editingLiveId.value) {
      await axios.put(`/api/academy/live-classes/${editingLiveId.value}`, newLive.value, { withCredentials: true })
    } else {
      await axios.post('/api/academy/live-classes', newLive.value, { withCredentials: true })
    }
    showLiveModal.value = false
    newLive.value = { title: '', meeting_link: '', thumbnail_url: '', scheduled_at: '', duration_minutes: 60, description: '' }
    await fetchLiveClasses()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to save live class')
  }
}

const deleteLiveClass = async (id) => {
  if (!confirm('Cancel this live class session?')) return
  try {
    await axios.delete(`/api/academy/live-classes/${id}`, { withCredentials: true })
    await fetchLiveClasses()
  } catch (err) {
    alert('Failed to cancel session')
  }
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  clubStore.fetchCourses()
  fetchLiveClasses()
})
</script>
