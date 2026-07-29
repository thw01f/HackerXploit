<template>
  <div class="max-w-4xl mx-auto px-4 py-8 space-y-6">
    
    <!-- Top Header -->
    <div class="flex items-center justify-between pb-4 border-b border-[#1f293d]">
      <div class="flex items-center space-x-3">
        <router-link to="/inbox" class="btn-ghost text-xs py-1.5 px-3 font-mono flex items-center space-x-1">
          <span>&larr; Back to Inbox</span>
        </router-link>
        <h1 class="text-xl font-mono font-extrabold text-white tracking-tight">
          Compose <span class="text-[#9fef00]">Platform Message</span>
        </h1>
      </div>
    </div>

    <!-- Main Card Container -->
    <div class="glass-panel border border-[#1f293d] rounded-2xl p-6 bg-[#0d1420]/90 shadow-2xl space-y-6">
      
      <form @submit.prevent="handleSendMessage" class="space-y-5 font-mono">
        
        <!-- Recipient Scope Selector (Only visible to Teachers and Admins) -->
        <div v-if="authStore.isTeacher || authStore.isAdmin">
          <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Recipient Target Scope</label>
          <select 
            v-model="form.scope" 
            @change="handleScopeChange"
            class="input-field w-full text-xs font-mono bg-[#0b0e14]"
          >
            <option value="individual">Direct 1-on-1 Message</option>
            <option v-if="authStore.isTeacher" value="all_members">All Approved Members (Site-Wide Broadcast)</option>
            <option v-if="authStore.isTeacher" value="role:member">Regular Members Only</option>
            <option v-if="authStore.isTeacher" value="role:teacher">Teachers & Staff Only</option>
            <option v-if="authStore.isAdmin" value="role:admin">Admins Only</option>
            <option v-if="authStore.isTeacher" value="custom_list">Custom User Group</option>
          </select>
        </div>

        <!-- User Selection Section (for 1-on-1 and custom_list) -->
        <div v-if="form.scope === 'individual' || form.scope === 'custom_list'" class="space-y-2">
          <div class="flex justify-between items-center">
            <label class="block text-xs font-bold text-[#00f0ff] uppercase tracking-wider">
              {{ !authStore.isTeacher && !authStore.isAdmin ? 'Select Recipient (Teacher or Admin)' : (form.scope === 'individual' ? 'Select Recipient User' : 'Select Recipients') }}
            </label>
            <span class="text-[11px] text-slate-400">Selected: {{ form.target_user_ids.length }}</span>
          </div>

          <!-- Search Filter Box -->
          <input 
            v-model="userSearchQuery" 
            type="text" 
            :placeholder="!authStore.isTeacher && !authStore.isAdmin ? 'Search instructors and admins by handle or name...' : 'Search users by handle or name...'" 
            class="input-field w-full text-xs font-mono mb-2"
          />

          <!-- Users List Scrollbox -->
          <div class="max-h-56 overflow-y-auto border border-[#1f293d] rounded-xl p-2 bg-[#0b0e14]/80 divide-y divide-[#1f293d]">
            <div v-if="filteredUserList.length === 0" class="p-4 text-center text-xs text-slate-500 font-mono">
              No matching recipients found.
            </div>

            <div 
              v-for="user in filteredUserList" 
              :key="user.id" 
              @click="selectUser(user.id)"
              :class="[
                'flex items-center justify-between p-2.5 rounded-lg cursor-pointer transition-colors hover:bg-[#151f30]',
                isUserSelected(user.id) ? 'bg-[#00f0ff]/15 border border-[#00f0ff]/40 shadow-[0_0_10px_rgba(0,240,255,0.1)]' : ''
              ]"
            >
              <div class="flex items-center space-x-3">
                <input 
                  type="checkbox" 
                  :checked="isUserSelected(user.id)" 
                  class="rounded border-slate-700 bg-slate-800 text-[#00f0ff] pointer-events-none" 
                />
                <img 
                  :src="user.avatar_url || '/uploads/avatars/default.png'" 
                  @error="$event.target.src='https://api.dicebear.com/7.x/bottts/svg?seed=' + user.username"
                  class="w-7 h-7 rounded-lg object-cover border border-[#1f293d]" 
                />
                <div>
                  <span class="text-xs font-bold text-white leading-tight block">@{{ user.username }}</span>
                  <span class="text-[10px] text-slate-400 block">{{ user.full_name }}</span>
                </div>
              </div>

              <div class="flex items-center space-x-2">
                <span :class="getRoleBadgeClass(user.role)" class="text-[9px] font-bold uppercase px-2 py-0.5 rounded border">
                  {{ user.role }}
                </span>
                <span v-if="user.specialization_role" class="text-[9px] font-mono text-[#9fef00] bg-[#9fef00]/10 px-2 py-0.5 rounded border border-[#9fef00]/20">
                  {{ user.specialization_role }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Subject Line -->
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Subject Header</label>
          <input 
            v-model="form.subject" 
            type="text" 
            placeholder="Enter message subject line..." 
            class="input-field w-full text-xs font-mono" 
            required 
          />
        </div>

        <!-- Body Content -->
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Message Body</label>
          <textarea 
            v-model="form.body" 
            rows="6" 
            placeholder="Write your detailed message content..." 
            class="input-field w-full text-xs font-mono leading-relaxed" 
            required
          ></textarea>
        </div>

        <!-- Allow Replies Checkbox -->
        <div class="flex items-center space-x-3 pt-1">
          <input 
            type="checkbox" 
            v-model="form.allow_reply" 
            id="allowReply" 
            class="rounded border-slate-700 bg-slate-800 text-[#9fef00] w-4 h-4" 
          />
          <label for="allowReply" class="text-xs text-slate-300 font-semibold cursor-pointer">
            Allow recipient to send direct replies (Default: Enabled)
          </label>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end space-x-4 border-t border-[#1f293d] pt-5">
          <router-link to="/inbox" class="btn-ghost text-xs py-2 px-5 font-mono">Cancel</router-link>
          <button 
            type="submit" 
            :disabled="submitting || !form.subject.trim() || !form.body.trim() || ((form.scope === 'individual' || form.scope === 'custom_list') && form.target_user_ids.length === 0)" 
            class="btn-htb text-xs py-2.5 px-6 font-mono font-bold shadow-lg"
          >
            {{ submitting ? 'Transmitting...' : 'Send Message' }}
          </button>
        </div>

      </form>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()
const submitting = ref(false)
const userSearchQuery = ref('')
const directoryUsers = ref([])

const form = ref({
  scope: 'individual',
  subject: '',
  body: '',
  allow_reply: true,
  target_user_ids: []
})

const handleScopeChange = () => {
  if (form.value.scope !== 'individual' && form.value.scope !== 'custom_list') {
    form.value.target_user_ids = []
  }
}

const selectUser = (userId) => {
  if (form.value.scope === 'individual') {
    form.value.target_user_ids = [userId]
  } else {
    const idx = form.value.target_user_ids.indexOf(userId)
    if (idx > -1) {
      form.value.target_user_ids.splice(idx, 1)
    } else {
      form.value.target_user_ids.push(userId)
    }
  }
}

const isUserSelected = (userId) => {
  return Array.isArray(form.value.target_user_ids) && form.value.target_user_ids.includes(userId)
}

const fetchUserDirectory = async () => {
  try {
    const res = await axios.get('/api/inbox/users')
    directoryUsers.value = res.data.users || []
  } catch (err) {
    console.error('Failed to load user directory', err)
  }
}

const filteredUserList = computed(() => {
  if (!userSearchQuery.value.trim()) return directoryUsers.value
  const q = userSearchQuery.value.toLowerCase()
  return directoryUsers.value.filter(u => 
    u.username.toLowerCase().includes(q) || 
    (u.full_name && u.full_name.toLowerCase().includes(q))
  )
})

const handleSendMessage = async () => {
  if (submitting.value) return
  submitting.value = true
  try {
    const payload = {
      scope: form.value.scope,
      subject: form.value.subject,
      body: form.value.body,
      allow_reply: form.value.allow_reply,
      target_user_ids: form.value.target_user_ids
    }
    await axios.post('/api/inbox/messages', payload)
    alert('Message sent successfully!')
    router.push('/inbox')
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to send message')
  } finally {
    submitting.value = false
  }
}

const getRoleBadgeClass = (role) => {
  if (role === 'root_admin' || role === 'admin') return 'bg-purple-950/80 text-purple-400 border-purple-800'
  if (role === 'teacher') return 'bg-amber-950/80 text-amber-400 border-amber-800'
  return 'bg-slate-800 text-slate-400 border-slate-700'
}

onMounted(() => {
  fetchUserDirectory()
})
</script>
