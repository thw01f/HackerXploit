<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full space-y-8">
      <div>
        <h1 class="text-3xl font-extrabold text-white">Opportunities Board</h1>
        <p class="text-slate-400 text-sm mt-1">Exclusive cybersecurity internships, research roles, and CTF team openings.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div v-for="opp in clubStore.opportunities" :key="opp.id" class="glass-panel p-6 space-y-4">
          <div class="flex justify-between items-start">
            <div>
              <span class="text-[10px] font-mono uppercase bg-teal-950 text-teal-300 px-2 py-0.5 rounded border border-teal-500/30">
                {{ opp.type }}
              </span>
              <h3 class="text-xl font-bold text-white mt-1">{{ opp.title }}</h3>
              <p class="text-xs text-cyan-400 font-mono">{{ opp.organization }} • {{ opp.location }}</p>
            </div>
          </div>

          <p class="text-slate-300 text-sm line-clamp-3">{{ opp.description }}</p>

          <div class="pt-4 border-t border-slate-800 flex justify-between items-center">
            <span class="text-xs text-slate-400 font-mono">Posted by Faculty/Admin</span>
            <button @click="handleApply(opp.id)" class="btn-neon-cyan text-xs py-1.5 px-4">
              Apply Now
            </button>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { useClubStore } from '../stores/club'

const clubStore = useClubStore()

onMounted(() => {
  clubStore.fetchOpportunities()
})

const handleApply = async (oppId) => {
  const coverLetter = prompt('Enter your brief cover letter or statement of interest:')
  if (coverLetter === null) return
  try {
    await axios.post(`/api/opportunities/${oppId}/apply`, { cover_letter: coverLetter })
    alert('Application submitted successfully!')
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to submit application')
  }
}
</script>
