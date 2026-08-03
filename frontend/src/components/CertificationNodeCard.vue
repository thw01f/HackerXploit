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
      <!-- Delete button (Studio only) -->
      <button
        v-if="editable"
        @click.stop="$emit('delete-node')"
        class="absolute -top-2 -right-2 z-20 w-6 h-6 rounded-full bg-rose-500 hover:bg-rose-400 text-white font-bold text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
        title="Delete certification"
      >&times;</button>

      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="text-[9px] uppercase font-extrabold px-2 py-0.5 rounded tracking-wider border" :class="badgeClass">
            {{ data.difficulty }}
          </span>
          <span v-if="data.status === 'draft'" class="text-[9px] uppercase font-extrabold px-2 py-0.5 rounded tracking-wider border bg-amber-400/15 text-amber-400 border-amber-400/30">Draft</span>
        </div>

        <h3 class="text-sm font-bold text-white group-hover:text-[#00f0ff] transition-colors leading-snug">
          {{ data.title }}
        </h3>
        <p v-if="data.provider" class="text-[10px] text-slate-500 uppercase font-bold mt-1">{{ data.provider }}</p>
      </div>

      <div class="mt-3 pt-2 border-t border-[#21262d] flex items-center justify-between text-[11px] text-slate-400">
        <span class="flex items-center space-x-1">
          <svg class="w-3.5 h-3.5 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <span>Cert</span>
        </span>
        <a
          v-if="!editable && data.exam_link"
          :href="data.exam_link"
          target="_blank"
          rel="noopener noreferrer"
          @click.stop
          class="text-[#9fef00] opacity-0 group-hover:opacity-100 transition-opacity font-bold"
        >Exam Info &rarr;</a>
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
  if (props.data.difficulty === 'Advanced') {
    return 'bg-[#161b22]/90 border-2 border-rose-400 text-slate-100 hover:border-rose-300'
  } else if (props.data.difficulty === 'Intermediate') {
    return 'bg-[#161b22]/85 border-2 border-amber-400 text-slate-100 hover:border-amber-300'
  } else if (props.data.difficulty === 'Beginner') {
    return 'bg-[#161b22]/80 border-2 border-[#00f0ff] text-slate-200 hover:border-[#00f0ff]/70'
  }
  return 'bg-[#161b22]/90 border-2 border-[#9fef00] text-slate-100 hover:border-[#9fef00]/70'
})

const badgeClass = computed(() => {
  if (props.data.difficulty === 'Advanced') return 'bg-rose-400/15 text-rose-400 border-rose-400/30'
  if (props.data.difficulty === 'Intermediate') return 'bg-amber-400/15 text-amber-400 border-amber-400/30'
  if (props.data.difficulty === 'Beginner') return 'bg-[#00f0ff]/15 text-[#00f0ff] border-[#00f0ff]/30'
  return 'bg-[#9fef00]/15 text-[#9fef00] border-[#9fef00]/30'
})
</script>
