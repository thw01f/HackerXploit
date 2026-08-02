<template>
  <div class="space-y-8">
    <AdminSubNav />

    <div>
      <span class="px-2.5 py-1 rounded bg-cyan-950 text-cyan-400 font-mono text-xs font-bold uppercase">ADMIN ONLY</span>
      <h1 class="text-3xl font-extrabold text-white mt-2">Custom Profile Field Definitions</h1>
      <p class="text-slate-400 text-sm mt-1">Configure custom profile fields for members and teachers. Automatic notifications are dispatched when a new field is created.</p>
    </div>

      <!-- Success Alert Banner -->
      <div v-if="successMsg" class="p-4 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-400 text-xs font-mono flex items-center justify-between">
        <span>{{ successMsg }}</span>
        <button @click="successMsg = ''" class="text-emerald-400 hover:text-white">&times;</button>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- New Field Form -->
        <div class="glass-panel p-6 space-y-4">
          <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3">Add Custom Field</h3>
          <form @submit.prevent="createField" class="space-y-4">
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Field Key</label>
              <input v-model="newField.field_key" type="text" required placeholder="discord_handle" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono" />
            </div>
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Label</label>
              <input v-model="newField.label" type="text" required placeholder="Discord Username" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs" />
            </div>
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Target Audience</label>
              <select v-model="newField.target_role" class="w-full bg-slate-900 border border-cyan-500/40 rounded-lg px-3 py-2 text-cyan-300 text-xs font-bold">
                <option value="all">All Users (Members & Teachers)</option>
                <option value="member">Members Only</option>
                <option value="teacher">Teachers Only</option>
              </select>
              <p class="text-[11px] text-slate-400 mt-1 font-mono">Selecting an audience dispatches fill-out notifications to matching users.</p>
            </div>
            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Field Type</label>
              <select v-model="newField.field_type" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs">
                <option value="text">Text Input</option>
                <option value="number">Number</option>
                <option value="date">Date</option>
                <option value="select">Dropdown Select</option>
                <option value="file">File Attachment</option>
              </select>
            </div>
            <div class="flex items-center space-x-2">
              <input type="checkbox" id="req" v-model="newField.required" class="w-4 h-4 text-cyan-500 rounded" />
              <label for="req" class="text-xs text-slate-300">Required Field</label>
            </div>
            <button type="submit" class="w-full btn-neon-cyan text-xs py-2.5 font-bold uppercase tracking-wider flex items-center justify-center gap-2">
              <svg class="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              <span>Create Field & Dispatch Notifications</span>
            </button>
          </form>
        </div>

        <!-- Field List -->
        <div class="lg:col-span-2 glass-panel p-6 space-y-4">
          <div class="border-b border-slate-800 pb-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 class="text-lg font-bold text-white flex items-center gap-2">
                <span>Existing Custom Fields</span>
                <span class="text-xs font-mono text-cyan-400">({{ filteredFields.length }} SHOWN)</span>
              </h3>
              <p class="text-[11px] text-slate-400 mt-0.5 font-mono">Note: Admins are privileged members and receive fields assigned to Members & All Users.</p>
            </div>
            
            <!-- Audience Filter Tabs -->
            <div class="flex items-center space-x-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800 self-start sm:self-auto">
              <button 
                v-for="t in filterTabs" 
                :key="t.id"
                @click="activeTab = t.id"
                :class="[
                  'px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all',
                  activeTab === t.id ? 'bg-cyan-500 text-black shadow-md' : 'text-slate-400 hover:text-white'
                ]"
              >
                {{ t.label }}
              </button>
            </div>
          </div>

          <div class="space-y-3">
            <div v-for="f in filteredFields" :key="f.id" class="p-4 bg-slate-900/80 rounded-xl border border-slate-800 flex flex-col sm:flex-row justify-between sm:items-center gap-3">
              <div>
                <div class="flex items-center space-x-2">
                  <span class="font-bold text-white text-sm">{{ f.label }}</span>
                  <span class="text-xs text-cyan-400 font-mono">({{ f.field_key }})</span>
                </div>
                <div class="flex flex-wrap items-center gap-2 text-[11px] text-slate-400 mt-2">
                  <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono uppercase">{{ f.field_type }}</span>
                  <span :class="[
                    'px-2 py-0.5 rounded font-bold font-mono border',
                    f.target_role === 'member' ? 'bg-cyan-950/60 text-cyan-400 border-cyan-500/30' :
                    f.target_role === 'teacher' ? 'bg-purple-950/60 text-purple-400 border-purple-500/30' :
                    'bg-slate-800 text-slate-300 border-slate-700'
                  ]">
                    {{ f.target_role === 'member' ? 'Members (Students & Admins)' : f.target_role === 'teacher' ? 'Teachers Only' : 'All Users' }}
                  </span>
                  <span v-if="f.required" class="text-amber-400 font-semibold">Required</span>
                </div>
              </div>

              <div class="flex items-center space-x-2 self-end sm:self-center">
                <button @click="toggleActive(f)" :class="f.active ? 'btn-neon-violet' : 'bg-slate-800 text-slate-400'" class="text-xs py-1.5 px-3">
                  {{ f.active ? 'Active' : 'Disabled' }}
                </button>
                <button @click="deleteField(f)" class="btn-ghost text-xs py-1.5 px-2.5 text-red-400 hover:bg-red-950/40 flex items-center gap-1">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                  <span>Delete</span>
                </button>
              </div>
            </div>
            <div v-if="filteredFields.length === 0" class="p-8 text-center text-slate-500 font-mono text-xs">
              No custom profile fields match the selected audience tab.
            </div>
          </div>
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import AdminSubNav from '../components/AdminSubNav.vue'

const fields = ref([])
const successMsg = ref('')
const activeTab = ref('all')

const filterTabs = [
  { id: 'all', label: 'All' },
  { id: 'member', label: 'Members' },
  { id: 'teacher', label: 'Teachers' }
]

const newField = ref({
  field_key: '',
  label: '',
  field_type: 'text',
  target_role: 'all',
  options: [],
  required: false
})

const fetchFields = async () => {
  try {
    const res = await axios.get('/api/admin/profile-fields')
    fields.value = res.data.fields
  } catch (err) {
    console.error(err)
  }
}

const filteredFields = computed(() => {
  if (activeTab.value === 'all') return fields.value
  return fields.value.filter(f => f.target_role === activeTab.value || f.target_role === 'all')
})

onMounted(fetchFields)

const createField = async () => {
  try {
    const res = await axios.post('/api/admin/profile-fields', newField.value)
    const count = res.data.notified_count || 0
    successMsg.value = `Custom field "${newField.value.label}" created successfully! Automated fill-out notifications sent to ${count} user(s).`
    newField.value = { field_key: '', label: '', field_type: 'text', target_role: 'all', options: [], required: false }
    await fetchFields()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to create field')
  }
}

const toggleActive = async (field) => {
  try {
    await axios.put(`/api/admin/profile-fields/${field.id}`, { active: !field.active })
    await fetchFields()
  } catch (err) {
    alert('Failed to update field')
  }
}

const deleteField = async (field) => {
  if (confirm(`Are you sure you want to delete custom field "${field.label}"?`)) {
    try {
      await axios.delete(`/api/admin/profile-fields/${field.id}`)
      successMsg.value = `Field "${field.label}" deleted.`
      await fetchFields()
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to delete field')
    }
  }
}
</script>
