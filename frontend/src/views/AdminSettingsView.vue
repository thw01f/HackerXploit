<template>
  <div class="space-y-8">
    <AdminSubNav />

    <div>
      <span class="px-2.5 py-1 rounded bg-purple-950 text-purple-400 font-mono text-xs font-bold uppercase">PLATFORM SECURITY & POLICY</span>
      <h1 class="text-3xl font-extrabold text-white mt-2">Registration, Security & Feature Toggles</h1>
      <p class="text-slate-400 text-sm mt-1">Configure email domain allowance, password complexity rules, and global feature toggles.</p>
    </div>

    <!-- Success Banner -->
    <div v-if="successMsg" class="p-4 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-400 text-xs font-mono flex items-center justify-between">
      <span>{{ successMsg }}</span>
      <button @click="successMsg = ''" class="text-emerald-400 hover:text-white">&times;</button>
    </div>

    <form @submit.prevent="saveSettings" class="space-y-6">
      <!-- Section 1: Registration Domain Allowance -->
      <div class="glass-panel p-6 space-y-4">
        <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3 flex items-center space-x-2">
          <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/>
          </svg>
          <span>Registration Domain Allowance</span>
        </h3>

        <div>
          <label class="block text-xs font-mono text-slate-300 uppercase mb-1">
            Allowed Email Domains (Comma-Separated)
          </label>
          <input 
            v-model="settings.allowed_email_domains" 
            type="text" 
            placeholder="gmail.com, srm.edu.in, hackerxploit.org" 
            class="w-full bg-slate-900 border border-cyan-500/40 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-cyan-500 focus:outline-none"
          />
          <p class="text-[11px] text-slate-400 mt-1 font-mono">
            Enter authorized domains separated by commas (e.g. <code>gmail.com, srm.edu.in, hackerxploit.org</code>). Use <code>*</code> to permit all domains.
          </p>
        </div>
      </div>

      <!-- Section 2: CTFd-Aligned Password Security Policy -->
      <div class="glass-panel p-6 space-y-4">
        <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3 flex items-center space-x-2">
          <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
          </svg>
          <span>CTFd Password Security Policy</span>
        </h3>

        <div>
          <label class="block text-xs font-mono text-slate-300 uppercase mb-1">
            Minimum Password Length
          </label>
          <input 
            v-model.number="settings.password_min_length" 
            type="number" 
            min="6" 
            max="64"
            class="w-full max-w-xs bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono"
          />
          <p class="text-[11px] text-slate-400 mt-1.5 font-mono">
            Aligned with CTFd security standard (minimum {{ settings.password_min_length || 8 }} characters). No forced arbitrary symbol restrictions.
          </p>
        </div>
      </div>

      <!-- Section 3: Site Feature Toggles -->
      <div class="glass-panel p-6 space-y-4">
        <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3 flex items-center gap-2">
          <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
          </svg>
          <span>Site Feature Toggles</span>
        </h3>

        <div class="p-4 bg-slate-900/80 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <h4 class="text-sm font-bold text-white">General Text Chat Channel</h4>
            <p class="text-xs text-slate-400 mt-0.5">Enable or disable real-time text chat at <code>/chat</code> site-wide.</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="settings.general_chat_enabled" class="sr-only peer">
            <div class="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-500"></div>
          </label>
        </div>
      </div>

      <div class="flex justify-end">
        <button type="submit" class="btn-neon-cyan py-2.5 px-6 text-xs font-bold font-mono uppercase tracking-wider flex items-center gap-2">
          <svg class="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
          <span>Save Policy & Security Settings</span>
        </button>
      </div>
    </form>

    <!-- Dashboard Announcements: multiple, custom label + link, independent of the form above -->
    <div class="glass-panel p-6 space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 class="text-lg font-bold text-white flex items-center gap-2">
          <svg class="w-5 h-5 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"/>
          </svg>
          <span>Dashboard Announcements</span>
        </h3>
        <button @click="openAnnouncementForm(null)" class="btn-neon-cyan text-xs py-2 px-4 font-bold flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          <span>New Announcement</span>
        </button>
      </div>
      <p class="text-[11px] text-slate-400 font-mono -mt-2">
        Shown at the top of every member's dashboard, in order. Each can be plain text or include a custom CTA button + link (e.g. "LAUNCH CTF ARENA &rarr;").
      </p>

      <div v-if="announcementsLoading" class="text-xs text-slate-500 font-mono text-center py-6">Loading announcements...</div>
      <div v-else-if="announcements.length === 0" class="text-xs text-slate-500 font-mono text-center py-6 border border-dashed border-slate-800 rounded-lg">
        No announcements yet. Create one to broadcast it on the member dashboard.
      </div>
      <div v-else class="space-y-2.5">
        <div
          v-for="(ann, idx) in announcements"
          :key="ann.id"
          class="p-4 rounded-xl border flex items-start justify-between gap-4"
          :class="ann.is_active ? 'bg-slate-900/80 border-slate-800' : 'bg-slate-900/40 border-slate-800/50 opacity-60'"
        >
          <div class="min-w-0 flex-1 space-y-1">
            <p class="text-sm text-white font-medium">{{ ann.message }}</p>
            <p v-if="ann.link && ann.button_label" class="text-[11px] font-mono text-[#9fef00] flex items-center gap-1.5">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
              <span>{{ ann.button_label }} &rarr; {{ ann.link }}</span>
            </p>
          </div>

          <div class="flex items-center gap-2 shrink-0">
            <button @click="moveAnnouncement(idx, -1)" :disabled="idx === 0" class="p-1.5 rounded-lg border border-slate-700 text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed" title="Move up">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>
            </button>
            <button @click="moveAnnouncement(idx, 1)" :disabled="idx === announcements.length - 1" class="p-1.5 rounded-lg border border-slate-700 text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed" title="Move down">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" :checked="ann.is_active" @change="toggleAnnouncementActive(ann)" class="sr-only peer">
              <div class="w-9 h-5 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#9fef00]"></div>
            </label>
            <button @click="openAnnouncementForm(ann)" class="p-1.5 rounded-lg border border-amber-600/40 text-amber-400 hover:bg-amber-950/40" title="Edit">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
            </button>
            <button @click="deleteAnnouncement(ann)" class="p-1.5 rounded-lg border border-rose-600/40 text-rose-400 hover:bg-rose-950/40" title="Delete">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Announcement Create/Edit Modal -->
    <div v-if="showAnnouncementModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div class="w-full max-w-lg glass-panel p-6 rounded-xl border border-slate-800 bg-[#111927] space-y-4">
        <h3 class="text-lg font-bold text-white">{{ announcementForm.id ? 'Edit Announcement' : 'New Announcement' }}</h3>

        <div>
          <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Message *</label>
          <textarea
            v-model="announcementForm.message"
            rows="2"
            placeholder="Next CTF competition is scheduled for Saturday."
            class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-[#9fef00] focus:outline-none"
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Button Label (optional)</label>
            <input
              v-model="announcementForm.button_label"
              type="text"
              placeholder="LAUNCH CTF ARENA"
              class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-[#9fef00] focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Link URL (optional)</label>
            <input
              v-model="announcementForm.link"
              type="url"
              placeholder="https://arena.hackerxploit.org"
              class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono focus:border-[#9fef00] focus:outline-none"
            />
          </div>
        </div>
        <p class="text-[11px] text-slate-400 font-mono">Leave both blank for a plain text banner, or fill both for a clickable CTA button.</p>

        <div class="flex items-center justify-between pt-2">
          <label class="flex items-center gap-2 text-xs font-mono text-slate-300">
            <input type="checkbox" v-model="announcementForm.is_active" class="w-4 h-4" />
            <span>Active</span>
          </label>
        </div>

        <p v-if="announcementFormError" class="text-xs text-rose-400 font-bold">{{ announcementFormError }}</p>

        <div class="flex justify-end gap-3 pt-2 border-t border-slate-800">
          <button @click="showAnnouncementModal = false" class="text-xs text-slate-400 hover:text-white px-3 py-2 font-mono">Cancel</button>
          <button @click="saveAnnouncement" class="btn-neon-cyan text-xs py-2 px-5 font-bold">
            {{ announcementForm.id ? 'Save Changes' : 'Create Announcement' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import AdminSubNav from '../components/AdminSubNav.vue'
import { useClubStore } from '../stores/club'

const clubStore = useClubStore()

const successMsg = ref('')
const settings = ref({
  general_chat_enabled: true,
  allowed_email_domains: 'gmail.com, srm.edu.in, hackerxploit.org',
  password_min_length: 8
})

const fetchSettings = async () => {
  try {
    const res = await axios.get('/api/admin/settings')
    settings.value = { ...settings.value, ...res.data }
  } catch (err) {
    console.error('Failed to load settings', err)
  }
}

const saveSettings = async () => {
  try {
    await axios.post('/api/admin/settings', settings.value)
    await clubStore.fetchStats()
    successMsg.value = 'Platform security and registration policy settings updated successfully!'
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to update settings')
  }
}

// ==================== Dashboard Announcements ====================
const announcements = ref([])
const announcementsLoading = ref(false)
const showAnnouncementModal = ref(false)
const announcementFormError = ref('')
const announcementForm = ref({ id: null, message: '', button_label: '', link: '', is_active: true })

const fetchAnnouncements = async () => {
  announcementsLoading.value = true
  try {
    const res = await axios.get('/api/admin/announcements')
    announcements.value = res.data.announcements || []
  } catch (err) {
    console.error('Failed to load announcements', err)
  } finally {
    announcementsLoading.value = false
  }
}

const openAnnouncementForm = (ann) => {
  announcementFormError.value = ''
  announcementForm.value = ann
    ? { id: ann.id, message: ann.message, button_label: ann.button_label || '', link: ann.link || '', is_active: ann.is_active }
    : { id: null, message: '', button_label: '', link: '', is_active: true }
  showAnnouncementModal.value = true
}

const saveAnnouncement = async () => {
  announcementFormError.value = ''
  if (!announcementForm.value.message.trim()) {
    announcementFormError.value = 'Message is required'
    return
  }
  const payload = {
    message: announcementForm.value.message.trim(),
    button_label: announcementForm.value.button_label.trim(),
    link: announcementForm.value.link.trim(),
    is_active: announcementForm.value.is_active
  }
  try {
    if (announcementForm.value.id) {
      await axios.put(`/api/admin/announcements/${announcementForm.value.id}`, payload)
    } else {
      await axios.post('/api/admin/announcements', payload)
    }
    showAnnouncementModal.value = false
    await fetchAnnouncements()
  } catch (err) {
    announcementFormError.value = err.response?.data?.error || 'Failed to save announcement'
  }
}

const toggleAnnouncementActive = async (ann) => {
  try {
    await axios.put(`/api/admin/announcements/${ann.id}`, { is_active: !ann.is_active })
    await fetchAnnouncements()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to update announcement')
  }
}

const deleteAnnouncement = async (ann) => {
  if (!confirm(`Delete this announcement? "${ann.message}"`)) return
  try {
    await axios.delete(`/api/admin/announcements/${ann.id}`)
    await fetchAnnouncements()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete announcement')
  }
}

const moveAnnouncement = async (idx, direction) => {
  const otherIdx = idx + direction
  if (otherIdx < 0 || otherIdx >= announcements.value.length) return
  const a = announcements.value[idx]
  const b = announcements.value[otherIdx]
  try {
    await Promise.all([
      axios.put(`/api/admin/announcements/${a.id}`, { display_order: b.display_order }),
      axios.put(`/api/admin/announcements/${b.id}`, { display_order: a.display_order })
    ])
    await fetchAnnouncements()
  } catch (err) {
    alert('Failed to reorder announcements')
  }
}

onMounted(() => {
  fetchSettings()
  fetchAnnouncements()
})
</script>
