<template>
  <div class="max-w-6xl mx-auto px-4 py-8 text-slate-100">
    <div class="flex items-center justify-between mb-8 pb-4 border-b border-slate-800">
      <div>
        <h1 class="text-3xl font-bold tracking-tight bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
          Academy Author Studio
        </h1>
        <p class="text-slate-400 text-sm mt-1">Create engaging cybersecurity courses with Markdown or upload pre-written .md files</p>
      </div>

      <!-- Mode Selector Buttons -->
      <div class="flex items-center gap-3 bg-slate-900 p-1.5 rounded-xl border border-slate-800">
        <button 
          @click="mode = 'write'" 
          :class="[mode === 'write' ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30' : 'text-slate-400 hover:text-slate-200']"
          class="px-4 py-2 text-sm font-medium rounded-lg border transition-all flex items-center gap-2">
          <Edit3 class="w-4 h-4" /> Live Markdown Editor
        </button>
        <button 
          @click="mode = 'upload'" 
          :class="[mode === 'upload' ? 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30' : 'text-slate-400 hover:text-slate-200']"
          class="px-4 py-2 text-sm font-medium rounded-lg border transition-all flex items-center gap-2">
          <UploadCloud class="w-4 h-4" /> Import .md File
        </button>
      </div>
    </div>

    <!-- Alert / Message -->
    <div v-if="statusMsg" :class="[isError ? 'bg-rose-500/10 border-rose-500/30 text-rose-400' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400']" class="p-4 rounded-xl border mb-6 text-sm flex items-center justify-between">
      <span>{{ statusMsg }}</span>
      <button @click="statusMsg = ''" class="text-xs underline opacity-80 hover:opacity-100">Dismiss</button>
    </div>

    <!-- Mode 1: Live Markdown Editor -->
    <div v-if="mode === 'write'" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Editor Column -->
      <div class="space-y-5 bg-slate-900/60 p-6 rounded-2xl border border-slate-800/80 backdrop-blur-md">
        <div>
          <label class="block text-xs font-semibold text-slate-400 uppercase mb-2">Chapter Title</label>
          <input 
            v-model="form.title" 
            type="text" 
            placeholder="e.g. Reverse Engineering 101: x86 Stack Analysis" 
            class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 transition-all font-medium text-lg" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-semibold text-slate-400 uppercase mb-2">Chapter Order Index</label>
            <input 
              v-model.number="form.order_index" 
              type="number" 
              min="1" 
              class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 focus:outline-none focus:border-cyan-500" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-400 uppercase mb-2">Cover Image URL</label>
            <input 
              v-model="form.cover_image" 
              type="text" 
              placeholder="/uploads/courses/cover.png" 
              class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500" />
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-400 uppercase mb-2">Short Description</label>
          <textarea 
            v-model="form.description" 
            rows="2" 
            placeholder="Brief overview of learning objectives..." 
            class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500"></textarea>
        </div>

        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="text-xs font-semibold text-slate-400 uppercase">Markdown Content</label>
            <div class="text-xs text-slate-500 flex items-center gap-3">
              <span>{{ wordCount }} words</span>
              <span>~{{ estimatedReadTime }} min read</span>
            </div>
          </div>
          <textarea 
            v-model="form.content_markdown" 
            rows="14" 
            placeholder="# Chapter 1: Fundamentals&#10;&#10;Write your course content using standard Markdown syntax..." 
            class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 font-mono text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500 leading-relaxed"></textarea>
        </div>

        <button 
          @click="publishContent" 
          :disabled="loading"
          class="w-full py-3.5 bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold rounded-xl transition-all duration-200 shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2">
          <Send class="w-5 h-5" /> {{ loading ? 'Publishing...' : 'Publish Course Chapter' }}
        </button>
      </div>

      <!-- Live Reader Preview Column -->
      <div class="bg-slate-950 p-8 rounded-2xl border border-slate-800/80 shadow-2xl space-y-6 overflow-hidden">
        <div class="flex items-center justify-between border-b border-slate-800 pb-4">
          <span class="text-xs font-semibold tracking-wider text-cyan-400 uppercase">Live Reader Preview</span>
          <span class="text-xs text-slate-500">Medium Reading Mode</span>
        </div>

        <div class="prose prose-invert max-w-none space-y-4">
          <h1 class="text-3xl font-bold text-slate-100 tracking-tight">{{ form.title || 'Untitled Chapter Title' }}</h1>
          <p class="text-slate-400 text-sm italic">{{ form.description || 'Course chapter summary will appear here.' }}</p>
          <hr class="border-slate-800 my-4" />
          <div class="text-slate-300 leading-relaxed whitespace-pre-line text-base font-sans">
            {{ form.content_markdown || 'Start typing in the editor on the left to see instant preview...' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Mode 2: Import .md File -->
    <div v-else class="max-w-2xl mx-auto bg-slate-900/60 p-8 rounded-2xl border border-slate-800/80 text-center space-y-6">
      <div class="w-16 h-16 mx-auto bg-indigo-500/10 rounded-2xl flex items-center justify-center text-indigo-400 border border-indigo-500/20">
        <FileText class="w-8 h-8" />
      </div>

      <div>
        <h2 class="text-xl font-bold text-slate-100">Upload Markdown File (.md)</h2>
        <p class="text-slate-400 text-sm mt-1">Automatic Front-Matter Metadata Extraction (title, description, order_index)</p>
      </div>

      <!-- Drag & Drop Zone -->
      <div 
        @dragover.prevent 
        @drop.prevent="handleFileDrop" 
        class="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-2xl p-8 transition-all bg-slate-950/50 cursor-pointer text-slate-400 hover:text-slate-200"
        @click="$refs.fileInput.click()">
        <input ref="fileInput" type="file" accept=".md" class="hidden" @change="handleFileSelect" />
        <UploadCloud class="w-10 h-10 mx-auto mb-3 text-indigo-400 opacity-80" />
        <p class="font-medium text-sm">Click to select or drag & drop your <code class="text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">.md</code> file here</p>
        <p v-if="selectedFileName" class="text-xs text-emerald-400 mt-2 font-semibold">Selected: {{ selectedFileName }}</p>
      </div>

      <button 
        @click="uploadFile" 
        :disabled="!selectedFile || loading"
        class="w-full py-3.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold rounded-xl transition-all shadow-lg shadow-indigo-600/20 flex items-center justify-center gap-2">
        <UploadCloud class="w-5 h-5" /> {{ loading ? 'Uploading & Parsing...' : 'Parse Front-Matter & Publish' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Edit3, UploadCloud, FileText, Send } from 'lucide-vue-next'

const router = useRouter()
const mode = ref('write')
const loading = ref(false)
const statusMsg = ref('')
const isError = ref(false)

const form = ref({
  title: '',
  description: '',
  cover_image: '',
  order_index: 1,
  content_markdown: ''
})

const selectedFile = ref(null)
const selectedFileName = ref('')

const wordCount = computed(() => {
  if (!form.value.content_markdown) return 0
  return form.value.content_markdown.trim().split(/\s+/).length
})

const estimatedReadTime = computed(() => {
  return Math.max(1, Math.ceil(wordCount.value / 200))
})

const publishContent = async () => {
  if (!form.value.title || !form.value.content_markdown) {
    statusMsg.value = 'Please provide a title and markdown content.'
    isError.value = true
    return
  }

  loading.value = true
  statusMsg.value = ''

  try {
    const res = await axios.post('/api/academy/write', form.value, { withCredentials: true })
    statusMsg.value = 'Course chapter published successfully!'
    isError.value = false
    setTimeout(() => {
      if (res.data?.course?.slug) {
        router.push(`/academy/course/${res.data.course.slug}`)
      }
    }, 1200)
  } catch (err) {
    statusMsg.value = err.response?.data?.error || 'Failed to publish course chapter.'
    isError.value = true
  } finally {
    loading.value = false
  }
}

const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
    selectedFileName.value = file.name
  }
}

const handleFileDrop = (e) => {
  const file = e.dataTransfer.files[0]
  if (file && file.name.endsWith('.md')) {
    selectedFile.value = file
    selectedFileName.value = file.name
  }
}

const uploadFile = async () => {
  if (!selectedFile.value) return

  loading.value = true
  statusMsg.value = ''

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const res = await axios.post('/api/academy/write', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      withCredentials: true
    })
    statusMsg.value = 'Markdown file uploaded & front-matter parsed successfully!'
    isError.value = false
    setTimeout(() => {
      if (res.data?.course?.slug) {
        router.push(`/academy/course/${res.data.course.slug}`)
      }
    }, 1200)
  } catch (err) {
    statusMsg.value = err.response?.data?.error || 'Failed to upload and parse markdown file.'
    isError.value = true
  } finally {
    loading.value = false
  }
}
</script>
