<template>
  <div class="space-y-8">
      <div>
        <span class="px-2.5 py-1 rounded bg-purple-950 text-purple-400 font-mono text-xs font-bold uppercase">ADMIN ONLY</span>
        <h1 class="text-3xl font-extrabold text-white mt-2">Password Reset Requests</h1>
        <p class="text-slate-400 text-sm mt-1">Review pending user password reset requests and issue 8-character single-use codes (expires in 30 minutes).</p>
      </div>

      <div class="glass-panel p-6 space-y-4">
        <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3 flex items-center justify-between">
          <span>Pending Password Reset Queue</span>
          <span class="text-xs font-mono text-cyan-400">{{ requests.length }} PENDING</span>
        </h3>

        <div class="space-y-3">
          <div v-for="req in requests" :key="req.id" class="p-4 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <span class="font-bold text-white">User #{{ req.user_id }}</span>
              <span class="text-xs text-cyan-400 font-mono ml-2">@{{ req.username }}</span>
              <p class="text-xs text-slate-400 mt-0.5">{{ req.email }} • Requested: {{ new Date(req.created_at).toLocaleString() }}</p>
            </div>
            <button @click="generateCode(req.user_id)" class="btn-neon-violet text-xs py-2 px-4">
              Generate 8-Char Code
            </button>
          </div>
          <div v-if="requests.length === 0" class="text-center py-6 text-slate-500 text-xs font-mono">
            No pending password reset requests.
          </div>
        </div>
      </div>

      <!-- Generated Code Alert Modal -->
      <div v-if="generatedCode" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
        <div class="w-full max-w-md glass-panel p-6 rounded-2xl border border-cyan-500/40 text-center space-y-4">
          <h3 class="text-xl font-bold text-white">Reset Code Issued</h3>
          <p class="text-xs text-slate-300">Provide this 8-character code to <strong>@{{ targetUsername }}</strong>. It expires in 30 minutes.</p>
          <div class="p-4 bg-slate-950 rounded-xl border border-cyan-500/50 font-mono text-2xl font-bold text-cyan-400 tracking-widest select-all">
            {{ generatedCode }}
          </div>
          <button @click="generatedCode = null" class="btn-neon-cyan text-xs py-2 px-6">Close</button>
        </div>
      </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const requests = ref([])
const generatedCode = ref(null)
const targetUsername = ref('')

const fetchRequests = async () => {
  try {
    const res = await axios.get('/api/admin/password-requests')
    requests.value = res.data.requests
  } catch (err) {
    console.error(err)
  }
}

onMounted(fetchRequests)

const generateCode = async (userId) => {
  try {
    const res = await axios.post('/api/admin/password-requests/generate', { user_id: userId })
    generatedCode.value = res.data.code
    targetUsername.value = res.data.user.username
    await fetchRequests()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to generate code')
  }
}
</script>
