<template>
  <div class="container py-4">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-info" role="status"></div>
      <p class="mt-2 text-muted">Loading member portfolio...</p>
    </div>

    <div v-else-if="error" class="card card-custom p-5 text-center">
      <div class="mb-3 text-warning">
        <i class="bi bi-shield-lock display-1"></i>
      </div>
      <h3 class="fw-bold text-white">Private Profile</h3>
      <p class="text-muted fs-5 mb-4">{{ error }}</p>
      <div>
        <router-link to="/" class="btn btn-cyber">Return to Home</router-link>
      </div>
    </div>

    <div v-else-if="profile" class="row g-4">
      <!-- Member Header Banner -->
      <div class="col-12">
        <div class="card card-custom p-4 border-info">
          <div class="d-flex align-items-center flex-wrap gap-4">
            <div class="avatar-box bg-dark border border-info rounded-circle d-flex align-items-center justify-content-center text-info fw-bold fs-2" style="width: 80px; height: 80px;">
              {{ profile.user.username.charAt(0).toUpperCase() }}
            </div>
            <div>
              <div class="d-flex align-items-center gap-2">
                <h2 class="fw-bold text-white mb-0">{{ profile.user.username }}</h2>
                <span class="badge bg-primary text-uppercase">{{ profile.user.role }}</span>
              </div>
              <p class="text-muted mb-0 mt-1">
                <i class="bi bi-calendar3 me-1"></i> Member Since {{ profile.user.created_at ? new Date(profile.user.created_at).toLocaleDateString() : 'N/A' }}
              </p>
            </div>

            <div class="ms-auto d-flex gap-3">
              <div class="text-center px-3 py-2 bg-dark rounded border border-secondary">
                <div class="fs-4 fw-bold text-info">{{ profile.stats.total_courses_completed }}</div>
                <div class="text-muted extra-small">COURSES</div>
              </div>
              <div v-if="profile.stats.total_certificates !== null" class="text-center px-3 py-2 bg-dark rounded border border-secondary">
                <div class="fs-4 fw-bold text-warning">{{ profile.stats.total_certificates }}</div>
                <div class="text-muted extra-small">CERTS</div>
              </div>
              <div v-if="profile.stats.total_activity_hours !== null" class="text-center px-3 py-2 bg-dark rounded border border-secondary">
                <div class="fs-4 fw-bold text-success">{{ profile.stats.total_activity_hours }}h</div>
                <div class="text-muted extra-small">LAB TIME</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Left Column: Courses & Certificates -->
      <div class="col-md-7">
        <div class="card card-custom p-4 mb-4">
          <h5 class="fw-bold text-white mb-3"><i class="bi bi-journal-code text-info me-2"></i>Completed Curriculum</h5>
          <div v-if="profile.completed_courses.length === 0" class="text-muted small italic">No completed courses yet.</div>
          <div v-else class="list-group list-group-flush bg-transparent">
            <div v-for="course in profile.completed_courses" :key="course.id" class="list-group-item bg-transparent text-white px-0 py-3 border-secondary">
              <div class="fw-bold text-info fs-6">{{ course.title }}</div>
              <p class="text-muted small mb-0 mt-1">{{ course.description }}</p>
            </div>
          </div>
        </div>

        <div v-if="profile.certificates && profile.certificates.length > 0" class="card card-custom p-4">
          <h5 class="fw-bold text-white mb-3"><i class="bi bi-award text-warning me-2"></i>Verified Platform Certificates</h5>
          <div class="row g-3">
            <div v-for="cert in profile.certificates" :key="cert.id" class="col-sm-6">
              <div class="p-3 bg-dark rounded border border-secondary">
                <div class="fw-bold text-white small">Certificate #{{ cert.cert_id }}</div>
                <div class="text-muted extra-small mt-1">Issued: {{ new Date(cert.issued_at).toLocaleDateString() }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Trophy Case -->
      <div class="col-md-5">
        <div class="card card-custom p-4">
          <h5 class="fw-bold text-white mb-3"><i class="bi bi-trophy text-warning me-2"></i>Competition Trophy Case</h5>
          <div v-if="profile.trophy_case.length === 0" class="text-muted small">No competition participations yet.</div>
          <div v-else class="d-flex flex-column gap-3">
            <div v-for="(t, idx) in profile.trophy_case" :key="idx" class="p-3 bg-dark rounded border border-secondary d-flex align-items-center justify-content-between">
              <div>
                <div class="fw-bold text-white">{{ t.competition_title }}</div>
                <div class="text-muted extra-small text-uppercase">{{ t.category }}</div>
              </div>
              <span :class="['badge', t.result === 'winner' ? 'bg-warning text-dark' : 'bg-secondary']">
                {{ t.result }}
              </span>
            </div>
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
const profile = ref(null)

const fetchPublicProfile = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await axios.get(`/api/profile/public/${route.params.username}`)
    profile.value = res.data
  } catch (err) {
    error.value = err.response?.data?.error || 'Unable to access public profile.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPublicProfile()
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
</style>
