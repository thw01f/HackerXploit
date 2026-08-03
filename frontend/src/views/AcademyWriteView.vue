<template>
  <div class="h-[calc(100vh-80px)] text-slate-100 font-mono bg-[#0b0e14] flex flex-col overflow-hidden selection:bg-[#00f0ff] selection:text-black">

    <!-- Top Control Bar -->
    <div class="h-12 bg-[#161b22] border-b border-[#21262d] px-4 flex items-center justify-between flex-shrink-0">
      <div class="flex items-center space-x-3 text-xs min-w-0">
        <router-link to="/academy" class="text-slate-400 hover:text-white flex items-center space-x-1 flex-shrink-0">
          <span>&larr; Academy</span>
        </router-link>
        <span class="text-slate-600">/</span>
        <span class="font-bold text-[#00f0ff] flex items-center space-x-1.5 flex-shrink-0">
          <svg class="w-4 h-4 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
          </svg>
          <span>Studio</span>
        </span>
        <span class="text-slate-600">/</span>
        <span class="text-slate-300 font-bold truncate">{{ currentNote.title || 'Untitled Note.md' }}</span>
      </div>

      <div class="flex items-center space-x-2 flex-shrink-0">
        <!-- New Path Button -->
        <button @click="promptNewPath" class="px-2.5 py-1 text-[11px] font-bold bg-[#21262d] hover:bg-[#30363d] text-slate-300 rounded border border-[#30363d] transition-all flex items-center space-x-1">
          <svg class="w-3.5 h-3.5 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          <span>New Path</span>
        </button>

        <!-- Mode Switcher -->
        <button
          @click="mode = mode === 'editor' ? 'upload' : 'editor'"
          class="px-3 py-1 text-[11px] font-bold bg-[#00f0ff]/15 text-[#00f0ff] border border-[#00f0ff]/30 rounded transition-all hover:bg-[#00f0ff]/25 flex items-center gap-1.5"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
          </svg>
          <span>{{ mode === 'editor' ? 'Import .md File' : 'Back to Editor' }}</span>
        </button>

        <!-- Publish Button -->
        <button
          @click="publishCurrentNote"
          :disabled="loading || !currentNote.title.trim() || !currentNote.content_markdown.trim() || !currentNote.module_id"
          class="btn-htb text-xs py-1 px-4 font-bold uppercase tracking-wider shadow-lg flex items-center gap-1.5"
        >
          <svg class="w-3.5 h-3.5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
          <span>{{ loading ? 'Publishing...' : 'Publish Note' }}</span>
        </button>
      </div>
    </div>

    <!-- Main Workspace -->
    <div class="flex-1 flex overflow-hidden">

      <!-- Column 1: Left Path -> Module -> Note Tree Sidebar -->
      <div class="w-80 bg-[#161b22] border-r border-[#21262d] flex flex-col flex-shrink-0 select-none">

        <!-- Sidebar Header -->
        <div class="p-3 border-b border-[#21262d] flex items-center justify-between text-xs text-slate-400 font-bold uppercase tracking-wider">
          <span>Content Tree</span>
          <span class="text-[10px] text-[#9fef00]">Path &rsaquo; Module &rsaquo; Note</span>
        </div>

        <!-- Tree -->
        <div class="flex-1 overflow-y-auto p-2 space-y-2">
          <div v-if="paths.length === 0" class="p-4 text-center text-slate-500 text-xs italic">
            No paths yet. Click "New Path" to get started.
          </div>

          <div v-for="path in paths" :key="path.id" class="space-y-1">

            <!-- Path Header -->
            <div class="px-2 py-1.5 rounded hover:bg-[#21262d] text-xs font-bold text-slate-300 flex items-center justify-between cursor-pointer group transition-colors">
              <div @click="togglePath(path.id)" class="flex items-center space-x-2 truncate flex-1">
                <svg class="w-4 h-4 text-[#00f0ff] flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                </svg>
                <span class="truncate uppercase text-[11px] tracking-wider">{{ path.title }}</span>
                <span class="text-[10px] text-slate-500 font-mono">({{ path.modules.length }})</span>
              </div>
              <div class="opacity-0 group-hover:opacity-100 flex items-center space-x-1 transition-opacity">
                <button @click.stop="promptNewModule(path)" title="New Module" class="text-[10px] hover:text-[#9fef00] p-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                </button>
                <button @click.stop="renamePath(path)" title="Rename Path" class="text-[10px] hover:text-[#00f0ff] p-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21H3v-3.5L16.732 3.732z"/></svg>
                </button>
                <button @click.stop="deletePath(path)" title="Delete Path" class="text-[10px] hover:text-rose-400 p-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </button>
              </div>
            </div>

            <!-- Modules within this Path -->
            <div v-if="openPaths[path.id]" class="pl-3 space-y-1">
              <p v-if="!path.modules.length" class="pl-3 py-1 text-[10px] text-slate-600 italic">No modules yet.</p>

              <div v-for="mod in path.modules" :key="mod.id" class="space-y-0.5">
                <div
                  @dragover.prevent
                  @drop.prevent="onModuleDrop($event, mod)"
                  class="px-2 py-1.5 rounded hover:bg-[#21262d] text-xs font-bold text-slate-400 flex items-center justify-between cursor-pointer group/mod transition-colors"
                >
                  <div @click="toggleModule(mod.id)" class="flex items-center space-x-2 truncate flex-1">
                    <svg class="w-3.5 h-3.5 text-amber-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                    </svg>
                    <span class="truncate text-[11px]">{{ mod.title }}</span>
                    <span class="text-[10px] text-slate-600 font-mono">({{ mod.notes.length }})</span>
                  </div>
                  <div class="opacity-0 group-hover/mod:opacity-100 flex items-center space-x-1 transition-opacity">
                    <button @click.stop="createNewNote(mod)" title="New Note" class="text-[10px] hover:text-[#9fef00] p-1">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                    </button>
                    <button @click.stop="renameModule(mod)" title="Rename Module" class="text-[10px] hover:text-[#00f0ff] p-1">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21H3v-3.5L16.732 3.732z"/></svg>
                    </button>
                    <button @click.stop="deleteModule(path, mod)" title="Delete Module" class="text-[10px] hover:text-rose-400 p-1">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                    </button>
                  </div>
                </div>

                <!-- Notes within this Module -->
                <div v-if="openModules[mod.id]" class="pl-5 space-y-0.5">
                  <div
                    v-for="(note, idx) in mod.notes"
                    :key="note.id"
                    draggable="true"
                    @dragstart="onNoteDragStart($event, note, mod)"
                    @click="selectNote(note, mod)"
                    :class="[
                      'px-2 py-1.5 rounded text-xs cursor-pointer flex items-center justify-between truncate transition-all group/note',
                      currentNote.id === note.id ? 'bg-[#00f0ff]/15 text-[#00f0ff] font-bold border-l-2 border-[#00f0ff]' : 'text-slate-400 hover:text-white hover:bg-[#21262d]'
                    ]"
                  >
                    <div class="flex items-center space-x-2 truncate">
                      <span class="text-slate-500 text-[10px]">{{ idx + 1 }}.</span>
                      <span class="truncate">{{ note.title }}</span>
                    </div>
                    <div class="opacity-0 group-hover/note:opacity-100 flex items-center space-x-1 transition-opacity">
                      <button @click.stop="moveNoteUp(mod, idx)" title="Move Up" class="hover:text-[#00f0ff] text-[10px] px-0.5 font-bold">▲</button>
                      <button @click.stop="moveNoteDown(mod, idx)" title="Move Down" class="hover:text-[#00f0ff] text-[10px] px-0.5 font-bold">▼</button>
                      <button @click.stop="deleteNote(mod, note.id)" title="Delete Note" class="text-[10px] text-rose-400 hover:scale-110 px-0.5">✕</button>
                    </div>
                  </div>
                  <div v-if="!mod.notes.length" class="pl-3 py-1 text-[10px] text-slate-600 italic">
                    Drop a note here, or click + above
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>

      <!-- Mode A: Split Editor & MkDocs-Style Live Preview -->
      <div v-if="mode === 'editor'" class="flex-1 flex overflow-hidden">

        <!-- Column 2: Raw Markdown Text Editor -->
        <div class="flex-1 bg-[#0b0e14] flex flex-col border-r border-[#21262d]">

          <!-- Note Metadata Header -->
          <div class="p-4 bg-[#161b22]/50 border-b border-[#21262d] space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-[10px] font-bold text-slate-400 uppercase mb-1">Note Title</label>
                <input
                  v-model="currentNote.title"
                  type="text"
                  placeholder="e.g. Reverse Engineering 101"
                  class="input-field text-xs w-full bg-[#0b0e14] py-1.5"
                />
              </div>
              <div>
                <label class="block text-[10px] font-bold text-slate-400 uppercase mb-1">Assign to Module</label>
                <select v-model="currentNote.module_id" class="input-field text-xs w-full bg-[#0b0e14] py-1.5 text-slate-300">
                  <optgroup v-for="path in paths" :key="path.id" :label="path.title">
                    <option v-for="mod in path.modules" :key="mod.id" :value="mod.id">{{ mod.title }}</option>
                  </optgroup>
                </select>
              </div>
            </div>
          </div>

          <!-- Raw Markdown Area -->
          <div class="flex-1 relative">
            <textarea
              v-model="currentNote.content_markdown"
              placeholder="# Write Markdown note...\n\nUse [links](https://example.com) and images ![alt](url)..."
              class="w-full h-full p-5 bg-[#0b0e14] text-slate-200 font-mono text-xs leading-relaxed focus:outline-none resize-none"
            ></textarea>
          </div>

        </div>

        <!-- Column 3: MkDocs Material Rendered Preview & TOC -->
        <div class="flex-1 bg-[#0d1420] flex overflow-hidden">

          <!-- Content Pane -->
          <div class="flex-1 overflow-y-auto p-8 space-y-6">

            <!-- Breadcrumbs -->
            <div class="text-xs text-slate-400 font-mono flex items-center space-x-2">
              <span class="text-[#00f0ff] uppercase font-bold">{{ currentPathTitle || 'Path' }}</span>
              <span>&rsaquo;</span>
              <span class="text-slate-300 uppercase font-bold">{{ currentModuleTitle || 'Module' }}</span>
              <span>&rsaquo;</span>
              <span class="text-white font-bold">{{ currentNote.title || 'Untitled Note' }}</span>
            </div>

            <!-- Rendered Markdown Article Body -->
            <div
              class="mkdocs-content prose prose-invert max-w-none text-slate-200 font-sans leading-relaxed text-sm"
              v-html="renderedPreviewHtml"
            ></div>

          </div>

          <!-- Right Sidebar: MkDocs On-This-Page TOC -->
          <div class="w-56 bg-[#161b22]/70 border-l border-[#21262d] p-4 hidden lg:block overflow-y-auto font-mono">
            <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-3">On this page</div>
            <ul v-if="tocHeadings.length" class="space-y-1.5 text-xs">
              <li
                v-for="h in tocHeadings"
                :key="h.id"
                :class="[
                  'hover:text-[#00f0ff] cursor-pointer transition-colors truncate',
                  h.level === 1 ? 'font-bold text-white' : (h.level === 2 ? 'pl-2 text-slate-300' : 'pl-4 text-slate-400')
                ]"
              >
                <a :href="`#${h.id}`" class="block truncate">{{ h.text }}</a>
              </li>
            </ul>
            <div v-else class="text-[11px] text-slate-500 italic">No section headings found</div>
          </div>

        </div>

      </div>

      <!-- Mode B: Direct Drag & Drop .md File Import Zone -->
      <div v-else class="flex-1 bg-[#0b0e14] p-12 flex flex-col items-center justify-center text-center">
        <div
          @dragover.prevent
          @drop.prevent="handleFileDrop"
          @click="$refs.fileInput.click()"
          class="w-full max-w-xl border-2 border-dashed border-[#21262d] hover:border-[#00f0ff] rounded-3xl p-12 bg-[#161b22]/50 cursor-pointer transition-all space-y-4"
        >
          <input ref="fileInput" type="file" accept=".md" class="hidden" @change="handleFileSelect" />
          <div class="text-5xl">📁</div>
          <h2 class="text-lg font-bold text-white uppercase tracking-wider">Drag & Drop .md File</h2>
          <p class="text-xs text-slate-400 max-w-md mx-auto">
            Upload your markdown file directly. Front-matter metadata (title) will be auto-extracted. It's added to the currently selected module.
          </p>
          <div v-if="selectedFileName" class="text-xs font-bold text-[#9fef00] pt-2">
            Loaded File: {{ selectedFileName }}
          </div>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const mode = ref('editor')
const loading = ref(false)
const selectedFileName = ref('')

const openPaths = ref({})
const openModules = ref({})

const paths = ref([])

const currentNote = ref({
  id: null,
  title: 'New Security Note',
  module_id: null,
  content_markdown: '# New Security Note\n\nWrite your module note content here...'
})

const currentPathTitle = computed(() => {
  const p = paths.value.find(p => p.modules.some(m => m.id === currentNote.value.module_id))
  return p?.title || ''
})
const currentModuleTitle = computed(() => {
  for (const p of paths.value) {
    const m = p.modules.find(m => m.id === currentNote.value.module_id)
    if (m) return m.title
  }
  return ''
})

// Fetch the full Path -> Module -> Note tree from the real API
const fetchTree = async () => {
  try {
    const res = await axios.get('/api/academy/courses', { withCredentials: true })
    const courses = res.data.courses || []

    const realPaths = []
    for (const c of courses) {
      const pathEntry = { id: c.id, slug: c.slug, title: c.title, modules: [] }
      try {
        const overviewRes = await axios.get(`/api/academy/course/${c.slug}/overview`, { withCredentials: true })
        for (const mod of (overviewRes.data.modules || [])) {
          const modEntry = { id: mod.id, title: mod.title, description: mod.description, cover_image: mod.cover_image, notes: [] }
          try {
            const modRes = await axios.get(`/api/academy/modules/${mod.id}/read`, { withCredentials: true })
            modEntry.notes = (modRes.data.notes || []).map(n => ({
              id: n.id, title: n.title, content_markdown: n.content_markdown, attachments: n.attachments || []
            }))
          } catch (e) { /* module has no readable notes yet */ }
          pathEntry.modules.push(modEntry)
          openModules.value[mod.id] = true
        }
      } catch (e) { /* path has no modules yet */ }
      realPaths.push(pathEntry)
      openPaths.value[c.id] = true
    }

    paths.value = realPaths

    if (!currentNote.value.module_id) {
      const firstModule = realPaths.flatMap(p => p.modules)[0]
      if (firstModule?.notes.length) {
        currentNote.value = { ...firstModule.notes[0], module_id: firstModule.id }
      } else if (firstModule) {
        currentNote.value.module_id = firstModule.id
      }
    }
  } catch (err) {
    console.error('Failed to fetch content tree', err)
  }
}

// Reorder Notes UP/DOWN inside a Module and persist to server
const moveNoteUp = async (mod, idx) => {
  if (idx <= 0) return
  const temp = mod.notes[idx]
  mod.notes[idx] = mod.notes[idx - 1]
  mod.notes[idx - 1] = temp
  await persistNoteOrder(mod)
}

const moveNoteDown = async (mod, idx) => {
  if (idx >= mod.notes.length - 1) return
  const temp = mod.notes[idx]
  mod.notes[idx] = mod.notes[idx + 1]
  mod.notes[idx + 1] = temp
  await persistNoteOrder(mod)
}

const persistNoteOrder = async (mod) => {
  const noteIds = mod.notes.map(n => n.id).filter(id => typeof id === 'number')
  if (noteIds.length) {
    try {
      await axios.put(`/api/academy/modules/${mod.id}/reorder-notes`, { note_ids: noteIds }, { withCredentials: true })
    } catch (e) {
      console.error('Failed to persist note order on server', e)
    }
  }
}

// MkDocs Custom Markdown-to-HTML parser with callout alerts and clickable links
const renderedPreviewHtml = computed(() => {
  let md = currentNote.value.content_markdown || ''

  // 1. Callout alert boxes
  md = md.replace(/^>\s*\[!NOTE\]\s*\n?/gm, '<div class="my-4 p-4 rounded-xl bg-cyan-950/60 border-l-4 border-[#00f0ff] text-cyan-200 text-xs font-mono"><strong class="text-[#00f0ff] uppercase block mb-1">ℹ️ Note</strong>')
  md = md.replace(/^>\s*\[!TIP\]\s*\n?/gm, '<div class="my-4 p-4 rounded-xl bg-emerald-950/60 border-l-4 border-[#9fef00] text-emerald-200 text-xs font-mono"><strong class="text-[#9fef00] uppercase block mb-1">Tip</strong>')
  md = md.replace(/^>\s*\[!WARNING\]\s*\n?/gm, '<div class="my-4 p-4 rounded-xl bg-amber-950/60 border-l-4 border-amber-400 text-amber-200 text-xs font-mono"><strong class="text-amber-400 uppercase block mb-1">Warning</strong>')
  md = md.replace(/^>\s*\[!IMPORTANT\]\s*\n?/gm, '<div class="my-4 p-4 rounded-xl bg-rose-950/60 border-l-4 border-rose-500 text-rose-200 text-xs font-mono"><strong class="text-rose-400 uppercase block mb-1">Important</strong>')

  // Close blockquote divs if open
  md = md.split('\n\n').map(block => {
    if (block.includes('<div class="my-4 p-4 rounded-xl') && !block.includes('</div>')) {
      return block + '</div>'
    }
    return block
  }).join('\n\n')

  // 2. Headings with IDs for TOC navigation
  md = md.replace(/^### (.*$)/gim, (m, p1) => `<h3 id="${slugify(p1)}" class="text-lg font-bold text-white mt-6 mb-3 font-serif border-b border-[#21262d] pb-1">${p1}</h3>`)
  md = md.replace(/^## (.*$)/gim, (m, p1) => `<h2 id="${slugify(p1)}" class="text-xl font-extrabold text-[#00f0ff] mt-8 mb-4 font-serif border-b border-[#21262d] pb-1">${p1}</h2>`)
  md = md.replace(/^# (.*$)/gim, (m, p1) => `<h1 id="${slugify(p1)}" class="text-3xl font-extrabold text-white mb-6 font-serif">${p1}</h1>`)

  // 3. Images ![alt](url)
  md = md.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" class="my-4 rounded-xl border border-[#21262d] max-h-96 w-full object-cover shadow-lg" />')

  // 4. Links [text](url) -> Clickable target="_blank"
  md = md.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-[#00f0ff] font-bold underline hover:text-[#9fef00] transition-colors">$1 &rarr;</a>')

  // 5. Code blocks ```
  md = md.replace(/```([a-z]*)\n([\s\S]*?)```/g, '<div class="my-4 rounded-xl overflow-hidden bg-[#0b0e14] border border-[#21262d] font-mono"><div class="px-4 py-1.5 bg-[#161b22] text-[10px] text-slate-400 uppercase font-bold border-b border-[#21262d] flex justify-between"><span>Code Snippet</span></div><pre class="p-4 text-xs text-slate-200 overflow-x-auto"><code>$2</code></pre></div>')

  // 6. Inline code `code`
  md = md.replace(/`([^`]+)`/g, '<code class="bg-[#161b22] text-[#9fef00] px-1.5 py-0.5 rounded text-xs font-mono border border-[#21262d]">$1</code>')

  // 7. Paragraphs & line breaks
  return md.split('\n\n').map(p => {
    if (p.trim().startsWith('<h') || p.trim().startsWith('<div') || p.trim().startsWith('<pre')) return p
    return `<p class="mb-4 leading-relaxed text-slate-300">${p}</p>`
  }).join('')
})

// TOC Extraction
const tocHeadings = computed(() => {
  const md = currentNote.value.content_markdown || ''
  const lines = md.split('\n')
  const headings = []

  lines.forEach(line => {
    const h1 = line.match(/^# (.*$)/)
    const h2 = line.match(/^## (.*$)/)
    const h3 = line.match(/^### (.*$)/)

    if (h1) headings.push({ level: 1, text: h1[1].trim(), id: slugify(h1[1].trim()) })
    else if (h2) headings.push({ level: 2, text: h2[1].trim(), id: slugify(h2[1].trim()) })
    else if (h3) headings.push({ level: 3, text: h3[1].trim(), id: slugify(h3[1].trim()) })
  })

  return headings
})

const slugify = (text) => {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
}

// Path / Module / Note Management
const togglePath = (pathId) => {
  openPaths.value[pathId] = !openPaths.value[pathId]
}
const toggleModule = (moduleId) => {
  openModules.value[moduleId] = !openModules.value[moduleId]
}

const selectNote = (note, mod) => {
  currentNote.value = { ...note, module_id: mod.id }
  mode.value = 'editor'
}

const promptNewPath = async () => {
  const name = prompt('Enter new Path title:')
  if (name && name.trim()) {
    try {
      await axios.post('/api/academy/courses', {
        title: name.trim(),
        description: `Learning path: ${name.trim()}`,
        status: 'published'
      }, { withCredentials: true })
      await fetchTree()
    } catch (e) {
      alert(e.response?.data?.error || 'Failed to create path')
    }
  }
}

const renamePath = async (path) => {
  const newName = prompt('Enter new Path title:', path.title)
  if (newName && newName.trim() && newName.trim() !== path.title) {
    try {
      await axios.put(`/api/academy/courses/${path.id}`, { title: newName.trim() }, { withCredentials: true })
      await fetchTree()
    } catch (e) {
      alert(e.response?.data?.error || 'Failed to rename path')
    }
  }
}

const deletePath = async (path) => {
  if (!confirm(`Delete path "${path.title}" and every module/note inside it? This cannot be undone.`)) return
  try {
    await axios.delete(`/api/academy/courses/${path.id}`, { withCredentials: true })
    await fetchTree()
  } catch (e) {
    alert(e.response?.data?.error || 'Failed to delete path')
  }
}

const promptNewModule = async (path) => {
  const name = prompt('Enter new Module title:')
  if (name && name.trim()) {
    try {
      const res = await axios.post(`/api/academy/courses/${path.id}/modules`, { title: name.trim() }, { withCredentials: true })
      await fetchTree()
      openModules.value[res.data.id] = true
    } catch (e) {
      alert(e.response?.data?.error || 'Failed to create module')
    }
  }
}

const renameModule = async (mod) => {
  const newName = prompt('Enter new Module title:', mod.title)
  if (newName && newName.trim() && newName.trim() !== mod.title) {
    try {
      await axios.put(`/api/academy/chapters/${mod.id}`, { title: newName.trim() }, { withCredentials: true })
      await fetchTree()
    } catch (e) {
      alert(e.response?.data?.error || 'Failed to rename module')
    }
  }
}

const deleteModule = async (path, mod) => {
  if (!confirm(`Delete module "${mod.title}" and every note inside it? This cannot be undone.`)) return
  try {
    await axios.delete(`/api/academy/chapters/${mod.id}`, { withCredentials: true })
    await fetchTree()
  } catch (e) {
    alert(e.response?.data?.error || 'Failed to delete module')
  }
}

const deleteNote = async (mod, noteId) => {
  if (!confirm('Delete this note?')) return
  try {
    await axios.delete(`/api/academy/notes/${noteId}`, { withCredentials: true })
  } catch (e) {
    console.error('Failed to delete note on server', e)
  }
  mod.notes = mod.notes.filter(n => n.id !== noteId)
  if (currentNote.value.id === noteId) {
    if (mod.notes.length) {
      selectNote(mod.notes[0], mod)
    } else {
      currentNote.value = { id: null, title: 'New Security Note', module_id: mod.id, content_markdown: '# New Security Note\n\nWrite your module note content here...' }
    }
  }
}

const createNewNote = (mod) => {
  currentNote.value = {
    id: null,
    title: 'Untitled Security Note',
    module_id: mod.id,
    content_markdown: '# New Security Note\n\nWrite your module note content here...'
  }
  openModules.value[mod.id] = true
  mode.value = 'editor'
}

const onNoteDragStart = (e, note, fromModule) => {
  e.dataTransfer.setData('application/json', JSON.stringify({ noteId: note.id, fromModuleId: fromModule.id }))
}

const onModuleDrop = async (e, targetModule) => {
  const rawData = e.dataTransfer.getData('application/json')
  if (!rawData) return
  const { noteId, fromModuleId } = JSON.parse(rawData)
  if (fromModuleId === targetModule.id) return

  let srcModule = null
  for (const p of paths.value) {
    const m = p.modules.find(m => m.id === fromModuleId)
    if (m) { srcModule = m; break }
  }
  if (!srcModule) return

  const idx = srcModule.notes.findIndex(n => n.id === noteId)
  if (idx === -1) return

  // Moving a note between modules has no dedicated endpoint - reassign via
  // delete-then-recreate isn't safe (loses the id/attachments), so this
  // updates order within the source and target locally then persists both
  // reorder calls; actual re-parenting happens through the note's own
  // content_markdown staying intact while we PUT a fresh chapter_id... but
  // ModuleNote has no "move" endpoint, so fall back to editing the note
  // directly: recreate under the target module, delete the original.
  try {
    const note = srcModule.notes[idx]
    await axios.post(`/api/academy/modules/${targetModule.id}/notes`, {
      title: note.title,
      content_markdown: note.content_markdown
    }, { withCredentials: true })
    await axios.delete(`/api/academy/notes/${noteId}`, { withCredentials: true })
    openModules.value[targetModule.id] = true
    await fetchTree()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to move note')
  }
}

const parseLocalFile = (filename, content) => {
  let title = filename.replace(/\.md$/i, '')
  let markdown = content

  const pattern = /^\s*---\s*\n([\s\S]*?)\n\s*---\s*\n([\s\S]*)$/
  const match = content.match(pattern)
  if (match) {
    markdown = match[2]
    match[1].split('\n').forEach(line => {
      if (line.includes(':')) {
        const [k, v] = line.split(':', 2)
        const key = k.trim().toLowerCase()
        const val = v.trim().replace(/^["']|["']$/g, '')
        if (key === 'title') title = val
      }
    })
  }

  if (!currentNote.value.module_id) {
    alert('Select or create a module first, then import your file.')
    return
  }

  currentNote.value = {
    id: null,
    title,
    module_id: currentNote.value.module_id,
    content_markdown: markdown
  }
  mode.value = 'editor'
}

const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    selectedFileName.value = file.name
    const reader = new FileReader()
    reader.onload = (evt) => parseLocalFile(file.name, evt.target.result)
    reader.readAsText(file)
  }
}

const handleFileDrop = (e) => {
  const file = e.dataTransfer.files[0]
  if (file && file.name.endsWith('.md')) {
    selectedFileName.value = file.name
    const reader = new FileReader()
    reader.onload = (evt) => parseLocalFile(file.name, evt.target.result)
    reader.readAsText(file)
  }
}

const publishCurrentNote = async () => {
  const cleanTitle = currentNote.value.title.replace(/\.md$/i, '').trim()
  if (!cleanTitle || !currentNote.value.content_markdown.trim() || !currentNote.value.module_id) {
    alert('Please provide a note title, content, and target module before publishing.')
    return
  }

  loading.value = true
  try {
    const payload = { title: cleanTitle, content_markdown: currentNote.value.content_markdown }

    if (currentNote.value.id) {
      await axios.put(`/api/academy/notes/${currentNote.value.id}`, payload, { withCredentials: true })
    } else {
      const res = await axios.post(`/api/academy/modules/${currentNote.value.module_id}/notes`, payload, { withCredentials: true })
      currentNote.value.id = res.data.id
    }

    alert('Note published successfully!')
    await fetchTree()
  } catch (err) {
    console.error('Publish note error:', err)
    const errMsg = err.response?.data?.error || err.message || 'Failed to publish note'
    alert(`Publish Error: ${errMsg}`)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (!authStore.isTeacher) {
    router.push('/academy')
    return
  }
  await fetchTree()

  // Deep-link support from ModuleOverviewView's "Add Note"/"Edit Note"
  // actions: ?module=<id>&note=<id> opens an existing note, ?module=<id>&new=1
  // starts a fresh one pre-scoped to that module.
  const targetModuleId = Number(route.query.module)
  if (targetModuleId) {
    let targetModule = null
    for (const p of paths.value) {
      const m = p.modules.find(m => m.id === targetModuleId)
      if (m) { targetModule = m; break }
    }
    if (targetModule) {
      openModules.value[targetModule.id] = true
      if (route.query.note) {
        const noteId = Number(route.query.note)
        const note = targetModule.notes.find(n => n.id === noteId)
        if (note) selectNote(note, targetModule)
      } else if (route.query.new === '1') {
        createNewNote(targetModule)
      }
    }
  }
})
</script>
