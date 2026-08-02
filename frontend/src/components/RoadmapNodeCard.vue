<template>
  <div class="relative" :class="fullWidth ? 'w-full' : 'w-[220px]'">
    <Handle v-if="editable" type="target" :position="Position.Top" class="hx-flow-handle" />

    <div
      class="relative p-4 rounded-xl transition-all duration-300 cursor-pointer backdrop-blur-md flex flex-col justify-between group font-mono"
      :class="[
        borderClass,
        selected ? 'ring-2 ring-[#00f0ff] shadow-[0_0_25px_rgba(0,240,255,0.4)]' : 'shadow-lg hover:shadow-2xl'
      ]"
      @click="$emit('select')"
    >
      <!-- Status Corner Indicator -->
      <div v-if="!editable" class="absolute -top-2 -right-2 z-20">
        <span
          v-if="data.user_status === 'done'"
          class="w-6 h-6 rounded-full bg-[#9fef00] text-black font-extrabold text-xs flex items-center justify-center shadow-[0_0_10px_rgba(159,239,0,0.8)] border border-black"
        >&#10003;</span>
        <span
          v-else-if="data.user_status === 'in_progress'"
          class="w-6 h-6 rounded-full bg-amber-400 text-black font-extrabold text-[10px] flex items-center justify-center shadow-[0_0_10px_rgba(251,191,36,0.8)] border border-black animate-pulse"
        >&#8987;</span>
      </div>

      <!-- Delete button (Studio only) -->
      <button
        v-if="editable"
        @click.stop="$emit('delete-node')"
        class="absolute -top-2 -right-2 z-20 w-6 h-6 rounded-full bg-rose-500 hover:bg-rose-400 text-white font-bold text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
        title="Delete node"
      >&times;</button>

      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="text-[9px] uppercase font-extrabold px-2 py-0.5 rounded tracking-wider border" :class="badgeClass">
            {{ data.importance }}
          </span>
          <span class="text-[10px] text-slate-400 capitalize font-mono">{{ data.node_type }}</span>
        </div>

        <h3 class="text-sm font-bold text-white group-hover:text-[#00f0ff] transition-colors leading-snug">
          {{ data.label }}
        </h3>
      </div>

      <div class="mt-3 pt-2 border-t border-[#21262d] flex items-center justify-between text-[11px] text-slate-400">
        <span class="flex items-center space-x-1">
          <svg class="w-3.5 h-3.5 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
          </svg>
          <span>{{ data.resources?.length || 0 }}</span>
        </span>
        <span v-if="!editable" class="text-[#9fef00] opacity-0 group-hover:opacity-100 transition-opacity font-bold">Details &rarr;</span>
      </div>
    </div>

    <Handle v-if="editable" type="source" :position="Position.Bottom" class="hx-flow-handle" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'

const props = defineProps({
  data: { type: Object, required: true },
  selected: { type: Boolean, default: false },
  editable: { type: Boolean, default: false },
  fullWidth: { type: Boolean, default: false }
})

defineEmits(['select', 'delete-node'])

const borderClass = computed(() => {
  if (props.data.importance === 'recommended') {
    return 'bg-[#161b22]/90 border-2 border-[#9fef00] text-slate-100 hover:border-[#00f0ff]'
  } else if (props.data.importance === 'alternative') {
    return 'bg-[#161b22]/80 border-2 border-dashed border-amber-400 text-slate-200 hover:border-amber-300'
  }
  return 'bg-[#161b22]/60 border border-slate-700 text-slate-400 hover:border-slate-500'
})

const badgeClass = computed(() => {
  if (props.data.importance === 'recommended') return 'bg-[#9fef00]/15 text-[#9fef00] border-[#9fef00]/30'
  if (props.data.importance === 'alternative') return 'bg-amber-400/15 text-amber-400 border-amber-400/30'
  return 'bg-slate-800 text-slate-400 border-slate-700'
})
</script>

<style>
.hx-flow-handle {
  width: 10px;
  height: 10px;
  background: #9fef00;
  border: 2px solid #0b0e14;
}
</style>
