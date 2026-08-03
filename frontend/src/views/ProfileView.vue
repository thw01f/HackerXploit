<template>
  <div class="space-y-8">
      <div>
        <h1 class="text-3xl font-extrabold text-white">Settings</h1>
        <p class="text-slate-400 text-sm mt-1">Manage your account, security, notifications, appearance, and privacy.</p>
      </div>

      <!-- Settings Tab Bar -->
      <div class="flex flex-wrap gap-2 border-b border-[#1f293d] pb-px font-mono">
        <button
          v-for="tab in settingsTabs"
          :key="tab.value"
          @click="activeTab = tab.value"
          :class="[
            'px-4 py-2.5 text-sm font-bold rounded-t-lg border-b-2 transition-all -mb-px',
            activeTab === tab.value ? 'text-[#9fef00] border-[#9fef00]' : 'text-slate-400 border-transparent hover:text-white hover:border-slate-700'
          ]"
        >
          {{ tab.label }}
        </button>
      </div>

      <div v-show="activeTab === 'account'" class="space-y-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left: Avatar Upload & Profile Details -->
        <div class="lg:col-span-2 glass-panel p-8 space-y-6">
          <h3 class="text-lg font-bold text-white border-b border-slate-800 pb-3">Personal Profile</h3>

          <div class="flex items-center space-x-6">
            <div class="relative">
              <img :src="authStore.user?.avatar_url || '/uploads/avatars/default.png'" @error="$event.target.src='/uploads/avatars/default.png'" class="w-20 h-20 rounded-2xl object-cover border-2 border-cyan-500/40" />
            </div>
            <div>
              <label class="btn-ghost text-xs py-2 px-4 cursor-pointer inline-block">
                <span>Upload New Avatar</span>
                <input type="file" @change="uploadAvatar" class="hidden" accept="image/*" />
              </label>
              <p class="text-[11px] text-slate-400 mt-1">Files are scanned with ClamAV and compressed to WebP.</p>
            </div>
          </div>

          <!-- Locked Registration Details - collected once at signup, immutable
               afterwards; only an admin/teacher can correct these. -->
          <div class="pt-2 space-y-3">
            <h4 class="text-xs font-mono font-bold uppercase text-slate-400 tracking-wider">Registration Details (Locked)</h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-mono text-slate-500 uppercase mb-1">Full Name</label>
                <input :value="authStore.user?.full_name" type="text" disabled class="w-full bg-slate-900/60 border border-slate-800 rounded-lg px-3 py-2 text-slate-400 text-sm cursor-not-allowed" />
              </div>
              <div>
                <label class="block text-xs font-mono text-slate-500 uppercase mb-1">Username</label>
                <input :value="authStore.user?.username" type="text" disabled class="w-full bg-slate-900/60 border border-slate-800 rounded-lg px-3 py-2 text-slate-400 text-sm cursor-not-allowed" />
              </div>
              <div>
                <label class="block text-xs font-mono text-slate-500 uppercase mb-1">SRM Email Address</label>
                <input :value="authStore.user?.email" type="text" disabled class="w-full bg-slate-900/60 border border-slate-800 rounded-lg px-3 py-2 text-slate-400 text-sm cursor-not-allowed" />
              </div>
              <div>
                <label class="block text-xs font-mono text-slate-500 uppercase mb-1">Registration Number</label>
                <input :value="authStore.user?.registration_number" type="text" disabled class="w-full bg-slate-900/60 border border-slate-800 rounded-lg px-3 py-2 text-slate-400 text-sm cursor-not-allowed" />
              </div>
            </div>
            <p class="text-[11px] text-slate-500 font-mono">Locked after registration - contact an admin if any of these need correcting.</p>
          </div>

          <form @submit.prevent="updateProfile" class="space-y-4 pt-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-mono text-slate-300 uppercase mb-1">
                  Academic Year <span class="text-red-500 font-bold">*</span>
                </label>
                <select v-model="form.academic_year" required class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm">
                  <option value="I">1st Year (I)</option>
                  <option value="II">2nd Year (II)</option>
                  <option value="III">3rd Year (III)</option>
                  <option value="IV">4th Year (IV)</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-mono text-slate-300 uppercase mb-1">
                  Department <span class="text-red-500 font-bold">*</span>
                </label>
                <input v-model="form.department" type="text" required placeholder="Cyber Security" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" />
              </div>
            </div>

            <div>
              <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Bio / Research Focus</label>
              <textarea v-model="form.bio" rows="2" placeholder="Tell us about your cyber interests..." class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm"></textarea>
            </div>

            <!-- Resume Upload Section -->
            <div class="pt-4 border-t border-slate-800 space-y-3">
              <h4 class="text-xs font-mono font-bold uppercase text-cyan-400 tracking-wider flex items-center gap-1.5">
                <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <span>Curriculum Vitae / Resume Upload</span>
              </h4>

              <div class="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
                <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div>
                    <p class="text-xs font-bold text-white">Upload Your CV / Resume (PDF)</p>
                    <p class="text-[11px] text-slate-400 font-mono mt-0.5">ClamAV scanned · Max <strong class="text-white">2 MB</strong> · PDF only</p>
                  </div>

                  <div class="flex items-center gap-2">
                    <!-- Re-upload / Upload -->
                    <label class="btn-ghost text-xs py-1.5 px-3 border border-cyan-500/40 text-cyan-300 font-bold cursor-pointer whitespace-nowrap hover:bg-cyan-500/10">
                      <span>{{ form.resume_url ? 'Replace' : 'Upload PDF' }}</span>
                      <input type="file" @change="uploadResume" class="hidden" accept=".pdf" />
                    </label>
                    <!-- Delete -->
                    <button v-if="form.resume_url" @click="deleteResume" type="button"
                      class="p-1.5 text-red-400 border border-red-500/40 rounded-lg hover:bg-red-500/20 transition-all" title="Remove Resume">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                      </svg>
                    </button>
                  </div>
                </div>

                <!-- Attached indicator -->
                <div v-if="form.resume_url" class="flex items-center gap-2">
                  <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                  <span class="text-xs text-emerald-400 font-mono font-bold">Resume Attached</span>
                  <a :href="form.resume_url" target="_blank" class="text-xs text-cyan-400 hover:underline font-mono">[View PDF]</a>
                </div>
                <p v-else class="text-[11px] text-slate-500 font-mono">No resume uploaded yet.</p>
              </div>
            </div>

            <!-- Private Contact Info (Confidential) -->
            <div class="pt-4 border-t border-slate-800 space-y-4">
              <div class="flex items-center justify-between">
                <h4 class="text-xs font-mono font-bold uppercase text-cyan-400 tracking-wider flex items-center gap-1.5">
                  <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                  </svg>
                  <span>Private Contact Information</span>
                </h4>
                <span class="text-[10px] text-slate-400 font-mono">Visible ONLY to Teachers & Platform Admins</span>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-mono text-slate-300 uppercase mb-1">
                    Personal Gmail Address <span class="text-red-500 font-bold">*</span>
                  </label>
                  <input v-model="form.personal_gmail" type="email" required placeholder="yourname@gmail.com" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono" />
                </div>
                <div>
                  <label class="block text-xs font-mono text-slate-300 uppercase mb-1">
                    Phone Number / WhatsApp <span class="text-red-500 font-bold">*</span>
                  </label>
                  <input v-model="form.phone_number" type="tel" required placeholder="e.g. +91 XXXXXXXXXX" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono" />
                </div>
              </div>
            </div>

            <!-- Social & Portfolio Connections -->
            <div class="pt-4 border-t border-slate-800 space-y-4">
              <h4 class="text-xs font-mono font-bold uppercase text-[#9fef00] tracking-wider">Cyber Portfolios & Social Links</h4>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-mono text-slate-300 uppercase mb-1">
                    LinkedIn Profile URL <span class="text-red-500 font-bold">*</span>
                  </label>
                  <input v-model="form.linkedin_url" type="url" required placeholder="https://linkedin.com/in/username" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono" />
                </div>
                <div>
                  <label class="block text-xs font-mono text-slate-300 uppercase mb-1">
                    GitHub Profile URL <span class="text-red-500 font-bold">*</span>
                  </label>
                  <input v-model="form.github_url" type="url" required placeholder="https://github.com/username" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono" />
                </div>
                <div>
                  <label class="block text-xs font-mono text-slate-300 uppercase mb-1">
                    TryHackMe Profile URL <span class="text-red-500 font-bold">*</span>
                  </label>
                  <input v-model="form.tryhackme_url" type="url" required placeholder="https://tryhackme.com/p/username" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono" />
                </div>
                <div>
                  <label class="block text-xs font-mono text-slate-300 uppercase mb-1">Portfolio Website URL</label>
                  <input v-model="form.website_url" type="url" placeholder="https://yourname.dev" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono" />
                </div>
                <div class="sm:col-span-2">
                  <label class="block text-xs font-mono text-slate-300 uppercase mb-1">HackTheBox Profile URL</label>
                  <input v-model="form.htb_url" type="url" placeholder="https://app.hackthebox.com/profile/12345" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs font-mono" />
                </div>
              </div>
            </div>

            <button type="submit" class="btn-neon-cyan text-xs py-2.5 px-6 font-bold uppercase tracking-wider flex items-center gap-2">
              <svg class="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
              <span>Save & Sync Settings</span>
            </button>
          </form>
        </div>

        <!-- Right: Active Device Sessions -->
        <div class="glass-panel p-6 space-y-4">
          <div class="border-b border-slate-800 pb-3">
            <div class="flex items-center justify-between">
              <h3 class="text-sm font-mono font-bold text-white uppercase">Active Device Sessions</h3>
              <span class="text-[10px] text-slate-500 font-mono">{{ devices.length }} active</span>
            </div>
            <div class="flex gap-2 mt-3 flex-wrap">
              <button v-if="devices.length > 1" @click="logoutAllOthers" class="text-[10px] font-mono font-bold py-1 px-2.5 rounded border border-red-500/40 text-red-400 hover:bg-red-500/10 transition-all">
                Revoke All Other Devices
              </button>
            </div>
          </div>

          <div class="space-y-2 max-h-96 overflow-y-auto pr-1">
            <div v-for="s in devices" :key="s.id"
              :class="s.is_current_device ? 'border-cyan-500/50 bg-cyan-950/20' : isToolSession(s) ? 'border-amber-500/20 bg-amber-950/10' : 'border-slate-800 bg-slate-900/60'"
              class="p-3 rounded-lg border space-y-1">
              <div class="flex justify-between items-start gap-2">
                <div class="min-w-0 flex items-start gap-2">
                  <svg class="w-7 h-7 p-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="deviceIconPath(s)"/>
                  </svg>
                  <div class="min-w-0">
                    <span class="text-[11px] font-bold text-white flex items-center gap-1.5 flex-wrap">
                      <span class="truncate max-w-[160px]">{{ friendlyAgent(effectiveAgent(s)) }}</span>
                      <span v-if="s.is_current_device" class="text-[9px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 font-mono border border-cyan-500/30 shrink-0">THIS DEVICE</span>
                      <span v-else-if="isToolSession(s)" class="text-[9px] px-1.5 py-0.5 rounded bg-amber-950/60 text-amber-400 font-mono border border-amber-500/30 shrink-0">API/TOOL</span>
                    </span>
                    <p class="text-[10px] font-mono text-cyan-400 mt-0.5">{{ s.ip_address }}</p>
                    <p class="text-[10px] text-slate-500 font-mono" :title="formatDateTime(s.last_active_at || s.created_at)">
                      Active {{ timeAgo(s.last_active_at || s.created_at) }}
                    </p>
                  </div>
                </div>
                <button v-if="!s.is_current_device" @click="revokeDevice(s.id)"
                  class="shrink-0 p-1 text-red-400 hover:text-red-300 border border-red-500/30 rounded hover:bg-red-500/10 transition-all" title="Revoke">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
              </div>
            </div>
            <p v-if="devices.length === 0" class="text-xs text-slate-500 font-mono text-center py-4">No active sessions found.</p>
          </div>
        </div>
      </div>

      <!-- Security: Change Password -->
      <div class="glass-panel p-8 bg-[#111927] border border-[#1f293d] space-y-6">
        <div class="border-b border-[#1f293d] pb-4">
          <h3 class="text-lg font-bold text-white font-mono">Security</h3>
          <p class="text-slate-400 text-xs mt-1">Change your password. This signs you out on every other device and revokes CTFd SSO tokens - only this session stays active.</p>
        </div>

        <form @submit.prevent="submitChangePassword" class="space-y-4 max-w-md">
          <div v-if="passwordError" class="p-3 bg-rose-950/80 border border-rose-500/50 text-rose-300 rounded-lg text-xs font-bold">
            {{ passwordError }}
          </div>
          <div v-if="passwordSuccess" class="p-3 bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 rounded-lg text-xs font-bold">
            {{ passwordSuccess }}
          </div>

          <div>
            <label class="block text-xs font-mono text-slate-400 uppercase mb-1">Current Password</label>
            <input v-model="passwordForm.current_password" type="password" required class="input-field w-full" placeholder="••••••••••••" />
          </div>
          <div>
            <label class="block text-xs font-mono text-slate-400 uppercase mb-1">New Password</label>
            <input v-model="passwordForm.new_password" type="password" required minlength="8" class="input-field w-full" placeholder="••••••••••••" />
          </div>
          <div>
            <label class="block text-xs font-mono text-slate-400 uppercase mb-1">Confirm New Password</label>
            <input v-model="passwordForm.confirm_password" type="password" required minlength="8" class="input-field w-full" placeholder="••••••••••••" />
          </div>

          <button type="submit" :disabled="passwordSubmitting" class="btn-neon-cyan text-xs py-2.5 px-6 font-bold">
            {{ passwordSubmitting ? 'Updating...' : 'Update Password' }}
          </button>
        </form>
      </div>
      </div>

      <!-- Notification Preferences -->
      <div v-show="activeTab === 'notifications'" class="glass-panel p-8 bg-[#111927] border border-[#1f293d] space-y-6">
        <div class="border-b border-[#1f293d] pb-4">
          <h3 class="text-lg font-bold text-white font-mono">Notification Preferences</h3>
          <p class="text-slate-400 text-xs mt-1">The in-app notification bell always shows these. These toggles control whether HackerXploit ALSO emails you.</p>
        </div>

        <div class="space-y-3 max-w-xl">
          <label class="flex items-center justify-between p-4 rounded-xl border border-slate-800 bg-slate-900/60 cursor-pointer">
            <div>
              <span class="text-sm font-bold text-white block">Inbox Messages</span>
              <span class="text-xs text-slate-400">New messages and replies sent to you (only if you're offline at the time).</span>
            </div>
            <input type="checkbox" v-model="notifPrefs.email_inbox_messages" class="w-5 h-5 accent-[#9fef00] shrink-0 ml-4" />
          </label>

          <label class="flex items-center justify-between p-4 rounded-xl border border-slate-800 bg-slate-900/60 cursor-pointer">
            <div>
              <span class="text-sm font-bold text-white block">Announcements</span>
              <span class="text-xs text-slate-400">Role changes, new profile fields, and other admin broadcasts.</span>
            </div>
            <input type="checkbox" v-model="notifPrefs.email_announcements" class="w-5 h-5 accent-[#9fef00] shrink-0 ml-4" />
          </label>

          <label class="flex items-center justify-between p-4 rounded-xl border border-slate-800 bg-slate-900/60 cursor-pointer">
            <div>
              <span class="text-sm font-bold text-white block">Account & Approval Updates</span>
              <span class="text-xs text-slate-400">Approved, rejected, or suspended status changes to your account.</span>
            </div>
            <input type="checkbox" v-model="notifPrefs.email_account_updates" class="w-5 h-5 accent-[#9fef00] shrink-0 ml-4" />
          </label>
        </div>

        <div class="flex items-center gap-3">
          <button @click="saveNotifPrefs" :disabled="notifSaving" class="btn-neon-cyan text-xs py-2.5 px-6 font-bold">
            {{ notifSaving ? 'Saving...' : 'Save Preferences' }}
          </button>
          <span v-if="notifSaved" class="text-xs text-emerald-400 font-bold">✓ Saved</span>
        </div>
      </div>

      <!-- Appearance -->
      <div v-show="activeTab === 'appearance'" class="glass-panel p-8 bg-[#111927] border border-[#1f293d] space-y-6">
        <div class="border-b border-[#1f293d] pb-4">
          <h3 class="text-lg font-bold text-white font-mono">Appearance</h3>
          <p class="text-slate-400 text-xs mt-1">Choose how HackerXploit looks on this device.</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-xl">
          <button
            v-for="opt in themeOptions"
            :key="opt.value"
            @click="theme.setMode(opt.value)"
            :class="[
              'flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all font-mono',
              theme.mode.value === opt.value ? 'border-[#9fef00] bg-[#9fef00]/10' : 'border-slate-800 bg-slate-900/60 hover:border-slate-700'
            ]"
          >
            <svg class="w-6 h-6" :class="theme.mode.value === opt.value ? 'text-[#9fef00]' : 'text-slate-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="opt.icon"/>
            </svg>
            <span :class="theme.mode.value === opt.value ? 'text-white font-bold' : 'text-slate-400'" class="text-xs uppercase tracking-wide">
              {{ opt.label }}
            </span>
          </button>
        </div>
        <p class="text-[11px] text-slate-500 font-mono">
          "System" follows your OS/browser's light or dark setting automatically and switches live if you change it.
        </p>

        <div class="border-t border-[#1f293d] pt-6 space-y-3">
          <div>
            <h4 class="text-sm font-bold text-white font-mono">Time Format</h4>
            <p class="text-slate-400 text-xs mt-1">Applies to every clock and timestamp across the platform.</p>
          </div>
          <div class="grid grid-cols-2 gap-3 max-w-xs">
            <button
              v-for="opt in timeFormatOptions"
              :key="opt.value"
              @click="prefs.setTimeFormat(opt.value)"
              :class="[
                'flex flex-col items-center gap-1 p-3 rounded-xl border-2 transition-all font-mono',
                prefs.timeFormat.value === opt.value ? 'border-[#9fef00] bg-[#9fef00]/10' : 'border-slate-800 bg-slate-900/60 hover:border-slate-700'
              ]"
            >
              <span :class="prefs.timeFormat.value === opt.value ? 'text-white font-bold' : 'text-slate-400'" class="text-sm tabular-nums">
                {{ opt.preview }}
              </span>
              <span :class="prefs.timeFormat.value === opt.value ? 'text-[#9fef00] font-bold' : 'text-slate-500'" class="text-[11px] uppercase tracking-wide">
                {{ opt.label }}
              </span>
            </button>
          </div>
        </div>

        <div class="border-t border-[#1f293d] pt-6 space-y-3">
          <div>
            <h4 class="text-sm font-bold text-white font-mono">Font Size</h4>
            <p class="text-slate-400 text-xs mt-1">Scales text and UI elements across the whole platform.</p>
          </div>
          <div class="grid grid-cols-4 gap-3 max-w-lg">
            <button
              v-for="opt in fontScaleOptions"
              :key="opt.value"
              @click="prefs.setFontScale(opt.value)"
              :class="[
                'flex flex-col items-center gap-1 p-3 rounded-xl border-2 transition-all font-mono',
                prefs.fontScale.value === opt.value ? 'border-[#9fef00] bg-[#9fef00]/10' : 'border-slate-800 bg-slate-900/60 hover:border-slate-700'
              ]"
            >
              <span :class="[prefs.fontScale.value === opt.value ? 'text-white font-bold' : 'text-slate-400', opt.previewClass]">
                Aa
              </span>
              <span :class="prefs.fontScale.value === opt.value ? 'text-[#9fef00] font-bold' : 'text-slate-500'" class="text-[11px] uppercase tracking-wide">
                {{ opt.label }}
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Privacy & Data Governance (embedded) -->
      <div v-show="activeTab === 'privacy'" class="glass-panel p-8 bg-[#111927] border border-[#1f293d] space-y-6">
        <div class="border-b border-[#1f293d] pb-4">
          <h3 class="text-lg font-bold text-white font-mono">Privacy & Data Governance</h3>
          <p class="text-slate-400 text-xs mt-1">Manage public profile visibility, export your data, or request deletion.</p>
        </div>

        <!-- Public Profile Toggles -->
        <div class="space-y-3">
          <h4 class="font-mono font-bold text-xs text-white uppercase border-b border-[#1f293d] pb-2">Public Profile Settings</h4>
          <div class="p-4 rounded-xl bg-[#090d16] border border-[#1f293d] flex items-center justify-between">
            <div>
              <p class="font-mono font-bold text-sm text-white">Make Profile Publicly Accessible</p>
              <p class="text-xs text-slate-400 font-mono mt-0.5">Enables public portfolio at /u/{{ authStore.user?.username }}</p>
            </div>
            <input type="checkbox" v-model="privacy.is_public" @change="savePrivacy" class="w-5 h-5 text-[#9fef00] bg-slate-900 border-slate-700 rounded cursor-pointer" />
          </div>
          <div class="p-4 rounded-xl bg-[#090d16] border border-[#1f293d] flex items-center justify-between" :class="{ 'opacity-40 pointer-events-none': !privacy.is_public }">
            <div>
              <p class="font-mono font-bold text-sm text-white">Show Activity Hours</p>
              <p class="text-xs text-slate-400 font-mono mt-0.5">Display total platform lab & learning hours publicly</p>
            </div>
            <input type="checkbox" v-model="privacy.show_activity_hours" :disabled="!privacy.is_public" @change="savePrivacy" class="w-5 h-5 text-[#9fef00] bg-slate-900 border-slate-700 rounded cursor-pointer" />
          </div>
          <div class="p-4 rounded-xl bg-[#090d16] border border-[#1f293d] flex items-center justify-between" :class="{ 'opacity-40 pointer-events-none': !privacy.is_public }">
            <div>
              <p class="font-mono font-bold text-sm text-white">Show Verified Certificates</p>
              <p class="text-xs text-slate-400 font-mono mt-0.5">Displays issued platform completion certificates publicly</p>
            </div>
            <input type="checkbox" v-model="privacy.show_certificates" :disabled="!privacy.is_public" @change="savePrivacy" class="w-5 h-5 text-[#9fef00] bg-slate-900 border-slate-700 rounded cursor-pointer" />
          </div>
        </div>

        <!-- Data Exports -->
        <div class="space-y-3 pt-4 border-t border-[#1f293d]">
          <h4 class="font-mono font-bold text-xs text-white uppercase border-b border-[#1f293d] pb-2">Data Exports</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button @click="window.open('/api/portfolio/export-pdf', '_blank')" class="p-4 rounded-xl bg-[#090d16] border border-[#1f293d] text-left hover:border-cyan-500/30 transition-all">
              <p class="font-mono font-bold text-sm text-cyan-400">Portfolio PDF</p>
              <p class="text-xs text-slate-400 mt-1">Export a formatted 2-page PDF portfolio summary.</p>
            </button>
            <button @click="window.open('/api/profile/export-my-data', '_blank')" class="p-4 rounded-xl bg-[#090d16] border border-[#1f293d] text-left hover:border-[#9fef00]/30 transition-all">
              <p class="font-mono font-bold text-sm text-[#9fef00]">Full Archive (.zip)</p>
              <p class="text-xs text-slate-400 mt-1">Download all your data as a ZIP archive.</p>
            </button>
          </div>
        </div>

        <!-- Danger Zone -->
        <div class="space-y-3 pt-4 border-t border-[#1f293d]">
          <h4 class="font-mono font-bold text-xs text-red-400 uppercase border-b border-[#1f293d] pb-2">Danger Zone</h4>
          <div class="p-4 rounded-xl bg-red-950/30 border border-red-500/40 space-y-3">
            <p class="font-mono font-bold text-sm text-red-400">Request Account Deletion</p>
            <p class="text-xs text-slate-400">Deletion requests are queued for admin review to preserve certificate integrity.</p>
            <button @click="showDeleteModal = true" class="btn-ghost text-xs font-mono text-red-400 border-red-500/50 hover:bg-red-950/60 py-2 px-4">
              Request Account Deletion
            </button>
          </div>
        </div>
      </div>

      <!-- Deletion Request Modal -->
      <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
        <div class="w-full max-w-md glass-panel p-6 rounded-xl border border-red-500/40 bg-[#111927] space-y-4">
          <h3 class="font-mono font-bold text-lg text-red-400">Request Account Deletion</h3>
          <p class="text-xs font-mono text-slate-300">Please explain your reason. An administrator will review shortly.</p>
          <textarea v-model="deleteReason" rows="3" placeholder="Reason for deletion request..." class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs"></textarea>
          <div class="flex justify-end space-x-3 pt-2">
            <button @click="showDeleteModal = false" class="btn-ghost text-xs font-mono py-2 px-4">Cancel</button>
            <button :disabled="submittingDelete" @click="submitDeleteRequest" class="btn-ghost text-xs font-mono text-red-400 border-red-500/50 py-2 px-4">
              {{ submittingDelete ? 'Submitting...' : 'Submit Request' }}
            </button>
          </div>
        </div>
      </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useTheme } from '../stores/theme'
import { usePreferences } from '../stores/preferences'

const authStore = useAuthStore()
const router = useRouter()
const theme = useTheme()
const prefs = usePreferences()

const settingsTabs = [
  { value: 'account', label: 'Account Settings & Security' },
  { value: 'notifications', label: 'Notifications' },
  { value: 'appearance', label: 'Appearance' },
  { value: 'privacy', label: 'Privacy & Data' }
]
const activeTab = ref('account')

const themeOptions = [
  { value: 'light', label: 'Light', icon: 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z' },
  { value: 'dark', label: 'Dark', icon: 'M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z' },
  { value: 'system', label: 'System', icon: 'M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25' }
]

const timeFormatOptions = [
  { value: '12h', label: '12-Hour', preview: '2:30 PM' },
  { value: '24h', label: '24-Hour', preview: '14:30' }
]

const fontScaleOptions = [
  { value: 'sm', label: 'Small', previewClass: 'text-xs' },
  { value: 'md', label: 'Default', previewClass: 'text-sm' },
  { value: 'lg', label: 'Large', previewClass: 'text-base' },
  { value: 'xl', label: 'X-Large', previewClass: 'text-lg' }
]

const form = ref({
  academic_year: authStore.user?.academic_year || 'I',
  department: authStore.user?.department || '',
  bio: authStore.user?.bio || '',
  personal_gmail: authStore.user?.personal_gmail || authStore.user?.gmail || '',
  phone_number: authStore.user?.phone_number || '',
  resume_url: authStore.user?.resume_url || '',
  website_url: authStore.user?.website_url || '',
  github_url: authStore.user?.github_url || '',
  linkedin_url: authStore.user?.linkedin_url || '',
  tryhackme_url: authStore.user?.tryhackme_url || '',
  htb_url: authStore.user?.htb_url || ''
})

const devices = ref([])

const fetchDevices = async () => {
  try {
    const res = await axios.get('/api/club/profile/devices')
    devices.value = res.data.devices
  } catch (err) {
    console.error(err)
  }
}

// Security: change password
const passwordForm = ref({ current_password: '', new_password: '', confirm_password: '' })
const passwordSubmitting = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')

const submitChangePassword = async () => {
  passwordError.value = ''
  passwordSuccess.value = ''
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = 'New password and confirmation do not match'
    return
  }
  if (passwordForm.value.new_password.length < 8) {
    passwordError.value = 'New password must be at least 8 characters'
    return
  }
  passwordSubmitting.value = true
  try {
    await axios.post('/api/auth/change-password', {
      current_password: passwordForm.value.current_password,
      new_password: passwordForm.value.new_password
    })
    passwordForm.value = { current_password: '', new_password: '', confirm_password: '' }
    // A password change is a credential event - log the user out of this
    // session too (the backend already revokes every OTHER session/CTFd SSO
    // token), so they consciously re-authenticate with the new password
    // rather than keep working under a session tied to the old one.
    passwordSuccess.value = 'Password changed successfully. Logging you out for security - please sign in again with your new password.'
    setTimeout(async () => {
      await authStore.logout()
      router.push('/login')
    }, 2000)
  } catch (err) {
    passwordError.value = err.response?.data?.error || 'Failed to change password'
  } finally {
    passwordSubmitting.value = false
  }
}

// Notification preferences
const notifPrefs = ref({ email_inbox_messages: true, email_announcements: false, email_account_updates: true })
const notifSaving = ref(false)
const notifSaved = ref(false)

const fetchNotifPrefs = async () => {
  try {
    const res = await axios.get('/api/notifications/preferences')
    notifPrefs.value = {
      email_inbox_messages: res.data.email_inbox_messages,
      email_announcements: res.data.email_announcements,
      email_account_updates: res.data.email_account_updates
    }
  } catch (err) {
    console.error(err)
  }
}

const saveNotifPrefs = async () => {
  notifSaving.value = true
  notifSaved.value = false
  try {
    await axios.put('/api/notifications/preferences', notifPrefs.value)
    notifSaved.value = true
    setTimeout(() => { notifSaved.value = false }, 2500)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to save notification preferences')
  } finally {
    notifSaving.value = false
  }
}



const uploadAvatar = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  formData.append('feature', 'avatars')

  try {
    const res = await axios.post('/api/uploads', formData)
    await axios.put('/api/club/profile', { avatar_url: res.data.url })
    await authStore.fetchMe()
    alert('Avatar uploaded & processed through security pipeline successfully!')
  } catch (err) {
    alert(err.response?.data?.error || 'Avatar upload failed')
  }
}

const uploadResume = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  // 2MB client-side guard
  if (file.size > 2 * 1024 * 1024) {
    alert('Resume must be under 2 MB. Please compress your PDF and try again.')
    e.target.value = ''
    return
  }
  // If re-uploading, delete old file first
  if (form.value.resume_url) {
    try { await axios.delete('/api/club/profile/resume') } catch (_) {}
  }
  const formData = new FormData()
  formData.append('file', file)
  formData.append('feature', 'resumes')
  try {
    const res = await axios.post('/api/uploads', formData)
    form.value.resume_url = res.data.url
    await axios.put('/api/club/profile', { resume_url: res.data.url })
    await authStore.fetchMe()
    alert('Resume uploaded & scanned successfully!')
  } catch (err) {
    alert(err.response?.data?.error || 'Resume upload failed')
  }
}

const deleteResume = async () => {
  if (!confirm('Remove your uploaded resume?')) return
  try {
    await axios.delete('/api/club/profile/resume')
    form.value.resume_url = ''
    await authStore.fetchMe()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete resume')
  }
}

const updateProfile = async () => {
  try {
    await axios.put('/api/club/profile', form.value)
    await authStore.fetchMe()
    alert('Profile updated successfully!')
  } catch (err) {
    alert('Failed to update profile')
  }
}

const revokeDevice = async (id) => {
  if (confirm('Revoke this device session server-side immediately?')) {
    try {
      await axios.delete(`/api/club/profile/devices/${id}`)
      await fetchDevices()
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to revoke device')
    }
  }
}

const logoutAllOthers = async () => {
  if (confirm('Log out all other active devices except this one?')) {
    try {
      await axios.delete('/api/club/profile/devices/others')
      await fetchDevices()
    } catch (err) { alert('Failed to revoke other devices') }
  }
}

// Browser/OS/device-type detection for the device session cards. Werkzeug's
// request.user_agent does zero parsing by default (its __bool__ only checks
// .browser, which stays unset without a custom parser class) - the backend
// only ever gives us the raw header string, so this does its own lightweight
// matching rather than relying on anything upstream.
const detectBrowser = (ua) => {
  // Order matters: Edge/Opera/Chromium UAs all also contain "Chrome/", and
  // Chrome's UA also contains "Safari/" - most-specific match first.
  let m
  if ((m = ua.match(/Edg\/(\d+)/))) return `Edge ${m[1]}`
  if ((m = ua.match(/OPR\/(\d+)/))) return `Opera ${m[1]}`
  if ((m = ua.match(/Firefox\/(\d+)/))) return `Firefox ${m[1]}`
  if ((m = ua.match(/Chromium\/(\d+)/))) return `Chromium ${m[1]}`
  if ((m = ua.match(/Chrome\/(\d+)/))) return `Chrome ${m[1]}`
  if (/Safari/.test(ua) && (m = ua.match(/Version\/(\d+)/))) return `Safari ${m[1]}`
  return null
}

const detectOS = (ua) => {
  if (/Windows NT 10/.test(ua)) return 'Windows 10/11'
  if (/Windows NT/.test(ua)) return 'Windows'
  if (/Mac OS X/.test(ua)) return 'macOS'
  if (/CrOS/.test(ua)) return 'ChromeOS'
  if (/Android/.test(ua)) return 'Android'
  if (/iPhone|iPad|iPod/.test(ua)) return 'iOS'
  if (/Linux/.test(ua)) return 'Linux'
  return null
}

const isMobileUA = (ua) => /Mobile|Android|iPhone|iPad/.test(ua)

// Returns a concise browser/agent label
const friendlyAgent = (ua) => {
  if (!ua || ua === 'Unknown') return 'Unknown Device'
  if (ua.startsWith('curl/')) return 'cURL ' + ua.split('/')[1]
  if (ua.startsWith('Werkzeug/')) return 'Werkzeug ' + ua.split('/')[1]
  if (ua.startsWith('Python-urllib/')) return 'Python urllib'
  if (ua.startsWith('python-requests/')) return 'Python requests'

  const browser = detectBrowser(ua)
  const os = detectOS(ua)
  if (browser && os) return `${browser} on ${os}`
  if (browser) return browser
  if (os) return os
  return ua.substring(0, 40)
}

const formatDateTime = (isoStr) => {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleString(undefined, { hour12: prefs.is12h.value })
}

// Concise relative time for "Active X ago" - a raw timestamp answers "when",
// but what actually matters for reviewing sessions is "is this recent or
// stale", which a relative label answers at a glance (full timestamp is
// still available via the title tooltip).
const timeAgo = (dateStr) => {
  if (!dateStr) return 'unknown'
  const seconds = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000)
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}d ago`
  return new Date(dateStr).toLocaleDateString()
}

// SVG path for a small device-type icon on each session card
// Sessions created before the request.user_agent parsing fix (see
// backend/app/routes/auth.py) have user_agent='Unknown' but their
// device_label happens to hold the real header (it was always read
// directly, bypassing the buggy check) - fall back to it so old sessions
// still get a real label instead of "Unknown Device" forever.
const effectiveAgent = (s) => (s.user_agent && s.user_agent !== 'Unknown' ? s.user_agent : s.device_label)

const deviceIconPath = (s) => {
  if (isToolSession(s)) return 'M10 20l4-16m4 4l4 4-4 4M6 8l-4 4 4 4' // </>
  const ua = effectiveAgent(s)
  if (ua && isMobileUA(ua)) return 'M12 18h.01M8 21h8a1 1 0 001-1V4a1 1 0 00-1-1H8a1 1 0 00-1 1v16a1 1 0 001 1z' // phone
  return 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' // monitor
}

// True if session came from a tool (curl, Werkzeug etc.)
const isToolSession = (s) => {
  const ua = effectiveAgent(s)
  if (!ua) return false
  return ['curl/', 'Werkzeug/', 'Python-urllib/', 'python-requests/'].some(t => ua.startsWith(t))
}

// Privacy settings
const privacy = ref({ is_public: false, show_activity_hours: true, show_certificates: true })
const showDeleteModal = ref(false)
const deleteReason = ref('')
const submittingDelete = ref(false)

const fetchPrivacy = async () => {
  try { const r = await axios.get('/api/profile/privacy'); privacy.value = r.data } catch (_) {}
}
const savePrivacy = async () => {
  try { const r = await axios.post('/api/profile/privacy', privacy.value); privacy.value = r.data } catch (_) {}
}
const submitDeleteRequest = async () => {
  submittingDelete.value = true
  try {
    await axios.post('/api/profile/request-deletion', { reason: deleteReason.value })
    alert('Deletion request submitted for admin review.')
    showDeleteModal.value = false
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to submit.')
  } finally { submittingDelete.value = false }
}

onMounted(() => { fetchDevices(); fetchPrivacy(); fetchNotifPrefs() })
</script>
