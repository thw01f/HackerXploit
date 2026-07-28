<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <div class="flex items-center space-x-3 mb-6">
      <router-link to="/admin" class="btn-ghost text-xs py-1.5 px-3">&larr; Control Center</router-link>
      <h1 class="text-2xl font-bold text-white tracking-tight">System Feature Settings & Toggles</h1>
    </div>

    <div class="glass-panel border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-6">
      <div class="space-y-4">
        <!-- Feature Toggle: General Chat -->
        <div class="p-5 bg-slate-950/60 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <h3 class="text-sm font-bold text-white">General Text Chat Channel</h3>
            <p class="text-xs text-slate-400 mt-1">Enable or disable real-time text chat at <code>/chat</code> site-wide.</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="generalChatEnabled" @change="saveSettings" class="sr-only peer">
            <div class="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-500"></div>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const generalChatEnabled = ref(true)

const fetchSettings = async () => {
  try {
    const res = await axios.get('/api/admin/settings')
    generalChatEnabled.value = res.data.general_chat_enabled
  } catch (err) {
    console.error('Failed to load settings', err)
  }
}

const saveSettings = async () => {
  try {
    await axios.post('/api/admin/settings', {
      general_chat_enabled: generalChatEnabled.value
    })
    alert('System settings updated')
  } catch (err) {
    alert('Failed to update settings')
  }
}

onMounted(() => {
  fetchSettings()
})
</script>
