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

    <!-- Vue Flow Canvas (read-only: no dragging, no connecting) -->
    <div class="w-full h-full pt-14">
      <VueFlow
        v-model:nodes="nodes"
        v-model:edges="edges"
        :default-viewport="{ zoom: 0.8 }"
        :nodes-draggable="false"
        :nodes-connectable="false"
        :edges-updatable="false"
        class="hx-roadmap-canvas"
      >
        <template #node-roadmapNode="nodeProps">
          <RoadmapNodeCard
            :data="nodeProps.data"
            :selected="selectedNode?.id === nodeProps.data.id"
            @select="selectNode(nodeProps.data)"
          />
        </template>

        <Background pattern-color="#1f293d" :gap="20" />
        <Controls />
        <MiniMap />
      </VueFlow>
    </div>

    <!-- Fixed Legend Panel -->
    <div class="absolute bottom-6 left-6 z-20 bg-[#161b22]/95 backdrop-blur-md p-4 rounded-xl border border-[#21262d] shadow-2xl text-xs space-y-3 max-w-xs">
      <div class="flex items-center justify-between border-b border-[#21262d] pb-2">
        <span class="font-extrabold text-white uppercase text-[11px] tracking-wider">// ROADMAP LEGEND</span>
        <span class="text-[10px] text-slate-400">Guide</span>
      </div>

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

      <div class="pt-2 border-t border-[#21262d] space-y-1.5 text-[11px]">
        <div class="flex items-center space-x-2">
          <span class="w-3.5 h-3.5 rounded-full bg-[#9fef00] text-black font-extrabold text-[9px] flex items-center justify-center">&#10003;</span>
          <span class="text-slate-200">Done / Completed</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="w-3.5 h-3.5 rounded-full bg-amber-400 text-black font-extrabold text-[9px] flex items-center justify-center">&#8987;</span>
          <span class="text-slate-300">In Progress</span>
        </div>
      </div>
    </div>

    <!-- Side Detail Slide-in Panel / Mobile Bottom Sheet -->
    <div
      v-if="selectedNode"
      class="fixed inset-y-0 right-0 z-50 w-full sm:w-[480px] bg-[#161b22] border-l border-[#21262d] shadow-2xl flex flex-col transform transition-transform duration-300 ease-out"
      :class="selectedNode ? 'translate-x-0' : 'translate-x-full'"
    >
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
          &times;
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-6 space-y-6">
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

        <div class="prose prose-invert max-w-none text-xs leading-relaxed space-y-4">
          <div v-html="selectedNode.description_html"></div>
        </div>

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
import { ref, onMounted } from 'vue'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import RoadmapNodeCard from './RoadmapNodeCard.vue'
import { useRoadmapGraph } from '../composables/useRoadmapGraph'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

const props = defineProps({
  roadmapSlug: {
    type: String,
    default: 'cyber-security'
  }
})

const {
  roadmapTitle, nodes, edges,
  progressPercent, doneCount, totalCount, updatingProgress,
  fetchRoadmapData, cycleNodeProgress,
  getStatusColorClass, getCycleButtonClass, getCycleButtonText
} = useRoadmapGraph(props.roadmapSlug)

const selectedNode = ref(null)

const selectNode = (node) => {
  selectedNode.value = node
}

onMounted(() => {
  fetchRoadmapData()
})
</script>

<style scoped>
.hx-roadmap-canvas {
  width: 100%;
  height: 100%;
  background: #0b0e14;
}
</style>
