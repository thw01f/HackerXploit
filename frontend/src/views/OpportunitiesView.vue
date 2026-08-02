<template>
  <div class="space-y-8">
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 class="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <span>Opportunities Board</span>
            <span class="text-xs font-mono uppercase bg-teal-950/80 text-teal-400 border border-teal-500/30 px-2.5 py-1 rounded-full">
              Skill Matching
            </span>
          </h1>
          <p class="text-slate-400 text-sm mt-1">
            Exclusive cybersecurity internships, jobs, research roles, and CTF team recruitment postings.
          </p>
        </div>

        <div class="flex items-center gap-3">
          <button 
            @click="openMySkillsModal" 
            class="bg-slate-900 hover:bg-slate-800 text-cyan-400 border border-cyan-500/30 text-xs font-mono py-2.5 px-4 rounded-lg flex items-center gap-2"
          >
            Manage My Skills Profile
          </button>

          <button 
            v-if="authStore.isTeacher" 
            @click="showPostModal = true" 
            class="btn-neon-violet text-xs font-semibold py-2.5 px-5"
          >
            + Post Opportunity
          </button>
        </div>
      </div>

      <!-- Filter Bar -->
      <div class="glass-panel p-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label class="block text-xs font-mono text-slate-400 uppercase mb-1">Opportunity Type</label>
          <select v-model="filterType" @change="fetchOpportunities" class="input-field text-xs py-2">
            <option value="all">All Types</option>
            <option value="internship">Internship</option>
            <option value="job">Full-time Job</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-mono text-slate-400 uppercase mb-1">Skill Filter</label>
          <select v-model="filterMatchedOnly" @change="fetchOpportunities" class="input-field text-xs py-2">
            <option value="all">All Opportunities</option>
            <option value="matched">Matched My Skills Only</option>
          </select>
        </div>

        <div class="flex items-end pb-1">
          <label class="flex items-center gap-2 text-xs font-mono text-slate-300 cursor-pointer">
            <input type="checkbox" v-model="includeExpired" @change="fetchOpportunities" class="rounded border-slate-700 bg-slate-900 text-cyan-500" />
            <span>Show Expired Positions</span>
          </label>
        </div>
      </div>

      <!-- Opportunities Grid -->
      <div v-if="loading" class="text-center py-12 text-slate-500 font-mono text-sm">
        Loading opportunities...
      </div>

      <div v-else-if="filteredOpportunities.length === 0" class="glass-panel p-12 text-center text-slate-400 space-y-2">
        <p class="font-bold text-base">No opportunities found</p>
        <p class="text-xs text-slate-500">Try adjusting your type or skill filter settings.</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div 
          v-for="opp in filteredOpportunities" 
          :key="opp.id" 
          class="glass-panel p-6 flex flex-col justify-between space-y-4 hover:border-slate-700 transition-all duration-200"
        >
          <div class="space-y-3">
            <!-- Header Badges -->
            <div class="flex justify-between items-start">
              <div>
                <span class="text-[10px] font-mono uppercase bg-teal-950/80 text-teal-300 px-2 py-0.5 rounded border border-teal-500/30">
                  {{ opp.type }}
                </span>
                <h3 class="text-xl font-bold text-white mt-1 leading-snug">{{ opp.title }}</h3>
                <p class="text-xs text-cyan-400 font-mono font-semibold">{{ opp.company }} • {{ opp.location }}</p>
              </div>

              <!-- Skill Match Badge -->
              <span 
                :class="opp.matched_skills_count > 0 ? 'bg-emerald-950 text-emerald-300 border-emerald-500/40' : 'bg-slate-900 text-slate-400 border-slate-800'"
                class="text-[10px] font-mono font-bold px-2.5 py-1 rounded-full border flex items-center gap-1.5"
              >
                <span>{{ opp.matched_skills_count }} of {{ opp.total_skills_count }} skills match</span>
              </span>
            </div>

            <!-- Description -->
            <p class="text-slate-300 text-xs line-clamp-3 leading-relaxed">{{ opp.description }}</p>

            <!-- Required Skills List Tags -->
            <div v-if="opp.skills && opp.skills.length > 0" class="flex flex-wrap gap-1.5 pt-1">
              <span 
                v-for="s in opp.skills" 
                :key="s.id" 
                :class="userSkillIds.includes(s.id) ? 'bg-cyan-950/80 text-cyan-300 border-cyan-500/50 font-bold' : 'bg-slate-900 text-slate-400 border-slate-800'"
                class="text-[10px] font-mono px-2 py-0.5 rounded border"
              >
                {{ s.name }}
              </span>
            </div>

            <!-- Deadline: same boxed grid style as the Competitions date block,
                 for visual consistency between the two card types. -->
            <div class="text-xs bg-[#080c14] rounded-xl border border-[#1f293d]/80 font-mono overflow-hidden">
              <div class="grid grid-cols-[auto_1fr] items-center gap-x-3 p-3">
                <span class="text-slate-500 flex items-center gap-1.5 whitespace-nowrap">
                  <svg class="w-4 h-4 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  Deadline
                </span>
                <span :class="isExpired(opp.deadline) ? 'text-red-400' : 'text-amber-400'" class="font-semibold text-right tabular-nums">
                  {{ formatDate(opp.deadline) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Apply Action -->
          <div class="pt-4 border-t border-slate-800 flex justify-between items-center gap-3">
            <span class="text-xs text-slate-500 font-mono">Posted by Faculty/Admin</span>

            <a
              v-if="opp.apply_link"
              :href="opp.apply_link"
              target="_blank"
              class="btn-neon-cyan text-xs py-1.5 px-4 inline-flex items-center gap-1 shrink-0"
            >
              Apply via Link ↗
            </a>

            <button
              v-else
              @click="handleApplyInternal(opp.id)"
              class="btn-neon-cyan text-xs py-1.5 px-4 shrink-0"
            >
              Submit Application
            </button>
          </div>
        </div>
      </div>

    <!-- Modal 1: Manage User Skills -->
    <div v-if="showSkillsModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="glass-panel max-w-lg w-full p-6 space-y-4">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <h3 class="text-lg font-bold text-white">Select Your Technical Skills</h3>
          <button @click="showSkillsModal = false" class="text-slate-400 hover:text-white font-mono">✕</button>
        </div>

        <p class="text-xs text-slate-400">
          Select all skills you possess. Opportunities will automatically highlight match counts for your profile.
        </p>

        <div class="flex flex-wrap gap-2 max-h-60 overflow-y-auto p-2 bg-slate-900/80 rounded border border-slate-800">
          <button 
            v-for="s in masterSkills" 
            :key="s.id" 
            @click="toggleUserSkill(s.id)"
            :class="[
              'text-xs font-mono px-3 py-1.5 rounded-lg border transition-all duration-150',
              selectedUserSkillIds.includes(s.id) 
                ? 'bg-cyan-500 text-slate-950 border-cyan-400 font-bold' 
                : 'bg-slate-950 text-slate-300 border-slate-800 hover:border-slate-700'
            ]"
          >
            {{ selectedUserSkillIds.includes(s.id) ? '✓ ' : '+ ' }}{{ s.name }}
          </button>
        </div>

        <div class="flex justify-end gap-3 pt-3 border-t border-slate-800">
          <button @click="showSkillsModal = false" class="text-xs text-slate-400 hover:text-white px-3 py-2 font-mono">Cancel</button>
          <button @click="saveUserSkills" class="btn-neon-cyan text-xs py-2 px-5">Save Skills Profile</button>
        </div>
      </div>
    </div>

    <!-- Modal 2: Post Opportunity (Teacher/Admin) -->
    <div v-if="showPostModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="glass-panel max-w-xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-bold text-white">Post New Opportunity</h3>

        <form @submit.prevent="submitPost" class="space-y-4 text-xs">
          <div>
            <label class="block font-mono text-slate-400 mb-1">Title *</label>
            <input v-model="newOpp.title" required class="input-field" placeholder="e.g. Offensive Security Intern" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block font-mono text-slate-400 mb-1">Company / Organization *</label>
              <input v-model="newOpp.company" required class="input-field" placeholder="e.g. CrowdStrike" />
            </div>

            <div>
              <label class="block font-mono text-slate-400 mb-1">Type</label>
              <select v-model="newOpp.type" class="input-field">
                <option value="internship">Internship</option>
                <option value="job">Full-time Job</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block font-mono text-slate-400 mb-1">Description *</label>
            <textarea v-model="newOpp.description" rows="3" required class="input-field" placeholder="Job description and prerequisites..."></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block font-mono text-slate-400 mb-1">Application Deadline</label>
              <input v-model="newOpp.deadline" type="datetime-local" class="input-field" />
            </div>

            <div>
              <label class="block font-mono text-slate-400 mb-1">Application Link (Optional)</label>
              <input v-model="newOpp.apply_link" type="url" class="input-field" placeholder="https://..." />
            </div>
          </div>

          <div>
            <label class="block font-mono text-slate-400 mb-1">Required Skills (Select multiple)</label>
            <div class="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto p-2 bg-slate-900 rounded border border-slate-800">
              <button 
                type="button"
                v-for="s in masterSkills" 
                :key="s.id" 
                @click="toggleNewOppSkill(s.id)"
                :class="newOppSkillIds.includes(s.id) ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-slate-950 text-slate-400 border border-slate-800'"
                class="text-[10px] font-mono px-2 py-1 rounded"
              >
                {{ s.name }}
              </button>
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-3 border-t border-slate-800">
            <button type="button" @click="showPostModal = false" class="text-xs text-slate-400 hover:text-white px-3 py-2 font-mono">Cancel</button>
            <button type="submit" class="btn-neon-violet text-xs py-2 px-5">Publish Opportunity</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const opportunities = ref([])
const masterSkills = ref([])
const userSkillIds = ref([])

const filterType = ref('all')
const filterMatchedOnly = ref('all')
const includeExpired = ref(false)
const loading = ref(false)

const showSkillsModal = ref(false)
const showPostModal = ref(false)
const selectedUserSkillIds = ref([])

const newOppSkillIds = ref([])
const newOpp = ref({
  title: '',
  company: '',
  type: 'internship',
  description: '',
  deadline: '',
  apply_link: ''
})

const fetchOpportunities = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/opportunities', {
      params: {
        type: filterType.value,
        include_expired: includeExpired.value
      }
    })
    opportunities.value = res.data.opportunities || []
  } catch (err) {
    console.error('Failed to load opportunities:', err)
  } finally {
    loading.value = false
  }
}

const fetchSkills = async () => {
  try {
    const resMaster = await axios.get('/api/opportunities/skills')
    masterSkills.value = resMaster.data.skills || []

    const resUser = await axios.get('/api/opportunities/user/skills')
    userSkillIds.value = (resUser.data.skills || []).map(s => s.id)
  } catch (err) {
    console.error('Failed to load skills:', err)
  }
}

onMounted(async () => {
  await fetchSkills()
  await fetchOpportunities()
})

const filteredOpportunities = computed(() => {
  if (filterMatchedOnly.value === 'matched') {
    return opportunities.value.filter(o => o.matched_skills_count > 0)
  }
  return opportunities.value
})

const formatDate = (isoStr) => {
  if (!isoStr) return 'No Deadline'
  return new Date(isoStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

const isExpired = (isoStr) => {
  if (!isoStr) return false
  return new Date(isoStr) < new Date()
}

const openMySkillsModal = () => {
  selectedUserSkillIds.value = [...userSkillIds.value]
  showSkillsModal.value = true
}

const toggleUserSkill = (skillId) => {
  const idx = selectedUserSkillIds.value.indexOf(skillId)
  if (idx > -1) {
    selectedUserSkillIds.value.splice(idx, 1)
  } else {
    selectedUserSkillIds.value.push(skillId)
  }
}

const saveUserSkills = async () => {
  try {
    await axios.post('/api/opportunities/user/skills', { skill_ids: selectedUserSkillIds.value })
    userSkillIds.value = [...selectedUserSkillIds.value]
    showSkillsModal.value = false
    await fetchOpportunities()
  } catch (err) {
    alert('Failed to save skills profile')
  }
}

const toggleNewOppSkill = (skillId) => {
  const idx = newOppSkillIds.value.indexOf(skillId)
  if (idx > -1) {
    newOppSkillIds.value.splice(idx, 1)
  } else {
    newOppSkillIds.value.push(skillId)
  }
}

const submitPost = async () => {
  try {
    await axios.post('/api/opportunities', {
      ...newOpp.value,
      skill_ids: newOppSkillIds.value
    })
    showPostModal.value = false
    newOpp.value = { title: '', company: '', type: 'internship', description: '', deadline: '', apply_link: '' }
    newOppSkillIds.value = []
    await fetchOpportunities()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to post opportunity')
  }
}

const handleApplyInternal = async (oppId) => {
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
