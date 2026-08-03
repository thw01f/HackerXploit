<template>
  <div class="min-h-screen bg-[#0b0e14] text-slate-100 font-mono pb-20">
    <div class="w-full px-4 sm:px-6 lg:px-8 pt-4 max-w-4xl mx-auto space-y-6">

      <div v-if="loading" class="animate-pulse h-96 bg-[#151f30] rounded-3xl border border-[#1f293d]"></div>

      <template v-else>
        <div class="flex items-center justify-between border-b border-[#1f293d] pb-4">
          <div class="flex items-center gap-2 text-xs">
            <router-link :to="backLink" class="text-[#00f0ff] hover:underline font-bold">&larr; {{ moduleTitle || 'Module' }}</router-link>
            <span class="text-slate-600">/</span>
            <span class="text-slate-300 font-bold">{{ isEditing ? 'Edit Note' : 'New Note' }}</span>
          </div>
          <button @click="save" :disabled="saving || !form.title.trim()" class="btn-htb text-xs py-2 px-5 font-bold uppercase tracking-wider">
            {{ saving ? 'Saving...' : 'Save Note' }}
          </button>
        </div>

        <div v-if="errorMessage" class="p-3 rounded-lg bg-red-950/80 border border-red-500/50 text-red-300 text-xs">
          {{ errorMessage }}
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-xs text-slate-400 uppercase mb-1.5">Note Title</label>
            <input v-model="form.title" type="text" placeholder="e.g. Setting Up Your Lab" class="input-field w-full py-2.5" />
          </div>

          <div>
            <label class="block text-xs text-slate-400 uppercase mb-1.5">Content (Markdown)</label>
            <textarea
              v-model="form.content_markdown"
              rows="24"
              placeholder="# Heading&#10;&#10;Write your note content here using Markdown..."
              class="input-field w-full py-3 font-mono text-sm leading-relaxed"
            ></textarea>
          </div>

          <!-- Attachments - only available once the note actually exists -->
          <div v-if="isEditing" class="space-y-2 pt-2 border-t border-[#1f293d]">
            <label class="block text-xs text-slate-400 uppercase mb-1.5">Attachments</label>
            <div v-if="attachments.length" class="flex flex-wrap gap-2">
              <span v-for="att in attachments" :key="att.name" class="text-[11px] bg-[#151f30] border border-[#1f293d] rounded-lg px-2.5 py-1.5 text-slate-300 flex items-center gap-1.5">
                <svg class="w-3 h-3 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
                {{ att.name }}
              </span>
            </div>
            <button type="button" @click="triggerAttachmentUpload" :disabled="uploadingAttachment" class="btn-ghost text-[11px] py-1.5 px-3 text-[#00f0ff] border border-[#00f0ff]/40 hover:bg-[#00f0ff]/10 font-bold">
              {{ uploadingAttachment ? 'Uploading...' : '+ Upload Attachment' }}
            </button>
            <input ref="attachmentFileInput" type="file" class="hidden" @change="handleAttachmentUpload" />
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const saving = ref(false)
const errorMessage = ref('')
const isEditing = ref(false)
const moduleId = ref(null)
const courseId = ref(null)
const courseSlug = ref('')
const moduleTitle = ref('')

const form = ref({ title: '', content_markdown: '' })

const attachments = ref([])
const uploadingAttachment = ref(false)
const attachmentFileInput = ref(null)

const backLink = computed(() => moduleId.value ? `/academy/course/${courseSlug.value}/module/${moduleId.value}` : '/academy')

const load = async () => {
  loading.value = true
  try {
    if (route.params.noteId) {
      isEditing.value = true
      const res = await axios.get(`/api/academy/notes/${route.params.noteId}`, { withCredentials: true })
      form.value = { title: res.data.title, content_markdown: res.data.content_markdown }
      attachments.value = res.data.attachments || []
      moduleId.value = res.data.module.id
      moduleTitle.value = res.data.module.title
      courseSlug.value = res.data.module.course_slug
      courseId.value = res.data.module.course_id
    } else if (route.params.moduleId) {
      isEditing.value = false
      moduleId.value = Number(route.params.moduleId)
      const res = await axios.get(`/api/academy/modules/${moduleId.value}/overview`, { withCredentials: true })
      moduleTitle.value = res.data.title
      courseSlug.value = res.data.course.slug
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Failed to load note.'
  } finally {
    loading.value = false
  }
}

const save = async () => {
  saving.value = true
  errorMessage.value = ''
  try {
    if (isEditing.value) {
      await axios.put(`/api/academy/notes/${route.params.noteId}`, form.value, { withCredentials: true })
    } else {
      await axios.post(`/api/academy/modules/${moduleId.value}/notes`, form.value, { withCredentials: true })
    }
    router.push(backLink.value)
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Failed to save note.'
  } finally {
    saving.value = false
  }
}

const triggerAttachmentUpload = () => {
  if (attachmentFileInput.value) attachmentFileInput.value.click()
}

const handleAttachmentUpload = async (e) => {
  const file = e.target.files?.[0]
  if (!file || !courseId.value) return

  uploadingAttachment.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)

    const res = await axios.post(
      `/api/academy/courses/${courseId.value}/notes/${route.params.noteId}/attachments`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' }, withCredentials: true }
    )
    attachments.value = res.data.attachments || attachments.value
  } catch (err) {
    alert('Failed to upload attachment: ' + (err.response?.data?.error || err.message))
  } finally {
    uploadingAttachment.value = false
  }
}

onMounted(load)
</script>
