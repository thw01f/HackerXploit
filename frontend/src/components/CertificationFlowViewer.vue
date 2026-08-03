<template>
  <div class="relative w-full h-full bg-[#0b0e14] font-mono overflow-hidden">
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center text-slate-500 text-xs z-10">
      Loading certifications...
    </div>
    <div v-else-if="nodes.length === 0" class="absolute inset-0 flex items-center justify-center text-slate-500 text-xs z-10 text-center px-6">
      No certifications in this category yet.
    </div>

    <VueFlow
      v-model:nodes="nodes"
      v-model:edges="edges"
      :default-viewport="{ zoom: 0.9 }"
      :nodes-draggable="false"
      :nodes-connectable="false"
      :edges-updatable="false"
      class="hx-cert-flow-canvas"
    >
      <template #node-certNode="nodeProps">
        <CertificationNodeCard
          :data="nodeProps.data"
          :selected="selectedCert?.id === nodeProps.data.id"
          @select="selectCert(nodeProps.data)"
        />
      </template>

      <Background :pattern-color="isDark ? '#1f293d' : '#cbd5e1'" :gap="20" />
      <Controls />
    </VueFlow>

    <!-- Backdrop - click anywhere outside the panel to close it -->
    <div
      v-if="selectedCert"
      class="fixed inset-0 z-40 bg-black/40"
      @click="selectedCert = null"
    ></div>

    <!-- Detail Panel -->
    <div
      v-if="selectedCert"
      class="fixed inset-y-0 right-0 z-50 w-full sm:w-[460px] bg-[#161b22] border-l border-[#21262d] shadow-2xl flex flex-col"
    >
      <div class="p-5 border-b border-[#21262d] flex items-center justify-between bg-[#0b0e14]/50">
        <div>
          <span class="text-xs text-[#00f0ff] font-bold uppercase tracking-wider block mb-1">// CERTIFICATION</span>
          <h2 class="text-xl font-extrabold text-white leading-tight">{{ selectedCert.title }}</h2>
        </div>
        <button @click="selectedCert = null" class="p-2 text-slate-400 hover:text-white hover:bg-[#21262d] rounded-lg transition-colors">&times;</button>
      </div>

      <div class="flex-1 overflow-y-auto p-6 space-y-5">
        <div class="flex items-center gap-2 text-sm">
          <span v-if="selectedCert.provider" class="px-3 py-1.5 rounded bg-[#0b0e14] border border-[#21262d] text-slate-300 font-bold uppercase">{{ selectedCert.provider }}</span>
          <span class="px-3 py-1.5 rounded bg-[#0b0e14] border border-[#21262d] text-[#00f0ff] font-bold uppercase">{{ selectedCert.difficulty }}</span>
        </div>

        <p class="text-sm text-slate-300 leading-relaxed whitespace-pre-line">{{ selectedCert.description || 'No description provided.' }}</p>

        <a
          v-if="selectedCert.exam_link"
          :href="selectedCert.exam_link"
          target="_blank"
          rel="noopener noreferrer"
          class="block text-center btn-htb text-sm py-3 font-bold"
        >
          View Exam Info &rarr;
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import CertificationNodeCard from './CertificationNodeCard.vue'
import { useTheme } from '../stores/theme'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'

const props = defineProps({
  categorySlug: { type: String, required: true }
})

const { isDark } = useTheme()
const nodes = ref([])
const edges = ref([])
const loading = ref(true)
const selectedCert = ref(null)

const selectCert = (cert) => {
  selectedCert.value = cert
}

const fetchCategory = async (slug) => {
  if (!slug) {
    nodes.value = []
    edges.value = []
    return
  }
  loading.value = true
  selectedCert.value = null
  try {
    const res = await axios.get(`/api/certification-categories/${slug}/full`)
    const { certifications, edges: apiEdges } = res.data
    nodes.value = certifications.map((c, idx) => ({
      id: String(c.id),
      type: 'certNode',
      position: { x: c.position_x ?? (idx % 4) * 240, y: c.position_y ?? Math.floor(idx / 4) * 160 },
      data: { ...c }
    }))
    edges.value = apiEdges.map(e => ({
      id: `e${e.id}`,
      source: String(e.source_cert_id),
      target: String(e.target_cert_id),
      label: e.label || ''
    }))
  } catch (err) {
    console.error('Failed to load certification category', err)
    nodes.value = []
    edges.value = []
  } finally {
    loading.value = false
  }
}

watch(() => props.categorySlug, (slug) => fetchCategory(slug))

onMounted(() => fetchCategory(props.categorySlug))
</script>

<style scoped>
.hx-cert-flow-canvas {
  width: 100%;
  height: 100%;
  background: #0b0e14;
}

html.light .hx-cert-flow-canvas {
  background: #f8fafc;
}
</style>
