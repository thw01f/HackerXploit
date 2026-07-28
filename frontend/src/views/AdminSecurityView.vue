<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full space-y-8">
      <div>
        <h1 class="text-3xl font-extrabold text-white">Security & Login Activity</h1>
        <p class="text-slate-400 text-sm mt-1">Admin-only visibility into authentication attempts and security lockouts.</p>
      </div>

      <div class="glass-panel p-6 space-y-4">
        <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3">Authentication Log Feed</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs font-mono">
            <thead class="bg-slate-900 text-slate-400 uppercase">
              <tr>
                <th class="p-3">Timestamp</th>
                <th class="p-3">Email Attempted</th>
                <th class="p-3">IP Address</th>
                <th class="p-3">Result</th>
                <th class="p-3">Reason / Details</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800 text-slate-300">
              <tr v-for="act in activities" :key="act.id" class="hover:bg-slate-800/40">
                <td class="p-3 text-slate-500">{{ new Date(act.timestamp).toLocaleString() }}</td>
                <td class="p-3 font-bold text-white">{{ act.email_attempted }}</td>
                <td class="p-3 text-cyan-400">{{ act.ip_address }}</td>
                <td class="p-3 font-bold">
                  <span :class="act.success ? 'text-emerald-400' : 'text-red-400'">
                    {{ act.success ? 'SUCCESS' : 'FAILED' }}
                  </span>
                </td>
                <td class="p-3 text-slate-400">{{ act.failure_reason || 'N/A' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

const activities = ref([])

onMounted(async () => {
  try {
    const res = await axios.get('/api/admin/security/login-activity')
    activities.value = res.data.activities
  } catch (err) {
    alert('Access prohibited or error loading security log')
  }
})
</script>
