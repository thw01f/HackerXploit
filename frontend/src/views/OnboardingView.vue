<template>
  <div class="min-h-screen bg-[#0b0e14] text-slate-100 py-8 px-4 sm:px-6 flex flex-col justify-between items-center">
    
    <!-- Top Minimal Header with ONLY Sign Out -->
    <header class="w-full max-w-4xl flex items-center justify-between py-2 border-b border-slate-800/80 mb-6">
      <div class="flex items-center space-x-3">
        <img src="/logo.png" class="w-9 h-9 object-contain" alt="HackerXploit" />
        <span class="font-extrabold text-lg text-white font-mono">Hacker<span class="text-red-500">Xploit</span></span>
      </div>
      <button 
        @click="handleLogout" 
        class="btn-ghost text-xs py-2 px-4 font-mono text-red-400 border-red-500/30 hover:bg-red-950/40 flex items-center gap-1.5"
      >
        <span>Sign Out</span>
      </button>
    </header>

    <div class="max-w-2xl w-full space-y-8 my-auto">
      
      <!-- Top Branding & Welcome Banner -->
      <div class="text-center space-y-3">
        <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#151f30] border border-[#9fef00]/40 text-[#9fef00] text-xs font-mono">
          <span class="w-2 h-2 rounded-full bg-[#9fef00]"></span>
          <span>OPERATOR INITIALIZATION // FIRST LOGIN SETUP</span>
        </div>
        <h1 class="text-3xl font-extrabold text-white font-mono tracking-tight">Complete Your Cyber Profile</h1>
        <p class="text-xs text-slate-400 max-w-md mx-auto">
          Welcome to HackerXploit! Please configure your operator credentials and select your cyber specialization role to complete system onboarding.
        </p>
      </div>

      <!-- Main Onboarding Form Card -->
      <div class="glass-panel p-6 sm:p-8 border border-slate-800 rounded-2xl shadow-2xl space-y-8">
        
        <!-- SECTION 1: Specialization Role Selection -->
        <div class="space-y-4">
          <label class="block text-xs font-bold text-[#9fef00] font-mono uppercase tracking-wider">
            1. Select Cyber Specialization Role <span class="text-rose-400">*</span>
          </label>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <!-- Option 1: Security Analyst (Blue Team Shield Insignia) -->
            <div 
              @click="selectedRole = 'Security Analyst'"
              :class="[
                'p-5 rounded-2xl border cursor-pointer transition-all duration-200 flex flex-col justify-between space-y-4 select-none relative overflow-hidden',
                selectedRole === 'Security Analyst' 
                  ? 'bg-cyan-950/30 border-cyan-400 shadow-xl shadow-cyan-500/15 scale-[1.03] ring-1 ring-cyan-400/50' 
                  : 'bg-slate-900/80 border-slate-800 hover:border-cyan-500/40 hover:bg-slate-900'
              ]"
            >
              <div class="flex items-center justify-between">
                <!-- Custom Blue Team Shield Badge -->
                <div class="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-400/40 flex items-center justify-center text-cyan-400 shadow-inner">
                  <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                  </svg>
                </div>
                <span v-if="selectedRole === 'Security Analyst'" class="text-xs px-2.5 py-1 rounded-md bg-cyan-400/20 text-cyan-300 font-extrabold font-mono border border-cyan-400/50 uppercase">ACTIVE ROLE</span>
              </div>
              <div>
                <h4 class="font-extrabold text-base text-white font-mono flex items-center gap-2">
                  <span>Security Analyst</span>
                  <span class="text-[10px] text-cyan-400 font-mono px-1.5 py-0.5 rounded bg-cyan-950/60 border border-cyan-500/30">BLUE TEAM</span>
                </h4>
                <p class="text-xs text-slate-300 mt-1.5 leading-relaxed font-sans">SOC Operations, Blue Team Defense, Threat Intelligence & Incident Response.</p>
              </div>
            </div>

            <!-- Option 2: Penetration Tester (Red Team Trident Insignia) -->
            <div 
              @click="selectedRole = 'Penetration Tester'"
              :class="[
                'p-5 rounded-2xl border cursor-pointer transition-all duration-200 flex flex-col justify-between space-y-4 select-none relative overflow-hidden',
                selectedRole === 'Penetration Tester' 
                  ? 'bg-[#9fef00]/10 border-[#9fef00] shadow-xl shadow-[#9fef00]/15 scale-[1.03] ring-1 ring-[#9fef00]/50' 
                  : 'bg-slate-900/80 border-slate-800 hover:border-[#9fef00]/40 hover:bg-slate-900'
              ]"
            >
              <div class="flex items-center justify-between">
                <!-- Custom Red Team Exploit Trident Badge -->
                <div class="w-12 h-12 rounded-xl bg-[#9fef00]/10 border border-[#9fef00]/40 flex items-center justify-center text-[#9fef00] shadow-inner">
                  <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                  </svg>
                </div>
                <span v-if="selectedRole === 'Penetration Tester'" class="text-xs px-2.5 py-1 rounded-md bg-[#9fef00]/20 text-[#9fef00] font-extrabold font-mono border border-[#9fef00]/50 uppercase">ACTIVE ROLE</span>
              </div>
              <div>
                <h4 class="font-extrabold text-base text-white font-mono flex items-center gap-2">
                  <span>Penetration Tester</span>
                  <span class="text-[10px] text-[#9fef00] font-mono px-1.5 py-0.5 rounded bg-emerald-950/60 border border-[#9fef00]/30">RED TEAM</span>
                </h4>
                <p class="text-xs text-slate-300 mt-1.5 leading-relaxed font-sans">Offensive Security, Ethical Exploitation, Vulnerability Research & Breach Assessment.</p>
              </div>
            </div>

            <!-- Option 3: Security Engineer (Purple Hexagon Matrix Insignia) -->
            <div 
              @click="selectedRole = 'Security Engineer'"
              :class="[
                'p-5 rounded-2xl border cursor-pointer transition-all duration-200 flex flex-col justify-between space-y-4 select-none relative overflow-hidden',
                selectedRole === 'Security Engineer' 
                  ? 'bg-purple-950/30 border-purple-400 shadow-xl shadow-purple-500/15 scale-[1.03] ring-1 ring-purple-400/50' 
                  : 'bg-slate-900/80 border-slate-800 hover:border-purple-500/40 hover:bg-slate-900'
              ]"
            >
              <div class="flex items-center justify-between">
                <!-- Custom Purple SecOps Engineering Matrix Badge -->
                <div class="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-400/40 flex items-center justify-center text-purple-400 shadow-inner">
                  <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                  </svg>
                </div>
                <span v-if="selectedRole === 'Security Engineer'" class="text-xs px-2.5 py-1 rounded-md bg-purple-400/20 text-purple-300 font-extrabold font-mono border border-purple-400/50 uppercase">ACTIVE ROLE</span>
              </div>
              <div>
                <h4 class="font-extrabold text-base text-white font-mono flex items-center gap-2">
                  <span>Security Engineer</span>
                  <span class="text-[10px] text-purple-400 font-mono px-1.5 py-0.5 rounded bg-purple-950/60 border border-purple-500/30">PURPLE / SecOps</span>
                </h4>
                <p class="text-xs text-slate-300 mt-1.5 leading-relaxed font-sans">DevSecOps Infrastructure, Cryptography, Systems Hardening & Automation.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- SECTION 2: Academic & Personal Information -->
        <div class="space-y-4 pt-4 border-t border-slate-800">
          <label class="block text-xs font-bold text-cyan-400 font-mono uppercase tracking-wider">
            2. {{ isTeacher ? 'Teacher Credentials' : 'Academic Information' }}
          </label>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs text-slate-400 font-mono mb-1">Full Legal Name <span class="text-rose-400">*</span></label>
              <input 
                v-model="form.full_name" 
                type="text" 
                placeholder="e.g. GOWTHAMAN GS" 
                class="input-field text-xs py-2 w-full"
                required
              />
            </div>

            <div>
              <label class="block text-xs text-slate-400 font-mono mb-1">
                {{ isTeacher ? 'Staff / Employee ID' : 'Student Roll Number / ID' }} <span class="text-rose-400">*</span>
              </label>
              <input 
                v-model="form.student_id" 
                type="text" 
                :placeholder="isTeacher ? 'e.g. TCH-2026-08' : 'e.g. RA2311030050008'" 
                class="input-field text-xs py-2 w-full"
                required
              />
            </div>

            <div v-if="!isTeacher">
              <label class="block text-xs text-slate-400 font-mono mb-1">Academic Year <span class="text-rose-400">*</span></label>
              <select 
                v-model="form.academic_year" 
                class="input-field text-xs py-2 w-full bg-slate-900 border border-slate-700 rounded-lg text-white"
                required
              >
                <option value="I">1st Year (I)</option>
                <option value="II">2nd Year (II)</option>
                <option value="III">3rd Year (III)</option>
                <option value="IV">4th Year (IV)</option>
              </select>
            </div>

            <div>
              <label class="block text-xs text-slate-400 font-mono mb-1">Department</label>
              <input 
                v-model="form.department" 
                type="text" 
                placeholder="e.g. Cyber Security" 
                class="input-field text-xs py-2 w-full"
              />
            </div>

            <div>
              <label class="block text-xs text-slate-400 font-mono mb-1">
                Gmail Address <span class="text-[10px] text-cyan-400 font-normal font-mono">(Private to Teachers/Admins)</span>
              </label>
              <input 
                v-model="form.gmail" 
                type="email" 
                placeholder="yourname@gmail.com" 
                class="input-field text-xs py-2 w-full"
              />
            </div>

            <div>
              <label class="block text-xs text-slate-400 font-mono mb-1">
                Phone Number / WhatsApp <span class="text-[10px] text-cyan-400 font-normal font-mono">(Private to Teachers/Admins)</span>
              </label>
              <input 
                v-model="form.phone_number" 
                type="tel" 
                placeholder="e.g. 6379855124" 
                class="input-field text-xs py-2 w-full"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs text-slate-400 font-mono mb-1">Operator Bio / Research Focus</label>
            <textarea 
              v-model="form.bio" 
              rows="2" 
              placeholder="Brief summary of your cybersecurity background and target learning goals..." 
              class="input-field text-xs w-full py-2"
            ></textarea>
          </div>
        </div>

        <!-- SECTION 3: Cyber Portfolios & Social Links (Synced to CTFd) -->
        <div class="space-y-4 pt-4 border-t border-slate-800">
          <label class="block text-xs font-bold text-amber-400 font-mono uppercase tracking-wider">
            3. Cyber Portfolios & Profiles (Synced to CTFd)
          </label>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs text-slate-400 font-mono mb-1">Portfolio Website URL</label>
              <input v-model="form.website_url" type="url" placeholder="https://yourname.dev" class="input-field text-xs py-2 w-full" />
            </div>
            <div>
              <label class="block text-xs text-slate-400 font-mono mb-1">GitHub Profile URL</label>
              <input v-model="form.github_url" type="url" placeholder="https://github.com/username" class="input-field text-xs py-2 w-full" />
            </div>
            <div>
              <label class="block text-xs text-slate-400 font-mono mb-1">LinkedIn Profile URL</label>
              <input v-model="form.linkedin_url" type="url" placeholder="https://linkedin.com/in/username" class="input-field text-xs py-2 w-full" />
            </div>
            <div>
              <label class="block text-xs text-slate-400 font-mono mb-1">TryHackMe Profile URL</label>
              <input v-model="form.tryhackme_url" type="url" placeholder="https://tryhackme.com/p/username" class="input-field text-xs py-2 w-full" />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs text-slate-400 font-mono mb-1">HackTheBox Profile URL</label>
              <input v-model="form.htb_url" type="url" placeholder="https://app.hackthebox.com/profile/12345" class="input-field text-xs py-2 w-full" />
            </div>
          </div>
        </div>

        <!-- SECTION 4: Dynamic Custom Profile Fields (If Configured by Admin) -->
        <div v-if="customFields.length > 0" class="space-y-4 pt-4 border-t border-slate-800">
          <label class="block text-xs font-bold text-purple-400 font-mono uppercase tracking-wider">
            4. Required Club Profile Fields
          </label>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div v-for="field in customFields" :key="field.field_key">
              <label class="block text-xs text-slate-400 font-mono mb-1">
                {{ field.label }} <span v-if="field.required" class="text-rose-400">*</span>
              </label>

              <!-- Select Field -->
              <select 
                v-if="field.field_type === 'select'" 
                v-model="customForm[field.field_key]"
                class="input-field text-xs py-2 w-full bg-slate-900"
              >
                <option value="">Select option...</option>
                <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
              </select>

              <!-- Input Field -->
              <input 
                v-else 
                v-model="customForm[field.field_key]" 
                :type="field.field_type === 'number' ? 'number' : field.field_type === 'date' ? 'date' : 'text'"
                :placeholder="'Enter ' + field.label"
                class="input-field text-xs py-2 w-full"
              />
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="pt-4 border-t border-slate-800 flex justify-end">
          <button 
            @click="submitOnboarding" 
            :disabled="submitting || !selectedRole || !form.full_name.trim() || !form.student_id.trim()" 
            class="btn-neon-cyan py-3 px-8 text-xs font-bold font-mono uppercase tracking-wider w-full sm:w-auto"
          >
            {{ submitting ? 'Saving Credentials...' : 'Complete Initialization & Enter Platform' }}
          </button>
        </div>

      </div>
    </div>

    <!-- Minimal Footer -->
    <footer class="py-4 text-center text-[11px] font-mono text-slate-500">
      HackerXploit Cybersecurity Platform &bull; Operator System Initialization
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

const selectedRole = ref('Penetration Tester')
const submitting = ref(false)
const customFields = ref([])
const customForm = ref({})

const form = ref({
  full_name: authStore.user?.full_name || '',
  student_id: authStore.user?.student_id || '',
  academic_year: authStore.user?.academic_year || 'I',
  department: authStore.user?.department || 'Cyber Security',
  graduation_year: authStore.user?.graduation_year || 2026,
  bio: authStore.user?.bio || '',
  gmail: authStore.user?.gmail || '',
  phone_number: authStore.user?.phone_number || '',
  website_url: authStore.user?.website_url || '',
  github_url: authStore.user?.github_url || '',
  linkedin_url: authStore.user?.linkedin_url || '',
  tryhackme_url: authStore.user?.tryhackme_url || '',
  htb_url: authStore.user?.htb_url || ''
})

const isTeacher = computed(() => {
  return authStore.user?.role === 'teacher'
})

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

const fetchCustomFields = async () => {
  try {
    const res = await axios.get('/api/auth/custom-fields')
    const fields = res.data.fields || []
    customFields.value = fields.filter(f => f.active && (f.target_role === 'all' || f.target_role === authStore.user?.role))
  } catch (err) {
    console.error('Failed to load custom profile fields', err)
  }
}

const submitOnboarding = async () => {
  if (!selectedRole.value || !form.value.full_name.trim() || !form.value.student_id.trim()) {
    alert('Please fill in all required fields.')
    return
  }

  submitting.value = true
  try {
    const payload = {
      specialization_role: selectedRole.value,
      full_name: form.value.full_name.trim(),
      student_id: form.value.student_id.trim(),
      academic_year: form.value.academic_year,
      department: form.value.department.trim(),
      graduation_year: form.value.graduation_year,
      bio: form.value.bio.trim(),
      gmail: form.value.gmail.trim(),
      phone_number: form.value.phone_number.trim(),
      website_url: form.value.website_url.trim(),
      github_url: form.value.github_url.trim(),
      linkedin_url: form.value.linkedin_url.trim(),
      tryhackme_url: form.value.tryhackme_url.trim(),
      htb_url: form.value.htb_url.trim(),
      custom_fields: customForm.value
    }

    const res = await axios.post('/api/auth/onboarding', payload)
    authStore.user = res.data.user
    router.push('/dashboard')
  } catch (err) {
    console.error('Onboarding error details:', err)
    alert('Onboarding failed: ' + (err.response?.data?.error || err.message))
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchCustomFields()
})
</script>
