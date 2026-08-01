<template>
  <div class="min-h-screen flex flex-col justify-between bg-[#0b0e14]">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full space-y-8">
      
      <!-- Loading State -->
      <div v-if="loading" class="py-16 text-center font-mono text-sm text-slate-500">
        Loading member portfolio...
      </div>

      <!-- Private Profile Error State -->
      <div v-else-if="error" class="glass-panel p-12 text-center max-w-lg mx-auto space-y-4 border border-amber-500/40 bg-[#111927]">
        <div class="w-12 h-12 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center justify-center mx-auto">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
          </svg>
        </div>
        <h3 class="font-mono font-bold text-xl text-white">Private Profile</h3>
        <p class="text-xs font-mono text-slate-400">{{ error }}</p>
        <router-link to="/" class="btn-htb text-xs font-mono py-2 px-5 inline-block">Return to Home</router-link>
      </div>

      <!-- Public Profile Layout -->
      <div v-else-if="profile" class="space-y-8">
        
        <!-- Header Banner Card -->
        <div class="glass-panel p-8 bg-[#111927] border border-[#9fef00]/40 flex flex-col md:flex-row items-center justify-between gap-6">
          <div class="flex items-center space-x-6">
            <div class="w-20 h-20 rounded-xl bg-[#090d16] border-2 border-[#9fef00]/60 flex items-center justify-center text-[#9fef00] font-mono font-extrabold text-3xl shadow-lg">
              {{ profile.user.username.charAt(0).toUpperCase() }}
            </div>
            <div>
              <div class="flex items-center space-x-3">
                <h2 class="font-mono font-extrabold text-2xl text-white">@{{ profile.user.username }}</h2>
                <span class="text-[10px] font-mono font-bold uppercase bg-[#151f30] text-[#00f0ff] px-2.5 py-0.5 rounded border border-[#00f0ff]/30">
                  {{ profile.user.role }}
                </span>
              </div>
              <p class="text-xs font-mono text-slate-400 mt-1">
                Member Since {{ profile.user.created_at ? new Date(profile.user.created_at).toLocaleDateString() : 'N/A' }}
              </p>
            </div>
          </div>

          <div class="flex items-center space-x-4">
            <div class="bg-[#090d16] px-4 py-2.5 rounded-xl border border-[#1f293d] text-center">
              <span class="block text-xl font-extrabold font-mono text-[#00f0ff]">{{ profile.stats.total_courses_completed }}</span>
              <span class="text-[10px] font-mono text-slate-400 uppercase">COURSES</span>
            </div>
            <div v-if="profile.stats.total_certificates !== null" class="bg-[#090d16] px-4 py-2.5 rounded-xl border border-[#1f293d] text-center">
              <span class="block text-xl font-extrabold font-mono text-amber-400">{{ profile.stats.total_certificates }}</span>
              <span class="text-[10px] font-mono text-slate-400 uppercase">CERTS</span>
            </div>
            <div v-if="profile.stats.total_activity_hours !== null" class="bg-[#090d16] px-4 py-2.5 rounded-xl border border-[#1f293d] text-center">
              <span class="block text-xl font-extrabold font-mono text-[#9fef00]">{{ profile.stats.total_activity_hours }}h</span>
              <span class="text-[10px] font-mono text-slate-400 uppercase">LAB TIME</span>
            </div>
          </div>
        </div>

        <!-- Content Grid (2 Columns) -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          <!-- Left Column: Courses & Certificates -->
          <div class="lg:col-span-2 space-y-6">
            <div class="glass-panel p-6 bg-[#111927] border border-[#1f293d] space-y-4">
              <h3 class="font-mono font-bold text-base text-white uppercase border-b border-[#1f293d] pb-3">Completed Curriculum</h3>
              <div v-if="profile.completed_courses.length === 0" class="text-xs font-mono text-slate-500 py-4 text-center">
                No completed courses yet.
              </div>
              <div v-else class="space-y-3">
                <div v-for="course in profile.completed_courses" :key="course.id" class="p-3.5 rounded-lg bg-[#090d16] border border-[#1f293d]">
                  <h4 class="font-mono font-bold text-sm text-[#00f0ff]">{{ course.title }}</h4>
                  <p class="text-xs text-slate-400 mt-1 leading-relaxed">{{ course.description }}</p>
                </div>
              </div>
            </div>

            <div v-if="profile.certificates && profile.certificates.length > 0" class="glass-panel p-6 bg-[#111927] border border-[#1f293d] space-y-4">
              <h3 class="font-mono font-bold text-base text-white uppercase border-b border-[#1f293d] pb-3">Verified Platform Certificates</h3>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div v-for="cert in profile.certificates" :key="cert.id" class="p-4 rounded-lg bg-[#090d16] border border-[#9fef00]/30 space-y-1">
                  <span class="block font-mono font-bold text-xs text-[#9fef00]">Certificate #{{ cert.cert_id }}</span>
                  <span class="block font-mono text-[10px] text-slate-400">Issued: {{ new Date(cert.issued_at).toLocaleDateString() }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Column: Trophy Case -->
          <div class="glass-panel p-6 bg-[#111927] border border-[#1f293d] space-y-4 self-start">
            <h3 class="font-mono font-bold text-base text-white uppercase border-b border-[#1f293d] pb-3">Trophy Case</h3>
            <div v-if="profile.trophy_case.length === 0" class="text-xs font-mono text-slate-500 py-4 text-center">
              No competition records found.
            </div>
            <div v-else class="space-y-3">
              <div v-for="(t, idx) in profile.trophy_case" :key="idx" class="p-3 rounded-lg bg-[#090d16] border border-[#1f293d] flex items-center justify-between">
                <div>
                  <h4 class="font-mono font-bold text-xs text-white">{{ t.competition_title }}</h4>
                  <span class="text-[10px] font-mono text-slate-400 uppercase">{{ t.category }}</span>
                </div>
                <span class="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded" :class="t.result === 'winner' ? 'bg-amber-400 text-black' : 'bg-[#151f30] text-[#00f0ff] border border-[#00f0ff]/30'">
                  {{ t.result }}
                </span>
              </div>
            </div>
          </div>

        </div>

      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

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
