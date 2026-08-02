<template>
  <div class="space-y-8">
      
      <!-- Title & Subtitle -->
      <div class="text-center max-w-xl mx-auto mb-8 space-y-2">
        <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#151f30] border border-[#9fef00]/30 text-[#9fef00] text-xs font-mono">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#9fef00] opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-[#9fef00]"></span>
          </span>
          <span>IDENTITY BADGE</span>
        </div>
        <h1 class="text-3xl font-extrabold text-white font-mono">Virtual Member ID Card</h1>
        <p class="text-slate-400 text-sm">
          {{ authStore.isTeacher ? 'Official faculty credentials with event scanning & QR attendance access.' : 'Official club credentials with live event participation status & QR verification.' }}
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="py-16 text-center font-mono text-sm text-slate-500">
        Loading ID badge credentials...
      </div>

      <!-- Error State -->
      <div v-else-if="loadError" class="py-16 text-center space-y-3 max-w-md mx-auto">
        <p class="text-sm text-rose-400 font-mono">Failed to load your ID badge credentials.</p>
        <button @click="fetchIDCard" class="btn-ghost text-xs py-2 px-4">Retry</button>
      </div>

      <!-- Card Display -->
      <div v-else-if="cardData" class="max-w-2xl mx-auto flex flex-col items-center w-full relative">

        <!-- Card View Toggle Selector -->
        <div class="flex items-center gap-2 bg-[#0c1117] p-1.5 rounded-xl border border-[#1a2332] font-mono text-xs shadow-xl z-20 mb-4">
          <button 
            @click="activeCardView = 'physical'"
            :class="[
              'px-4 py-2 rounded-lg font-bold transition-all flex items-center gap-2',
              activeCardView === 'physical' ? 'bg-[#9fef00] text-black shadow-lg scale-105' : 'text-slate-400 hover:text-white'
            ]"
          >
            <span>Hanging 3D Badge</span>
          </button>
          <button 
            v-if="!authStore.isTeacher"
            @click="activeCardView = 'qr'"
            :class="[
              'px-4 py-2 rounded-lg font-bold transition-all flex items-center gap-2',
              activeCardView === 'qr' ? 'bg-[#00f0ff] text-black shadow-lg scale-105' : 'text-slate-400 hover:text-white'
            ]"
          >
            <span>QR Live Pass</span>
          </button>
          <button 
            v-if="authStore.isTeacher"
            @click="activeCardView = 'scanner'; loadActiveClubEvents()"
            :class="[
              'px-4 py-2 rounded-lg font-bold transition-all flex items-center gap-2',
              activeCardView === 'scanner' ? 'bg-amber-400 text-black shadow-lg scale-105' : 'text-slate-400 hover:text-white'
            ]"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            <span>QR Scanner</span>
          </button>
        </div>

        <!-- 1. Physical Member ID Badge Mode (CSS 3D Interactive Tilt) -->
        <div 
          v-if="activeCardView === 'physical'" 
          class="w-full max-w-md perspective-container relative pt-8"
          @mousemove="handleMouseMove"
          @mouseleave="handleMouseLeave"
        >
          <!-- Lanyard Strap Header Loop -->
          <div class="absolute -top-12 left-1/2 -translate-x-1/2 flex flex-col items-center z-10 pointer-events-none">
            <!-- Woven Fabric Strap -->
            <div :class="['w-12 h-20 bg-gradient-to-b border-x-2 shadow-2xl relative flex items-center justify-center overflow-hidden rounded-t-md', theme.lanyardStrap]">
              <div class="absolute inset-0 bg-[radial-gradient(#ffffff_1.5px,transparent_1.5px)] [background-size:6px_6px] opacity-20"></div>
              <span :class="['text-[9px] font-mono font-extrabold rotate-90 tracking-widest whitespace-nowrap opacity-90 drop-shadow', theme.strapText]">
                HACKERXPLOIT
              </span>
            </div>
            <!-- Heavy Metallic Clip -->
            <div class="w-9 h-7 rounded-md border-2 border-slate-300 bg-gradient-to-b from-slate-200 via-slate-400 to-slate-700 shadow-xl flex items-center justify-center -mt-1">
              <div class="w-4 h-3 bg-slate-900 border border-slate-500 rounded-sm"></div>
            </div>
          </div>

          <!-- Card Outer Container -->
          <div 
            :class="['glass-panel p-6 rounded-2xl border-2 bg-gradient-to-b shadow-2xl relative overflow-hidden transition-transform duration-100 ease-out transform-gpu mt-2', theme.borderClass, theme.bgGradient]"
            :style="cardTransformStyle"
          >
            
            <!-- Dynamic Glare Light Overlay -->
            <div 
              class="absolute inset-0 pointer-events-none transition-opacity duration-200"
              :style="glareOverlayStyle"
            ></div>

            <!-- Hologram Flare Top-Right -->
            <div :class="['absolute -right-12 -top-12 w-32 h-32 bg-gradient-to-br rounded-full blur-2xl pointer-events-none', theme.holoGlow]"></div>

            <!-- Lanyard Punch Hole -->
            <div class="w-14 h-4 mx-auto mb-4 bg-[#070a10] border-2 border-slate-600 rounded-full flex items-center justify-center shadow-inner">
              <div class="w-7 h-1.5 bg-slate-500 rounded-full"></div>
            </div>

            <!-- Header Row -->
            <div class="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-5">
              <div class="flex items-center space-x-2.5">
                <img src="/logo.png" class="w-14 h-14 object-contain drop-shadow-[0_0_8px_rgba(255,255,255,0.5)]" alt="HackerXploit" />
                <div>
                  <h4 class="font-mono text-xs font-extrabold leading-tight">
                    <span class="text-white">HACKER</span><span class="text-red-500">XPLOIT</span>
                  </h4>
                  <span :class="['text-[9px] font-mono tracking-widest uppercase block -mt-0.5 font-bold', theme.textAccent]">OFFSEC MEMBER BADGE</span>
                </div>
              </div>

              <div class="text-right font-mono">
                <span class="text-[9px] text-slate-400 block">BADGE ID</span>
                <span class="text-xs font-bold text-white tracking-wider">{{ cardData.user.badge_id || cardData.user.member_id }}</span>
              </div>
            </div>

            <!-- Main Badge Content: Photo, User Details -->
            <div class="flex items-start space-x-4 mb-6">
              <!-- Avatar Photo Frame with Hologram Chip -->
              <div class="relative flex-shrink-0">
                <img 
                  :src="avatarSrc" 
                  @error="onAvatarError"
                  class="w-24 h-28 rounded-xl object-cover border-2 bg-[#070a10] shadow-xl"
                  :style="{ borderColor: theme.hex }" 
                />
                <div :class="['absolute -bottom-2 -right-2 w-10 h-6 rounded border flex items-center justify-center text-[8px] font-mono font-extrabold shadow-lg', theme.chipBg]">
                  CHIP
                </div>
              </div>

              <!-- User Info Block -->
              <div class="flex-1 min-w-0 space-y-1.5 font-mono">
                <span class="text-[9px] text-slate-400 uppercase tracking-widest block font-bold">
                  {{ authStore.isAdmin ? 'PLATFORM ADMINISTRATOR' : (authStore.isTeacher ? 'FACULTY MEMBER' : 'OPERATOR NAME') }}
                </span>
                <h3 class="text-base font-extrabold text-white uppercase tracking-tight truncate leading-tight">
                  {{ cardData.user.full_name || cardData.user.username }}
                </h3>
                <p :class="['text-xs font-bold truncate', theme.textAccent]">@{{ cardData.user.username }}</p>

                <!-- Role Badges Row -->
                <div class="pt-2 flex flex-wrap gap-1.5">
                  <span :class="['text-[10px] font-extrabold uppercase px-2 py-0.5 rounded border shadow', theme.badgeBg]">
                    {{ theme.title }}
                  </span>
                  <template v-if="authStore.isAdmin">
                    <span class="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-rose-950/80 text-rose-300 border border-rose-500/50 shadow">
                      SYSTEM GOVERNANCE
                    </span>
                  </template>
                  <template v-else-if="authStore.isTeacher">
                    <span class="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-500/50 shadow">
                      EVENT HOST / SCANNER
                    </span>
                  </template>
                  <template v-else>
                    <span class="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-[#151f30] text-slate-300 border border-slate-700 shadow">
                      {{ cardData.user.role?.replace('_', ' ') }}
                    </span>
                    <span :class="['text-[10px] font-extrabold uppercase px-2 py-0.5 rounded border shadow', cardData.live_status?.is_active_event ? 'bg-emerald-950 text-[#9fef00] border-[#9fef00]' : 'bg-slate-900 text-slate-400 border-slate-700']">
                      {{ cardData.live_status?.is_active_event ? 'LIVE EVENT' : 'STANDBY' }}
                    </span>
                  </template>
                </div>
              </div>
            </div>

            <!-- Barcode & Official Seal Footer -->
            <div class="pt-4 border-t border-slate-800/80 flex items-center justify-between font-mono">
              <div class="space-y-1">
                <!-- Barcode simulation -->
                <div class="flex space-x-0.5 h-6 items-center">
                  <div v-for="i in 30" :key="i" :class="[i % 3 === 0 ? 'w-1' : 'w-0.5', i % 5 === 0 ? theme.barcodeColor : 'bg-slate-300']" class="h-full"></div>
                </div>
                <span class="text-[8px] text-slate-400 tracking-widest block uppercase font-bold">OFFICIAL HACKERXPLOIT CREDENTIAL</span>
              </div>

              <div class="text-right">
                <span class="text-[9px] text-slate-400 block">VALID THRU</span>
                <span class="text-xs font-bold text-white">DEC 2026</span>
              </div>
            </div>

          </div>
        </div>

        <!-- 2. QR Live Event Pass View (Student Only) -->
        <div v-else-if="activeCardView === 'qr' && !authStore.isTeacher" class="w-full max-w-md">
          <div class="glass-panel p-6 rounded-2xl border-2 border-[#00f0ff]/60 bg-[#111927] shadow-2xl relative space-y-5">
            
            <div class="text-center border-b border-[#1f293d] pb-4">
              <span class="text-xs font-mono font-bold text-[#00f0ff] uppercase bg-[#151f30] px-3 py-1 rounded-full border border-[#00f0ff]/40">
                OFFICIAL QR VERIFICATION PASS
              </span>
              <h3 class="text-lg font-bold text-white font-mono mt-2">Scan for Attendance & Event Access</h3>
            </div>

            <!-- Large Center QR Code (rendered fully client-side - the verification
                 URL embeds a live bearer token, so it's never sent to a third party
                 just to draw a QR image) -->
            <div class="flex flex-col items-center justify-center p-4 bg-white rounded-xl border-2 border-[#00f0ff] shadow-xl max-w-[220px] mx-auto">
              <img
                v-if="qrDataUrl"
                :src="qrDataUrl"
                alt="QR Verification"
                class="w-44 h-44 object-contain"
              />
              <div v-else class="w-44 h-44 flex items-center justify-center text-[10px] font-mono text-slate-500">
                Generating QR...
              </div>
              <span class="text-[10px] font-mono font-bold text-slate-700 mt-2">HX-VERIFY-ID</span>
            </div>

            <div class="bg-[#090d16] p-3 rounded-lg border border-[#1f293d] text-center font-mono space-y-1">
              <span class="text-[10px] text-slate-400 uppercase block font-bold">SECURITY TOKEN HASH</span>
              <p class="text-xs text-[#00f0ff] font-bold break-all">{{ cardData.token }}</p>
            </div>

          </div>
        </div>

        <!-- 3. QR Attendance Scanner View (Club Events - Admin/Teacher Only) -->
        <div v-else-if="activeCardView === 'scanner' && authStore.isTeacher" class="w-full max-w-lg space-y-5">
          <div class="glass-panel p-6 rounded-2xl border-2 border-amber-500/60 bg-[#111927] shadow-2xl relative space-y-5">
            
            <div class="text-center border-b border-[#1f293d] pb-4">
              <span class="text-xs font-mono font-bold text-amber-400 uppercase bg-[#151f30] px-3 py-1 rounded-full border border-amber-500/40 inline-flex items-center gap-1.5">
                <span class="relative flex h-2 w-2">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2 w-2 bg-amber-400"></span>
                </span>
                CLUB EVENT QR ATTENDANCE SCANNER
              </span>
              <h3 class="text-lg font-bold text-white font-mono mt-2">Scan & Approve Member Attendance</h3>
              <p class="text-xs text-slate-400 font-mono mt-0.5">Attendance window: 30 minutes before start to 30 minutes after event end.</p>
            </div>

            <!-- Active Club Event Dropdown Selector -->
            <div class="font-mono space-y-1.5">
              <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider">Select Active Club Event</label>
              <select 
                v-model="selectedClubEventId" 
                @change="onClubEventChange" 
                class="input-field w-full text-xs font-mono bg-[#0b0e14] border-amber-500/40 text-amber-300 font-bold"
              >
                <option v-if="clubEventsLoading" value="" disabled>Loading active club events...</option>
                <option v-else-if="clubEvents.length === 0" value="" disabled>No Club Events currently scheduled</option>
                <option v-for="ev in clubEvents" :key="ev.id" :value="ev.id">
                  {{ ev.title }} ({{ formatKolkataTime(ev.starts_at) }} IST) - {{ ev.is_scan_allowed ? 'SCAN READY' : 'LOCKED' }}
                </option>
              </select>
            </div>

            <!-- Time Window Status Banner -->
            <div v-if="selectedClubEvent" class="font-mono text-xs p-3.5 rounded-xl border bg-emerald-950/40 border-emerald-500/50 text-emerald-300">
              <div class="flex items-center justify-between font-bold mb-1">
                <span class="uppercase tracking-wider flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  {{ selectedClubEvent.in_scheduled_window ? 'SCANNER WINDOW ACTIVE (SCHEDULED)' : 'SCANNER ACTIVE (TEACHER SCAN MODE)' }}
                </span>
                <span class="text-[10px] uppercase bg-black/40 px-2 py-0.5 rounded border border-current">
                  {{ selectedClubEvent.attendee_count || 0 }} Scanned
                </span>
              </div>
              <p class="text-[11px] leading-relaxed opacity-90">
                Scanner is active for <strong>{{ selectedClubEvent.title }}</strong>. Scan or input member badge code below.
              </p>
            </div>

            <!-- Camera & Scanner Form -->
            <div v-if="selectedClubEvent && selectedClubEvent.is_scan_allowed" class="space-y-4 font-mono">
              
              <!-- Camera Viewport -->
              <div class="relative bg-black rounded-xl overflow-hidden border-2 border-amber-500/40 h-52 flex flex-col items-center justify-center group shadow-inner">
                <video ref="videoElem" autoplay playsinline webkit-playsinline muted class="w-full h-full object-cover" v-show="cameraActive"></video>

                <!-- Scanner Reticle HUD -->
                <div class="absolute inset-0 pointer-events-none border-2 border-amber-500/20 rounded-xl flex flex-col items-center justify-between p-4">
                  <div class="w-full flex justify-between">
                    <div class="w-4 h-4 border-t-2 border-l-2 border-amber-400"></div>
                    <div class="w-4 h-4 border-t-2 border-r-2 border-amber-400"></div>
                  </div>
                  <div class="w-28 h-28 border border-amber-400/40 rounded-lg relative overflow-hidden flex items-center justify-center">
                    <div class="absolute w-full h-0.5 bg-amber-400 shadow-[0_0_8px_#fbbf24] animate-bounce"></div>
                  </div>
                  <div class="w-full flex justify-between">
                    <div class="w-4 h-4 border-b-2 border-l-2 border-amber-400"></div>
                    <div class="w-4 h-4 border-b-2 border-r-2 border-amber-400"></div>
                  </div>
                </div>

                <div v-if="!cameraActive" class="absolute inset-0 flex flex-col items-center justify-center bg-[#090d16]/95 p-4 text-center space-y-2">
                  <svg class="w-8 h-8 text-amber-400 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                  <p class="text-xs text-slate-300 font-bold">Webcam Sensor & Scanner</p>

                  <button @click="startCamera" class="btn-htb text-[11px] py-1.5 px-3 bg-amber-400 hover:bg-amber-300 text-black font-extrabold shadow">
                    Start Optical Camera
                  </button>

                  <p v-if="cameraErrorMsg" class="text-[10px] text-rose-300 bg-rose-950/80 p-2 rounded border border-rose-500/50 max-w-xs mt-1 leading-tight">
                    {{ cameraErrorMsg }}
                  </p>
                </div>

                <div v-if="cameraActive" class="absolute bottom-2 left-2 z-30 bg-black/80 text-emerald-400 px-2.5 py-1 rounded text-[10px] font-bold border border-emerald-500/40 flex items-center gap-1.5 animate-pulse">
                  <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                  LIVE QR SCANNER ACTIVE (Align QR Code)
                </div>

                <button v-else @click="stopCamera" class="absolute top-2 right-2 z-30 bg-black/80 text-rose-400 hover:text-white px-2 py-1 rounded text-[10px] font-bold border border-rose-500/40">
                  Stop Camera
                </button>
              </div>

              <!-- Input Code / Token Field & Remark Field -->
              <div class="space-y-3 bg-[#080c14] p-4 rounded-xl border border-[#1f293d]">
                <div class="space-y-1">
                  <label class="block text-[11px] font-bold text-slate-300 uppercase">1. Member Badge Code / QR Token</label>
                  <input 
                    v-model="scanTokenInput" 
                    type="text" 
                    placeholder="Scan QR or enter Badge ID (e.g. HX-STU-0001)..."
                    class="input-field text-xs font-mono bg-[#0c1117] w-full border-slate-700"
                    @keyup.enter="submitAttendanceScan"
                  />
                </div>

                <div class="space-y-1">
                  <label class="block text-[11px] font-bold text-slate-300 uppercase">2. Optional Remark / Notes</label>
                  <input 
                    v-model="scanRemark" 
                    type="text" 
                    placeholder="Optional remark (e.g. Approved by Admin, Lab seat #3, Late arrival)..." 
                    class="input-field text-xs font-mono bg-[#0c1117] w-full border-slate-700"
                    @keyup.enter="submitAttendanceScan"
                  />
                </div>

                <button 
                  @click="submitAttendanceScan" 
                  :disabled="scanningSubmitting || !scanTokenInput.trim()"
                  class="btn-htb w-full text-xs py-2.5 px-4 font-mono font-extrabold bg-amber-400 hover:bg-amber-300 text-black shadow-lg flex items-center justify-center gap-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                  </svg>
                  <span>{{ scanningSubmitting ? 'Verifying & Recording...' : 'Approve & Record Attendance' }}</span>
                </button>

                <!-- Feedback Toasts -->
                <div v-if="scanResultSuccess" class="p-3 bg-emerald-950/90 border border-emerald-500 text-emerald-300 rounded-lg text-xs font-mono font-bold flex items-center gap-2">
                  <span>{{ scanResultSuccess }}</span>
                </div>
                <div v-if="scanResultError" class="p-3 bg-rose-950/90 border border-rose-500 text-rose-300 rounded-lg text-xs font-mono font-bold flex items-center gap-2">
                  <span>{{ scanResultError }}</span>
                </div>
              </div>

            </div>

            <!-- Scanner Locked Warning Container -->
            <div v-else-if="selectedClubEvent && !selectedClubEvent.is_scan_allowed" class="p-8 text-center bg-[#090d16] rounded-xl border border-slate-800 space-y-3 font-mono">
              <svg class="w-12 h-12 text-slate-600 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
              <h4 class="text-sm font-bold text-white uppercase">Attendance Scanner Locked</h4>
              <p class="text-xs text-slate-400 leading-relaxed max-w-sm mx-auto">
                Camera and QR verification window for <strong>{{ selectedClubEvent.title }}</strong> opens strictly 30 minutes prior to event start time.
              </p>
            </div>

          </div>
        </div>

        <!-- Bottom Controls -->
        <div class="flex flex-wrap gap-3 justify-center w-full pt-4 font-mono z-20">
          <a :href="cardData.verification_url" target="_blank" class="btn-ghost text-xs text-[#00f0ff] border-[#00f0ff]/30 hover:border-[#00f0ff] py-2.5 px-5 rounded-xl flex items-center gap-2">
            <svg class="w-4 h-4 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
            </svg>
            <span>Public Verification Link</span>
          </a>
          <button class="btn-htb text-xs py-2.5 px-5 rounded-xl flex items-center gap-2" :disabled="regenerating" @click="regenerateToken">
            <svg class="w-4 h-4" :class="regenerating ? 'animate-spin' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            <span>{{ regenerating ? 'Regenerating...' : 'Regenerate Token' }}</span>
          </button>
        </div>

      </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { usePreferences } from '@/stores/preferences'

const authStore = useAuthStore()
const prefs = usePreferences()
const loading = ref(true)
const cardData = ref(null)
const regenerating = ref(false)
const activeCardView = ref('physical')
const avatarLoadError = ref(false)

// 3D Physics Tilt State
const rotateX = ref(0)
const rotateY = ref(0)
const glareX = ref(50)
const glareY = ref(50)

const defaultAvatarSvg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'><rect width='100' height='100' fill='%230b0e14'/><circle cx='50' cy='38' r='20' fill='%231f293d' stroke='%239fef00' stroke-width='2'/><path d='M20,85 C20,62 35,55 50,55 C65,55 80,62 80,85 Z' fill='%231f293d' stroke='%239fef00' stroke-width='2'/></svg>"

const avatarSrc = computed(() => {
  if (avatarLoadError.value || !cardData.value?.user?.avatar_url) {
    return defaultAvatarSvg
  }
  return cardData.value.user.avatar_url
})

const onAvatarError = () => {
  avatarLoadError.value = true
}

const handleMouseMove = (e) => {
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const centerX = rect.width / 2
  const centerY = rect.height / 2

  // Pitch (-15 to 15 deg) & Yaw (-15 to 15 deg)
  rotateX.value = -((y - centerY) / centerY) * 14
  rotateY.value = ((x - centerX) / centerX) * 14

  glareX.value = (x / rect.width) * 100
  glareY.value = (y / rect.height) * 100
}

const handleMouseLeave = () => {
  rotateX.value = 0
  rotateY.value = 0
  glareX.value = 50
  glareY.value = 50
}

const cardTransformStyle = computed(() => ({
  transform: `perspective(1000px) rotateX(${rotateX.value}deg) rotateY(${rotateY.value}deg) scale3d(1.02, 1.02, 1.02)`
}))

const glareOverlayStyle = computed(() => ({
  background: `radial-gradient(circle at ${glareX.value}% ${glareY.value}%, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 70%)`,
  opacity: rotateX.value !== 0 || rotateY.value !== 0 ? 1 : 0
}))

const theme = computed(() => {
  const userRole = cardData.value?.user?.role || authStore.user?.role
  
  if (userRole === 'root_admin' || userRole === 'admin') {
    return {
      title: userRole === 'root_admin' ? 'ROOT ADMINISTRATOR' : 'PLATFORM ADMIN',
      shortRole: 'ADMIN',
      hex: '#ff003c',
      borderClass: 'border-red-600 shadow-[0_20px_50px_rgba(255,0,60,0.3)]',
      bgGradient: 'from-[#2b040a] via-[#1a0206] to-[#0d0103]',
      lanyardStrap: 'from-[#3b050e] via-[#240308] to-[#0f0103] border-red-600',
      strapText: 'text-red-500',
      holoGlow: 'from-red-600/30 to-red-500/20',
      badgeBg: 'bg-red-950/80 text-red-400 border-red-600/50',
      textAccent: 'text-red-500',
      chipBg: 'bg-gradient-to-r from-red-600 to-red-700 border-red-400 text-white',
      barcodeColor: 'bg-red-600'
    }
  }

  if (userRole === 'teacher' || userRole === 'teacher_admin') {
    return {
      title: 'FACULTY / TEACHER',
      shortRole: 'TEACHER',
      hex: '#fbbf24',
      borderClass: 'border-amber-400/90 shadow-[0_20px_50px_rgba(251,191,36,0.25)]',
      bgGradient: 'from-[#1c1404] via-[#120d02] to-[#050301]',
      lanyardStrap: 'from-[#2e2006] via-[#1c1303] to-[#0a0701] border-amber-400/90',
      strapText: 'text-amber-400',
      holoGlow: 'from-amber-400/30 to-yellow-500/20',
      badgeBg: 'bg-amber-400/20 text-amber-300 border-amber-400/40',
      textAccent: 'text-amber-400',
      chipBg: 'bg-gradient-to-r from-amber-400 to-yellow-500 border-amber-200 text-black',
      barcodeColor: 'bg-amber-400'
    }
  }

  const role = cardData.value?.user?.specialization_role || authStore.user?.specialization_role || 'Security Analyst'
  if (role === 'Penetration Tester') {
    return {
      title: 'PENETRATION TESTER',
      shortRole: 'PENTESTER',
      hex: '#9fef00',
      borderClass: 'border-[#9fef00]/80 shadow-[0_20px_50px_rgba(159,239,0,0.2)]',
      bgGradient: 'from-[#111c14] via-[#0a140d] to-[#050a06]',
      lanyardStrap: 'from-[#0d1f12] via-[#09140c] to-[#040805] border-[#9fef00]/80',
      strapText: 'text-[#9fef00]',
      holoGlow: 'from-[#9fef00]/30 to-emerald-500/20',
      badgeBg: 'bg-[#9fef00]/15 text-[#9fef00] border-[#9fef00]/40',
      textAccent: 'text-[#9fef00]',
      chipBg: 'bg-gradient-to-r from-lime-400 to-emerald-500 border-lime-200 text-black',
      barcodeColor: 'bg-[#9fef00]'
    }
  } else if (role === 'Security Engineer') {
    return {
      title: 'SECURITY ENGINEER',
      shortRole: 'ENGINEER',
      hex: '#ffb700',
      borderClass: 'border-[#ffb700]/80 shadow-[0_20px_50px_rgba(255,183,0,0.2)]',
      bgGradient: 'from-[#211508] via-[#140c04] to-[#080401]',
      lanyardStrap: 'from-[#291a0a] via-[#170e05] to-[#0a0501] border-[#ffb700]/80',
      strapText: 'text-[#ffb700]',
      holoGlow: 'from-[#ffb700]/30 to-orange-500/20',
      badgeBg: 'bg-[#ffb700]/15 text-[#ffb700] border-[#ffb700]/40',
      textAccent: 'text-[#ffb700]',
      chipBg: 'bg-gradient-to-r from-amber-400 to-orange-500 border-amber-200 text-black',
      barcodeColor: 'bg-[#ffb700]'
    }
  } else {
    // Security Analyst
    return {
      title: 'SECURITY ANALYST',
      shortRole: 'ANALYST',
      hex: '#00f0ff',
      borderClass: 'border-[#00f0ff]/80 shadow-[0_20px_50px_rgba(0,240,255,0.2)]',
      bgGradient: 'from-[#091829] via-[#06101c] to-[#03080f]',
      lanyardStrap: 'from-[#0b1d30] via-[#071321] to-[#03080e] border-[#00f0ff]/80',
      strapText: 'text-[#00f0ff]',
      holoGlow: 'from-[#00f0ff]/30 to-blue-500/20',
      badgeBg: 'bg-[#00f0ff]/15 text-[#00f0ff] border-[#00f0ff]/40',
      textAccent: 'text-[#00f0ff]',
      chipBg: 'bg-gradient-to-r from-cyan-400 to-blue-500 border-cyan-200 text-black',
      barcodeColor: 'bg-[#00f0ff]'
    }
  }
})

const loadError = ref(false)
const qrDataUrl = ref('')

const loadQrCodeScript = () => {
  return new Promise((resolve) => {
    if (window.QRCode) {
      resolve(true)
      return
    }
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js'
    script.onload = () => resolve(true)
    script.onerror = () => resolve(false)
    document.head.appendChild(script)
  })
}

const generateQrCode = async (verificationUrl) => {
  qrDataUrl.value = ''
  if (!verificationUrl) return
  const loaded = await loadQrCodeScript()
  if (!loaded || !window.QRCode) return
  try {
    qrDataUrl.value = await window.QRCode.toDataURL(verificationUrl, { width: 360, margin: 1 })
  } catch (err) {
    console.error('Failed to render QR code', err)
  }
}

const fetchIDCard = async () => {
  loading.value = true
  loadError.value = false
  try {
    const res = await axios.get('/api/profile/id-card')
    cardData.value = res.data
    generateQrCode(res.data?.verification_url)
  } catch (err) {
    console.error('Failed to load ID Card', err)
    cardData.value = null
    loadError.value = true
  } finally {
    loading.value = false
  }
}

const regenerateToken = async () => {
  regenerating.value = true
  try {
    const res = await axios.post('/api/profile/id-card/regenerate')
    if (cardData.value) {
      cardData.value.token = res.data.token
      cardData.value.verification_url = res.data.verification_url
      generateQrCode(res.data.verification_url)
    }
  } catch (err) {
    alert(err.response?.data?.error || 'Token regeneration failed')
  } finally {
    regenerating.value = false
  }
}

// Club Event & QR Scanner state
const clubEvents = ref([])
const clubEventsLoading = ref(false)
const selectedClubEventId = ref('')
const selectedClubEvent = ref(null)

const scanTokenInput = ref('')
const scanRemark = ref('')
const scanningSubmitting = ref(false)
const scanResultSuccess = ref('')
const scanResultError = ref('')

const cameraActive = ref(false)
const videoElem = ref(null)
let mediaStream = null

const loadActiveClubEvents = async () => {
  clubEventsLoading.value = true
  try {
    const res = await axios.get('/api/competitions/club-events/active')
    clubEvents.value = res.data.club_events || []
    if (clubEvents.value.length > 0) {
      selectedClubEventId.value = clubEvents.value[0].id
      selectedClubEvent.value = clubEvents.value[0]
    }
  } catch (err) {
    console.error('Failed to load active club events', err)
  } finally {
    clubEventsLoading.value = false
  }
}

const onClubEventChange = () => {
  selectedClubEvent.value = clubEvents.value.find(e => e.id === Number(selectedClubEventId.value)) || null
  scanResultSuccess.value = ''
  scanResultError.value = ''
}

const cameraErrorMsg = ref('')
let scanInterval = null
let lastScannedToken = ''
let lastScanTime = 0

const loadJsQrScript = () => {
  return new Promise((resolve) => {
    if (window.jsQR) {
      resolve(true)
      return
    }
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js'
    script.onload = () => resolve(true)
    script.onerror = () => resolve(false)
    document.head.appendChild(script)
  })
}

const startQrScannerLoop = async () => {
  let detector = null
  if ('BarcodeDetector' in window) {
    try {
      detector = new window.BarcodeDetector({ formats: ['qr_code'] })
    } catch (e) {
      detector = null
    }
  }

  if (!detector) {
    await loadJsQrScript()
  }

  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d', { willReadFrequently: true })

  scanInterval = setInterval(async () => {
    if (!cameraActive.value || !videoElem.value || videoElem.value.readyState < 2) return

    const video = videoElem.value
    const now = Date.now()
    if (now - lastScanTime < 2500) return // Cooldown between automatic scans

    try {
      let detectedText = null

      if (detector) {
        const barcodes = await detector.detect(video)
        if (barcodes && barcodes.length > 0) {
          detectedText = barcodes[0].rawValue
        }
      } else if (window.jsQR && video.videoWidth > 0 && video.videoHeight > 0) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
        const code = window.jsQR(imageData.data, imageData.width, imageData.height, {
          inversionAttempts: 'dontInvert'
        })
        if (code && code.data) {
          detectedText = code.data
        }
      }

      if (detectedText && detectedText.trim()) {
        const cleanText = detectedText.trim()
        if (cleanText !== lastScannedToken || (now - lastScanTime > 4000)) {
          lastScannedToken = cleanText
          lastScanTime = now
          scanTokenInput.value = cleanText
          
          // Audio feedback beep
          try {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)()
            const osc = audioCtx.createOscillator()
            const gain = audioCtx.createGain()
            osc.connect(gain)
            gain.connect(audioCtx.destination)
            osc.frequency.value = 880
            gain.gain.value = 0.1
            osc.start()
            osc.stop(audioCtx.currentTime + 0.15)
          } catch (e) {}

          await submitAttendanceScan()
        }
      }
    } catch (err) {
      // Ignore frame scan errors
    }
  }, 250)
}

const stopQrScannerLoop = () => {
  if (scanInterval) {
    clearInterval(scanInterval)
    scanInterval = null
  }
}

const startCamera = async () => {
  cameraErrorMsg.value = ''

  // Mobile Web Security Check: navigator.mediaDevices requires HTTPS or localhost
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
      cameraErrorMsg.value = 'Mobile security requires an HTTPS connection to open camera. Access site over https:// or use manual ID entry.'
    } else {
      cameraErrorMsg.value = 'Camera API is unsupported on this mobile browser. Use manual ID entry below.'
    }
    return
  }

  let stream = null
  const constraintsToTry = [
    { video: { facingMode: { ideal: 'environment' }, width: { ideal: 1280 }, height: { ideal: 720 } } },
    { video: { facingMode: 'environment' } },
    { video: { facingMode: 'user' } },
    { video: true }
  ]

  for (const constraint of constraintsToTry) {
    try {
      stream = await navigator.mediaDevices.getUserMedia(constraint)
      if (stream) break
    } catch (err) {
      // Try next constraint set
    }
  }

  if (!stream) {
    cameraErrorMsg.value = 'Camera permission denied or device camera unavailable. Please check mobile browser site permissions.'
    return
  }

  mediaStream = stream
  if (videoElem.value) {
    videoElem.value.srcObject = mediaStream
    videoElem.value.setAttribute('playsinline', 'true')
    videoElem.value.setAttribute('webkit-playsinline', 'true')
    videoElem.value.muted = true
    try {
      await videoElem.value.play()
    } catch (e) {
      console.warn('Video playback error:', e)
    }
  }
  cameraActive.value = true
  startQrScannerLoop()
}

const stopCamera = () => {
  stopQrScannerLoop()
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }
  cameraActive.value = false
}

const submitAttendanceScan = async () => {
  if (!selectedClubEvent.value || !scanTokenInput.value.trim()) return

  scanningSubmitting.value = true
  scanResultSuccess.value = ''
  scanResultError.value = ''

  let tokenToSend = scanTokenInput.value.trim()
  if (tokenToSend.includes('/verify/')) {
    tokenToSend = tokenToSend.split('/verify/').pop().split('?')[0].split('/')[0].trim()
  } else if (tokenToSend.includes('token=')) {
    tokenToSend = tokenToSend.split('token=').pop().split('&')[0].trim()
  }

  try {
    const res = await axios.post(`/api/competitions/${selectedClubEvent.value.id}/attendance/scan`, {
      token: tokenToSend,
      remark: scanRemark.value.trim()
    })
    scanResultSuccess.value = res.data.message || 'Attendance recorded successfully!'
    scanTokenInput.value = ''
    scanRemark.value = ''
    // Refresh attendee count
    await loadActiveClubEvents()
  } catch (err) {
    scanResultError.value = err.response?.data?.error || 'Attendance verification failed'
  } finally {
    scanningSubmitting.value = false
  }
}

const formatKolkataTime = (isoStr) => {
  if (!isoStr) return ''
  try {
    return new Date(isoStr).toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      hour: '2-digit',
      minute: '2-digit',
      hour12: prefs.is12h.value
    })
  } catch (e) {
    return isoStr
  }
}

onMounted(() => {
  fetchIDCard()
  if (authStore.isTeacher) {
    loadActiveClubEvents()
  }
})

onUnmounted(() => {
  stopCamera()
})

onBeforeRouteLeave(() => {
  stopCamera()
})
</script>
