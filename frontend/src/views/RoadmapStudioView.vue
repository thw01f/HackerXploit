<template>
  <div class="space-y-6 font-mono">
    <div class="flex items-center justify-between border-b border-[#1f293d] pb-4">
      <div>
        <h1 class="text-2xl font-extrabold text-white">Roadmap Studio</h1>
        <p class="text-xs text-slate-400 mt-1">Build a career path visually - add nodes, drag to arrange, connect them, then save.</p>
      </div>
      <router-link to="/academy" class="btn-ghost text-xs py-2 px-4">&larr; Back to Academy</router-link>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-6" style="height: calc(100vh - 220px);">

      <!-- Left: Roadmap picker -->
      <div class="glass-panel p-4 space-y-4 overflow-y-auto">
        <div class="space-y-2">
          <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Roadmaps</h3>
          <button
            v-for="rm in roadmaps"
            :key="rm.slug"
            @click="selectRoadmap(rm.slug)"
            :class="[
              'w-full text-left px-3 py-2.5 rounded-xl border text-xs transition-all',
              activeSlug === rm.slug ? 'border-[#9fef00] bg-[#9fef00]/10 text-white font-bold' : 'border-slate-800 bg-slate-900/60 text-slate-300 hover:border-slate-700'
            ]"
          >
            {{ rm.title }}
            <span class="block text-[10px] text-slate-500 mt-0.5">{{ rm.nodes_count }} nodes</span>
          </button>
          <p v-if="roadmaps.length === 0" class="text-xs text-slate-500 text-center py-4">No roadmaps yet.</p>
        </div>

        <div class="pt-4 border-t border-slate-800 space-y-2">
          <input v-model="newRoadmapTitle" type="text" placeholder="New roadmap title" class="input-field w-full text-xs py-2" />
          <button @click="createRoadmap" :disabled="!newRoadmapTitle.trim() || creating" class="btn-htb w-full text-xs py-2">
            {{ creating ? 'Creating...' : '+ New Roadmap' }}
          </button>
        </div>

        <div v-if="activeSlug" class="pt-4 border-t border-slate-800">
          <button @click="deleteActiveRoadmap" class="w-full text-xs py-2 rounded-lg text-rose-400 border border-rose-500/40 hover:bg-rose-500/10 transition-all">
            Delete This Roadmap
          </button>
        </div>
      </div>

      <!-- Center: Canvas -->
      <div class="glass-panel p-0 overflow-hidden relative flex flex-col">
        <div v-if="!activeSlug" class="flex-1 flex items-center justify-center text-slate-500 text-xs">
          Select or create a roadmap to start editing.
        </div>

        <template v-else>
          <div class="flex items-center gap-3 p-3 border-b border-[#1f293d] bg-[#0b0e14]">
            <button @click="addNode" class="btn-ghost text-xs py-1.5 px-3">+ Add Node</button>
            <button @click="saveLayout" :disabled="saving" class="btn-htb text-xs py-1.5 px-4">
              {{ saving ? 'Saving...' : 'Save Layout' }}
            </button>
            <span v-if="saveMessage" class="text-[11px] text-emerald-400">{{ saveMessage }}</span>
            <span class="text-[11px] text-slate-500 ml-auto">Drag a node's handle to another node to connect. Select a connection + press Delete to remove it.</span>
          </div>

          <div class="flex-1 relative">
            <VueFlow
              v-model:nodes="nodes"
              v-model:edges="edges"
              :default-viewport="{ zoom: 0.9 }"
              @connect="onConnect"
              class="hx-roadmap-canvas"
            >
              <template #node-roadmapNode="nodeProps">
                <RoadmapNodeCard
                  :data="nodeProps.data"
                  :selected="nodeProps.selected"
                  editable
                  @select="openNodePanel(nodeProps.data)"
                  @delete-node="deleteNode(nodeProps.data)"
                />
              </template>

              <Background pattern-color="#1f293d" :gap="20" />
              <Controls />
              <MiniMap />
            </VueFlow>
          </div>
        </template>
      </div>
    </div>

    <!-- Node Detail Side Panel -->
    <div
      v-if="activeNode"
      class="fixed inset-y-0 right-0 z-50 w-full sm:w-[440px] bg-[#161b22] border-l border-[#21262d] shadow-2xl flex flex-col"
    >
      <div class="p-5 border-b border-[#21262d] flex items-center justify-between bg-[#0b0e14]/50">
        <span class="text-[10px] text-[#00f0ff] font-bold uppercase tracking-wider">// Edit Node</span>
        <button @click="closeNodePanel" class="p-1.5 text-slate-400 hover:text-white hover:bg-[#21262d] rounded-lg transition-colors">&times;</button>
      </div>

      <div class="flex-1 overflow-y-auto p-5 space-y-4 text-xs">
        <div>
          <label class="block text-slate-400 uppercase mb-1 text-[11px]">Label</label>
          <input v-model="nodeForm.label" type="text" class="input-field w-full py-2" />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-slate-400 uppercase mb-1 text-[11px]">Type</label>
            <select v-model="nodeForm.node_type" class="input-field w-full py-2 bg-[#0b0e14]">
              <option value="section">Section</option>
              <option value="topic">Topic</option>
              <option value="subtopic">Subtopic</option>
            </select>
          </div>
          <div>
            <label class="block text-slate-400 uppercase mb-1 text-[11px]">Importance</label>
            <select v-model="nodeForm.importance" class="input-field w-full py-2 bg-[#0b0e14]">
              <option value="recommended">Recommended</option>
              <option value="alternative">Alternative</option>
              <option value="optional">Optional</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-slate-400 uppercase mb-1 text-[11px]">Layout Group (optional tag)</label>
          <input v-model="nodeForm.layout_group" type="text" placeholder="e.g. red_team" class="input-field w-full py-2" />
        </div>

        <div>
          <label class="block text-slate-400 uppercase mb-1 text-[11px]">Description (Markdown)</label>
          <textarea v-model="nodeForm.description_markdown" rows="6" class="input-field w-full py-2"></textarea>
        </div>

        <button @click="saveNodeDetails" :disabled="savingNode" class="btn-htb w-full py-2 text-xs">
          {{ savingNode ? 'Saving...' : 'Save Node' }}
        </button>

        <!-- Resources -->
        <div class="pt-4 border-t border-[#21262d] space-y-3">
          <h3 class="text-[11px] font-extrabold text-[#00f0ff] uppercase tracking-wider">Resources</h3>

          <div v-for="res in activeNode.resources" :key="res.id" class="p-2.5 bg-[#0b0e14] rounded-lg border border-[#21262d] flex items-center justify-between gap-2">
            <div class="min-w-0">
              <p class="text-white font-bold truncate">{{ res.title }}</p>
              <p class="text-slate-500 text-[10px] truncate">{{ res.url }}</p>
            </div>
            <button @click="deleteResource(res.id)" class="text-rose-400 hover:text-rose-300 shrink-0">&times;</button>
          </div>

          <div class="space-y-2 pt-2">
            <input v-model="resourceForm.title" type="text" placeholder="Resource title" class="input-field w-full py-1.5 text-[11px]" />
            <input v-model="resourceForm.url" type="text" placeholder="https://..." class="input-field w-full py-1.5 text-[11px]" />
            <select v-model="resourceForm.resource_type" class="input-field w-full py-1.5 text-[11px] bg-[#0b0e14]">
              <option value="article">Article</option>
              <option value="video">Video</option>
              <option value="doc">Doc</option>
            </select>
            <button @click="addResource" :disabled="!resourceForm.title.trim() || !resourceForm.url.trim()" class="btn-ghost w-full py-1.5 text-[11px]">
              + Add Resource
            </button>
          </div>
        </div>
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
import RoadmapNodeCard from '../components/RoadmapNodeCard.vue'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

const roadmaps = ref([])
const activeSlug = ref('')
const nodes = ref([])
const edges = ref([])
const newRoadmapTitle = ref('')
const creating = ref(false)
const saving = ref(false)
const saveMessage = ref('')

const activeNode = ref(null)
const nodeForm = ref({ label: '', node_type: 'topic', importance: 'recommended', layout_group: '', description_markdown: '' })
const savingNode = ref(false)
const resourceForm = ref({ title: '', url: '', resource_type: 'article' })

let nodeCounter = 0

const toFlowNode = (n, idx) => ({
  id: String(n.id),
  type: 'roadmapNode',
  position: { x: n.position_x ?? (idx % 4) * 240, y: n.position_y ?? Math.floor(idx / 4) * 160 },
  data: { ...n }
})

const fetchRoadmaps = async () => {
  const res = await axios.get('/api/roadmaps')
  roadmaps.value = res.data
}

const selectRoadmap = async (slug) => {
  activeSlug.value = slug
  saveMessage.value = ''
  activeNode.value = null
  const res = await axios.get(`/api/roadmaps/${slug}`)
  const { nodes: apiNodes, edges: apiEdges } = res.data

  nodes.value = apiNodes.map(toFlowNode)
  edges.value = apiEdges.map(e => ({
    id: `e${e.id}`,
    source: String(e.source_node_id),
    target: String(e.target_node_id),
    label: e.label || ''
  }))
}

const createRoadmap = async () => {
  creating.value = true
  try {
    const slug = newRoadmapTitle.value.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
    const res = await axios.post('/api/roadmaps', { slug, title: newRoadmapTitle.value.trim() })
    newRoadmapTitle.value = ''
    await fetchRoadmaps()
    await selectRoadmap(res.data.slug)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to create roadmap')
  } finally {
    creating.value = false
  }
}

const deleteActiveRoadmap = async () => {
  if (!confirm(`Delete the "${activeSlug.value}" roadmap? This cannot be undone.`)) return
  try {
    await axios.delete(`/api/roadmaps/${activeSlug.value}`)
    activeSlug.value = ''
    nodes.value = []
    edges.value = []
    activeNode.value = null
    await fetchRoadmaps()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete roadmap')
  }
}

const addNode = async () => {
  nodeCounter += 1
  const res = await axios.post(`/api/roadmaps/${activeSlug.value}/nodes`, {
    label: `New Node ${nodeCounter}`,
    node_type: 'topic',
    position_x: 40,
    position_y: 40
  })
  nodes.value.push(toFlowNode(res.data, nodes.value.length))
}

const deleteNode = async (nodeData) => {
  if (!confirm(`Delete node "${nodeData.label}"? This removes its resources and connections too.`)) return
  try {
    await axios.delete(`/api/roadmaps/nodes/${nodeData.id}`)
    nodes.value = nodes.value.filter(n => n.id !== String(nodeData.id))
    edges.value = edges.value.filter(e => e.source !== String(nodeData.id) && e.target !== String(nodeData.id))
    if (activeNode.value?.id === nodeData.id) activeNode.value = null
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete node')
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
    await axios.put(`/api/roadmaps/${activeSlug.value}/layout`, {
      nodes: nodes.value.map(n => ({ id: Number(n.id), position_x: n.position.x, position_y: n.position.y })),
      edges: edges.value.map(e => ({ source_node_id: Number(e.source), target_node_id: Number(e.target), label: e.label || null }))
    })
    saveMessage.value = 'Saved'
    setTimeout(() => { saveMessage.value = '' }, 2000)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to save layout')
  } finally {
    saving.value = false
  }
}

const openNodePanel = (nodeData) => {
  activeNode.value = nodeData
  nodeForm.value = {
    label: nodeData.label,
    node_type: nodeData.node_type,
    importance: nodeData.importance,
    layout_group: nodeData.layout_group || '',
    description_markdown: nodeData.description_markdown || ''
  }
  resourceForm.value = { title: '', url: '', resource_type: 'article' }
}

const closeNodePanel = () => {
  activeNode.value = null
}

const syncNodeDataLocally = (nodeId, patch) => {
  const flowNode = nodes.value.find(n => n.id === String(nodeId))
  if (flowNode) Object.assign(flowNode.data, patch)
  if (activeNode.value?.id === nodeId) Object.assign(activeNode.value, patch)
}

const saveNodeDetails = async () => {
  savingNode.value = true
  try {
    const res = await axios.put(`/api/roadmaps/nodes/${activeNode.value.id}`, nodeForm.value)
    syncNodeDataLocally(activeNode.value.id, res.data)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to save node')
  } finally {
    savingNode.value = false
  }
}

const addResource = async () => {
  try {
    const res = await axios.post(`/api/roadmaps/nodes/${activeNode.value.id}/resources`, resourceForm.value)
    activeNode.value.resources = [...(activeNode.value.resources || []), res.data]
    syncNodeDataLocally(activeNode.value.id, { resources: activeNode.value.resources })
    resourceForm.value = { title: '', url: '', resource_type: 'article' }
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to add resource')
  }
}

const deleteResource = async (resourceId) => {
  try {
    await axios.delete(`/api/roadmaps/resources/${resourceId}`)
    activeNode.value.resources = activeNode.value.resources.filter(r => r.id !== resourceId)
    syncNodeDataLocally(activeNode.value.id, { resources: activeNode.value.resources })
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete resource')
  }
}

onMounted(async () => {
  await fetchRoadmaps()
  if (roadmaps.value.length > 0) {
    await selectRoadmap(roadmaps.value[0].slug)
  }
})
</script>

<style scoped>
.hx-roadmap-canvas {
  width: 100%;
  height: 100%;
  background: #0b0e14;
}
</style>
