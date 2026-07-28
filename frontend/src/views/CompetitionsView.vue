<template>
  <div class="min-h-screen flex flex-col justify-between bg-slate-950 text-slate-100">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full space-y-8">
      <!-- Header & Actions -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 class="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <span>CTF & Competitions Board</span>
            <span class="text-xs font-mono uppercase bg-cyan-950/80 text-cyan-400 border border-cyan-500/30 px-2.5 py-1 rounded-full">
              Lifecycle System
            </span>
          </h1>
          <p class="text-slate-400 text-sm mt-1">
            Discover hackathons, CTFs, workshops, submit registration proof, and view team achievements.
          </p>
        </div>

        <button 
          v-if="authStore.isTeacher" 
          @click="showAnnounceModal = true" 
          class="btn-neon-violet text-sm font-semibold py-2.5 px-5 flex items-center justify-center gap-2"
        >
          <span>+ Announce Competition</span>
        </button>
      </div>

      <!-- Category Tabs -->
      <div class="flex flex-wrap gap-2 border-b border-slate-800 pb-3">
        <button 
          v-for="cat in categories" 
          :key="cat" 
          @click="activeCategory = cat; fetchCompetitions()"
          :class="[
            'px-4 py-2 text-xs font-mono font-bold uppercase rounded-lg transition-all duration-200',
            activeCategory === cat 
              ? 'bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/20' 
              : 'bg-slate-900/80 text-slate-400 hover:text-white hover:bg-slate-800'
          ]"
        >
          {{ cat }}
        </button>
      </div>

      <!-- Filter Bar -->
      <div class="glass-panel p-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label class="block text-xs font-mono text-slate-400 uppercase mb-1">Status</label>
          <select v-model="filterStatus" @change="fetchCompetitions" class="input-field text-xs py-2">
            <option value="all">All Statuses</option>
            <option value="upcoming">Upcoming</option>
            <option value="ongoing">Ongoing</option>
            <option value="ended">Ended</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-mono text-slate-400 uppercase mb-1">Priority</label>
          <select v-model="filterPriority" @change="fetchCompetitions" class="input-field text-xs py-2">
            <option value="all">All Priorities</option>
            <option value="high">High Priority</option>
            <option value="medium">Medium Priority</option>
            <option value="normal">Normal Priority</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-mono text-slate-400 uppercase mb-1">My Involvement</label>
          <select v-model="filterInvolvement" @change="fetchCompetitions" class="input-field text-xs py-2">
            <option value="all">All Involvement</option>
            <option value="applied">Applied (Any)</option>
            <option value="verified">Verified Participant</option>
            <option value="not_applied">Not Applied</option>
          </select>
        </div>
      </div>

      <!-- Competitions Grid -->
      <div v-if="loading" class="text-center py-12 text-slate-500 font-mono text-sm">
        Loading competitions...
      </div>

      <div v-else-if="competitions.length === 0" class="glass-panel p-12 text-center text-slate-400 space-y-2">
        <p class="font-bold text-base">No competitions found</p>
        <p class="text-xs text-slate-500">Try adjusting your filters or category selection.</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="comp in competitions" 
          :key="comp.id" 
          :class="[
            'glass-panel p-6 flex flex-col justify-between transition-all duration-300 hover:border-slate-700',
            getPriorityBorderClass(comp.priority)
          ]"
        >
          <div class="space-y-4">
            <!-- Poster Header Image (if exists) -->
            <div v-if="comp.poster_image" class="w-full h-40 rounded-lg overflow-hidden bg-slate-900 border border-slate-800">
              <img :src="comp.poster_image" alt="Poster" class="w-full h-full object-cover" />
            </div>

            <!-- Header Info & Badges -->
            <div class="flex justify-between items-start gap-2">
              <div>
                <span class="text-[10px] font-mono uppercase bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
                  {{ comp.category }}
                </span>
                <h3 class="text-lg font-bold text-white mt-1 leading-snug">{{ comp.title }}</h3>
              </div>

              <span :class="getPriorityBadgeClass(comp.priority)" class="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded border">
                {{ comp.priority }}
              </span>
            </div>

            <!-- Description -->
            <p class="text-slate-300 text-xs line-clamp-3 leading-relaxed">
              {{ comp.description }}
            </p>

            <!-- External Link -->
            <div v-if="comp.external_link" class="pt-1">
              <a :href="comp.external_link" target="_blank" class="text-xs text-cyan-400 hover:underline inline-flex items-center gap-1 font-mono">
                🔗 Event Page / Registration Link
              </a>
            </div>

            <!-- Dates -->
            <div class="space-y-1 text-[11px] font-mono text-slate-400 bg-slate-900/60 p-2.5 rounded border border-slate-800">
              <div class="flex justify-between">
                <span>Starts:</span>
                <span class="text-slate-200">{{ formatDate(comp.starts_at) }}</span>
              </div>
              <div class="flex justify-between">
                <span>Ends:</span>
                <span class="text-slate-200">{{ formatDate(comp.ends_at) }}</span>
              </div>
              <div v-if="comp.application_deadline" class="flex justify-between text-amber-400">
                <span>Deadline:</span>
                <span>{{ formatDate(comp.application_deadline) }}</span>
              </div>
            </div>

            <!-- User Involvement Badge -->
            <div class="flex items-center justify-between pt-1">
              <span class="text-[11px] text-slate-400 font-mono">Involvement:</span>
              <span :class="getInvolvementBadgeClass(comp.user_involvement)" class="text-[10px] font-mono uppercase px-2 py-0.5 rounded font-semibold border">
                {{ formatInvolvement(comp.user_involvement) }}
              </span>
            </div>
          </div>

          <!-- Card Actions -->
          <div class="pt-4 mt-4 border-t border-slate-800 space-y-2">
            <button 
              v-if="comp.user_involvement === 'not_applied'" 
              @click="openApplyModal(comp)" 
              class="w-full btn-neon-cyan text-xs py-2"
            >
              ✋ I'm Applying (Submit Proof)
            </button>

            <button 
              v-else 
              @click="openApplyModal(comp)" 
              class="w-full bg-slate-800 text-slate-300 hover:bg-slate-700 text-xs py-2 rounded font-mono border border-slate-700"
            >
              Update Registration Proof
            </button>

            <!-- Teacher Control Buttons -->
            <div v-if="authStore.isTeacher" class="grid grid-cols-2 gap-2 pt-1">
              <button 
                @click="openVerificationQueue(comp)" 
                class="bg-purple-950/80 hover:bg-purple-900 text-purple-300 border border-purple-600/40 text-[11px] font-mono py-1.5 rounded"
              >
                🔍 Queue
              </button>
              <button 
                @click="openWrapupModal(comp)" 
                class="bg-amber-950/80 hover:bg-amber-900 text-amber-300 border border-amber-600/40 text-[11px] font-mono py-1.5 rounded"
              >
                🏁 Wrap-up
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Modal 1: Student Application Proof -->
    <div v-if="showApplyModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="glass-panel max-w-lg w-full p-6 space-y-4">
        <h3 class="text-lg font-bold text-white">Upload Registration Proof</h3>
        <p class="text-xs text-slate-400">
          Upload a screenshot of your external registration confirmation or team ticket for <strong class="text-white">{{ selectedComp?.title }}</strong>.
        </p>

        <div class="space-y-3">
          <input type="file" @change="handleFileUpload" accept="image/*" class="input-field text-xs py-2" />
          <div v-if="uploading" class="text-xs text-cyan-400 font-mono">Uploading & scanning with ClamAV...</div>
          <div v-if="uploadedScreenshotUrl" class="w-full h-36 rounded overflow-hidden bg-slate-900 border border-slate-700">
            <img :src="uploadedScreenshotUrl" alt="Proof" class="w-full h-full object-contain" />
          </div>
        </div>

        <div class="flex justify-end gap-3 pt-2">
          <button @click="showApplyModal = false" class="text-xs text-slate-400 hover:text-white px-3 py-2 font-mono">Cancel</button>
          <button @click="submitApplicationProof" :disabled="!uploadedScreenshotUrl || submitting" class="btn-neon-cyan text-xs py-2 px-5">
            Submit Application
          </button>
        </div>
      </div>
    </div>

    <!-- Modal 2: Teacher Announce Competition -->
    <div v-if="showAnnounceModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="glass-panel max-w-xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-bold text-white">Announce New Competition</h3>
        
        <form @submit.prevent="submitAnnounce" class="space-y-4 text-xs">
          <div>
            <label class="block font-mono text-slate-400 mb-1">Title *</label>
            <input v-model="newComp.title" required class="input-field" placeholder="e.g. DEF CON CTF Quals" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block font-mono text-slate-400 mb-1">Category</label>
              <select v-model="newComp.category" class="input-field">
                <option value="ctf">CTF</option>
                <option value="hackathon">Hackathon</option>
                <option value="workshop">Workshop</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label class="block font-mono text-slate-400 mb-1">Priority</label>
              <select v-model="newComp.priority" class="input-field">
                <option value="high">High (Red)</option>
                <option value="medium">Medium (Amber)</option>
                <option value="normal">Normal (Gray)</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block font-mono text-slate-400 mb-1">Description *</label>
            <textarea v-model="newComp.description" rows="3" required class="input-field" placeholder="Overview of the competition..."></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block font-mono text-slate-400 mb-1">Starts At *</label>
              <input v-model="newComp.starts_at" type="datetime-local" required class="input-field" />
            </div>

            <div>
              <label class="block font-mono text-slate-400 mb-1">Ends At *</label>
              <input v-model="newComp.ends_at" type="datetime-local" required class="input-field" />
            </div>
          </div>

          <div>
            <label class="block font-mono text-slate-400 mb-1">Application Deadline</label>
            <input v-model="newComp.application_deadline" type="datetime-local" class="input-field" />
          </div>

          <div>
            <label class="block font-mono text-slate-400 mb-1">External Registration Link</label>
            <input v-model="newComp.external_link" type="url" class="input-field" placeholder="https://..." />
          </div>

          <div class="flex justify-end gap-3 pt-3 border-t border-slate-800">
            <button type="button" @click="showAnnounceModal = false" class="text-xs text-slate-400 hover:text-white px-3 py-2 font-mono">Cancel</button>
            <button type="submit" class="btn-neon-violet text-xs py-2 px-5">Publish Competition</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal 3: Verification Queue -->
    <div v-if="showQueueModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="glass-panel max-w-4xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <h3 class="text-lg font-bold text-white">Verification Queue: {{ selectedComp?.title }}</h3>
          <button @click="showQueueModal = false" class="text-slate-400 hover:text-white font-mono">✕</button>
        </div>

        <div v-if="queueList.length === 0" class="py-8 text-center text-slate-500 font-mono text-xs">
          No application submissions in queue.
        </div>

        <div v-else class="space-y-4">
          <div v-for="app in queueList" :key="app.id" class="p-4 bg-slate-900/90 rounded-lg border border-slate-800 grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
            <!-- Left: Applicant details -->
            <div class="space-y-2">
              <div class="flex items-center gap-2">
                <span class="font-bold text-white text-sm">{{ app.applicant_full_name }}</span>
                <span class="text-xs text-slate-400">(@{{ app.applicant_username }})</span>
              </div>
              <p class="text-xs text-slate-400 font-mono">Applied: {{ formatDate(app.applied_at) }}</p>
              <div>
                <span :class="app.application_status === 'verified' ? 'text-emerald-400' : 'text-amber-400'" class="text-xs font-mono font-bold uppercase">
                  Status: {{ app.application_status }}
                </span>
              </div>

              <div class="flex gap-2 pt-2">
                <button @click="verifyApp(app.id, 'verified')" class="btn-neon-cyan text-xs py-1 px-3">Approve</button>
                <button @click="verifyApp(app.id, 'rejected')" class="bg-red-950 hover:bg-red-900 text-red-300 border border-red-600/40 text-xs py-1 px-3 rounded font-mono">Reject</button>
              </div>
            </div>

            <!-- Right: Side-by-side Screenshot -->
            <div class="w-full h-44 bg-slate-950 rounded border border-slate-800 overflow-hidden">
              <a :href="app.application_screenshot" target="_blank" class="block w-full h-full">
                <img :src="app.application_screenshot" alt="Screenshot Proof" class="w-full h-full object-contain" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal 4: Post-Event Wrap-up -->
    <div v-if="showWrapupModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="glass-panel max-w-3xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <h3 class="text-lg font-bold text-white">Post-Event Wrap-up: {{ selectedComp?.title }}</h3>
          <button @click="showWrapupModal = false" class="text-slate-400 hover:text-white font-mono">✕</button>
        </div>

        <div class="space-y-4 text-xs">
          <div>
            <label class="block font-mono text-slate-400 mb-1">Event Summary Notes</label>
            <textarea v-model="wrapupData.summary_notes" rows="2" class="input-field" placeholder="Describe the team performance and achievements..."></textarea>
          </div>

          <h4 class="font-bold text-slate-200 border-b border-slate-800 pb-1">Verified Participants Results & Certificates</h4>

          <div v-for="(p, idx) in wrapupParticipants" :key="p.id" class="p-3 bg-slate-900 rounded border border-slate-800 space-y-2">
            <div class="flex justify-between items-center font-bold text-slate-100">
              <span>{{ p.applicant_full_name }} (@{{ p.applicant_username }})</span>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block font-mono text-slate-400 mb-1">Result</label>
                <select v-model="p.result" class="input-field text-xs py-1">
                  <option value="participated">Participated</option>
                  <option value="winner">Winner (Auto-Certificate)</option>
                  <option value="runner_up">Runner Up (Auto-Certificate)</option>
                  <option value="not_selected">Not Selected</option>
                </select>
              </div>

              <div>
                <label class="block font-mono text-slate-400 mb-1">Placement Label</label>
                <input v-model="p.placement_label" class="input-field text-xs py-1" placeholder="e.g. 1st Place / Top 5" />
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-3 border-t border-slate-800">
            <button @click="showWrapupModal = false" class="text-xs text-slate-400 hover:text-white px-3 py-2 font-mono">Cancel</button>
            <button @click="submitWrapup" class="btn-neon-violet text-xs py-2 px-5">Submit Wrap-up</button>
          </div>
        </div>
      </div>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const categories = ['All', 'CTF', 'Hackathon', 'Workshop', 'Other']
const activeCategory = ref('All')

const filterStatus = ref('all')
const filterPriority = ref('all')
const filterInvolvement = ref('all')

const competitions = ref([])
const loading = ref(false)

const showApplyModal = ref(false)
const showAnnounceModal = ref(false)
const showQueueModal = ref(false)
const showWrapupModal = ref(false)

const selectedComp = ref(null)
const uploading = ref(false)
const submitting = ref(false)
const uploadedScreenshotUrl = ref('')

const queueList = ref([])
const wrapupParticipants = ref([])
const wrapupData = ref({ summary_notes: '' })

const newComp = ref({
  title: '',
  description: '',
  category: 'ctf',
  priority: 'normal',
  starts_at: '',
  ends_at: '',
  application_deadline: '',
  external_link: ''
})

const fetchCompetitions = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/competitions', {
      params: {
        category: activeCategory.value,
        status: filterStatus.value,
        priority: filterPriority.value,
        involvement: filterInvolvement.value
      }
    })
    competitions.value = res.data.competitions || []
  } catch (err) {
    console.error('Failed to load competitions:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCompetitions()
})

const formatDate = (isoStr) => {
  if (!isoStr) return 'N/A'
  return new Date(isoStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

const getPriorityBorderClass = (priority) => {
  if (priority === 'high') return 'border-l-4 border-l-red-500'
  if (priority === 'medium') return 'border-l-4 border-l-amber-500'
  return 'border-l-4 border-l-slate-500'
}

const getPriorityBadgeClass = (priority) => {
  if (priority === 'high') return 'bg-red-950/80 text-red-400 border-red-600/40'
  if (priority === 'medium') return 'bg-amber-950/80 text-amber-400 border-amber-600/40'
  return 'bg-slate-800 text-slate-300 border-slate-700'
}

const getInvolvementBadgeClass = (status) => {
  if (status === 'verified') return 'bg-emerald-950/80 text-emerald-400 border-emerald-600/40'
  if (status === 'pending_verification') return 'bg-amber-950/80 text-amber-400 border-amber-600/40'
  if (status === 'rejected') return 'bg-red-950/80 text-red-400 border-red-600/40'
  return 'bg-slate-900 text-slate-400 border-slate-800'
}

const formatInvolvement = (status) => {
  if (status === 'pending_verification') return 'Pending Verification'
  if (status === 'verified') return 'Verified Participant'
  if (status === 'rejected') return 'Rejected'
  return 'Not Applied'
}

const openApplyModal = (comp) => {
  selectedComp.value = comp
  uploadedScreenshotUrl.value = comp.user_participation?.application_screenshot || ''
  showApplyModal.value = true
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  uploading.value = true
  const formData = new FormData()
  formData.append('file', file)
  formData.append('feature', 'competitions')

  try {
    const res = await axios.post('/api/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    uploadedScreenshotUrl.value = res.data.url
  } catch (err) {
    alert(err.response?.data?.error || "couldn't be verified as a valid file")
  } finally {
    uploading.value = false
  }
}

const submitApplicationProof = async () => {
  if (!selectedComp.value || !uploadedScreenshotUrl.value) return
  submitting.value = true

  try {
    await axios.post(`/api/competitions/${selectedComp.value.id}/apply`, {
      application_screenshot: uploadedScreenshotUrl.value
    })
    showApplyModal.value = false
    await fetchCompetitions()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to submit application')
  } finally {
    submitting.value = false
  }
}

const submitAnnounce = async () => {
  try {
    await axios.post('/api/competitions', newComp.value)
    showAnnounceModal.value = false
    newComp.value = { title: '', description: '', category: 'ctf', priority: 'normal', starts_at: '', ends_at: '', application_deadline: '', external_link: '' }
    await fetchCompetitions()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to announce competition')
  }
}

const openVerificationQueue = async (comp) => {
  selectedComp.value = comp
  try {
    const res = await axios.get(`/api/competitions/${comp.id}/applications`)
    queueList.value = res.data.applications || []
    showQueueModal.value = true
  } catch (err) {
    alert('Failed to load queue')
  }
}

const verifyApp = async (appId, status) => {
  try {
    await axios.post(`/api/competitions/${selectedComp.value.id}/applications/${appId}/verify`, { status })
    await openVerificationQueue(selectedComp.value)
    await fetchCompetitions()
  } catch (err) {
    alert('Verification update failed')
  }
}

const openWrapupModal = async (comp) => {
  selectedComp.value = comp
  try {
    const res = await axios.get(`/api/competitions/${comp.id}/applications`)
    wrapupParticipants.value = res.data.applications.map(a => ({
      participation_id: a.id,
      applicant_full_name: a.applicant_full_name,
      applicant_username: a.applicant_username,
      result: a.result || 'participated',
      placement_label: a.placement_label || ''
    }))
    wrapupData.value.summary_notes = comp.wrapup_notes || ''
    showWrapupModal.value = true
  } catch (err) {
    alert('Failed to load wrapup details')
  }
}

const submitWrapup = async () => {
  try {
    await axios.post(`/api/competitions/${selectedComp.value.id}/wrapup`, {
      summary_notes: wrapupData.value.summary_notes,
      participants: wrapupParticipants.value
    })
    showWrapupModal.value = false
    await fetchCompetitions()
  } catch (err) {
    alert('Wrap-up submission failed')
  }
}
</script>
