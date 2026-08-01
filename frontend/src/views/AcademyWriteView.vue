<template>
  <div class="h-[calc(100vh-80px)] text-slate-100 font-mono bg-[#0b0e14] flex flex-col overflow-hidden selection:bg-[#00f0ff] selection:text-black">
    
    <!-- Top Control Bar -->
    <div class="h-12 bg-[#161b22] border-b border-[#21262d] px-4 flex items-center justify-between flex-shrink-0">
      <div class="flex items-center space-x-3 text-xs">
        <router-link to="/academy" class="text-slate-400 hover:text-white flex items-center space-x-1">
          <span>&larr; Academy</span>
        </router-link>
        <span class="text-slate-600">/</span>
        <span class="text-slate-600">/</span>
        <span class="font-bold text-[#00f0ff] flex items-center space-x-1.5">
          <svg class="w-4 h-4 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
          </svg>
          <span>Modules</span>
        </span>
        <span class="text-slate-600">/</span>
        <span class="text-slate-300 font-bold">{{ currentNote.title || 'Untitled Note.md' }}</span>
      </div>

      <div class="flex items-center space-x-2">
        <!-- New Module Folder Button -->
        <button @click="promptNewFolder" class="px-2.5 py-1 text-[11px] font-bold bg-[#21262d] hover:bg-[#30363d] text-slate-300 rounded border border-[#30363d] transition-all flex items-center space-x-1">
          <svg class="w-3.5 h-3.5 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          <span>+ New Module</span>
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
          :disabled="loading || !currentNote.title.trim() || !currentNote.content_markdown.trim()" 
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
      
      <!-- Column 1: Left Modules Explorer Sidebar -->
      <div class="w-72 bg-[#161b22] border-r border-[#21262d] flex flex-col flex-shrink-0 select-none">
        
        <!-- Sidebar Header -->
        <div class="p-3 border-b border-[#21262d] flex items-center justify-between text-xs text-slate-400 font-bold uppercase tracking-wider">
          <span>Modules Tree</span>
          <span class="text-[10px] text-[#9fef00]">Module Workspace</span>
        </div>

        <!-- Folder Tree & Files -->
        <div class="flex-1 overflow-y-auto p-2 space-y-3">
          <div v-if="folders.length === 0" class="p-4 text-center text-slate-500 text-xs italic">
            No module folders yet. Click "+ New Module" or create a note below.
          </div>

          <div v-for="folder in folders" :key="folder.name" class="space-y-1">
            
            <!-- Folder Header (Drag Target & Management Menu) -->
            <div 
              @dragover.prevent="onFolderDragOver($event, folder.name)"
              @drop.prevent="onFolderDrop($event, folder.name)"
              class="px-2 py-1.5 rounded hover:bg-[#21262d] text-xs font-bold text-slate-300 flex items-center justify-between cursor-pointer group transition-colors"
            >
              <div @click="toggleFolder(folder.name)" class="flex items-center space-x-2 truncate flex-1">
                <svg class="w-4 h-4 text-amber-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                </svg>
                <span class="truncate uppercase text-[11px] tracking-wider text-[#00f0ff]">{{ folder.name }}</span>
                <span class="text-[10px] text-slate-500 font-mono">({{ folder.notes.length }})</span>
              </div>

              <!-- Module Action Menu -->
              <div class="opacity-0 group-hover:opacity-100 flex items-center space-x-1 transition-opacity">
                <button @click.stop="renameFolder(folder.name)" title="Rename Module" class="text-[10px] hover:text-[#00f0ff] p-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 210.382H3v-3.572L16.732 3.732z"/>
                  </svg>
                </button>
                <button @click.stop="deleteFolder(folder.name)" title="Delete Module" class="text-[10px] hover:text-rose-400 p-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Folder Notes List with Re-Ordering Arrows -->
            <div v-if="openFolders[folder.name]" class="pl-4 space-y-0.5">
              <div 
                v-for="(note, idx) in folder.notes" 
                :key="note.id"
                draggable="true"
                @dragstart="onNoteDragStart($event, note, folder.name)"
                @click="selectNote(note)"
                :class="[
                  'px-2 py-1.5 rounded text-xs cursor-pointer flex items-center justify-between truncate transition-all group/note',
                  currentNote.id === note.id ? 'bg-[#00f0ff]/15 text-[#00f0ff] font-bold border-l-2 border-[#00f0ff]' : 'text-slate-400 hover:text-white hover:bg-[#21262d]'
                ]"
              >
                <div class="flex items-center space-x-2 truncate">
                  <span class="text-slate-500 text-[10px]">{{ idx + 1 }}.</span>
                  <span class="truncate">{{ note.title }}</span>
                </div>

                <!-- Reorder UP/DOWN & Delete controls -->
                <div class="opacity-0 group-hover/note:opacity-100 flex items-center space-x-1 transition-opacity">
                  <button @click.stop="moveNoteUp(folder, idx)" title="Move Up" class="hover:text-[#00f0ff] text-[10px] px-0.5 font-bold">▲</button>
                  <button @click.stop="moveNoteDown(folder, idx)" title="Move Down" class="hover:text-[#00f0ff] text-[10px] px-0.5 font-bold">▼</button>
                  <button @click.stop="deleteNote(folder.name, note.id)" title="Delete Note" class="text-[10px] text-rose-400 hover:scale-110 px-0.5">✕</button>
                </div>
              </div>

              <div v-if="!folder.notes.length" class="pl-3 py-1 text-[10px] text-slate-600 italic">
                Drop .md file here
              </div>
            </div>

          </div>
        </div>

        <!-- Quick Add Note in Selected Module -->
        <div class="p-3 border-t border-[#21262d] bg-[#0d1420] space-y-2">
          <button @click="createNewNote" class="w-full py-1.5 text-xs font-bold bg-[#21262d] hover:bg-[#30363d] text-slate-200 rounded border border-[#30363d] transition-all">
            + New Note in Module
          </button>
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
                <select v-model="currentNote.folder" class="input-field text-xs w-full bg-[#0b0e14] py-1.5 text-slate-300 uppercase">
                  <option v-for="f in folders" :key="f.name" :value="f.name">{{ f.name }}</option>
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
              <span class="text-[#00f0ff] uppercase font-bold">Modules</span>
              <span>&rsaquo;</span>
              <span class="text-slate-300 uppercase font-bold">{{ currentNote.folder || 'General' }}</span>
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
            Upload your markdown file directly. Front-matter metadata (title, module) will be auto-extracted.
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
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const mode = ref('editor')
const loading = ref(false)
const selectedFileName = ref('')

const openFolders = ref({})

const folders = ref([])

const currentNote = ref({
  id: Date.now(),
  title: 'New Security Note',
  folder: 'general',
  content_markdown: '# New Security Note\n\nWrite your module note content here...'
})

// Fetch real courses & chapters from database on mount
const fetchRealCoursesAndChapters = async () => {
  try {
    const res = await axios.get('/api/academy/courses', { withCredentials: true })
    const courses = res.data.courses || []
    
    const realFolders = []
    for (const c of courses) {
      const folderKey = c.title.toLowerCase().replace(/[^a-z0-9]+/g, '-')
      openFolders.value[folderKey] = true

      try {
        const detailRes = await axios.get(`/api/academy/course/${c.slug}`, { withCredentials: true })
        const chapters = detailRes.data.chapters || []
        realFolders.push({
          name: folderKey,
          course_id: c.id,
          slug: c.slug,
          notes: chapters.map(ch => ({
            id: ch.id,
            course_id: c.id,
            title: ch.title,
            folder: folderKey,
            content_markdown: ch.content_markdown
          }))
        })
      } catch (e) {
        realFolders.push({
          name: folderKey,
          course_id: c.id,
          slug: c.slug,
          notes: []
        })
      }
    }

    folders.value = realFolders

    if (realFolders.length && realFolders[0].notes.length) {
      currentNote.value = { ...realFolders[0].notes[0] }
    } else if (realFolders.length) {
      currentNote.value.folder = realFolders[0].name
      currentNote.value.course_id = realFolders[0].course_id
    }
  } catch (err) {
    console.error('Failed to fetch real courses', err)
  }
}

// Reorder Notes UP/DOWN inside a folder and persist to server
const moveNoteUp = async (folderObj, idx) => {
  if (idx <= 0) return
  const temp = folderObj.notes[idx]
  folderObj.notes[idx] = folderObj.notes[idx - 1]
  folderObj.notes[idx - 1] = temp

  await persistNoteOrder(folderObj)
}

const moveNoteDown = async (folderObj, idx) => {
  if (idx >= folderObj.notes.length - 1) return
  const temp = folderObj.notes[idx]
  folderObj.notes[idx] = folderObj.notes[idx + 1]
  folderObj.notes[idx + 1] = temp

  await persistNoteOrder(folderObj)
}

const persistNoteOrder = async (folderObj) => {
  if (folderObj && folderObj.course_id) {
    const chapterIds = folderObj.notes
      .map(n => n.id)
      .filter(id => typeof id === 'number' && id < 1000000000)
    
    if (chapterIds.length) {
      try {
        await axios.put(`/api/academy/courses/${folderObj.course_id}/reorder-chapters`, { chapter_ids: chapterIds }, { withCredentials: true })
      } catch (e) {
        console.error('Failed to persist note order on server', e)
      }
    }
  }
}

// MkDocs Custom Markdown-to-HTML parser with callout alerts and clickable links
const renderedPreviewHtml = computed(() => {
  let md = currentNote.value.content_markdown || ''
  
  // 1. Callout alert boxes
  md = md.replace(/^>\s*\[!NOTE\]\s*\n?/gm, '<div class="my-4 p-4 rounded-xl bg-cyan-950/60 border-l-4 border-[#00f0ff] text-cyan-200 text-xs font-mono"><strong class="text-[#00f0ff] uppercase block mb-1">ℹ️ Note</strong>')
  md = md.replace(/^>\s*\[!TIP\]\s*\n?/gm, '<div class="my-4 p-4 rounded-xl bg-emerald-950/60 border-l-4 border-[#9fef00] text-emerald-200 text-xs font-mono"><strong class="text-[#9fef00] uppercase block mb-1">💡 Tip</strong>')
  md = md.replace(/^>\s*\[!WARNING\]\s*\n?/gm, '<div class="my-4 p-4 rounded-xl bg-amber-950/60 border-l-4 border-amber-400 text-amber-200 text-xs font-mono"><strong class="text-amber-400 uppercase block mb-1">⚠️ Warning</strong>')
  md = md.replace(/^>\s*\[!IMPORTANT\]\s*\n?/gm, '<div class="my-4 p-4 rounded-xl bg-rose-950/60 border-l-4 border-rose-500 text-rose-200 text-xs font-mono"><strong class="text-rose-400 uppercase block mb-1">🚨 Important</strong>')
  
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

// Module & Note Management
const toggleFolder = (folderName) => {
  openFolders.value[folderName] = !openFolders.value[folderName]
}

const selectNote = (note) => {
  currentNote.value = { ...note }
  mode.value = 'editor'
}

const promptNewFolder = async () => {
  const name = prompt('Enter new Module Folder name:')
  if (name && name.trim()) {
    const key = name.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-')
    try {
      const res = await axios.post('/api/academy/courses', {
        title: name.trim(),
        description: `Academy Module ${name.trim()}`,
        status: 'published'
      }, { withCredentials: true })
      await fetchRealCoursesAndChapters()
    } catch (e) {
      if (!folders.value.some(f => f.name === key)) {
        folders.value.push({ name: key, notes: [] })
        openFolders.value[key] = true
      }
    }
  }
}

const renameFolder = async (oldName) => {
  const newName = prompt('Enter new Module Folder name:', oldName)
  if (newName && newName.trim() && newName.trim().toLowerCase() !== oldName) {
    const folderObj = folders.value.find(f => f.name === oldName)
    if (folderObj && folderObj.course_id) {
      try {
        await axios.put(`/api/academy/courses/${folderObj.course_id}`, {
          title: newName.trim()
        }, { withCredentials: true })
        await fetchRealCoursesAndChapters()
      } catch (e) {
        folderObj.name = newName.trim().toLowerCase()
      }
    }
  }
}

const deleteFolder = async (folderName) => {
  if (!confirm(`Delete module "${folderName.toUpperCase()}" and all notes inside it?`)) return
  const folderObj = folders.value.find(f => f.name === folderName)
  if (folderObj && folderObj.course_id) {
    try {
      await axios.delete(`/api/academy/courses/${folderObj.course_id}`, { withCredentials: true })
      await fetchRealCoursesAndChapters()
      return
    } catch (e) {
      console.error(e)
    }
  }
  folders.value = folders.value.filter(f => f.name !== folderName)
}

const deleteNote = async (folderName, noteId) => {
  if (!confirm('Delete this note chapter?')) return
  
  if (typeof noteId === 'number' && noteId < 1000000000) {
    try {
      await axios.delete(`/api/academy/chapters/${noteId}`, { withCredentials: true })
    } catch (e) {
      console.error('Failed to delete chapter on server', e)
    }
  }

  const folderObj = folders.value.find(f => f.name === folderName)
  if (folderObj) {
    folderObj.notes = folderObj.notes.filter(n => n.id !== noteId)
    if (currentNote.value.id === noteId && folderObj.notes.length) {
      currentNote.value = { ...folderObj.notes[0] }
    }
    await persistNoteOrder(folderObj)
  }
}

const createNewNote = () => {
  const targetFolder = currentNote.value.folder || (folders.value[0] ? folders.value[0].name : 'general')
  const targetCourseId = currentNote.value.course_id || (folders.value[0] ? folders.value[0].course_id : null)
  
  const newNoteItem = {
    id: Date.now(),
    course_id: targetCourseId,
    title: 'Untitled Security Note',
    folder: targetFolder,
    content_markdown: '# New Security Note\n\nWrite your module note content here...'
  }

  let f = folders.value.find(fold => fold.name === targetFolder)
  if (!f) {
    f = { name: targetFolder, notes: [] }
    folders.value.push(f)
    openFolders.value[targetFolder] = true
  }
  f.notes.push(newNoteItem)
  currentNote.value = newNoteItem
  mode.value = 'editor'
}

const onNoteDragStart = (e, note, fromFolder) => {
  e.dataTransfer.setData('application/json', JSON.stringify({ noteId: note.id, fromFolder }))
}

const onFolderDragOver = (e) => {
  e.dataTransfer.dropEffect = 'move'
}

const onFolderDrop = async (e, targetFolder) => {
  const rawData = e.dataTransfer.getData('application/json')
  if (rawData) {
    const { noteId, fromFolder } = JSON.parse(rawData)
    if (fromFolder !== targetFolder) {
      const srcDir = folders.value.find(f => f.name === fromFolder)
      const dstDir = folders.value.find(f => f.name === targetFolder)
      if (srcDir && dstDir) {
        const idx = srcDir.notes.findIndex(n => n.id === noteId)
        if (idx !== -1) {
          const [movedNote] = srcDir.notes.splice(idx, 1)
          movedNote.folder = targetFolder
          movedNote.course_id = dstDir.course_id
          dstDir.notes.push(movedNote)
          if (currentNote.value.id === noteId) {
            currentNote.value.folder = targetFolder
            currentNote.value.course_id = dstDir.course_id
          }
          await persistNoteOrder(srcDir)
          await persistNoteOrder(dstDir)
        }
      }
    }
  }
}

const parseLocalFile = (filename, content) => {
  let title = filename.replace(/\.md$/i, '')
  let folder = folders.value[0] ? folders.value[0].name : 'general'
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
        if (key === 'folder' || key === 'module') folder = val.toLowerCase()
      }
    })
  }

  const loadedNote = {
    id: Date.now(),
    title,
    folder,
    content_markdown: markdown
  }

  let dstDir = folders.value.find(f => f.name === folder)
  if (!dstDir) {
    dstDir = { name: folder, notes: [] }
    folders.value.push(dstDir)
    openFolders.value[folder] = true
  }
  dstDir.notes.push(loadedNote)
  currentNote.value = loadedNote
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
  if (!cleanTitle || !currentNote.value.content_markdown.trim()) {
    alert('Please provide a note title and content before publishing.')
    return
  }

  loading.value = true
  try {
    const payload = {
      title: cleanTitle,
      description: `Academy Module: ${currentNote.value.folder || 'General'}`,
      content_markdown: currentNote.value.content_markdown
    }
    
    // Only pass course_id if it's a real numeric database ID
    if (currentNote.value.course_id && typeof currentNote.value.course_id === 'number' && currentNote.value.course_id < 1000000000) {
      payload.course_id = currentNote.value.course_id
    }

    const res = await axios.post('/api/academy/write', payload, { withCredentials: true })

    alert('Note published successfully to Academy Modules!')
    if (res.data?.course?.slug) {
      router.push(`/academy/course/${res.data.course.slug}`)
    } else {
      await fetchRealCoursesAndChapters()
    }
  } catch (err) {
    console.error('Publish note error:', err)
    const errMsg = err.response?.data?.error || err.message || 'Failed to publish note'
    alert(`Publish Error: ${errMsg}`)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (!authStore.isTeacher) {
    router.push('/academy')
    return
  }
  fetchRealCoursesAndChapters()
})
</script>
