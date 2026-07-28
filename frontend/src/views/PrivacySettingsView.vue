<template>
  <div class="container py-4">
    <div class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card card-custom p-4 mb-4">
          <h3 class="fw-bold text-white mb-2"><i class="bi bi-shield-lock text-info me-2"></i>Privacy & Data Settings</h3>
          <p class="text-muted">Manage your public profile visibility, download a full data export, or request account deletion.</p>

          <hr class="border-secondary my-4">

          <!-- Public Profile Toggles -->
          <h5 class="fw-bold text-white mb-3">Public Profile Settings</h5>
          <div class="d-flex flex-column gap-3 mb-4">
            <div class="form-check form-switch p-3 bg-dark rounded border border-secondary d-flex align-items-center justify-content-between">
              <label class="form-check-label text-white fw-semibold mb-0" for="isPublicSwitch">
                Make Profile Publicly Accessible
                <div class="text-muted extra-small fw-normal">Enables public portfolio view at /u/{{ currentUsername }}</div>
              </label>
              <input class="form-check-input ms-3" type="checkbox" role="switch" id="isPublicSwitch" v-model="settings.is_public" @change="saveSettings">
            </div>

            <div class="form-check form-switch p-3 bg-dark rounded border border-secondary d-flex align-items-center justify-content-between" :class="{ 'opacity-50': !settings.is_public }">
              <label class="form-check-label text-white fw-semibold mb-0" for="activitySwitch">
                Show Activity Hours on Public Profile
                <div class="text-muted extra-small fw-normal">Displays total platform lab and learning hours</div>
              </label>
              <input class="form-check-input ms-3" type="checkbox" role="switch" id="activitySwitch" v-model="settings.show_activity_hours" :disabled="!settings.is_public" @change="saveSettings">
            </div>

            <div class="form-check form-switch p-3 bg-dark rounded border border-secondary d-flex align-items-center justify-content-between" :class="{ 'opacity-50': !settings.is_public }">
              <label class="form-check-label text-white fw-semibold mb-0" for="certsSwitch">
                Show Verified Certificates
                <div class="text-muted extra-small fw-normal">Displays issued platform completion certificates</div>
              </label>
              <input class="form-check-input ms-3" type="checkbox" role="switch" id="certsSwitch" v-model="settings.show_certificates" :disabled="!settings.is_public" @change="saveSettings">
            </div>
          </div>

          <div v-if="settings.is_public" class="mb-4 p-3 bg-dark rounded border border-info d-flex align-items-center justify-content-between">
            <span class="text-info small"><i class="bi bi-link-45deg me-1"></i> Your public portfolio URL:</span>
            <router-link :to="`/u/${currentUsername}`" target="_blank" class="btn btn-sm btn-outline-info">View /u/{{ currentUsername }}</router-link>
          </div>

          <hr class="border-secondary my-4">

          <!-- One-Click Resume Export & Data Export -->
          <h5 class="fw-bold text-white mb-3">Data Exports</h5>
          <div class="row g-3 mb-4">
            <div class="col-md-6">
              <div class="p-3 bg-dark rounded border border-secondary h-100 d-flex flex-column justify-content-between">
                <div>
                  <h6 class="fw-bold text-info"><i class="bi bi-file-earmark-pdf me-2"></i>Portfolio PDF Resume</h6>
                  <p class="text-muted extra-small">Export a formatted 2-page PDF summary of your courses, certificates, and competition awards.</p>
                </div>
                <button class="btn btn-sm btn-cyber w-100 mt-2" @click="downloadPortfolioPDF">
                  <i class="bi bi-download me-1"></i> Export PDF Resume
                </button>
              </div>
            </div>

            <div class="col-md-6">
              <div class="p-3 bg-dark rounded border border-secondary h-100 d-flex flex-column justify-content-between">
                <div>
                  <h6 class="fw-bold text-success"><i class="bi bi-file-earmark-zip me-2"></i>Full Account Archive (.zip)</h6>
                  <p class="text-muted extra-small">Download a complete zip archive containing your profile JSON, activity logs, and PDF certificates.</p>
                </div>
                <button class="btn btn-sm btn-outline-success w-100 mt-2" @click="downloadDataExport">
                  <i class="bi bi-download me-1"></i> Export My Data (.zip)
                </button>
              </div>
            </div>
          </div>

          <hr class="border-secondary my-4">

          <!-- Account Deletion Request -->
          <h5 class="fw-bold text-white mb-2 text-danger">Danger Zone</h5>
          <div class="p-3 bg-dark rounded border border-danger">
            <h6 class="fw-bold text-danger">Request Account Deletion</h6>
            <p class="text-muted extra-small mb-3">Account deletion requests are queued for administrative review to preserve system certificate verification and CTFd shadow user integrity.</p>
            <button class="btn btn-sm btn-outline-danger" @click="showDeleteModal = true">
              Request Account Deletion
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Deletion Modal -->
    <div v-if="showDeleteModal" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
      <div class="card card-custom p-4 max-w-md w-100 border-danger">
        <h5 class="fw-bold text-danger mb-2"><i class="bi bi-exclamation-triangle-fill me-2"></i>Request Account Deletion</h5>
        <p class="text-muted small">Please tell us why you wish to request account deletion. An administrator will review your request shortly.</p>
        <textarea v-model="deleteReason" class="form-control bg-dark text-white border-secondary mb-3" rows="3" placeholder="Reason for deletion request..."></textarea>
        <div class="d-flex justify-content-end gap-2">
          <button class="btn btn-sm btn-secondary" @click="showDeleteModal = false">Cancel</button>
          <button class="btn btn-sm btn-danger" :disabled="submittingDelete" @click="submitDeleteRequest">
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
    const res = await axios.get('/api/profile/privacy', {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    settings.value = res.data
  } catch (err) {
    console.error(err)
  }
}

const saveSettings = async () => {
  try {
    const res = await axios.post('/api/profile/privacy', settings.value, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
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
    await axios.post('/api/profile/request-deletion', { reason: deleteReason.value }, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
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

<style scoped>
.card-custom {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(0, 240, 255, 0.2);
  backdrop-filter: blur(10px);
}
.extra-small {
  font-size: 0.75rem;
}
.btn-cyber {
  background: #00F0FF;
  color: #0F172A;
  font-weight: 600;
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
