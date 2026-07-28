<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full space-y-8">
      <div>
        <span class="px-2.5 py-1 rounded bg-cyan-950 text-cyan-400 font-mono text-xs font-bold uppercase">ADMIN ONLY</span>
        <h1 class="text-3xl font-extrabold text-white mt-2">Custom Profile Field Definitions</h1>
        <p class="text-slate-400 text-sm mt-1">Configure registration and profile fields. Active fields appear dynamically on public registration.</p>
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
            <button type="submit" class="w-full btn-neon-cyan text-xs py-2">Create Custom Field</button>
          </form>
        </div>

        <!-- Field List -->
        <div class="lg:col-span-2 glass-panel p-6 space-y-4">
          <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3 flex justify-between items-center">
            <span>Existing Custom Fields</span>
            <span class="text-xs font-mono text-cyan-400">{{ fields.length }} TOTAL</span>
          </h3>

          <div class="space-y-3">
            <div v-for="f in fields" :key="f.id" class="p-4 bg-slate-900/80 rounded-xl border border-slate-800 flex justify-between items-center">
              <div>
                <span class="font-bold text-white">{{ f.label }}</span>
                <span class="text-xs text-cyan-400 font-mono ml-2">({{ f.field_key }})</span>
                <div class="flex items-center space-x-2 text-[11px] text-slate-400 mt-1">
                  <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">{{ f.field_type }}</span>
                  <span v-if="f.required" class="text-amber-400 font-semibold">Required</span>
                </div>
              </div>
              <button @click="toggleActive(f)" :class="f.active ? 'btn-neon-violet' : 'bg-slate-800 text-slate-400'" class="text-xs py-1.5 px-3">
                {{ f.active ? 'Active' : 'Disabled' }}
              </button>
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
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

const fields = ref([])
const newField = ref({
  field_key: '',
  label: '',
  field_type: 'text',
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

onMounted(fetchFields)

const createField = async () => {
  try {
    await axios.post('/api/admin/profile-fields', newField.value)
    newField.value = { field_key: '', label: '', field_type: 'text', options: [], required: false }
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
</script>
