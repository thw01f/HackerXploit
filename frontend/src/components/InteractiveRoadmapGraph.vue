<template>
  <div class="relative w-full h-full bg-[#0b0e14] text-slate-100 font-mono overflow-hidden select-none">
    
    <!-- Top Progress Bar Header -->
    <div class="absolute top-0 left-0 right-0 z-20 h-14 bg-[#161b22]/90 backdrop-blur-md border-b border-[#21262d] px-6 flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <router-link to="/academy" class="text-slate-400 hover:text-[#00f0ff] transition-colors flex items-center space-x-1.5 text-xs font-bold">
          <span>&larr; Academy</span>
        </router-link>
        <span class="text-slate-600">|</span>
        <div class="flex items-center space-x-2">
          <span class="w-2.5 h-2.5 rounded-full bg-[#9fef00] animate-pulse"></span>
          <h1 class="text-sm font-extrabold text-white tracking-wide uppercase">{{ roadmapTitle || 'Cyber Security Roadmap' }}</h1>
        </div>
      </div>

      <!-- Completion Stats & Progress Bar -->
      <div class="flex items-center space-x-6">
        <div class="flex items-center space-x-3 text-xs">
          <span class="text-slate-400 uppercase font-bold">Progress:</span>
          <span class="text-[#00f0ff] font-extrabold text-sm">{{ progressPercent }}%</span>
          <span class="text-slate-500 text-[11px]">({{ doneCount }}/{{ totalCount }} nodes)</span>
        </div>

        <div class="w-48 h-2.5 bg-[#0b0e14] rounded-full border border-[#21262d] overflow-hidden">
          <div 
            class="h-full bg-gradient-to-r from-[#00f0ff] to-[#9fef00] transition-all duration-500 ease-out shadow-[0_0_12px_rgba(159,239,0,0.5)]"
            :style="{ width: `${progressPercent}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Canvas Pan & Zoom Workspace -->
    <div 
      ref="canvasContainer"
      class="w-full h-full cursor-grab active:cursor-grabbing pt-14"
      @mousedown="startPan"
      @mousemove="doPan"
      @mouseup="stopPan"
      @mouseleave="stopPan"
      @wheel.prevent="handleWheelZoom"
      @touchstart="handleTouchStart"
      @touchmove="handleTouchMove"
      @touchend="handleTouchEnd"
    >
      <!-- Transformed Graph Container -->
      <div 
        class="relative min-w-[1200px] min-h-[1600px] transition-transform duration-75 origin-top-left p-16"
        :style="{ transform: `translate(${panX}px, ${panY}px) scale(${zoomLevel})` }"
      >
        <!-- SVG Connections Layer -->
        <svg class="absolute inset-0 w-full h-full pointer-events-none z-0 overflow-visible">
          <defs>
            <linearGradient id="edge-glow" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#00f0ff" stop-opacity="0.6"/>
              <stop offset="100%" stop-color="#9fef00" stop-opacity="0.6"/>
            </linearGradient>
          </defs>
          <path
            v-for="(edge, idx) in calculatedEdges"
            :key="'edge-' + idx"
            :d="edge.d"
            stroke="url(#edge-glow)"
            stroke-width="2"
            fill="none"
            stroke-dasharray="4 2"
            class="opacity-60 transition-all duration-300 hover:opacity-100"
          />
        </svg>

        <!-- Node Tree Layout -->
        <div class="relative z-10 space-y-16 flex flex-col items-center">
          <div 
            v-for="group in nodeGroups" 
            :key="group.id" 
            class="w-full max-w-5xl flex flex-col items-center space-y-8"
          >
            <!-- Section Header Banner -->
            <div 
              :id="'node-' + group.sectionNode.id"
              @click.stop="selectNode(group.sectionNode)"
              class="px-8 py-3 bg-[#161b22]/90 border-2 border-[#00f0ff] rounded-xl shadow-[0_0_20px_rgba(0,240,255,0.2)] text-center cursor-pointer hover:border-[#9fef00] hover:shadow-[0_0_25px_rgba(159,239,0,0.3)] transition-all duration-300 transform hover:-translate-y-0.5"
            >
              <span class="text-[10px] text-[#00f0ff] uppercase font-bold tracking-widest block mb-0.5">// PHASE SECTION</span>
              <h2 class="text-base font-extrabold text-white font-serif uppercase tracking-wider">{{ group.sectionNode.label }}</h2>
            </div>

            <!-- Topic Nodes Grid / Flow Branch -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full px-4">
              <div
                v-for="node in group.childNodes"
                :key="node.id"
                :id="'node-' + node.id"
                @click.stop="selectNode(node)"
                class="relative p-5 rounded-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1 backdrop-blur-md flex flex-col justify-between group"
                :class="[
                  getNodeBorderClass(node),
                  selectedNode?.id === node.id ? 'ring-2 ring-[#00f0ff] shadow-[0_0_25px_rgba(0,240,255,0.4)]' : 'shadow-lg hover:shadow-2xl'
                ]"
              >
                <!-- Status Corner Indicator -->
                <div class="absolute -top-2 -right-2 z-20">
                  <span 
                    v-if="node.user_status === 'done'" 
                    class="w-6 h-6 rounded-full bg-[#9fef00] text-black font-extrabold text-xs flex items-center justify-center shadow-[0_0_10px_rgba(159,239,0,0.8)] border border-black"
                  >
                    ✓
                  </span>
                  <span 
                    v-else-if="node.user_status === 'in_progress'" 
                    class="w-6 h-6 rounded-full bg-amber-400 text-black font-extrabold text-[10px] flex items-center justify-center shadow-[0_0_10px_rgba(251,191,36,0.8)] border border-black animate-pulse"
                  >
                    ⏳
                  </span>
                </div>

                <div>
                  <!-- Node Metadata Badges -->
                  <div class="flex items-center justify-between mb-2">
                    <span 
                      class="text-[9px] uppercase font-extrabold px-2 py-0.5 rounded tracking-wider border"
                      :class="getImportanceBadgeClass(node.importance)"
                    >
                      {{ node.importance }}
                    </span>
                    <span class="text-[10px] text-slate-400 capitalize font-mono">{{ node.node_type }}</span>
                  </div>

                  <!-- Node Label -->
                  <h3 class="text-sm font-bold text-white group-hover:text-[#00f0ff] transition-colors leading-snug">
                    {{ node.label }}
                  </h3>
                </div>

                <!-- Footer Resource Count & Action Indicator -->
                <div class="mt-4 pt-3 border-t border-[#21262d] flex items-center justify-between text-[11px] text-slate-400">
                  <span class="flex items-center space-x-1">
                    <svg class="w-3.5 h-3.5 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                    </svg>
                    <span>{{ node.resources?.length || 0 }} resources</span>
                  </span>
                  <span class="text-[#9fef00] opacity-0 group-hover:opacity-100 transition-opacity font-bold">Details &rarr;</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- On-Canvas Zoom & Reset Controls -->
    <div class="absolute bottom-6 right-6 z-20 flex flex-col space-y-2 bg-[#161b22]/90 backdrop-blur-md p-2 rounded-xl border border-[#21262d] shadow-xl">
      <button 
        @click="zoomIn" 
        class="w-8 h-8 rounded-lg bg-[#21262d] hover:bg-[#30363d] text-white font-bold flex items-center justify-center transition-colors text-sm"
        title="Zoom In"
      >+</button>
      <button 
        @click="resetZoom" 
        class="w-8 h-8 rounded-lg bg-[#21262d] hover:bg-[#30363d] text-[#00f0ff] text-[10px] font-bold flex items-center justify-center transition-colors"
        title="Reset Zoom"
      >RESET</button>
      <button 
        @click="zoomOut" 
        class="w-8 h-8 rounded-lg bg-[#21262d] hover:bg-[#30363d] text-white font-bold flex items-center justify-center transition-colors text-sm"
        title="Zoom Out"
      >&minus;</button>
    </div>

    <!-- Fixed Legend Panel -->
    <div class="absolute bottom-6 left-6 z-20 bg-[#161b22]/95 backdrop-blur-md p-4 rounded-xl border border-[#21262d] shadow-2xl text-xs space-y-3 max-w-xs">
      <div class="flex items-center justify-between border-b border-[#21262d] pb-2">
        <span class="font-extrabold text-white uppercase text-[11px] tracking-wider">// ROADMAP LEGEND</span>
        <span class="text-[10px] text-slate-400">Guide</span>
      </div>

      <!-- Importance Levels -->
      <div class="space-y-1.5 text-[11px]">
        <div class="flex items-center space-x-2">
          <span class="w-3 h-3 rounded bg-[#161b22] border-2 border-[#9fef00]"></span>
          <span class="text-slate-200">Recommended (Core Path)</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="w-3 h-3 rounded bg-[#161b22] border-2 border-dashed border-amber-400"></span>
          <span class="text-slate-300">Alternative (Elective)</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="w-3 h-3 rounded bg-[#161b22] border border-slate-600"></span>
          <span class="text-slate-400">Optional (Advanced)</span>
        </div>
      </div>

      <!-- Progress Indicators -->
      <div class="pt-2 border-t border-[#21262d] space-y-1.5 text-[11px]">
        <div class="flex items-center space-x-2">
          <span class="w-3.5 h-3.5 rounded-full bg-[#9fef00] text-black font-extrabold text-[9px] flex items-center justify-center">✓</span>
          <span class="text-slate-200">Done / Completed</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="w-3.5 h-3.5 rounded-full bg-amber-400 text-black font-extrabold text-[9px] flex items-center justify-center">⏳</span>
          <span class="text-slate-300">In Progress</span>
        </div>
      </div>
    </div>

    <!-- MiniMap Canvas Overview -->
    <div class="hidden lg:block absolute bottom-6 right-24 z-20 w-36 h-28 bg-[#161b22]/95 border border-[#21262d] rounded-xl overflow-hidden shadow-2xl p-2">
      <span class="text-[9px] text-slate-500 uppercase font-bold block mb-1">MINIMAP</span>
      <div class="relative w-full h-20 bg-[#0b0e14] rounded border border-[#21262d] flex flex-col items-center justify-around py-1">
        <div 
          v-for="group in nodeGroups" 
          :key="'mini-' + group.id" 
          class="w-full flex justify-center space-x-1 px-1"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-[#00f0ff]"></span>
          <span 
            v-for="n in group.childNodes.slice(0, 3)" 
            :key="'mini-n-' + n.id" 
            class="w-1 h-1 rounded-full"
            :class="n.user_status === 'done' ? 'bg-[#9fef00]' : n.user_status === 'in_progress' ? 'bg-amber-400' : 'bg-slate-600'"
          ></span>
        </div>
      </div>
    </div>

    <!-- Side Detail Slide-in Panel / Mobile Bottom Sheet -->
    <div 
      v-if="selectedNode"
      class="fixed inset-y-0 right-0 z-50 w-full sm:w-[480px] bg-[#161b22] border-l border-[#21262d] shadow-2xl flex flex-col transform transition-transform duration-300 ease-out"
      :class="selectedNode ? 'translate-x-0' : 'translate-x-full'"
    >
      <!-- Panel Header -->
      <div class="p-6 border-b border-[#21262d] flex items-center justify-between bg-[#0b0e14]/50">
        <div>
          <span class="text-[10px] text-[#00f0ff] font-bold uppercase tracking-wider block mb-1">
            // NODE EXPLAINER & RESOURCES
          </span>
          <h2 class="text-lg font-extrabold text-white leading-tight">{{ selectedNode.label }}</h2>
        </div>
        <button 
          @click="selectedNode = null" 
          class="p-2 text-slate-400 hover:text-white hover:bg-[#21262d] rounded-lg transition-colors"
        >
          ✕
        </button>
      </div>

      <!-- Panel Body (Sanitized Markdown & Resources) -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">
        <!-- 3-State Progress Cycle Control Button -->
        <div class="bg-[#0b0e14] p-4 rounded-xl border border-[#21262d] flex items-center justify-between">
          <div>
            <span class="text-[11px] text-slate-400 uppercase font-bold block">Status:</span>
            <span 
              class="text-xs font-extrabold uppercase tracking-wide"
              :class="getStatusColorClass(selectedNode.user_status)"
            >
              {{ selectedNode.user_status === 'done' ? 'Completed' : selectedNode.user_status === 'in_progress' ? 'In Progress' : 'Not Started' }}
            </span>
          </div>

          <button 
            @click="cycleNodeProgress(selectedNode)"
            :disabled="updatingProgress"
            class="px-4 py-2 text-xs font-extrabold rounded-lg border transition-all flex items-center space-x-2 shadow-lg"
            :class="getCycleButtonClass(selectedNode.user_status)"
          >
            <span>{{ updatingProgress ? 'Updating...' : getCycleButtonText(selectedNode.user_status) }}</span>
          </button>
        </div>

        <!-- Rendered Description Markdown (sanitized server-side via bleach, see markdown_service.py) -->
        <div class="prose prose-invert max-w-none text-xs leading-relaxed space-y-4">
          <div v-html="selectedNode.description_html"></div>
        </div>

        <!-- Resource Links Grouped by Type -->
        <div v-if="selectedNode.resources && selectedNode.resources.length > 0" class="pt-4 border-t border-[#21262d] space-y-4">
          <h3 class="text-xs font-extrabold text-[#00f0ff] uppercase tracking-wider">// LEARNING RESOURCES</h3>
          
          <div class="space-y-2">
            <a 
              v-for="res in selectedNode.resources" 
              :key="res.id"
              :href="res.url"
              target="_blank"
              rel="noopener noreferrer"
              class="p-3 bg-[#0b0e14] hover:bg-[#21262d] rounded-xl border border-[#21262d] hover:border-[#00f0ff]/50 transition-all flex items-center justify-between group"
            >
              <div class="flex items-center space-x-3">
                <span class="p-2 rounded-lg bg-[#161b22] text-[#9fef00] text-xs font-bold uppercase">
                  {{ res.resource_type }}
                </span>
                <div>
                  <h4 class="text-xs font-bold text-slate-200 group-hover:text-[#00f0ff] transition-colors">{{ res.title }}</h4>
                  <span class="text-[10px] text-slate-500 truncate block max-w-[220px]">{{ res.url }}</span>
                </div>
              </div>
              <span class="text-[#00f0ff] group-hover:translate-x-1 transition-transform">&rarr;</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'

const props = defineProps({
  roadmapSlug: {
    type: String,
    default: 'cyber-security'
  }
})

const roadmapTitle = ref('')
const rawNodes = ref([])
const progressPercent = ref(0)
const doneCount = ref(0)
const totalCount = ref(0)
const selectedNode = ref(null)
const updatingProgress = ref(false)

// Pan & Zoom state
const panX = ref(0)
const panY = ref(0)
const zoomLevel = ref(1.0)
const isPanning = ref(false)
const startMouseX = ref(0)
const startMouseY = ref(0)

// Touch state for pinch zoom
const touchDistance = ref(0)

// Group nodes into sections & child topics
const nodeGroups = computed(() => {
  const sections = rawNodes.value.filter(n => n.node_type === 'section')
  return sections.map(sec => {
    const children = rawNodes.value.filter(n => n.parent_id === sec.id)
    return {
      id: sec.id,
      sectionNode: sec,
      childNodes: children.length > 0 ? children : rawNodes.value.filter(n => n.layout_group === sec.layout_group && n.id !== sec.id)
    }
  })
})

// Calculate connections between sections and child nodes
const calculatedEdges = computed(() => {
  const edges = []
  nodeGroups.value.forEach((group, idx) => {
    if (idx > 0) {
      const prevGroup = nodeGroups.value[idx - 1]
      edges.push({
        d: `M 600,${(idx - 1) * 320 + 100} C 600,${idx * 320 - 50} 600,${idx * 320 - 50} 600,${idx * 320}`
      })
    }
  })
  return edges
})

const fetchRoadmapData = async () => {
  try {
    const res = await axios.get(`/api/roadmaps/${props.roadmapSlug}`, { withCredentials: true })
    roadmapTitle.value = res.data.roadmap?.title || 'Cyber Security Roadmap'
    rawNodes.value = res.data.nodes || []
    progressPercent.value = res.data.progress_percent || 0
    doneCount.value = res.data.done_count || 0
    totalCount.value = res.data.total_count || 0
  } catch (e) {
    console.error('Failed to fetch roadmap data:', e)
  }
}

const selectNode = (node) => {
  selectedNode.value = node
}

const cycleNodeProgress = async (node) => {
  if (updatingProgress.value) return
  updatingProgress.value = true

  const nextStatusMap = {
    'not_started': 'in_progress',
    'in_progress': 'done',
    'done': 'not_started'
  }
  const nextStatus = nextStatusMap[node.user_status] || 'in_progress'

  try {
    const res = await axios.patch(`/api/roadmaps/nodes/${node.id}/progress`, {
      status: nextStatus
    }, { withCredentials: true })

    node.user_status = nextStatus
    progressPercent.value = res.data.progress_percent
    doneCount.value = res.data.done_count
    totalCount.value = res.data.total_count

    const rawIdx = rawNodes.value.findIndex(n => n.id === node.id)
    if (rawIdx !== -1) {
      rawNodes.value[rawIdx].user_status = nextStatus
    }
  } catch (e) {
    if (e.response && e.response.status === 401) {
      alert('Please log in to save your roadmap progress.')
    } else {
      console.error('Failed to update node progress:', e)
    }
  } finally {
    updatingProgress.value = false
  }
}

// Styling Helper Methods
const getNodeBorderClass = (node) => {
  if (node.importance === 'recommended') {
    return 'bg-[#161b22]/90 border-2 border-[#9fef00] text-slate-100 hover:border-[#00f0ff]'
  } else if (node.importance === 'alternative') {
    return 'bg-[#161b22]/80 border-2 border-dashed border-amber-400 text-slate-200 hover:border-amber-300'
  } else {
    return 'bg-[#161b22]/60 border border-slate-700 text-slate-400 hover:border-slate-500'
  }
}

const getImportanceBadgeClass = (importance) => {
  if (importance === 'recommended') return 'bg-[#9fef00]/15 text-[#9fef00] border-[#9fef00]/30'
  if (importance === 'alternative') return 'bg-amber-400/15 text-amber-400 border-amber-400/30'
  return 'bg-slate-800 text-slate-400 border-slate-700'
}

const getStatusColorClass = (status) => {
  if (status === 'done') return 'text-[#9fef00]'
  if (status === 'in_progress') return 'text-amber-400'
  return 'text-slate-400'
}

const getCycleButtonClass = (status) => {
  if (status === 'done') return 'bg-[#9fef00] text-black border-[#9fef00] hover:bg-[#8ee000]'
  if (status === 'in_progress') return 'bg-amber-400 text-black border-amber-400 hover:bg-amber-300'
  return 'bg-[#21262d] text-slate-200 border-[#30363d] hover:bg-[#30363d]'
}

const getCycleButtonText = (status) => {
  if (status === 'done') return 'Mark Not Started'
  if (status === 'in_progress') return 'Mark Completed ✓'
  return 'Start Practice ⏳'
}

// Pan & Zoom Event Handlers
const startPan = (e) => {
  if (e.target.closest('.cursor-pointer')) return
  isPanning.value = true
  startMouseX.value = e.clientX - panX.value
  startMouseY.value = e.clientY - panY.value
}

const doPan = (e) => {
  if (!isPanning.value) return
  panX.value = e.clientX - startMouseX.value
  panY.value = e.clientY - startMouseY.value
}

const stopPan = () => {
  isPanning.value = false
}

const handleWheelZoom = (e) => {
  const delta = e.deltaY < 0 ? 0.08 : -0.08
  zoomLevel.value = Math.min(Math.max(0.4, zoomLevel.value + delta), 2.2)
}

const zoomIn = () => { zoomLevel.value = Math.min(2.2, zoomLevel.value + 0.15) }
const zoomOut = () => { zoomLevel.value = Math.max(0.4, zoomLevel.value - 0.15) }
const resetZoom = () => { zoomLevel.value = 1.0; panX.value = 0; panY.value = 0 }

const handleTouchStart = (e) => {
  if (e.touches.length === 2) {
    touchDistance.value = Math.hypot(
      e.touches[0].clientX - e.touches[1].clientX,
      e.touches[0].clientY - e.touches[1].clientY
    )
  }
}

const handleTouchMove = (e) => {
  if (e.touches.length === 2) {
    const dist = Math.hypot(
      e.touches[0].clientX - e.touches[1].clientX,
      e.touches[0].clientY - e.touches[1].clientY
    )
    const factor = dist / touchDistance.value
    zoomLevel.value = Math.min(Math.max(0.4, zoomLevel.value * (factor > 1 ? 1.02 : 0.98)), 2.2)
    touchDistance.value = dist
  }
}

const handleTouchEnd = () => {
  touchDistance.value = 0
}

onMounted(() => {
  fetchRoadmapData()
  if (window.innerWidth < 768) {
    zoomLevel.value = 0.6
  }
})
</script>
