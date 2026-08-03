<template>
  <div class="max-w-3xl mx-auto space-y-8 pb-12 font-mono">

    <div class="text-center space-y-2">
      <span class="px-3 py-1 rounded bg-[#9fef00]/10 border border-[#9fef00]/30 text-[#9fef00] text-xs font-bold uppercase tracking-wider">
        Career Path
      </span>
      <h1 class="text-2xl font-extrabold text-white">{{ roadmapTitle || 'Cybersecurity Career Path' }}</h1>
      <p class="text-xs text-slate-400">Pick a specialization track and work through it step by step.</p>
    </div>

    <!-- Track Picker -->
    <div class="flex flex-wrap justify-center gap-2">
      <button
        v-for="track in tracks"
        :key="track"
        @click="selectedTrack = track"
        :class="[
          'px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wide border transition-all',
          selectedTrack === track ? 'bg-[#9fef00]/15 text-[#9fef00] border-[#9fef00]/40' : 'text-slate-400 border-slate-800 hover:border-slate-700'
        ]"
      >
        {{ track.replace('_', ' ') }}
      </button>
    </div>

    <!-- Progress summary for this track -->
    <div v-if="trackNodes.length" class="glass-panel p-4 flex items-center justify-between">
      <span class="text-xs text-slate-400">{{ trackDoneCount }} / {{ trackNodes.length }} completed</span>
      <div class="w-40 h-2 bg-[#0b0e14] rounded-full border border-[#21262d] overflow-hidden">
        <div class="h-full bg-gradient-to-r from-[#00f0ff] to-[#9fef00]" :style="{ width: trackProgressPercent + '%' }"></div>
      </div>
    </div>

    <!-- Sequential Path -->
    <div v-if="trackNodes.length === 0" class="glass-panel p-12 text-center text-slate-500 text-xs">
      No nodes tagged for this track yet.
    </div>

    <div v-else class="relative pl-8">
      <div class="absolute left-3 top-2 bottom-2 w-0.5 bg-[#1f293d]"></div>

      <div v-for="(node, idx) in trackNodes" :key="node.id" class="relative mb-6">
        <span
          class="absolute -left-8 top-3 w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-extrabold border-2"
          :class="node.user_status === 'done' ? 'bg-[#9fef00] text-black border-[#9fef00]' : 'bg-[#0b0e14] text-slate-400 border-slate-700'"
        >
          {{ node.user_status === 'done' ? '&#10003;' : idx + 1 }}
        </span>

        <RoadmapNodeCard :data="node" :selected="selectedNode?.id === node.id" full-width @select="selectNode(node)" />
      </div>
    </div>

    <!-- Backdrop - click anywhere outside the panel to close it -->
    <div
      v-if="selectedNode"
      class="fixed inset-0 z-40 bg-black/40"
      @click="selectedNode = null"
    ></div>

    <!-- Detail Panel -->
    <div
      v-if="selectedNode"
      class="fixed inset-y-0 right-0 z-50 w-full sm:w-[520px] bg-[#161b22] border-l border-[#21262d] shadow-2xl flex flex-col"
    >
      <div class="p-6 border-b border-[#21262d] flex items-center justify-between bg-[#0b0e14]/50">
        <h2 class="text-xl font-extrabold text-white leading-tight">{{ selectedNode.label }}</h2>
        <button @click="selectedNode = null" class="p-2 text-slate-400 hover:text-white hover:bg-[#21262d] rounded-lg transition-colors">&times;</button>
      </div>

      <div class="flex-1 overflow-y-auto p-6 space-y-6">
        <div class="bg-[#0b0e14] p-4 rounded-xl border border-[#21262d] flex items-center justify-between">
          <span class="text-sm font-extrabold uppercase" :class="getStatusColorClass(selectedNode.user_status)">
            {{ selectedNode.user_status === 'done' ? 'Completed' : selectedNode.user_status === 'in_progress' ? 'In Progress' : 'Not Started' }}
          </span>
          <button
            @click="cycleNodeProgress(selectedNode)"
            :disabled="updatingProgress"
            class="px-5 py-2.5 text-sm font-extrabold rounded-lg border transition-all"
            :class="getCycleButtonClass(selectedNode.user_status)"
          >
            {{ updatingProgress ? 'Updating...' : getCycleButtonText(selectedNode.user_status) }}
          </button>
        </div>

        <div class="prose prose-invert max-w-none text-sm leading-relaxed">
          <div v-html="selectedNode.description_html"></div>
        </div>

        <div v-if="selectedNode.resources?.length" class="pt-4 border-t border-[#21262d] space-y-2">
          <h3 class="text-sm font-extrabold text-[#00f0ff] uppercase tracking-wider mb-2">// LEARNING RESOURCES</h3>
          <a
            v-for="res in selectedNode.resources"
            :key="res.id"
            :href="res.url"
            target="_blank"
            rel="noopener noreferrer"
            class="block p-3.5 bg-[#0b0e14] hover:bg-[#21262d] rounded-xl border border-[#21262d] hover:border-[#00f0ff]/50 transition-all"
          >
            <span class="text-sm font-bold text-slate-200">{{ res.title }}</span>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import RoadmapNodeCard from '../components/RoadmapNodeCard.vue'
import { useRoadmapGraph } from '../composables/useRoadmapGraph'

const route = useRoute()

const {
  roadmapTitle, rawNodes,
  updatingProgress,
  fetchRoadmapData, cycleNodeProgress,
  getStatusColorClass, getCycleButtonClass, getCycleButtonText
} = useRoadmapGraph(() => route.params.slug || 'cyber-security')

const selectedTrack = ref('')
const selectedNode = ref(null)

const tracks = computed(() => {
  const groups = new Set(rawNodes.value.filter(n => n.layout_group).map(n => n.layout_group))
  return Array.from(groups)
})

const trackNodes = computed(() => {
  if (!selectedTrack.value) return []
  return rawNodes.value
    .filter(n => n.layout_group === selectedTrack.value && n.node_type !== 'section')
    .sort((a, b) => a.order_index - b.order_index)
})

const trackDoneCount = computed(() => trackNodes.value.filter(n => n.user_status === 'done').length)
const trackProgressPercent = computed(() => {
  if (trackNodes.value.length === 0) return 0
  return Math.round((trackDoneCount.value / trackNodes.value.length) * 100)
})

const selectNode = (node) => {
  selectedNode.value = node
}

watch(() => route.params.slug, async () => {
  selectedTrack.value = ''
  selectedNode.value = null
  await fetchRoadmapData()
  if (tracks.value.length > 0) selectedTrack.value = tracks.value[0]
})

onMounted(async () => {
  await fetchRoadmapData()
  if (tracks.value.length > 0) selectedTrack.value = tracks.value[0]
})
</script>
