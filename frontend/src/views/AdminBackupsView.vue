<template>
  <div class="container py-4">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h3 class="fw-bold text-white mb-1"><i class="bi bi-database-fill-gear text-info me-2"></i>Backup & Restore Engine</h3>
        <p class="text-muted mb-0">System snapshots, scheduled Celery Beat retention (keeps last 14), and database/media restoration.</p>
      </div>
      <button class="btn btn-cyber" :disabled="creating" @click="createBackupNow">
        <i class="bi bi-cloud-arrow-up-fill me-1"></i> {{ creating ? 'Creating Snapshot...' : 'Backup Now' }}
      </button>
    </div>

    <div class="card card-custom p-4">
      <h5 class="fw-bold text-white mb-3">System Backup Archives</h5>

      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-info" role="status"></div>
      </div>

      <div v-else-if="backups.length === 0" class="text-muted text-center py-4">
        No backups recorded yet. Click "Backup Now" to create your first manual system snapshot.
      </div>

      <div v-else class="table-responsive">
        <table class="table table-dark table-hover align-middle mb-0">
          <thead>
            <tr class="text-muted extra-small text-uppercase">
              <th>Filename</th>
              <th>Type</th>
              <th>Created By</th>
              <th>Created At</th>
              <th>Size</th>
              <th class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in backups" :key="b.id">
              <td class="fw-bold text-info fs-6">
                <i class="bi bi-file-earmark-zip me-2 text-warning"></i>{{ b.filename }}
              </td>
              <td>
                <span :class="['badge', b.type === 'manual' ? 'bg-primary' : 'bg-success']">
                  {{ b.type }}
                </span>
              </td>
              <td class="text-white">{{ b.created_by_username }}</td>
              <td class="text-muted small">{{ new Date(b.created_at).toLocaleString() }}</td>
              <td class="text-muted small">{{ (b.size_bytes / 1024 / 1024).toFixed(2) }} MB</td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-info me-2" @click="downloadBackup(b.id)">
                  <i class="bi bi-download"></i>
                </button>
                <button class="btn btn-sm btn-outline-warning me-2" @click="openRestoreModal(b)">
                  <i class="bi bi-arrow-counterclockwise"></i> Restore
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="deleteBackup(b.id)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Restore Confirmation Modal -->
    <div v-if="showRestoreModal" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
      <div class="card card-custom p-4 max-w-md w-100 border-warning">
        <h5 class="fw-bold text-warning mb-2"><i class="bi bi-exclamation-octagon-fill me-2"></i>Confirm System Restoration</h5>
        <p class="text-muted small mb-3">
          Restoring <strong>{{ selectedBackup?.filename }}</strong> will activate maintenance mode and overwrite current databases & uploaded files.
        </p>

        <div class="mb-3">
          <label class="form-label text-white extra-small fw-bold">Type site name "HackerXploit" to confirm:</label>
          <input type="text" v-model="siteNameConfirm" class="form-control bg-dark text-white border-warning" placeholder="HackerXploit">
        </div>

        <div class="d-flex justify-content-end gap-2">
          <button class="btn btn-sm btn-secondary" @click="showRestoreModal = false">Cancel</button>
          <button class="btn btn-sm btn-warning" :disabled="siteNameConfirm !== 'HackerXploit' || restoring" @click="executeRestore">
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

const loading = ref(true)
const creating = ref(false)
const backups = ref([])

const showRestoreModal = ref(false)
const selectedBackup = ref(null)
const siteNameConfirm = ref('')
const restoring = ref(false)

const getHeaders = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
})

const fetchBackups = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/admin/backups', getHeaders())
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
    await axios.post('/api/admin/backups/create', {}, getHeaders())
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
    await axios.delete(`/api/admin/backups/${id}`, getHeaders())
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
    }, getHeaders())
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

<style scoped>
.card-custom {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(0, 240, 255, 0.2);
  backdrop-filter: blur(10px);
}
.btn-cyber {
  background: #00F0FF;
  color: #0F172A;
  font-weight: 600;
}
.extra-small {
  font-size: 0.75rem;
}
.modal-backdrop-custom {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.8);
  z-index: 1050;
}
.max-w-md {
  max-width: 450px;
}
</style>
