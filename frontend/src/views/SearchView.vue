<template>
  <div class="max-w-4xl mx-auto px-4 py-8 text-slate-100">
    <div class="space-y-6 mb-8 text-center">
      <h1 class="text-3xl md:text-4xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
        Site-Wide Search
      </h1>
      <p class="text-slate-400 text-sm">Full-text PostgreSQL query engine across Academy courses, modules, and platform resources</p>

      <!-- Search Input Bar -->
      <div class="relative max-w-2xl mx-auto">
        <Search class="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
        <input 
          v-model="query" 
          @input="handleSearch"
          type="text" 
          placeholder="Search for courses, modules, topics (e.g. Memory Injection, Buffer Overflow)..." 
          class="w-full bg-slate-900 border border-slate-800 rounded-2xl pl-12 pr-4 py-4 text-slate-100 placeholder-slate-500 text-base focus:outline-none focus:border-cyan-500 shadow-xl transition-all" />
      </div>
    </div>

    <!-- Results Status -->
    <div v-if="loading" class="text-center py-12 text-slate-500 animate-pulse">
      Searching platform index...
    </div>

    <div v-else-if="searched && !results.length" class="text-center py-12 text-slate-500">
      No matching results found for "<strong class="text-slate-300">{{ query }}</strong>".
    </div>

    <!-- Results List -->
    <div v-else class="space-y-4">
      <div 
        v-for="res in results" 
        :key="res.id" 
        class="bg-slate-900/60 p-6 rounded-2xl border border-slate-800/80 hover:border-cyan-500/40 transition-all backdrop-blur-md flex items-start justify-between gap-4">
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              {{ res.type }}
            </span>
            <h2 class="text-lg font-bold text-slate-100 hover:text-cyan-300 transition-colors">
              <router-link :to="res.link">{{ res.title }}</router-link>
            </h2>
          </div>
          <p class="text-slate-400 text-sm leading-relaxed">{{ res.description }}</p>
        </div>

        <router-link 
          :to="res.link" 
          class="p-3 bg-slate-800 hover:bg-cyan-500 hover:text-slate-950 text-slate-300 rounded-xl transition-all flex-shrink-0">
          <ArrowRight class="w-5 h-5" />
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { Search, ArrowRight } from 'lucide-vue-next'

const query = ref('')
const results = ref([])
const loading = ref(false)
const searched = ref(false)
let debounceTimeout = null

const handleSearch = () => {
  if (debounceTimeout) clearTimeout(debounceTimeout)
  if (!query.value.trim()) {
    results.value = []
    searched.value = false
    return
  }

  debounceTimeout = setTimeout(async () => {
    loading.value = true
    try {
      const res = await axios.get('/api/search', { params: { q: query.value }, withCredentials: true })
      results.value = res.data.results || []
      searched.value = true
    } catch (err) {
      console.error('Search request failed:', err)
    } finally {
      loading.value = false
    }
  }, 300)
}
</script>
