<template>
  <div class="space-y-6 font-mono">
    <div class="flex items-center justify-between border-b border-[#1f293d] pb-4">
      <div>
        <h1 class="text-2xl font-extrabold text-white">Certification Studio</h1>
        <p class="text-xs text-slate-400 mt-1">Group certifications into categories, arrange them, then draw the progression path between them.</p>
      </div>
      <router-link to="/academy" class="btn-ghost text-xs py-2 px-4">&larr; Back to Academy</router-link>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-6" style="height: calc(100vh - 220px);">

      <!-- Left: Category picker -->
      <div class="glass-panel p-4 space-y-4 overflow-y-auto">
        <div class="space-y-2">
          <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Categories</h3>
          <button
            v-for="cat in categories"
            :key="cat.slug"
            @click="selectCategory(cat.slug)"
            :class="[
              'w-full text-left px-3 py-2.5 rounded-xl border text-xs transition-all',
              activeSlug === cat.slug ? 'border-[#9fef00] bg-[#9fef00]/10 text-white font-bold' : 'border-slate-800 bg-slate-900/60 text-slate-300 hover:border-slate-700'
            ]"
          >
            {{ cat.title }}
            <span class="block text-[10px] text-slate-500 mt-0.5">{{ cat.certifications_count }} certifications</span>
          </button>
          <p v-if="categories.length === 0" class="text-xs text-slate-500 text-center py-4">No categories yet.</p>
        </div>

        <div class="pt-4 border-t border-slate-800 space-y-2">
          <input v-model="newCategoryTitle" type="text" placeholder="New category title" class="input-field w-full text-xs py-2" />
          <button @click="createCategory" :disabled="!newCategoryTitle.trim() || creating" class="btn-htb w-full text-xs py-2">
            {{ creating ? 'Creating...' : '+ New Category' }}
          </button>
        </div>

        <div v-if="activeSlug" class="pt-4 border-t border-slate-800">
          <button @click="deleteActiveCategory" class="w-full text-xs py-2 rounded-lg text-rose-400 border border-rose-500/40 hover:bg-rose-500/10 transition-all">
            Delete This Category
          </button>
        </div>
      </div>

      <!-- Center: Canvas -->
      <div class="glass-panel p-0 overflow-hidden relative flex flex-col">
        <div v-if="!activeSlug" class="flex-1 flex items-center justify-center text-slate-500 text-xs">
          Select or create a category to start editing.
        </div>

        <template v-else>
          <div class="flex items-center gap-3 p-3 border-b border-[#1f293d] bg-[#0b0e14]">
            <button @click="addCertification" class="btn-ghost text-xs py-1.5 px-3">+ Add Certification</button>
            <button @click="saveLayout" :disabled="saving" class="btn-htb text-xs py-1.5 px-4">
              {{ saving ? 'Saving...' : 'Save Layout' }}
            </button>
            <span v-if="saveMessage" class="text-[11px] text-emerald-400">{{ saveMessage }}</span>
            <span class="text-[11px] text-slate-500 ml-auto">Drag a card's handle to another to connect. Select a connection + press Delete to remove it.</span>
          </div>

          <div class="flex-1 relative">
            <VueFlow
              v-model:nodes="nodes"
              v-model:edges="edges"
              :default-viewport="{ zoom: 0.9 }"
              :delete-key-code="['Backspace', 'Delete']"
              :pan-on-drag="canvasInteractive"
              :zoom-on-scroll="canvasInteractive"
              :zoom-on-pinch="canvasInteractive"
              :zoom-on-double-click="canvasInteractive"
              @connect="onConnect"
              class="hx-cert-canvas"
            >
              <template #node-certNode="nodeProps">
                <CertificationNodeCard
                  :data="nodeProps.data"
                  :selected="nodeProps.selected"
                  editable
                  @select="openCertPanel(nodeProps.data)"
                  @delete-node="deleteCertification(nodeProps.data)"
                />
              </template>

              <Background :pattern-color="isDark ? '#1f293d' : '#cbd5e1'" :gap="20" />
              <Controls @interaction-change="canvasInteractive = $event" />
              <MiniMap />
            </VueFlow>
          </div>
        </template>
      </div>
    </div>

    <!-- Certification Detail Side Panel -->
    <div
      v-if="activeCert"
      class="fixed inset-y-0 right-0 z-50 w-full sm:w-[440px] bg-[#161b22] border-l border-[#21262d] shadow-2xl flex flex-col"
    >
      <div class="p-5 border-b border-[#21262d] flex items-center justify-between bg-[#0b0e14]/50">
        <span class="text-[10px] text-[#00f0ff] font-bold uppercase tracking-wider">// Edit Certification</span>
        <button @click="closeCertPanel" class="p-1.5 text-slate-400 hover:text-white hover:bg-[#21262d] rounded-lg transition-colors">&times;</button>
      </div>

      <div class="flex-1 overflow-y-auto p-5 space-y-4 text-xs">
        <div>
          <label class="block text-slate-400 uppercase mb-1 text-[11px]">Title</label>
          <input v-model="certForm.title" type="text" class="input-field w-full py-2" />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-slate-400 uppercase mb-1 text-[11px]">Provider</label>
            <input v-model="certForm.provider" type="text" placeholder="e.g. CompTIA" class="input-field w-full py-2" />
          </div>
          <div>
            <label class="block text-slate-400 uppercase mb-1 text-[11px]">Difficulty</label>
            <select v-model="certForm.difficulty" class="input-field w-full py-2 bg-[#0b0e14]">
              <option value="Entry-level">Entry-level</option>
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-slate-400 uppercase mb-1 text-[11px]">Exam / Info Link</label>
            <input v-model="certForm.exam_link" type="url" placeholder="https://..." class="input-field w-full py-2" />
          </div>
          <div>
            <label class="block text-slate-400 uppercase mb-1 text-[11px]">Status</label>
            <select v-model="certForm.status" class="input-field w-full py-2 bg-[#0b0e14]">
              <option value="published">Published</option>
              <option value="draft">Draft</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-slate-400 uppercase mb-1 text-[11px]">Cover Image URL</label>
          <input v-model="certForm.cover_image" type="text" placeholder="/uploads/courses/cover.png or https://..." class="input-field w-full py-2" />
        </div>

        <div>
          <label class="block text-slate-400 uppercase mb-1 text-[11px]">Description</label>
          <textarea v-model="certForm.description" rows="5" class="input-field w-full py-2"></textarea>
        </div>

        <button @click="saveCertDetails" :disabled="savingCert" class="btn-htb w-full py-2 text-xs">
          {{ savingCert ? 'Saving...' : 'Save Certification' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import CertificationNodeCard from '../components/CertificationNodeCard.vue'
import { useTheme } from '../stores/theme'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

const { isDark } = useTheme()
// See RoadmapStudioView.vue for why this exists: Vue Flow's built-in
// Controls lock only toggles node dragging/connecting/selection, not canvas
// pan/zoom - mirror it onto the canvas's own pan/zoom props too.
const canvasInteractive = ref(true)
const categories = ref([])
const activeSlug = ref('')
const nodes = ref([])
const edges = ref([])
const newCategoryTitle = ref('')
const creating = ref(false)
const saving = ref(false)
const saveMessage = ref('')

const activeCert = ref(null)
const certForm = ref({ title: '', provider: '', description: '', exam_link: '', cover_image: '', difficulty: 'Intermediate', status: 'published' })
const savingCert = ref(false)

let certCounter = 0

const toFlowNode = (c, idx) => ({
  id: String(c.id),
  type: 'certNode',
  position: { x: c.position_x ?? (idx % 4) * 240, y: c.position_y ?? Math.floor(idx / 4) * 160 },
  data: { ...c }
})

const fetchCategories = async () => {
  const res = await axios.get('/api/certification-categories')
  categories.value = res.data
}

const selectCategory = async (slug) => {
  activeSlug.value = slug
  saveMessage.value = ''
  activeCert.value = null
  const res = await axios.get(`/api/certification-categories/${slug}/full`)
  const { certifications: apiCerts, edges: apiEdges } = res.data

  nodes.value = apiCerts.map(toFlowNode)
  edges.value = apiEdges.map(e => ({
    id: `e${e.id}`,
    source: String(e.source_cert_id),
    target: String(e.target_cert_id),
    label: e.label || ''
  }))
}

const createCategory = async () => {
  creating.value = true
  try {
    const slug = newCategoryTitle.value.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
    const res = await axios.post('/api/certification-categories', { slug, title: newCategoryTitle.value.trim() })
    newCategoryTitle.value = ''
    await fetchCategories()
    await selectCategory(res.data.slug)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to create category')
  } finally {
    creating.value = false
  }
}

const deleteActiveCategory = async () => {
  if (!confirm(`Delete the "${activeSlug.value}" category? Certifications in it are kept but become uncategorized.`)) return
  try {
    await axios.delete(`/api/certification-categories/${activeSlug.value}`)
    activeSlug.value = ''
    nodes.value = []
    edges.value = []
    activeCert.value = null
    await fetchCategories()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete category')
  }
}

const currentCategoryId = () => categories.value.find(c => c.slug === activeSlug.value)?.id

const addCertification = async () => {
  certCounter += 1
  const res = await axios.post('/api/certifications', {
    title: `New Certification ${certCounter}`,
    category_id: currentCategoryId(),
    difficulty: 'Intermediate',
    position_x: 40,
    position_y: 40
  })
  nodes.value.push(toFlowNode(res.data, nodes.value.length))
  await fetchCategories()
}

const deleteCertification = async (certData) => {
  if (!confirm(`Delete certification "${certData.title}"?`)) return
  try {
    await axios.delete(`/api/certifications/${certData.id}`)
    nodes.value = nodes.value.filter(n => n.id !== String(certData.id))
    edges.value = edges.value.filter(e => e.source !== String(certData.id) && e.target !== String(certData.id))
    if (activeCert.value?.id === certData.id) activeCert.value = null
    await fetchCategories()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete certification')
  }
}

const onConnect = (params) => {
  edges.value.push({
    id: `e${params.source}-${params.target}`,
    source: params.source,
    target: params.target
  })
}

const saveLayout = async () => {
  saving.value = true
  saveMessage.value = ''
  try {
    await axios.put(`/api/certification-categories/${activeSlug.value}/layout`, {
      certifications: nodes.value.map(n => ({ id: Number(n.id), position_x: n.position.x, position_y: n.position.y })),
      edges: edges.value.map(e => ({ source_cert_id: Number(e.source), target_cert_id: Number(e.target), label: e.label || null }))
    })
    saveMessage.value = 'Saved'
    setTimeout(() => { saveMessage.value = '' }, 2000)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to save layout')
  } finally {
    saving.value = false
  }
}

const openCertPanel = (certData) => {
  activeCert.value = certData
  certForm.value = {
    title: certData.title,
    provider: certData.provider || '',
    description: certData.description || '',
    exam_link: certData.exam_link || '',
    cover_image: certData.cover_image || '',
    difficulty: certData.difficulty,
    status: certData.status
  }
}

const closeCertPanel = () => {
  activeCert.value = null
}

const syncCertDataLocally = (certId, patch) => {
  const flowNode = nodes.value.find(n => n.id === String(certId))
  if (flowNode) Object.assign(flowNode.data, patch)
  if (activeCert.value?.id === certId) Object.assign(activeCert.value, patch)
}

const saveCertDetails = async () => {
  savingCert.value = true
  try {
    const res = await axios.put(`/api/certifications/${activeCert.value.id}`, certForm.value)
    syncCertDataLocally(activeCert.value.id, res.data)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to save certification')
  } finally {
    savingCert.value = false
  }
}

onMounted(async () => {
  await fetchCategories()
  if (categories.value.length > 0) {
    await selectCategory(categories.value[0].slug)
  }
})
</script>

<style scoped>
.hx-cert-canvas {
  width: 100%;
  height: 100%;
  background: #0b0e14;
}

html.light .hx-cert-canvas {
  background: #f8fafc;
}
</style>
