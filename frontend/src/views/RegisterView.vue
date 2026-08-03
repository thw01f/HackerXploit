<template>
  <div class="min-h-screen flex flex-col justify-between bg-[#0b0e14]">
    <Navbar />

    <main class="flex-1 flex items-center justify-center p-4">
      <div class="w-full max-w-lg glass-panel p-8 rounded-xl shadow-2xl relative border border-[#1f293d]">
        
        <!-- Header -->
        <div class="text-center mb-6">
          <img src="/logo.png" class="w-24 h-24 object-contain mx-auto mb-3" alt="HackerXploit Logo" />
          <h2 class="text-2xl font-bold font-mono">Join <span class="text-white">Hacker</span><span class="text-red-500">Xploit</span></h2>
          <p class="text-xs text-slate-400 font-mono mt-1">Collegiate Cybersecurity Registration Queue</p>
        </div>


        <!-- Success Message -->
        <div v-if="successMessage" class="mb-5 p-3.5 rounded-lg bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 text-xs font-mono">
          {{ successMessage }}
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="mb-5 p-3.5 rounded-lg bg-red-950/80 border border-red-500/50 text-red-300 text-xs font-mono">
          {{ errorMessage }}
        </div>

        <!-- Registration Form -->
        <form @submit.prevent="handleRegister" class="space-y-4">
          <p class="text-[11px] text-slate-500 font-mono -mt-1">
            The details below are collected once at registration and cannot be changed later - double-check them before submitting.
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-mono text-slate-400 uppercase mb-1">Full Name</label>
              <input v-model="form.full_name" type="text" required placeholder="GOWTHAMAN GS" class="w-full" />
            </div>
            <div>
              <label class="block text-xs font-mono text-slate-400 uppercase mb-1">Username</label>
              <input v-model="form.username" type="text" required placeholder="w01f" class="w-full" />
            </div>
            <div>
              <label class="block text-xs font-mono text-slate-400 uppercase mb-1">Registration Number</label>
              <input v-model="form.registration_number" type="text" required placeholder="e.g. RA2311030050008" class="w-full" />
            </div>
            <div>
              <label class="block text-xs font-mono text-slate-400 uppercase mb-1">SRM Email Address</label>
              <input v-model="form.email" type="email" required placeholder="w01f@srmist.edu.in" class="w-full" />
            </div>
          </div>
          <p v-if="allowedDomainsHint" class="text-[11px] text-cyan-400 font-mono -mt-2">
            Allowed email domains: {{ allowedDomainsHint }}
          </p>

          <!-- Dynamic Custom Profile Fields -->
          <div v-for="field in customFields" :key="field.id">
            <label class="block text-xs font-mono text-slate-400 uppercase mb-1">
              {{ field.label }} <span v-if="field.required" class="text-amber-400">*</span>
            </label>

            <select v-if="field.field_type === 'select'" v-model="form.custom_fields[field.field_key]" :required="field.required" class="w-full">
              <option value="">Select option...</option>
              <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
            </select>

            <input v-else-if="field.field_type === 'number'" v-model="form.custom_fields[field.field_key]" type="number" :required="field.required" class="w-full" />

            <input v-else-if="field.field_type === 'date'" v-model="form.custom_fields[field.field_key]" type="date" :required="field.required" class="w-full" />

            <input v-else v-model="form.custom_fields[field.field_key]" type="text" :required="field.required" :placeholder="field.label" class="w-full" />
          </div>

          <div>
            <label class="block text-xs font-mono text-slate-400 uppercase mb-1">Password</label>
            <input v-model="form.password" type="password" required placeholder="••••••••••••" class="w-full" />
            
            <!-- CTFd-style Password Requirement & Validation Hint -->
            <div class="mt-1.5 font-mono text-[11px]">
              <span v-if="!form.password" class="text-slate-500">
                Password must be at least {{ minPasswordLength }} characters long.
              </span>
              <span v-else-if="form.password.length < minPasswordLength" class="text-amber-400 font-semibold">
                Password must be at least {{ minPasswordLength }} characters (currently {{ form.password.length }}).
              </span>
              <span v-else class="text-emerald-400 font-semibold">
                Password length requirement satisfied ({{ form.password.length }} characters).
              </span>
            </div>
          </div>

          <!-- Turnstile CAPTCHA Widget -->
          <div v-if="turnstileSiteKey" class="flex justify-center pt-1">
            <TurnstileWidget ref="turnstileRef" :site-key="turnstileSiteKey" :theme="isDark ? 'dark' : 'light'" @verified="captchaToken = $event" @expired="captchaToken = ''" @error="captchaToken = ''" />
          </div>

          <button type="submit" :disabled="loading || (turnstileSiteKey && !captchaToken)" class="w-full btn-htb py-3 text-sm flex items-center justify-center space-x-2 mt-2">
            <span v-if="loading" class="animate-spin rounded-full h-4 w-4 border-2 border-black border-t-transparent"></span>
            <span>{{ loading ? 'SUBMITTING APPLICATION...' : 'CREATE ACCOUNT &rarr;' }}</span>
          </button>
        </form>

        <div class="mt-6 pt-4 border-t border-[#1f293d] text-center text-xs font-mono text-slate-400">
          Already registered? 
          <router-link to="/login" class="text-[#9fef00] font-semibold hover:underline">Sign In</router-link>
        </div>

      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import TurnstileWidget from '../components/TurnstileWidget.vue'
import { useAuthStore } from '../stores/auth'
import { useTheme } from '../stores/theme'

const authStore = useAuthStore()
const { isDark } = useTheme()

const form = ref({
  full_name: '',
  username: '',
  registration_number: '',
  email: '',
  password: '',
  custom_fields: {}
})

const customFields = ref([])
const allowedDomainsHint = ref('')
const minPasswordLength = ref(8)

const turnstileSiteKey = ref('')
const captchaToken = ref('')
const turnstileRef = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

onMounted(() => {
  // Fetched independently (not Promise.all'd together) - custom-fields
  // failing must never take the CAPTCHA widget down with it, and vice versa.
  axios.get('/api/auth/custom-fields')
    .then(res => { customFields.value = res.data.fields })
    .catch(err => console.error('Failed to load custom registration fields', err))

  axios.get('/api/auth/registration-config')
    .then(res => {
      if (res.data.allowed_email_domains) {
        const list = res.data.allowed_email_domains.split(',').map(d => d.trim()).filter(Boolean).map(d => '@' + d)
        allowedDomainsHint.value = list.join(', ')
      }
      if (res.data.min_password_length) {
        minPasswordLength.value = res.data.min_password_length
      }
      if (res.data.turnstile_site_key) {
        turnstileSiteKey.value = res.data.turnstile_site_key
      }
    })
    .catch(err => console.error('Failed to load registration config', err))

  // Fallback source for the site key - same field, same value, served by
  // the endpoint Login already relies on successfully. Covers the case
  // where registration-config fails/changes but public-settings doesn't.
  if (!turnstileSiteKey.value) {
    axios.get('/api/auth/public-settings')
      .then(res => {
        if (!turnstileSiteKey.value && res.data.turnstile_site_key) {
          turnstileSiteKey.value = res.data.turnstile_site_key
        }
      })
      .catch(err => console.error('Failed to load public settings', err))
  }
})

const handleRegister = async () => {
  if (turnstileSiteKey.value && !captchaToken.value) {
    errorMessage.value = 'Please complete CAPTCHA verification'
    return
  }

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const res = await authStore.register({
      ...form.value,
      captcha_token: captchaToken.value
    })
    successMessage.value = res.message
  } catch (err) {
    errorMessage.value = err.message
    // Turnstile tokens are single-use - a failed submission already burned
    // this one, so the widget must issue a fresh token before a retry can pass.
    captchaToken.value = ''
    turnstileRef.value?.reset()
  } finally {
    loading.value = false
  }
}
</script>
