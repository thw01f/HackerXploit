<template>
  <div class="space-y-8">
      
      <!-- Top Title -->
      <div class="border-b border-[#1f293d] pb-6">
        <h1 class="text-3xl font-extrabold text-white font-mono">Privacy & Data Governance</h1>
        <p class="text-slate-400 text-sm mt-1">Manage public profile visibility, download full data archives, or request account deletion.</p>
      </div>

      <!-- Main Panel Card -->
      <div class="glass-panel p-8 bg-[#111927] border border-[#1f293d] space-y-8">
        
        <!-- Public Profile Toggles -->
        <div class="space-y-4">
          <h3 class="font-mono font-bold text-base text-white uppercase border-b border-[#1f293d] pb-3">Public Profile Settings</h3>
          
          <div class="space-y-3">
            
            <div class="p-4 rounded-xl bg-[#090d16] border border-[#1f293d] flex items-center justify-between">
              <div>
                <h4 class="font-mono font-bold text-sm text-white">Make Profile Publicly Accessible</h4>
                <p class="text-xs text-slate-400 font-mono mt-0.5">Enables public portfolio view at /u/{{ currentUsername }}</p>
              </div>
              <input type="checkbox" v-model="settings.is_public" @change="saveSettings" class="w-5 h-5 text-[#9fef00] bg-slate-900 border-slate-700 rounded focus:ring-0 cursor-pointer" />
            </div>

            <div class="p-4 rounded-xl bg-[#090d16] border border-[#1f293d] flex items-center justify-between" :class="{ 'opacity-50 pointer-events-none': !settings.is_public }">
              <div>
                <h4 class="font-mono font-bold text-sm text-white">Show Activity Hours on Public Profile</h4>
                <p class="text-xs text-slate-400 font-mono mt-0.5">Displays total platform lab and learning hours</p>
              </div>
              <input type="checkbox" v-model="settings.show_activity_hours" :disabled="!settings.is_public" @change="saveSettings" class="w-5 h-5 text-[#9fef00] bg-slate-900 border-slate-700 rounded focus:ring-0 cursor-pointer" />
            </div>

            <div class="p-4 rounded-xl bg-[#090d16] border border-[#1f293d] flex items-center justify-between" :class="{ 'opacity-50 pointer-events-none': !settings.is_public }">
              <div>
                <h4 class="font-mono font-bold text-sm text-white">Show Verified Certificates</h4>
                <p class="text-xs text-slate-400 font-mono mt-0.5">Displays issued platform completion certificates</p>
              </div>
              <input type="checkbox" v-model="settings.show_certificates" :disabled="!settings.is_public" @change="saveSettings" class="w-5 h-5 text-[#9fef00] bg-slate-900 border-slate-700 rounded focus:ring-0 cursor-pointer" />
            </div>

          </div>

          <div v-if="settings.is_public" class="p-4 rounded-xl bg-[#151f30] border border-[#00f0ff]/40 flex items-center justify-between text-xs font-mono">
            <span class="text-[#00f0ff]">🔗 Your public portfolio URL:</span>
            <router-link :to="`/u/${currentUsername}`" target="_blank" class="btn-ghost text-xs py-1.5 px-3 text-[#00f0ff] border-[#00f0ff]/40">
              View /u/{{ currentUsername }} &rarr;
            </router-link>
          </div>
        </div>

        <!-- Data Exports -->
        <div class="space-y-4 pt-6 border-t border-[#1f293d]">
          <h3 class="font-mono font-bold text-base text-white uppercase border-b border-[#1f293d] pb-3">Data Exports</h3>
          
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="p-5 rounded-xl bg-[#090d16] border border-[#1f293d] flex flex-col justify-between space-y-4">
              <div>
                <h4 class="font-mono font-bold text-sm text-[#00f0ff]">📄 Portfolio PDF Resume</h4>
                <p class="text-xs text-slate-400 mt-1 leading-relaxed">Export a formatted 2-page PDF summary of your courses, certificates, and competition awards.</p>
              </div>
              <button @click="downloadPortfolioPDF" class="btn-htb text-xs font-mono py-2 px-4 w-full">
                📥 Export PDF Resume
              </button>
            </div>

            <div class="p-5 rounded-xl bg-[#090d16] border border-[#1f293d] flex flex-col justify-between space-y-4">
              <div>
                <h4 class="font-mono font-bold text-sm text-[#9fef00]">📦 Full Account Archive (.zip)</h4>
                <p class="text-xs text-slate-400 mt-1 leading-relaxed">Download a complete zip archive containing your profile JSON, activity logs, and PDF certificates.</p>
              </div>
              <button @click="downloadDataExport" class="btn-ghost text-xs font-mono text-[#9fef00] border-[#9fef00]/40 py-2 px-4 w-full">
                📥 Export My Data (.zip)
              </button>
            </div>
          </div>
        </div>

        <!-- Danger Zone -->
        <div class="space-y-4 pt-6 border-t border-[#1f293d]">
          <h3 class="font-mono font-bold text-base text-red-400 uppercase border-b border-[#1f293d] pb-3">Danger Zone</h3>
          
          <div class="p-5 rounded-xl bg-red-950/30 border border-red-500/40 space-y-3">
            <h4 class="font-mono font-bold text-sm text-red-400">Request Account Deletion</h4>
            <p class="text-xs text-slate-400 leading-relaxed">Account deletion requests are queued for administrative review to preserve system certificate verification and CTFd shadow user integrity.</p>
            <button @click="showDeleteModal = true" class="btn-ghost text-xs font-mono text-red-400 border-red-500/50 hover:bg-red-950/60 py-2 px-4">
              Request Account Deletion
            </button>
          </div>
        </div>

      </div>

      <!-- Deletion Request Modal -->
      <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
        <div class="w-full max-w-md glass-panel p-6 rounded-xl border border-red-500/40 bg-[#111927] space-y-4">
          <h3 class="font-mono font-bold text-lg text-red-400">🚨 Request Account Deletion</h3>
          <p class="text-xs font-mono text-slate-300">Please tell us why you wish to request account deletion. An administrator will review your request shortly.</p>
          <textarea v-model="deleteReason" rows="3" placeholder="Reason for deletion request..." class="w-full"></textarea>
          <div class="flex justify-end space-x-3 pt-2">
            <button @click="showDeleteModal = false" class="btn-ghost text-xs font-mono py-2 px-4">Cancel</button>
            <button :disabled="submittingDelete" @click="submitDeleteRequest" class="btn-ghost text-xs font-mono text-red-400 border-red-500/50 py-2 px-4">
              {{ submittingDelete ? 'Submitting...' : 'Submit Request' }}
            </button>
          </div>
        </div>
      </div>


  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const settings = ref({
  is_public: false,
  show_activity_hours: true,
  show_certificates: true
})

const currentUsername = ref(localStorage.getItem('username') || 'user')
const showDeleteModal = ref(false)
const deleteReason = ref('')
const submittingDelete = ref(false)

const fetchPrivacy = async () => {
  try {
    const res = await axios.get('/api/profile/privacy')
    settings.value = res.data
  } catch (err) {
    console.error(err)
  }
}

const saveSettings = async () => {
  try {
    const res = await axios.post('/api/profile/privacy', settings.value)
    settings.value = res.data
  } catch (err) {
    console.error(err)
  }
}

const downloadPortfolioPDF = () => {
  window.open('/api/portfolio/export-pdf', '_blank')
}

const downloadDataExport = () => {
  window.open('/api/profile/export-my-data', '_blank')
}

const submitDeleteRequest = async () => {
  submittingDelete.value = true
  try {
    await axios.post('/api/profile/request-deletion', { reason: deleteReason.value })
    alert('Your account deletion request has been submitted for administrator review.')
    showDeleteModal.value = false
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to submit deletion request.')
  } finally {
    submittingDelete.value = false
  }
}

onMounted(() => {
  fetchPrivacy()
})
</script>
