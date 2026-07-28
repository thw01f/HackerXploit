<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5 text-center">

        <div v-if="loading" class="py-5">
          <div class="spinner-border text-info" role="status"></div>
          <p class="mt-2 text-muted">Verifying ID Card Credentials...</p>
        </div>

        <div v-else-if="error" class="card card-custom p-5 border-danger text-center">
          <div class="text-danger mb-3">
            <i class="bi bi-x-circle-fill display-1"></i>
          </div>
          <h4 class="fw-bold text-white mb-2">Verification Failed</h4>
          <p class="text-muted small mb-4">{{ error }}</p>
          <router-link to="/" class="btn btn-sm btn-outline-secondary">Return to Home</router-link>
        </div>

        <div v-else-if="verification" class="card card-custom p-4 border-success text-start">
          <!-- Verified Shield Badge Header -->
          <div class="d-flex align-items-center justify-content-between mb-4 border-bottom border-secondary pb-3">
            <div class="d-flex align-items-center gap-2">
              <i class="bi bi-patch-check-fill text-success fs-3"></i>
              <div>
                <div class="fw-bold text-white fs-6">VERIFIED CLUB MEMBER</div>
                <div class="extra-small text-muted font-monospace">HACKERXPLOIT OFFICIAL IDENTITY</div>
              </div>
            </div>
            <span class="badge bg-success text-dark font-monospace">VALID</span>
          </div>

          <!-- Member Details -->
          <div class="d-flex align-items-center gap-3 mb-4">
            <div class="avatar-box bg-dark border border-success rounded-circle d-flex align-items-center justify-content-center text-success fw-bold fs-2" style="width: 70px; height: 70px;">
              {{ verification.member.username.charAt(0).toUpperCase() }}
            </div>
            <div>
              <h3 class="fw-bold text-white mb-0 font-monospace text-uppercase">{{ verification.member.username }}</h3>
              <span class="badge bg-primary text-uppercase me-2">{{ verification.member.role }}</span>
              <div class="text-muted extra-small font-monospace mt-1">ID: {{ verification.member.member_id }}</div>
            </div>
          </div>

          <!-- Member Since & Status -->
          <div class="p-3 bg-dark rounded border border-secondary mb-3">
            <div class="d-flex justify-content-between text-muted extra-small font-monospace mb-2">
              <span>MEMBER SINCE:</span>
              <span class="text-white">{{ verification.member.member_since }}</span>
            </div>
            <div class="d-flex justify-content-between text-muted extra-small font-monospace">
              <span>LIVE PARTICIPATION:</span>
              <span :class="verification.live_status.is_actively_participating ? 'text-success fw-bold' : 'text-muted'">
                {{ verification.live_status.is_actively_participating ? 'ACTIVE EVENT' : 'INACTIVE' }}
              </span>
            </div>
          </div>

          <div v-if="verification.live_status.is_actively_participating" class="p-2 mb-3 bg-success bg-opacity-20 border border-success rounded text-center">
            <span class="extra-small text-success font-monospace">
              <i class="bi bi-broadcast me-1"></i> Currently in: <strong>{{ verification.live_status.active_event_name }}</strong>
            </span>
          </div>

          <div class="text-muted extra-small text-center font-monospace mt-2">
            Verified at {{ new Date(verification.verified_at).toLocaleString() }}
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const loading = ref(true)
const error = ref(null)
const verification = ref(null)

const verifyToken = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await axios.get(`/api/verify/${route.params.token}`)
    verification.value = res.data
  } catch (err) {
    error.value = err.response?.data?.error || 'Invalid or revoked ID card token.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  verifyToken()
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
</style>
