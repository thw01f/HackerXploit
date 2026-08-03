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
            <img :src="course.cover_image" class="w-full h-full object-cover" />
            <div class="absolute inset-0 bg-gradient-to-t from-[#0d1420] via-[#0d1420]/60 to-transparent"></div>
          </div>

          <div class="p-6 md:p-8 -mt-16 relative z-10 font-mono space-y-4">
            <div class="flex items-center gap-2 text-lg">
              <router-link to="/academy" class="text-[#00f0ff] hover:underline font-bold">&larr; Academy</router-link>
              <span class="text-slate-600 text-sm">•</span>
              <span class="uppercase tracking-wider font-bold px-2.5 py-1 rounded text-sm" :class="difficultyBadgeClass">{{ course.difficulty }}</span>
              <span v-if="course.is_new" class="bg-[#9fef00] text-black font-extrabold px-2.5 py-1 rounded uppercase tracking-wider text-sm">New</span>
            </div>

            <h1 class="text-3xl md:text-4xl font-extrabold text-white tracking-tight font-serif">{{ course.title }}</h1>
            <p class="text-slate-300 text-sm max-w-3xl leading-relaxed font-sans">{{ course.description }}</p>

            <!-- Stats Row -->
            <div class="flex flex-wrap items-center gap-4 md:gap-6 pt-2 text-xs">
              <div class="flex items-center gap-1.5 text-slate-300">
                <svg class="w-4 h-4 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
                <span><strong class="text-white">{{ course.modules?.length || 0 }}</strong> Modules</span>
              </div>
              <div class="flex items-center gap-1.5 text-slate-300">
                <svg class="w-4 h-4 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                <span><strong class="text-white">{{ course.total_read_minutes || 0 }}</strong> min read</span>
              </div>
              <div v-if="videoResources.length" class="flex items-center gap-1.5 text-slate-300">
                <svg class="w-4 h-4 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                <span><strong class="text-white">{{ videoResources.length }}</strong> Videos</span>
              </div>
              <div v-if="otherResources.length" class="flex items-center gap-1.5 text-slate-300">
                <svg class="w-4 h-4 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/></svg>
                <span><strong class="text-white">{{ otherResources.length }}</strong> Resources</span>
              </div>
              <span class="text-slate-500">Author: <strong class="text-[#00f0ff]">{{ course.author_name }}</strong></span>
            </div>

            <!-- Progress + CTA -->
            <div class="pt-4 flex flex-col sm:flex-row sm:items-center gap-4">
              <div v-if="course.enrollment" class="flex-1 max-w-sm space-y-1.5">
                <div class="flex items-center justify-between text-xs">
                  <span class="text-slate-400 font-bold">Your Progress</span>
                  <span class="text-[#9fef00] font-bold">{{ course.enrollment.progress_percent }}%</span>
                </div>
                <div class="w-full bg-[#1f293d] h-2 rounded-full overflow-hidden">
                  <div class="bg-gradient-to-r from-[#00f0ff] to-[#9fef00] h-full transition-all duration-500" :style="{ width: `${course.enrollment.progress_percent}%` }"></div>
                </div>
              </div>
              <router-link :to="`/academy/course/${course.slug}/learn`" class="btn-htb py-3 px-6 text-sm font-bold uppercase tracking-wider text-center">
                {{ ctaLabel }}
              </router-link>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-8 items-start">
          <div class="space-y-8">

            <!-- Modules - each is its own "column" card with a cover page;
                 clicking one opens the Module Overview showing its Notes -->
            <section class="glass-panel p-6 rounded-3xl border border-[#1f293d] bg-[#0d1420] space-y-4 font-mono">
              <h3 class="text-sm font-extrabold text-white uppercase tracking-wider flex items-center gap-2">
                <svg class="w-4 h-4 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"/></svg>
                <span>Modules</span>
              </h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                <router-link
                  v-for="mod in course.modules"
                  :key="mod.id"
                  :to="`/academy/course/${course.slug}/module/${mod.id}`"
                  class="rounded-2xl overflow-hidden border transition-all group flex flex-col"
                  :class="mod.is_completed ? 'bg-[#9fef00]/5 border-[#9fef00]/40 hover:border-[#9fef00]' : mod.is_in_progress ? 'bg-[#0b0e14] border-amber-400/40 hover:border-amber-400/70' : 'bg-[#0b0e14] border-[#1f293d] hover:border-[#00f0ff]/50'"
                >
                  <div class="h-40 w-full overflow-hidden relative flex-shrink-0">
                    <img :src="mod.cover_image" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                    <span v-if="mod.is_completed" class="absolute top-2 right-2 w-6 h-6 rounded-full bg-[#9fef00] text-black flex items-center justify-center shadow-lg">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
                    </span>
                    <span v-else-if="mod.is_in_progress" class="absolute top-2 right-2 bg-amber-400 text-black text-[9px] font-mono font-extrabold px-2 py-0.5 rounded uppercase tracking-wider shadow-lg">
                      In Progress
                    </span>
                  </div>
                  <div class="p-3 space-y-1.5 flex-1 flex flex-col">
                    <h4
                      class="text-sm font-bold transition-colors line-clamp-2 leading-snug"
                      :class="mod.is_completed ? 'text-[#9fef00] line-through decoration-2' : 'text-slate-200 group-hover:text-[#00f0ff]'"
                    >
                      {{ mod.title }}
                    </h4>
                    <p v-if="mod.description" class="text-xs text-slate-500 line-clamp-2 flex-1">{{ mod.description }}</p>
                    <div class="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                      <span v-if="mod.is_completed || mod.is_in_progress" :class="mod.is_completed ? 'text-[#9fef00]' : 'text-amber-400'" class="font-bold">{{ mod.notes_completed }}/{{ mod.notes_count }} Notes</span>
                      <span v-else>{{ mod.notes_count }} Notes</span>
                      <span>{{ mod.read_time_minutes }} min</span>
                    </div>
                  </div>
                </router-link>
                <p v-if="!course.modules?.length" class="col-span-full text-xs text-slate-500 text-center py-6">No modules published yet.</p>
              </div>
            </section>

            <!-- Additional Resources: YouTube gets an embedded player; everything
                 else (GitHub, Drive, Google Doc, PDF, Markdown, Website, Note)
                 renders as an icon-coded card in one unified section. -->
            <section v-if="(course.resources || []).length" class="glass-panel p-6 rounded-3xl border border-[#1f293d] bg-[#0d1420] space-y-4 font-mono">
              <h3 class="text-sm font-extrabold text-white uppercase tracking-wider flex items-center gap-2">
                <svg class="w-4 h-4 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/></svg>
                <span>Additional Resources</span>
              </h3>

              <div v-if="videoResources.length" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div v-for="vid in videoResources" :key="vid.id" class="space-y-2">
                  <div class="aspect-video rounded-xl overflow-hidden border border-[#1f293d] bg-black">
                    <iframe
                      v-if="youtubeEmbedUrl(vid.url)"
                      :src="youtubeEmbedUrl(vid.url)"
                      class="w-full h-full"
                      frameborder="0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowfullscreen
                    ></iframe>
                    <a v-else :href="vid.url" target="_blank" rel="noopener noreferrer" class="w-full h-full flex items-center justify-center text-xs text-slate-400">Open video &rarr;</a>
                  </div>
                  <p class="text-xs font-bold text-slate-300">{{ vid.title }}</p>
                </div>
              </div>

              <div v-if="otherResources.length" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
                <component
                  :is="res.resource_type === 'note' ? 'div' : 'a'"
                  v-for="res in otherResources"
                  :key="res.id"
                  v-bind="res.resource_type === 'note' ? {} : { href: res.url, target: '_blank', rel: 'noopener noreferrer' }"
                  class="flex items-start gap-3 p-3.5 rounded-xl border transition-all group"
                  :class="[resourceMeta(res.resource_type).bg, res.resource_type !== 'note' ? 'hover:brightness-125 cursor-pointer' : '']"
                >
                  <div class="w-8 h-8 rounded-lg bg-black/20 flex items-center justify-center shrink-0" :class="resourceMeta(res.resource_type).color" v-html="resourceIconSvg(res.resource_type)"></div>
                  <div class="min-w-0 flex-1">
                    <span class="text-[9px] uppercase font-bold tracking-wider" :class="resourceMeta(res.resource_type).color">{{ resourceMeta(res.resource_type).label }}</span>
                    <p class="text-sm font-bold text-slate-200 truncate">{{ res.title }}</p>
                    <p v-if="res.description" class="text-xs text-slate-500 mt-0.5" :class="res.resource_type === 'note' ? 'whitespace-pre-line leading-relaxed' : 'truncate'">{{ res.description }}</p>
                  </div>
                  <span v-if="res.resource_type !== 'note'" class="text-slate-600 group-hover:text-white shrink-0">&rarr;</span>
                </component>
              </div>
            </section>

          </div>

          <!-- Teacher: Manage Resources -->
          <div v-if="authStore.isTeacher" class="space-y-6 sticky top-6">
            <div class="glass-panel p-5 rounded-3xl border border-[#1f293d] bg-[#0d1420] space-y-4 font-mono">
              <h3 class="text-xs font-extrabold text-[#00f0ff] uppercase tracking-wider">// Manage Modules</h3>

              <div class="space-y-2">
                <div v-for="mod in course.modules" :key="mod.id" class="flex items-center justify-between p-2.5 bg-[#0b0e14] rounded-lg border border-[#1f293d] gap-2">
                  <div class="min-w-0">
                    <p class="text-xs font-bold text-slate-200 truncate">{{ mod.title }}</p>
                    <span class="text-[10px] text-slate-500">{{ mod.notes_count }} notes</span>
                  </div>
                  <div class="flex items-center gap-2 shrink-0">
                    <router-link :to="`/academy/course/${course.slug}/module/${mod.id}`" title="Manage Notes" class="text-slate-500 hover:text-[#9fef00]">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                    </router-link>
                    <button @click="startEditModule(mod)" title="Edit Module Details" class="text-slate-500 hover:text-[#00f0ff]">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21H3v-3.5L16.732 3.732z"/></svg>
                    </button>
                    <button @click="deleteModule(mod.id)" class="text-rose-400 hover:text-rose-300">&times;</button>
                  </div>
                </div>
                <p v-if="!course.modules?.length" class="text-[11px] text-slate-500 text-center py-3">No modules yet.</p>
              </div>

              <div class="space-y-2 pt-3 border-t border-[#1f293d]">
                <p class="text-[10px] text-slate-500 uppercase font-bold">{{ editingModuleId ? 'Editing Module' : 'New Module' }}</p>
                <input v-model="moduleForm.title" type="text" placeholder="Module title" class="input-field w-full py-1.5 text-[11px]" />
                <input v-model="moduleForm.description" type="text" placeholder="Short description" class="input-field w-full py-1.5 text-[11px]" />
                <div v-if="moduleForm.cover_image" class="w-full h-20 rounded-lg overflow-hidden border border-[#1f293d]">
                  <img :src="moduleForm.cover_image" class="w-full h-full object-cover" />
                </div>
                <div class="flex items-center gap-2">
                  <input v-model="moduleForm.cover_image" type="text" placeholder="Cover image URL" class="input-field flex-1 py-1.5 text-[11px]" />
                  <button type="button" @click="triggerModuleCoverUpload" :disabled="moduleCoverUploading" class="btn-ghost text-[11px] py-1.5 px-2.5 text-[#00f0ff] border border-[#00f0ff]/40 hover:bg-[#00f0ff]/10 flex-shrink-0 font-bold">
                    {{ moduleCoverUploading ? '...' : 'Upload' }}
                  </button>
                  <input ref="moduleCoverFileInput" type="file" accept="image/*" class="hidden" @change="handleModuleCoverUpload" />
                </div>
                <div class="flex items-center gap-2">
                  <button v-if="editingModuleId" @click="cancelEditModule" class="btn-ghost flex-1 py-1.5 text-[11px]">Cancel</button>
                  <button @click="editingModuleId ? saveModuleEdit() : addModule()" :disabled="!moduleForm.title.trim()" class="btn-ghost flex-1 py-1.5 text-[11px]">
                    {{ editingModuleId ? 'Save Changes' : '+ Create Module' }}
                  </button>
                </div>
              </div>
            </div>

            <div class="glass-panel p-5 rounded-3xl border border-[#1f293d] bg-[#0d1420] space-y-4 font-mono">
              <h3 class="text-xs font-extrabold text-[#00f0ff] uppercase tracking-wider">// Manage Resources</h3>

              <div class="space-y-2">
                <div v-for="res in course.resources" :key="res.id" class="flex items-center gap-2.5 p-2.5 bg-[#0b0e14] rounded-lg border border-[#1f293d]">
                  <div class="w-6 h-6 rounded-md bg-black/20 flex items-center justify-center shrink-0" :class="resourceMeta(res.resource_type).color" v-html="resourceIconSvg(res.resource_type)"></div>
                  <div class="min-w-0 flex-1">
                    <span class="text-[9px] uppercase font-bold" :class="resourceMeta(res.resource_type).color">{{ resourceMeta(res.resource_type).label }}</span>
                    <p class="text-xs font-bold text-slate-200 truncate">{{ res.title }}</p>
                  </div>
                  <div class="flex items-center gap-2 shrink-0">
                    <button @click="startEditResource(res)" title="Edit Resource" class="text-slate-500 hover:text-[#00f0ff]">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21H3v-3.5L16.732 3.732z"/></svg>
                    </button>
                    <button @click="deleteResource(res.id)" class="text-rose-400 hover:text-rose-300">&times;</button>
                  </div>
                </div>
                <p v-if="!course.resources?.length" class="text-[11px] text-slate-500 text-center py-3">No resources added yet.</p>
              </div>

              <div class="space-y-2 pt-3 border-t border-[#1f293d]">
                <p class="text-[10px] text-slate-500 uppercase font-bold">{{ editingResourceId ? 'Editing Resource' : 'New Resource' }}</p>
                <select v-model="resourceForm.resource_type" class="input-field w-full py-1.5 text-[11px] bg-[#0b0e14]">
                  <option value="youtube">YouTube Video</option>
                  <option value="github">GitHub Link</option>
                  <option value="drive">Google Drive</option>
                  <option value="gdoc">Google Doc</option>
                  <option value="pdf">PDF File</option>
                  <option value="markdown">Markdown File</option>
                  <option value="website">Website Link</option>
                  <option value="note">Note</option>
                </select>
                <input v-model="resourceForm.title" type="text" placeholder="Title" class="input-field w-full py-1.5 text-[11px]" />

                <template v-if="resourceForm.resource_type === 'note'">
                  <textarea v-model="resourceForm.description" rows="3" placeholder="Note content..." class="input-field w-full py-1.5 text-[11px]"></textarea>
                </template>
                <template v-else>
                  <div class="flex items-center gap-2">
                    <input v-model="resourceForm.url" type="text" placeholder="https://..." class="input-field flex-1 py-1.5 text-[11px]" />
                    <button
                      v-if="['pdf', 'markdown'].includes(resourceForm.resource_type)"
                      type="button"
                      @click="triggerResourceFileUpload"
                      :disabled="resourceFileUploading"
                      class="btn-ghost text-[11px] py-1.5 px-2.5 text-[#00f0ff] border border-[#00f0ff]/40 hover:bg-[#00f0ff]/10 flex-shrink-0 font-bold"
                    >
                      {{ resourceFileUploading ? '...' : 'Upload' }}
                    </button>
                    <input
                      ref="resourceFileInput"
                      type="file"
                      :accept="resourceForm.resource_type === 'pdf' ? '.pdf,application/pdf' : '.md,text/markdown,text/plain'"
                      class="hidden"
                      @change="handleResourceFileUpload"
                    />
                  </div>
                  <input v-model="resourceForm.description" type="text" placeholder="Optional caption" class="input-field w-full py-1.5 text-[11px]" />
                </template>

                <div class="flex items-center gap-2">
                  <button v-if="editingResourceId" @click="cancelEditResource" class="btn-ghost flex-1 py-1.5 text-[11px]">Cancel</button>
                  <button @click="editingResourceId ? saveResourceEdit() : addResource()" :disabled="!canAddResource" class="btn-ghost flex-1 py-1.5 text-[11px]">
                    {{ editingResourceId ? 'Save Changes' : '+ Add Resource' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const route = useRoute()
const authStore = useAuthStore()

const course = ref({})
const loading = ref(true)
const error = ref('')

const resourceForm = ref({ title: '', url: '', resource_type: 'youtube', description: '' })
const editingResourceId = ref(null)
const moduleForm = ref({ title: '', description: '', cover_image: '' })
const editingModuleId = ref(null)
const moduleCoverUploading = ref(false)
const moduleCoverFileInput = ref(null)
const resourceFileUploading = ref(false)
const resourceFileInput = ref(null)

const videoResources = computed(() => (course.value.resources || []).filter(r => r.resource_type === 'youtube'))
const otherResources = computed(() => (course.value.resources || []).filter(r => r.resource_type !== 'youtube'))

// Icon/label/color per resource type - 'link' is kept as a legacy alias so
// pre-existing rows (from before the type list was expanded) still render.
const RESOURCE_META = {
  youtube: { label: 'YouTube', color: 'text-rose-400', bg: 'bg-rose-400/5 border-rose-400/20' },
  github: { label: 'GitHub', color: 'text-slate-200', bg: 'bg-slate-400/5 border-slate-400/20' },
  drive: { label: 'Google Drive', color: 'text-emerald-400', bg: 'bg-emerald-400/5 border-emerald-400/20' },
  gdoc: { label: 'Google Doc', color: 'text-blue-400', bg: 'bg-blue-400/5 border-blue-400/20' },
  pdf: { label: 'PDF', color: 'text-red-400', bg: 'bg-red-400/5 border-red-400/20' },
  markdown: { label: 'Markdown', color: 'text-violet-400', bg: 'bg-violet-400/5 border-violet-400/20' },
  website: { label: 'Website', color: 'text-[#00f0ff]', bg: 'bg-[#00f0ff]/5 border-[#00f0ff]/20' },
  link: { label: 'Website', color: 'text-[#00f0ff]', bg: 'bg-[#00f0ff]/5 border-[#00f0ff]/20' },
  note: { label: 'Note', color: 'text-amber-400', bg: 'bg-amber-400/5 border-amber-400/20' }
}
const resourceMeta = (type) => RESOURCE_META[type] || RESOURCE_META.website

const RESOURCE_ICONS = {
  youtube: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>',
  github: '<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.833.092-.647.35-1.088.636-1.338-2.221-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.31.678.921.678 1.856 0 1.34-.012 2.421-.012 2.751 0 .268.18.58.688.482A10.02 10.02 0 0022 12.017C22 6.484 17.522 2 12 2z"/></svg>',
  drive: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 001.7-9.71A6 6 0 006.663 6.07 4.998 4.998 0 003 11c0 .35.035.687.1 1.008A4.002 4.002 0 003 15z"/></svg>',
  gdoc: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>',
  pdf: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v6h6"/></svg>',
  markdown: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16M6 9l-4 3 4 3m8-6l4 3-4 3"/></svg>',
  website: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 002 2h3.947M12 21a9 9 0 100-18 9 9 0 000 18z"/></svg>',
  link: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/></svg>',
  note: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>'
}
const resourceIconSvg = (type) => RESOURCE_ICONS[type] || RESOURCE_ICONS.website

const canAddResource = computed(() => {
  if (!resourceForm.value.title.trim()) return false
  if (resourceForm.value.resource_type === 'note') return true
  return !!resourceForm.value.url.trim()
})

const difficultyBadgeClass = computed(() => {
  const d = course.value.difficulty
  if (d === 'Advanced') return 'bg-rose-400/15 text-rose-400'
  if (d === 'Intermediate') return 'bg-amber-400/15 text-amber-400'
  return 'bg-[#9fef00]/15 text-[#9fef00]'
})

const ctaLabel = computed(() => {
  if (!course.value.enrollment) return 'Start Learning'
  if (course.value.enrollment.progress_percent >= 100) return 'Review Path'
  return 'Continue Learning'
})

// Accepts youtube.com/watch?v=, youtu.be/, or an already-embeddable URL and
// normalizes it to the /embed/ form iframes need. Falls back to null (a
// plain "open video" link) for anything that doesn't look like YouTube.
const youtubeEmbedUrl = (url) => {
  if (!url) return null
  const watchMatch = url.match(/[?&]v=([^&]+)/)
  if (watchMatch) return `https://www.youtube.com/embed/${watchMatch[1]}`
  const shortMatch = url.match(/youtu\.be\/([^?&]+)/)
  if (shortMatch) return `https://www.youtube.com/embed/${shortMatch[1]}`
  if (url.includes('youtube.com/embed/')) return url
  return null
}

const fetchOverview = async () => {
  loading.value = true
  try {
    const res = await axios.get(`/api/academy/course/${route.params.slug}/overview`, { withCredentials: true })
    course.value = res.data
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load module overview.'
  } finally {
    loading.value = false
  }
}

const addResource = async () => {
  try {
    const res = await axios.post(`/api/academy/courses/${course.value.id}/resources`, resourceForm.value, { withCredentials: true })
    course.value.resources = [...(course.value.resources || []), res.data]
    resourceForm.value = { title: '', url: '', resource_type: resourceForm.value.resource_type, description: '' }
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to add resource')
  }
}

const startEditResource = (res) => {
  editingResourceId.value = res.id
  resourceForm.value = { title: res.title, url: res.url || '', resource_type: res.resource_type, description: res.description || '' }
}

const cancelEditResource = () => {
  editingResourceId.value = null
  resourceForm.value = { title: '', url: '', resource_type: 'youtube', description: '' }
}

const saveResourceEdit = async () => {
  try {
    const res = await axios.put(`/api/academy/courses/resources/${editingResourceId.value}`, resourceForm.value, { withCredentials: true })
    const idx = course.value.resources.findIndex(r => r.id === editingResourceId.value)
    if (idx !== -1) course.value.resources[idx] = res.data
    cancelEditResource()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to save resource')
  }
}

const triggerResourceFileUpload = () => {
  if (resourceFileInput.value) resourceFileInput.value.click()
}

const handleResourceFileUpload = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return

  resourceFileUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('feature', 'courses')

    const res = await axios.post('/api/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      withCredentials: true
    })

    if (res.data && res.data.url) {
      resourceForm.value.url = res.data.url
      if (!resourceForm.value.title.trim()) {
        resourceForm.value.title = file.name.replace(/\.[^/.]+$/, '')
      }
    }
  } catch (err) {
    alert('Failed to upload file: ' + (err.response?.data?.error || err.message))
  } finally {
    resourceFileUploading.value = false
    e.target.value = ''
  }
}

const deleteResource = async (resourceId) => {
  try {
    await axios.delete(`/api/academy/courses/resources/${resourceId}`, { withCredentials: true })
    course.value.resources = course.value.resources.filter(r => r.id !== resourceId)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete resource')
  }
}

const deleteModule = async (moduleId) => {
  if (!confirm('Delete this module and all its notes? This cannot be undone.')) return
  try {
    await axios.delete(`/api/academy/chapters/${moduleId}`, { withCredentials: true })
    course.value.modules = course.value.modules.filter(m => m.id !== moduleId)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete module')
  }
}

const addModule = async () => {
  try {
    const res = await axios.post(`/api/academy/courses/${course.value.id}/modules`, moduleForm.value, { withCredentials: true })
    course.value.modules = [...(course.value.modules || []), { ...res.data, read_time_minutes: 0 }]
    moduleForm.value = { title: '', description: '', cover_image: '' }
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to create module')
  }
}

const startEditModule = (mod) => {
  editingModuleId.value = mod.id
  moduleForm.value = { title: mod.title, description: mod.description || '', cover_image: mod.cover_image || '' }
}

const cancelEditModule = () => {
  editingModuleId.value = null
  moduleForm.value = { title: '', description: '', cover_image: '' }
}

const saveModuleEdit = async () => {
  try {
    const res = await axios.put(`/api/academy/chapters/${editingModuleId.value}`, moduleForm.value, { withCredentials: true })
    const idx = course.value.modules.findIndex(m => m.id === editingModuleId.value)
    if (idx !== -1) course.value.modules[idx] = { ...course.value.modules[idx], ...res.data }
    cancelEditModule()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to save module')
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

onMounted(fetchOverview)
</script>
