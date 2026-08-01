<template>
  <div class="w-full h-screen bg-[#0b0e14]">
    <InteractiveRoadmapGraph :roadmapSlug="slug" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import InteractiveRoadmapGraph from '../components/InteractiveRoadmapGraph.vue'

const route = useRoute()
const slug = computed(() => route.params.slug || 'cyber-security')
</script>
