<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <div class="flex items-center space-x-3 mb-6">
      <router-link to="/inbox" class="btn-ghost text-xs py-1.5 px-3">&larr; Back to Inbox</router-link>
      <h1 class="text-2xl font-bold text-white tracking-tight">Compose Broadcast Message</h1>
    </div>

    <div class="glass-panel border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-6">
      <form @submit.prevent="handleSendBroadcast" class="space-y-5">
        <!-- Target Scope -->
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Recipient Scope</label>
          <select v-model="form.scope" class="input-field w-full text-xs">
            <option value="all_members">All Approved Members (Site-Wide Broadcast)</option>
            <option value="role:member">Role: Regular Members Only</option>
            <option value="role:teacher">Role: Teachers & Staff Only</option>
            <option value="custom_list">Custom User List</option>
          </select>
        </div>

        <!-- Custom User List Input -->
        <div v-if="form.scope === 'custom_list' || form.scope === 'individual'" class="space-y-2">
          <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider">Select Users</label>
          <div class="max-h-48 overflow-y-auto border border-slate-800 rounded-xl p-3 bg-slate-950/60 divide-y divide-slate-800">
            <label v-for="user in availableUsers" :key="user.id" class="flex items-center space-x-3 py-1.5 cursor-pointer">
              <input type="checkbox" :value="user.id" v-model="form.target_user_ids" class="rounded border-slate-700 bg-slate-800 text-cyan-500" />
              <span class="text-xs text-slate-200 font-semibold">{{ user.username }} ({{ user.full_name || user.email }})</span>
            </label>
          </div>
        </div>

        <!-- Subject -->
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Message Subject</label>
          <input v-model="form.subject" type="text" placeholder="Enter broadcast subject line..." class="input-field w-full text-xs" required />
        </div>

        <!-- Body -->
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Message Body</label>
          <textarea v-model="form.body" rows="6" placeholder="Compose message body..." class="input-field w-full text-xs" required></textarea>
        </div>

        <!-- Options -->
        <div class="flex items-center space-x-3 pt-2">
          <input type="checkbox" v-model="form.allow_reply" id="allowReply" class="rounded border-slate-700 bg-slate-800 text-cyan-500" />
          <label for="allowReply" class="text-xs text-slate-300 font-semibold cursor-pointer">Allow recipient replies (Default: On)</label>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end space-x-4 border-t border-slate-800 pt-4">
          <router-link to="/inbox" class="btn-ghost text-xs py-2 px-5">Cancel</router-link>
          <button type="submit" :disabled="submitting || !form.subject.trim() || !form.body.trim()" class="btn-neon-cyan text-xs py-2 px-6 font-bold">
            Send Broadcast
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const submitting = ref(false)
const availableUsers = ref([])

const form = ref({
  scope: 'all_members',
  subject: '',
  body: '',
  allow_reply: true,
  target_user_ids: []
})

const fetchUsers = async () => {
  try {
    const res = await axios.get('/api/teacher/students?q=')
    availableUsers.value = res.data.students || []
  } catch (err) {
    console.error('Failed to load user list', err)
  }
}

const handleSendBroadcast = async () => {
  submitting.value = true
  try {
    await axios.post('/api/inbox/messages', form.value)
    alert('Broadcast message dispatched successfully!')
    router.push('/inbox')
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to send message')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchUsers()
})
</script>
