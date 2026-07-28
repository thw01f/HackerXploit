<template>
  <div class="container py-4">
    <div class="row justify-content-center">
      <div class="col-lg-6 col-md-8 text-center">

        <!-- Title & Subtitle -->
        <h2 class="fw-bold text-white mb-1"><i class="bi bi-person-badge-fill text-info me-2"></i>Virtual Cyberpunk ID Card</h2>
        <p class="text-muted mb-4">Official club credentials with live event participation status & QR verification.</p>

        <div v-if="loading" class="py-5">
          <div class="spinner-border text-info" role="status"></div>
        </div>

        <div v-else-if="cardData" class="d-flex flex-column align-items-center">

          <!-- 2D / 3D Cyberpunk Card Badge Container -->
          <div class="cyber-card-badge p-4 text-start position-relative mb-4 w-100 max-w-card" :class="{ 'pulse-active': cardData.live_status.is_active_event }">

            <!-- Lanyard Hole Clip -->
            <div class="lanyard-clip mx-auto mb-3"></div>

            <!-- Header Row -->
            <div class="d-flex align-items-center justify-content-between mb-3 border-bottom border-secondary pb-3">
              <div>
                <span class="badge bg-info text-dark fw-bold px-2 py-1">HACKERXPLOIT CLUB</span>
                <div class="extra-small text-muted font-monospace mt-1">ID: {{ cardData.user.member_id }}</div>
              </div>

              <!-- Live Status Dot Indicator -->
              <div class="d-flex align-items-center gap-2">
                <span :class="['status-dot', cardData.live_status.is_active_event ? 'dot-active' : 'dot-idle']"></span>
                <span class="extra-small font-monospace text-uppercase" :class="cardData.live_status.is_active_event ? 'text-success fw-bold' : 'text-muted'">
                  {{ cardData.live_status.is_active_event ? 'LIVE EVENT' : 'INACTIVE' }}
                </span>
              </div>
            </div>

            <!-- Main Body: Avatar, Callsign, Role -->
            <div class="d-flex align-items-center gap-3 mb-4">
              <div class="avatar-box bg-dark border border-info rounded-circle d-flex align-items-center justify-content-center text-info fw-bold fs-2" style="width: 70px; height: 70px;">
                {{ cardData.user.username.charAt(0).toUpperCase() }}
              </div>
              <div>
                <h3 class="fw-bold text-white mb-0 font-monospace text-uppercase">{{ cardData.user.username }}</h3>
                <span class="badge bg-primary text-uppercase me-2">{{ cardData.user.role }}</span>
                <div class="text-muted extra-small font-monospace mt-1">Member Since: {{ cardData.user.created_at ? new Date(cardData.user.created_at).toLocaleDateString() : 'N/A' }}</div>
              </div>
            </div>

            <!-- Active Event Indicator Banner -->
            <div v-if="cardData.live_status.is_active_event" class="p-2 mb-3 bg-success bg-opacity-20 border border-success rounded d-flex align-items-center gap-2">
              <i class="bi bi-broadcast text-success"></i>
              <span class="extra-small text-white font-monospace">ACTIVELY PARTICIPATING IN: <strong>{{ cardData.live_status.active_event_name }}</strong></span>
            </div>

            <!-- Footer Row: QR Code & Opaque Verification Link -->
            <div class="d-flex align-items-center justify-content-between pt-3 border-top border-secondary">
              <div>
                <div class="extra-small text-muted font-monospace mb-1">SCAN QR TO VERIFY</div>
                <div class="extra-small text-info font-monospace word-break-all max-w-token">
                  token: {{ cardData.token.substring(0, 16) }}...
                </div>
              </div>

              <!-- Embedded Canvas / Image QR Code -->
              <div class="bg-white p-1 rounded">
                <img :src="`https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=${encodeURIComponent(cardData.verification_url)}`" alt="QR Verification" style="width: 70px; height: 70px;" />
              </div>
            </div>
          </div>

          <!-- Controls -->
          <div class="d-flex flex-wrap gap-2 justify-content-center">
            <a :href="cardData.verification_url" target="_blank" class="btn btn-sm btn-outline-info">
              <i class="bi bi-box-arrow-up-right me-1"></i> Public Verification Link
            </a>
            <button class="btn btn-sm btn-outline-warning" :disabled="regenerating" @click="regenerateToken">
              <i class="bi bi-arrow-repeat me-1"></i> {{ regenerating ? 'Regenerating...' : 'Regenerate Token' }}
            </button>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const loading = ref(true)
const cardData = ref(null)
const regenerating = ref(false)

const getHeaders = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
})

const fetchIDCard = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/profile/id-card', getHeaders())
    cardData.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const regenerateToken = async () => {
  if (!confirm('Regenerating will invalidate your previous QR code token. Continue?')) return
  regenerating.value = true
  try {
    const res = await axios.post('/api/profile/id-card/regenerate', {}, getHeaders())
    cardData.value.token = res.data.token
    cardData.value.verification_url = res.data.verification_url
    alert('ID Card verification token regenerated successfully!')
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to regenerate token.')
  } finally {
    regenerating.value = false
  }
}

onMounted(() => {
  fetchIDCard()
})
</script>

<style scoped>
.cyber-card-badge {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  border: 2px solid #00F0FF;
  border-radius: 16px;
  box-shadow: 0 0 25px rgba(0, 240, 255, 0.25);
  backdrop-filter: blur(10px);
}
.pulse-active {
  border-color: #22c55e;
  box-shadow: 0 0 30px rgba(34, 197, 94, 0.35);
}
.lanyard-clip {
  width: 40px;
  height: 10px;
  background: #334155;
  border: 1px solid #00F0FF;
  border-radius: 4px;
}
.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}
.dot-active {
  background-color: #22c55e;
  box-shadow: 0 0 10px #22c55e;
  animation: pulse 1.5s infinite;
}
.dot-idle {
  background-color: #64748b;
}
@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
}
.max-w-card {
  max-width: 420px;
}
.extra-small {
  font-size: 0.75rem;
}
.max-w-token {
  max-width: 220px;
}
</style>
