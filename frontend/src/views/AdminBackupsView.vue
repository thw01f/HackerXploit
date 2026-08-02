<template>
  <div class="space-y-8">
    <AdminSubNav />

    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#1f293d] pb-6">
      <div>
        <h1 class="text-3xl sm:text-4xl font-extrabold text-white font-mono tracking-tight">Backup & Restore Engine</h1>
        <p class="text-slate-400 text-base mt-1.5">System snapshots, scheduled retention, and automated database/media archive restoration.</p>
      </div>
      <button class="btn-htb text-sm font-mono font-extrabold py-3 px-6 flex items-center gap-2 shadow-lg" :disabled="creating" @click="createBackupNow">
        <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/>
        </svg>
        <span>{{ creating ? 'Creating Snapshot...' : 'Backup Now' }}</span>
      </button>
    </div>

    <!-- Main Backup Archives Table Card -->
    <div class="glass-panel p-6 sm:p-8 bg-[#111927] border border-[#1f293d] space-y-6">
      <h3 class="font-mono font-extrabold text-xl text-white uppercase border-b border-[#1f293d] pb-4">System Backup Archives</h3>

      <div v-if="loading" class="py-12 text-center font-mono text-base text-slate-400">
        Loading system backups...
      </div>

      <div v-else-if="backups.length === 0" class="py-12 text-center font-mono text-sm text-slate-400">
        No backups recorded yet. Click "Backup Now" to create your first manual system snapshot.
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left font-mono text-sm">
          <thead>
            <tr class="border-b border-[#1f293d] text-slate-300 uppercase text-xs">
              <th class="py-4 px-4">Filename</th>
              <th class="py-4 px-4">Type</th>
              <th class="py-4 px-4">Created By</th>
              <th class="py-4 px-4">Created At</th>
              <th class="py-4 px-4">Size</th>
              <th class="py-4 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[#1f293d] text-slate-200">
            <tr v-for="b in backups" :key="b.id" class="hover:bg-[#151f30] transition-colors">
              <td class="py-4 px-4 font-extrabold text-[#00f0ff] flex items-center gap-2.5">
                <svg class="w-5 h-5 text-cyan-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 012-2h10a2 2 0 012 2m-14 0v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/>
                </svg>
                <span>{{ b.filename }}</span>
              </td>
              <td class="py-4 px-4">
                <span class="px-2.5 py-1 rounded-md text-xs uppercase font-extrabold" :class="b.type === 'manual' ? 'bg-[#151f30] text-[#9fef00] border border-[#9fef00]/30' : 'bg-slate-800 text-slate-300'">
                  {{ b.type }}
                </span>
              </td>
              <td class="py-4 px-4 text-slate-200 font-bold">{{ b.created_by_username }}</td>
              <td class="py-4 px-4 text-slate-400 text-xs">{{ new Date(b.created_at).toLocaleString() }}</td>
              <td class="py-4 px-4 text-slate-400 font-bold">{{ (b.size_bytes / 1024 / 1024).toFixed(2) }} MB</td>
              <td class="py-4 px-4 text-right space-x-2.5">
                <button @click="downloadBackup(b.id)" class="btn-ghost text-xs py-1.5 px-3 font-bold border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10">
                  Download
                </button>
                <button @click="confirmRestore(b)" class="btn-ghost text-xs py-1.5 px-3 font-bold border border-amber-500/30 text-amber-400 hover:bg-amber-500/10">
                  Restore
                </button>
                <button @click="deleteBackup(b.id)" class="btn-ghost text-xs py-1.5 px-3 font-bold border border-rose-500/30 text-rose-400 hover:bg-rose-500/10">
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

      <!-- Restore Confirmation Modal -->
      <div v-if="showRestoreModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
        <div class="w-full max-w-md glass-panel p-6 rounded-xl border border-amber-500/50 bg-[#111927] space-y-4">
          <h3 class="font-mono font-bold text-lg text-amber-400 flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <span>Confirm System Restoration</span>
          </h3>
          <p class="text-xs font-mono text-slate-300 leading-relaxed">
            Restoring <strong>{{ selectedBackup?.filename }}</strong> will activate maintenance mode and overwrite current databases & uploaded files.
          </p>

          <div class="space-y-1.5">
            <label class="block text-xs font-mono text-slate-400 uppercase">Type site name "HackerXploit" to confirm:</label>
            <input type="text" v-model="siteNameConfirm" placeholder="HackerXploit" class="w-full" />
          </div>

          <div class="flex justify-end space-x-3 pt-2">
            <button @click="showRestoreModal = false" class="btn-ghost text-xs font-mono py-2 px-4">Cancel</button>
            <button :disabled="siteNameConfirm !== 'HackerXploit' || restoring" @click="executeRestore" class="btn-ghost text-xs font-mono text-amber-400 border-amber-500/50 py-2 px-4">
              {{ restoring ? 'Restoring System...' : 'Confirm & Restore System' }}
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

const loading = ref(true)
const creating = ref(false)
const backups = ref([])

const showRestoreModal = ref(false)
const selectedBackup = ref(null)
const siteNameConfirm = ref('')
const restoring = ref(false)

const fetchBackups = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/admin/backups')
    backups.value = res.data.backups
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const createBackupNow = async () => {
  creating.value = true
  try {
    await axios.post('/api/admin/backups/create', {})
    await fetchBackups()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to create backup.')
  } finally {
    creating.value = false
  }
}

const downloadBackup = (id) => {
  window.open(`/api/admin/backups/${id}/download`, '_blank')
}

const deleteBackup = async (id) => {
  if (!confirm('Are you sure you want to delete this backup archive?')) return
  try {
    await axios.delete(`/api/admin/backups/${id}`)
    await fetchBackups()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete backup.')
  }
}

const openRestoreModal = (backup) => {
  selectedBackup.value = backup
  siteNameConfirm.value = ''
  showRestoreModal.value = true
}

const executeRestore = async () => {
  restoring.value = true
  try {
    await axios.post('/api/admin/backups/restore', {
      site_name: siteNameConfirm.value,
      backup_id: selectedBackup.value.id
    })
    alert('System backup restored successfully!')
    showRestoreModal.value = false
    await fetchBackups()
  } catch (err) {
    alert(err.response?.data?.message || err.response?.data?.error || 'Restoration failed.')
  } finally {
    restoring.value = false
  }
}

onMounted(() => {
  fetchBackups()
})
</script>
