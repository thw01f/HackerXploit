<template>
  <div class="space-y-8">
    <AdminSubNav />

    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#1f293d] pb-6">
      <div>
        <h1 class="text-3xl font-extrabold text-white font-mono">Backup & Restore Engine</h1>
        <p class="text-slate-400 text-sm mt-1">System snapshots, scheduled Celery Beat retention (keeps last 14), and database/media restoration.</p>
      </div>
      <button class="btn-htb text-xs font-mono py-2.5 px-5" :disabled="creating" @click="createBackupNow">
        ⚡ {{ creating ? 'Creating Snapshot...' : 'Backup Now' }}
      </button>
    </div>

      <!-- Main Backup Archives Table Card -->
      <div class="glass-panel p-6 bg-[#111927] border border-[#1f293d] space-y-4">
        <h3 class="font-mono font-bold text-base text-white uppercase border-b border-[#1f293d] pb-3">System Backup Archives</h3>

        <div v-if="loading" class="py-12 text-center font-mono text-sm text-slate-500">
          Loading system backups...
        </div>

        <div v-else-if="backups.length === 0" class="py-12 text-center font-mono text-xs text-slate-400">
          No backups recorded yet. Click "Backup Now" to create your first manual system snapshot.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left font-mono text-xs">
            <thead>
              <tr class="border-b border-[#1f293d] text-slate-400 uppercase text-[10px]">
                <th class="py-3 px-4">Filename</th>
                <th class="py-3 px-4">Type</th>
                <th class="py-3 px-4">Created By</th>
                <th class="py-3 px-4">Created At</th>
                <th class="py-3 px-4">Size</th>
                <th class="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#1f293d]">
              <tr v-for="b in backups" :key="b.id" class="hover:bg-[#151f30] transition-colors">
                <td class="py-3 px-4 font-bold text-[#00f0ff]">
                  📦 {{ b.filename }}
                </td>
                <td class="py-3 px-4">
                  <span class="px-2 py-0.5 rounded text-[10px] uppercase font-bold" :class="b.type === 'manual' ? 'bg-[#151f30] text-[#9fef00] border border-[#9fef00]/30' : 'bg-slate-800 text-slate-300'">
                    {{ b.type }}
                  </span>
                </td>
                <td class="py-3 px-4 text-slate-200">{{ b.created_by_username }}</td>
                <td class="py-3 px-4 text-slate-400">{{ new Date(b.created_at).toLocaleString() }}</td>
                <td class="py-3 px-4 text-slate-400">{{ (b.size_bytes / 1024 / 1024).toFixed(2) }} MB</td>
                <td class="py-3 px-4 text-right space-x-2">
                  <button @click="downloadBackup(b.id)" class="btn-ghost text-[11px] py-1 px-3">
                    📥 Download
                  </button>
                  <button @click="openRestoreModal(b)" class="btn-ghost text-[11px] py-1 px-3 text-amber-400 border-amber-400/40">
                    🔄 Restore
                  </button>
                  <button @click="deleteBackup(b.id)" class="btn-ghost text-[11px] py-1 px-3 text-red-400 border-red-500/40">
                    🗑️ Delete
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
          <h3 class="font-mono font-bold text-lg text-amber-400">⚠️ Confirm System Restoration</h3>
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
    alert(err.response?.data?.error || 'Restoration failed.')
  } finally {
    restoring.value = false
  }
}

onMounted(() => {
  fetchBackups()
})
</script>
