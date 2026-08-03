<template>
  <div class="min-h-screen bg-[#0b0e14] text-slate-100 font-sans pb-20 selection:bg-[#00f0ff] selection:text-black">
    <div class="w-full px-4 sm:px-6 lg:px-8 pt-4 space-y-8 max-w-[1600px] mx-auto">

      <!-- Loading Skeleton -->
      <div v-if="loading" class="animate-pulse space-y-8">
        <div class="h-64 bg-[#151f30] rounded-3xl border border-[#1f293d]"></div>
        <div class="h-96 bg-[#151f30] rounded-3xl border border-[#1f293d]"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-rose-500/10 border border-rose-500/30 text-rose-400 p-6 rounded-2xl text-center font-mono">
        {{ error }}
      </div>

      <div v-else class="space-y-8">

        <!-- Hero Banner -->
        <div class="glass-panel border border-[#1f293d] rounded-3xl bg-[#0d1420]/90 shadow-2xl relative overflow-hidden">
          <div class="h-52 md:h-64 w-full relative">
            <img :src="moduleData.cover_image" class="w-full h-full object-cover" />
            <div class="absolute inset-0 bg-gradient-to-t from-[#0d1420] via-[#0d1420]/60 to-transparent"></div>
          </div>

          <div class="p-6 md:p-8 -mt-16 relative z-10 font-mono space-y-4">
            <div class="flex items-center gap-2 text-lg">
              <router-link :to="`/academy/course/${moduleData.course?.slug}`" class="text-[#00f0ff] hover:underline font-bold">&larr; {{ moduleData.course?.title || 'Path' }}</router-link>
            </div>

            <h1 class="text-4xl md:text-5xl font-extrabold text-white tracking-tight font-serif">{{ moduleData.title }}</h1>
            <p v-if="moduleData.description" class="text-slate-300 text-base max-w-3xl leading-relaxed font-sans">{{ moduleData.description }}</p>

            <!-- Stats Row -->
            <div class="flex flex-wrap items-center gap-4 md:gap-6 pt-2 text-sm">
              <div class="flex items-center gap-2 text-slate-300">
                <svg class="w-5 h-5 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                <span><strong class="text-white">{{ moduleData.notes?.length || 0 }}</strong> Notes</span>
              </div>
              <div class="flex items-center gap-2 text-slate-300">
                <svg class="w-5 h-5 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                <span><strong class="text-white">{{ moduleData.total_read_minutes || 0 }}</strong> min read</span>
              </div>
            </div>

            <!-- Progress + CTA -->
            <div class="pt-4 flex flex-col sm:flex-row sm:items-center gap-4">
              <div v-if="moduleData.enrollment" class="flex-1 max-w-md space-y-3">
                <div class="space-y-1.5">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-slate-400 font-bold">Module Progress</span>
                    <span class="font-bold" :class="moduleData.module_progress_percent >= 100 ? 'text-[#9fef00]' : 'text-[#00f0ff]'">
                      {{ moduleData.module_notes_completed || 0 }}/{{ moduleData.module_notes_total || 0 }} notes &middot; {{ moduleData.module_progress_percent || 0 }}%
                    </span>
                  </div>
                  <div class="w-full bg-[#1f293d] h-2.5 rounded-full overflow-hidden">
                    <div class="bg-gradient-to-r from-[#00f0ff] to-[#9fef00] h-full transition-all duration-500" :style="{ width: `${moduleData.module_progress_percent || 0}%` }"></div>
                  </div>
                </div>
                <div class="space-y-1.5">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-slate-400 font-bold">Path Progress <span class="text-slate-600 font-normal normal-case">(all modules)</span></span>
                    <span class="text-[#9fef00] font-bold">{{ moduleData.enrollment.progress_percent }}%</span>
                  </div>
                  <div class="w-full bg-[#1f293d] h-2 rounded-full overflow-hidden">
                    <div class="bg-gradient-to-r from-[#00f0ff] to-[#9fef00] h-full transition-all duration-500" :style="{ width: `${moduleData.enrollment.progress_percent}%` }"></div>
                  </div>
                </div>
              </div>
              <router-link
                v-if="moduleData.notes?.length"
                :to="`/academy/course/${moduleData.course?.slug}/module/${moduleData.id}/read`"
                class="btn-htb py-3.5 px-7 text-base font-bold uppercase tracking-wider text-center"
              >
                Start Module &rarr;
              </router-link>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-8 items-start">

          <!-- Notes Outline -->
          <section class="glass-panel p-6 rounded-3xl border border-[#1f293d] bg-[#0d1420] space-y-4 font-mono">
            <h3 class="text-sm font-extrabold text-white uppercase tracking-wider flex items-center gap-2">
              <svg class="w-4 h-4 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"/></svg>
              <span>Notes</span>
            </h3>
            <div class="grid grid-cols-1 xl:grid-cols-2 gap-2.5">
              <router-link
                v-for="(note, idx) in moduleData.notes"
                :key="note.id"
                :to="`/academy/course/${moduleData.course?.slug}/module/${moduleData.id}/read?noteId=${note.id}`"
                class="flex items-center justify-between p-3.5 rounded-xl border transition-all group"
                :class="note.is_completed ? 'bg-[#9fef00]/5 border-[#9fef00]/30 hover:border-[#9fef00]/50' : 'bg-[#0b0e14] border-[#1f293d] hover:border-[#00f0ff]/50'"
              >
                <div class="flex items-center gap-3 min-w-0">
                  <span class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0" :class="note.is_completed ? 'bg-[#9fef00]/20 text-[#9fef00]' : 'bg-[#151f30] text-slate-300'">
                    <svg v-if="note.is_completed" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
                    <template v-else>{{ idx + 1 }}</template>
                  </span>
                  <span class="truncate text-sm font-semibold group-hover:text-[#00f0ff]" :class="note.is_completed ? 'text-[#9fef00]' : 'text-slate-200'">{{ note.title }}</span>
                  <svg v-if="note.has_attachments" class="w-3.5 h-3.5 text-slate-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
                </div>
                <span class="text-xs text-slate-500 flex-shrink-0">{{ note.read_time_minutes }} min</span>
              </router-link>
              <p v-if="!moduleData.notes?.length" class="col-span-full text-xs text-slate-500 text-center py-6">No notes published yet.</p>
            </div>
          </section>

          <!-- Teacher: Manage Module & Notes -->
          <div v-if="authStore.isTeacher" class="space-y-6 sticky top-6">
          <div class="glass-panel p-5 rounded-3xl border border-[#1f293d] bg-[#0d1420] space-y-4 font-mono">
            <h3 class="text-xs font-extrabold text-[#00f0ff] uppercase tracking-wider">// Module Details</h3>

            <div v-if="moduleForm.cover_image" class="w-full h-24 rounded-lg overflow-hidden border border-[#1f293d]">
              <img :src="moduleForm.cover_image" class="w-full h-full object-cover" />
            </div>
            <input v-model="moduleForm.title" type="text" placeholder="Module title" class="input-field w-full py-1.5 text-[11px]" />
            <input v-model="moduleForm.description" type="text" placeholder="Short description" class="input-field w-full py-1.5 text-[11px]" />
            <div class="flex items-center gap-2">
              <input v-model="moduleForm.cover_image" type="text" placeholder="Cover image URL" class="input-field flex-1 py-1.5 text-[11px]" />
              <button type="button" @click="triggerModuleCoverUpload" :disabled="moduleCoverUploading" class="btn-ghost text-[11px] py-1.5 px-2.5 text-[#00f0ff] border border-[#00f0ff]/40 hover:bg-[#00f0ff]/10 flex-shrink-0 font-bold">
                {{ moduleCoverUploading ? '...' : 'Upload' }}
              </button>
              <input ref="moduleCoverFileInput" type="file" accept="image/*" class="hidden" @change="handleModuleCoverUpload" />
            </div>
            <button @click="saveModuleDetails" :disabled="!moduleForm.title.trim() || savingModule" class="btn-htb w-full py-1.5 text-[11px]">
              {{ savingModule ? 'Saving...' : 'Save Module Details' }}
            </button>
          </div>

          <div class="glass-panel p-5 rounded-3xl border border-[#1f293d] bg-[#0d1420] space-y-4 font-mono">
            <h3 class="text-xs font-extrabold text-[#00f0ff] uppercase tracking-wider">// Manage Notes</h3>

            <div class="space-y-2">
              <div v-for="note in moduleData.notes" :key="note.id" class="flex items-center justify-between p-2.5 bg-[#0b0e14] rounded-lg border border-[#1f293d] gap-2">
                <p class="text-xs font-bold text-slate-200 truncate min-w-0">{{ note.title }}</p>
                <div class="flex items-center gap-2 shrink-0">
                  <router-link :to="`/academy/write?module=${moduleData.id}&note=${note.id}`" title="Edit Note" class="text-slate-500 hover:text-[#00f0ff]">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21H3v-3.5L16.732 3.732z"/></svg>
                  </router-link>
                  <button @click="deleteNote(note.id)" class="text-rose-400 hover:text-rose-300">&times;</button>
                </div>
              </div>
              <p v-if="!moduleData.notes?.length" class="text-[11px] text-slate-500 text-center py-3">No notes yet.</p>
            </div>

            <div class="pt-3 border-t border-[#1f293d]">
              <router-link :to="`/academy/write?module=${moduleData.id}&new=1`" class="btn-ghost w-full py-1.5 text-[11px] flex items-center justify-center gap-1.5">
                <svg class="w-3.5 h-3.5 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                <span>Add Note</span>
              </router-link>
            </div>
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
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const route = useRoute()
const authStore = useAuthStore()

const moduleData = ref({})
const loading = ref(true)
const error = ref('')

const moduleForm = ref({ title: '', description: '', cover_image: '' })
const savingModule = ref(false)
const moduleCoverUploading = ref(false)
const moduleCoverFileInput = ref(null)

const fetchModuleOverview = async () => {
  loading.value = true
  try {
    const res = await axios.get(`/api/academy/modules/${route.params.moduleId}/overview`, { withCredentials: true })
    moduleData.value = res.data
    moduleForm.value = { title: res.data.title, description: res.data.description || '', cover_image: res.data.cover_image || '' }
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load module overview.'
  } finally {
    loading.value = false
  }
}

const saveModuleDetails = async () => {
  savingModule.value = true
  try {
    const res = await axios.put(`/api/academy/chapters/${moduleData.value.id}`, moduleForm.value, { withCredentials: true })
    moduleData.value = { ...moduleData.value, ...res.data }
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to save module details')
  } finally {
    savingModule.value = false
  }
}

const triggerModuleCoverUpload = () => {
  if (moduleCoverFileInput.value) moduleCoverFileInput.value.click()
}

const handleModuleCoverUpload = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return

  moduleCoverUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('feature', 'courses')

    const res = await axios.post('/api/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      withCredentials: true
    })

    if (res.data && res.data.url) {
      moduleForm.value.cover_image = res.data.url
    }
  } catch (err) {
    alert('Failed to upload cover image: ' + (err.response?.data?.error || err.message))
  } finally {
    moduleCoverUploading.value = false
  }
}

const deleteNote = async (noteId) => {
  if (!confirm('Delete this note? This cannot be undone.')) return
  try {
    await axios.delete(`/api/academy/notes/${noteId}`, { withCredentials: true })
    moduleData.value.notes = moduleData.value.notes.filter(n => n.id !== noteId)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete note')
  }
}

onMounted(fetchModuleOverview)
</script>
