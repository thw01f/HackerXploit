<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full space-y-8">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-3xl font-extrabold text-white">CTF & Competitions</h1>
          <p class="text-slate-400 text-sm mt-1">Collegiate competitions, hackathons, and team verification.</p>
        </div>
        <button v-if="authStore.isTeacher" @click="showCreateModal = true" class="btn-neon-violet text-xs py-2.5 px-5">
          + Create Competition
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div v-for="comp in clubStore.competitions" :key="comp.id" class="glass-panel p-6 space-y-4">
          <div class="flex justify-between items-start">
            <div>
              <span class="text-[10px] font-mono uppercase bg-purple-950 text-purple-300 px-2 py-0.5 rounded border border-purple-500/30">
                {{ comp.location }}
              </span>
              <h3 class="text-xl font-bold text-white mt-1">{{ comp.title }}</h3>
            </div>
            <span :class="comp.status === 'approved' ? 'text-emerald-400' : 'text-amber-400'" class="text-xs font-mono font-bold uppercase">
              {{ comp.status }}
            </span>
          </div>

          <p class="text-slate-300 text-sm">{{ comp.description }}</p>

          <div v-if="comp.wrapup_notes" class="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-xs text-slate-300">
            <span class="font-bold text-cyan-400 block mb-1">Post-Event Wrap-up:</span>
            {{ comp.wrapup_notes }}
          </div>

          <div class="pt-4 border-t border-slate-800 flex justify-between items-center">
            <span class="text-xs text-slate-400 font-mono">
              {{ new Date(comp.start_date).toLocaleDateString() }}
            </span>
            <button @click="handleApply(comp.id)" class="btn-neon-cyan text-xs py-1.5 px-4">
              Apply / Register
            </button>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { useAuthStore } from '../stores/auth'
import { useClubStore } from '../stores/club'

const authStore = useAuthStore()
const clubStore = useClubStore()
const showCreateModal = ref(false)

onMounted(() => {
  clubStore.fetchCompetitions()
})

const handleApply = async (compId) => {
  try {
    const res = await axios.post(`/api/competitions/${compId}/apply`)
    alert('Application submitted successfully! A teacher will verify your application.')
  } catch (err) {
    alert(err.response?.data?.error || 'Application failed')
  }
}
</script>
