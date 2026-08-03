<template>
  <div class="space-y-8">
      <div v-if="loading" class="text-center py-16 text-slate-500 font-mono text-base">
        Loading student structured profile...
      </div>

      <div v-else-if="!profile" class="glass-panel p-12 text-center text-slate-400">
        Student profile not found.
      </div>

      <div v-else class="space-y-8">
        <!-- Header Banner -->
        <div class="glass-panel p-8 flex flex-col md:flex-row items-center justify-between gap-6 border-l-4 border-cyan-500">
          <div class="flex items-center space-x-6">
            <img :src="profile.overview.avatar_url || '/uploads/avatars/default.png'" @error="$event.target.src='/uploads/avatars/default.png'" class="w-28 h-28 rounded-2xl object-cover border-2 border-cyan-500/40 shadow-lg shadow-cyan-500/10" />
            <div>
              <div class="flex items-center gap-3">
                <h1 class="text-3xl font-bold text-white">{{ profile.overview.full_name || profile.overview.username }}</h1>
                <span class="text-sm font-mono px-3 py-1 rounded uppercase border bg-cyan-950/40 border-cyan-500/30 text-cyan-400">
                  {{ profile.overview.role }}
                </span>
              </div>
              <p class="text-sm font-mono text-cyan-400 mt-0.5">@{{ profile.overview.username }} | {{ profile.overview.email }}</p>
              <div class="flex items-center gap-2 text-sm font-mono text-slate-400 mt-1">
                <span class="px-2 py-0.5 rounded bg-[#9fef00]/10 border border-[#9fef00]/40 text-[#9fef00] font-bold">BADGE ID: {{ profile.overview.badge_id || ('HX-STU-' + String(profile.overview.id).padStart(4, '0')) }}</span>
                <span v-if="profile.overview.student_id">Student ID: {{ profile.overview.student_id }}</span>
              </div>
            </div>
          </div>

          <div class="flex flex-wrap gap-4 text-center">
            <div class="bg-slate-900/80 px-5 py-3 rounded-xl border border-slate-800">
              <p class="text-[11px] font-mono text-slate-400 uppercase">Active Hours</p>
              <p class="text-xl font-mono font-bold text-cyan-400">{{ profile.activity.total_hours }}h</p>
            </div>
            <div class="bg-slate-900/80 px-5 py-3 rounded-xl border border-slate-800">
              <p class="text-[11px] font-mono text-slate-400 uppercase">Leaderboard Score</p>
              <p class="text-xl font-mono font-bold text-amber-400">{{ profile.overview.leaderboard_score || 0 }}</p>
            </div>
          </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="flex border-b border-slate-800 space-x-1 text-base font-mono">
          <button @click="activeTab = 'overview'" :class="activeTab === 'overview' ? 'text-cyan-400 border-b-2 border-cyan-400 font-bold' : 'text-slate-400 hover:text-slate-200'" class="uppercase transition-colors flex items-center gap-1.5 pb-3 px-4">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
            Overview
          </button>
          <button @click="activeTab = 'activity'" :class="activeTab === 'activity' ? 'text-cyan-400 border-b-2 border-cyan-400 font-bold' : 'text-slate-400 hover:text-slate-200'" class="uppercase transition-colors flex items-center gap-1.5 pb-3 px-4">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
            Activity
          </button>
          <button @click="activeTab = 'academy'" :class="activeTab === 'academy' ? 'text-cyan-400 border-b-2 border-cyan-400 font-bold' : 'text-slate-400 hover:text-slate-200'" class="uppercase transition-colors flex items-center gap-1.5 pb-3 px-4">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
            Academy
          </button>
          <button @click="activeTab = 'trophy_case'" :class="activeTab === 'trophy_case' ? 'text-amber-400 border-b-2 border-amber-400 font-bold' : 'text-slate-400 hover:text-slate-200'" class="uppercase transition-colors flex items-center gap-1.5 pb-3 px-4">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"/></svg>
            Competitions & Trophy Case
            <span v-if="pendingCount > 0" class="bg-amber-400 text-black text-[11px] font-extrabold px-1.5 py-0.5 rounded-full leading-none">{{ pendingCount }}</span>
          </button>
        </div>

        <!-- TAB 1: OVERVIEW -->
        <div v-if="activeTab === 'overview'" class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="md:col-span-2 glass-panel p-6 space-y-6">
            <h3 class="text-base font-mono font-bold uppercase text-white border-b border-slate-800 pb-2">Bio & Focus Areas</h3>
            <p class="text-slate-300 text-base leading-relaxed whitespace-pre-line">{{ profile.overview.bio || 'No bio specified.' }}</p>

            <div class="pt-4 border-t border-slate-800 space-y-3">
              <h4 class="text-sm font-mono uppercase text-slate-400">Skills Taxonomy</h4>
              <div v-if="profile.overview.skills && profile.overview.skills.length" class="flex flex-wrap gap-2">
                <span v-for="skill in profile.overview.skills" :key="skill" class="px-2.5 py-1 text-sm font-mono rounded-lg bg-cyan-950/40 text-cyan-400 border border-cyan-500/30">
                  #{{ skill }}
                </span>
              </div>
              <p v-else class="text-sm text-slate-500 font-mono">No skill tags listed.</p>
            </div>
          </div>

          <div class="glass-panel p-6 space-y-4">
            <h3 class="text-base font-mono font-bold uppercase text-white border-b border-slate-800 pb-2">Academic & Contact Info</h3>
            <div class="space-y-3 text-sm font-mono">
              <div>
                <span class="text-slate-500 block">Academic Year:</span>
                <span class="text-cyan-400 font-bold">Year {{ profile.overview.academic_year || 'N/A' }}</span>
              </div>
              <div>
                <span class="text-slate-500 block">Department:</span>
                <span class="text-white">{{ profile.overview.department || 'Cyber Security' }}</span>
              </div>
              <div class="pt-2 border-t border-slate-800/80 space-y-2">
                <span class="text-amber-400 font-bold block mb-2 flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                  Private Contact (Admins/Teachers)
                </span>
                <p class="text-slate-300">Personal Gmail: <span class="text-white font-semibold">{{ profile.overview.personal_gmail || profile.overview.gmail || '—' }}</span></p>
                <p class="text-slate-300">Student Gmail: <span class="text-white font-semibold">{{ profile.overview.student_gmail || profile.overview.email || '—' }}</span></p>
                <p class="text-slate-300">Phone: <span class="text-white font-semibold">{{ profile.overview.phone_number || 'Not provided' }}</span></p>
                <div v-if="profile.overview.resume_url" class="pt-1">
                  <a :href="profile.overview.resume_url" target="_blank" class="text-sm text-cyan-400 hover:underline font-mono font-bold flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                    View / Download Resume
                  </a>
                </div>
                <p v-else class="text-sm text-slate-500 font-mono">No resume uploaded.</p>
              </div>
              <div class="pt-2 border-t border-slate-800/80">
                <span class="text-slate-500 block">Status:</span>
                <span class="text-emerald-400 font-bold uppercase">{{ profile.overview.status }}</span>
              </div>
              <div>
                <span class="text-slate-500 block">Joined:</span>
                <span class="text-white">{{ new Date(profile.overview.created_at).toLocaleDateString() }}</span>
              </div>
              <div>
                <span class="text-slate-500 block">Last Seen:</span>
                <span class="text-cyan-400">{{ profile.overview.last_seen_at ? new Date(profile.overview.last_seen_at).toLocaleString() : 'Never' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 2: ACTIVITY CHART -->
        <div v-if="activeTab === 'activity'" class="glass-panel p-8 space-y-8">
          <div class="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h3 class="text-xl font-bold text-white">30-Day Activity Matrix</h3>
              <p class="text-sm text-slate-400">Active hours accrued across HackerXploit subdomains.</p>
            </div>

            <div class="flex gap-4 font-mono text-sm">
              <span class="text-cyan-400">Club: {{ profile.activity.subdomain_breakdown.club }}h</span>
              <span class="text-purple-400">CTF: {{ profile.activity.subdomain_breakdown.ctf }}h</span>
              <span class="text-emerald-400">Intro: {{ profile.activity.subdomain_breakdown.intro }}h</span>
            </div>
          </div>

          <!-- CSS Bar Chart Visualization -->
          <div class="h-48 flex items-end gap-1 sm:gap-2 pt-8 pb-2 px-2 border-b border-slate-800">
            <div v-for="point in profile.activity.chart_data" :key="point.date" class="flex-1 flex flex-col items-center group relative">
              <div class="w-full bg-cyan-500/30 group-hover:bg-cyan-400 rounded-t transition-all" :style="{ height: Math.min(point.hours * 25 + 4, 180) + 'px' }"></div>
              <div class="absolute -top-8 hidden group-hover:block bg-slate-900 text-cyan-400 text-[11px] font-mono px-2 py-0.5 rounded border border-cyan-500/40 z-10 whitespace-nowrap shadow-lg">
                {{ point.date }}: {{ point.hours }}h
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 3: ACADEMY PROGRESS -->
        <div v-if="activeTab === 'academy'" class="space-y-4">
          <div v-if="profile.academy.length === 0" class="glass-panel p-8 text-center text-slate-400">
            No enrolled courses yet.
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div v-for="course in profile.academy" :key="course.course_id" class="glass-panel p-6 space-y-4 flex flex-col justify-between">
              <div class="space-y-3">
                <div class="flex justify-between items-start">
                  <h4 class="font-bold text-white text-base">{{ course.title }}</h4>
                  <span v-if="course.completed_at" class="text-[11px] font-mono px-2 py-0.5 rounded border border-emerald-500/40 bg-emerald-950/30 text-emerald-400">COMPLETED</span>
                </div>

                <div class="space-y-1">
                  <div class="flex justify-between text-sm font-mono text-slate-400">
                    <span>Progress</span>
                    <span>{{ course.progress_percent }}%</span>
                  </div>
                  <div class="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
                    <div class="bg-cyan-400 h-full rounded-full transition-all" :style="{ width: course.progress_percent + '%' }"></div>
                  </div>
                </div>

                <!-- Per-Module breakdown: completed modules render as a
                     "scratched" (struck-through) column but stay fully
                     legible - not just faded/hidden. -->
                <div v-if="course.modules_total" class="space-y-2 pt-2">
                  <div class="flex justify-between text-sm font-mono text-slate-400">
                    <span>Modules</span>
                    <span>{{ course.modules_completed }}/{{ course.modules_total }} completed</span>
                  </div>
                  <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    <div
                      v-for="mod in course.modules"
                      :key="mod.id"
                      class="rounded-lg border p-2.5 flex flex-col justify-between min-h-[62px]"
                      :class="moduleStatusClass(mod.status)"
                    >
                      <p
                        class="text-xs font-bold leading-snug line-clamp-2"
                        :class="mod.status === 'completed' ? 'line-through decoration-2 text-emerald-300' : 'text-slate-200'"
                      >
                        {{ mod.title }}
                      </p>
                      <div class="flex items-center justify-between mt-1.5 gap-1">
                        <span class="text-[10px] font-mono text-slate-500">{{ mod.notes_completed }}/{{ mod.notes_total }} notes</span>
                        <svg v-if="mod.status === 'completed'" class="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
                        <span v-else-if="mod.status === 'in_progress'" class="text-[9px] font-mono font-bold text-amber-400 uppercase flex-shrink-0">In Progress</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="course.certificate" class="pt-3 border-t border-slate-800 flex justify-between items-center text-sm font-mono">
                <span class="text-slate-400 flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                  Course Certificate
                </span>
                <a :href="course.certificate.file_path" target="_blank" class="text-cyan-400 hover:underline">Download PDF</a>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 4: TROPHY CASE -->
        <div v-if="activeTab === 'trophy_case'" class="space-y-6">
          <div v-if="profile.trophy_case.length === 0" class="glass-panel p-12 text-center text-slate-400">
            No competition applications or trophies found for this student.
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div v-for="item in profile.trophy_case" :key="item.participation_id" class="glass-panel p-6 space-y-4 border-l-4" :class="getTrophyBorderClass(item.result)">
              <div class="flex justify-between items-start gap-2">
                <div class="min-w-0">
                  <span class="text-xs font-mono uppercase px-2 py-0.5 rounded border border-slate-700 bg-slate-900 text-slate-300">
                    {{ item.category }}
                  </span>
                  <h4 class="font-bold text-white text-xl mt-1 truncate">{{ item.competition_title }}</h4>
                  <p class="text-xs text-slate-500 font-mono mt-0.5">Applied {{ formatDate(item.applied_at) }}</p>
                </div>

                <div class="flex flex-col items-end gap-1 shrink-0">
                  <span :class="getStatusBadgeClass(item.application_status)" class="text-sm font-mono px-3 py-1 rounded-lg border font-bold uppercase">
                    {{ formatStatus(item.application_status) }}
                  </span>
                  <span v-if="item.completion_status === 'pending_review'" class="text-[11px] font-mono px-2 py-0.5 rounded border border-violet-500/40 bg-violet-950/30 text-violet-300 font-bold uppercase">
                    Report Pending Review
                  </span>
                  <span v-else-if="item.completion_status === 'verified'" class="text-[11px] font-mono px-2 py-0.5 rounded border border-cyan-500/40 bg-cyan-950/30 text-cyan-300 font-bold uppercase">
                    Event Completed
                  </span>
                </div>
              </div>

              <!-- Result, once the event has actually been scored/wrapped up -->
              <div v-if="item.result && item.result !== 'participated'" class="flex items-center gap-2">
                <span :class="getResultBadgeClass(item.result)" class="text-sm font-mono px-3 py-1 rounded-lg border font-bold uppercase">
                  {{ item.result }}
                </span>
                <span v-if="item.placement_label" class="text-sm font-mono text-amber-300 font-bold">{{ item.placement_label }}</span>
              </div>
              <div v-else-if="item.self_reported_result && item.self_reported_result !== 'participated'" class="flex items-center gap-2">
                <span class="text-sm font-mono px-3 py-1 rounded-lg border border-slate-700 bg-slate-900 text-slate-300 font-bold uppercase">
                  Claimed: {{ item.self_reported_result }}
                </span>
                <span class="text-[11px] font-mono text-slate-500">(awaiting staff confirmation)</span>
              </div>

              <div v-if="item.application_screenshots && item.application_screenshots.length > 0" class="pt-2">
                <p class="text-xs font-mono text-slate-400 mb-1">Uploaded Registration Proof:</p>
                <div class="grid grid-cols-3 gap-1.5">
                  <a v-for="(shot, idx) in item.application_screenshots" :key="idx" :href="shot" target="_blank">
                    <img :src="shot" class="w-full h-24 object-cover rounded-xl border border-slate-800 hover:border-cyan-500/50 transition-colors" />
                  </a>
                </div>
              </div>

              <div v-if="item.event_photos && item.event_photos.length > 0" class="pt-1">
                <p class="text-xs font-mono text-slate-400 mb-1">Event Photos:</p>
                <div class="grid grid-cols-4 gap-1.5">
                  <a v-for="(photo, idx) in item.event_photos" :key="idx" :href="photo" target="_blank">
                    <img :src="photo" class="w-full h-14 object-cover rounded-lg border border-slate-800 hover:border-cyan-500/50 transition-colors" />
                  </a>
                </div>
              </div>

              <div v-if="item.user_certificate_file" class="pt-1">
                <p class="text-xs font-mono text-slate-400 mb-1">Student-Submitted Certificate:</p>
                <a :href="item.user_certificate_file" target="_blank">
                  <img :src="item.user_certificate_file" class="w-32 h-20 object-cover rounded-lg border border-slate-800 hover:border-cyan-500/50 transition-colors" />
                </a>
              </div>

              <p v-if="item.summary_notes" class="text-sm text-slate-300 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                "{{ item.summary_notes }}"
              </p>

              <div class="flex flex-wrap gap-3 text-sm font-mono">
                <a v-if="item.github_link" :href="item.github_link" target="_blank" class="text-cyan-400 hover:underline flex items-center gap-1">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
                  {{ item.github_link }}
                </a>
                <span v-if="item.prize_money" class="text-amber-400 font-bold">{{ item.prize_money }}</span>
              </div>

              <!-- Verification trail -->
              <p v-if="item.verified_by_name" class="text-xs font-mono text-slate-500">
                {{ item.application_status === 'rejected' ? 'Rejected' : 'Verified' }} by <span class="text-slate-300">{{ item.verified_by_name }}</span> on {{ formatDate(item.verified_at) }}
              </p>

              <!-- Reviewer actions: only while a decision is still pending -->
              <div v-if="item.application_status === 'pending_verification'" class="pt-3 border-t border-slate-800/80 flex gap-2">
                <button @click="reviewApplication(item, 'verified')" class="btn-neon-cyan text-xs px-3 py-1.5 font-bold flex-1">
                  ✓ Verify Application
                </button>
                <button @click="reviewApplication(item, 'rejected')" class="bg-rose-950 hover:bg-rose-900 text-rose-300 border border-rose-600/40 text-xs px-3 py-1.5 rounded font-mono font-bold flex-1">
                  ✕ Reject
                </button>
              </div>

              <div v-if="item.certificate" class="pt-3 border-t border-slate-800/80 flex justify-between items-center text-sm font-mono">
                <span class="text-amber-400 font-bold flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                  Winner Certificate
                </span>
                <a :href="item.certificate.file_path" target="_blank" class="btn-neon-cyan text-xs px-3 py-1">Download PDF</a>
              </div>
            </div>
          </div>
        </div>
      </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { usePreferences } from '../stores/preferences'

import axios from 'axios'

const route = useRoute()
const prefs = usePreferences()
const activeTab = ref('overview')
const profile = ref(null)
const loading = ref(true)

const pendingCount = computed(() => {
  if (!profile.value) return 0
  return profile.value.trophy_case.filter(t => t.application_status === 'pending_verification').length
})

const fetchProfile = async () => {
  loading.value = true
  const userId = route.params.id
  try {
    const res = await axios.get(`/api/teacher/students/${userId}`)
    profile.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const moduleStatusClass = (status) => {
  if (status === 'completed') return 'bg-emerald-950/20 border-emerald-500/30'
  if (status === 'in_progress') return 'bg-amber-950/20 border-amber-500/30'
  return 'bg-slate-900/60 border-slate-800'
}

const getResultBadgeClass = (res) => {
  if (res === 'winner') return 'border-amber-500/50 bg-amber-950/40 text-amber-300'
  if (res === 'runner_up') return 'border-slate-400/50 bg-slate-900 text-slate-200'
  return 'border-cyan-500/40 bg-cyan-950/30 text-cyan-400'
}

const getTrophyBorderClass = (res) => {
  if (res === 'winner') return 'border-amber-500'
  if (res === 'runner_up') return 'border-slate-400'
  return 'border-cyan-500'
}

const getStatusBadgeClass = (status) => {
  if (status === 'verified') return 'border-emerald-500/50 bg-emerald-950/40 text-emerald-300'
  if (status === 'rejected') return 'border-rose-500/50 bg-rose-950/40 text-rose-300'
  return 'border-amber-500/50 bg-amber-950/40 text-amber-300 animate-pulse'
}

const formatStatus = (status) => {
  if (status === 'pending_verification') return 'Pending Review'
  return status || 'Unknown'
}

const formatDate = (isoStr) => {
  if (!isoStr) return 'N/A'
  try {
    return new Date(isoStr).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata', day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: prefs.is12h.value })
  } catch (e) {
    return isoStr
  }
}

const reviewApplication = async (item, status) => {
  const verb = status === 'verified' ? 'verify' : 'reject'
  if (!confirm(`Are you sure you want to ${verb} this application?`)) return
  try {
    await axios.post(`/api/competitions/${item.competition_id}/applications/${item.participation_id}/verify`, { status })
    await fetchProfile()
  } catch (err) {
    alert(err.response?.data?.error || `Failed to ${verb} application`)
  }
}

onMounted(() => {
  fetchProfile()
})
</script>
