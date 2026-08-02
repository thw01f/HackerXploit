<template>
  <div class="space-y-8">
    <!-- Header & Actions -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1f293d] pb-6">
      <div>
        <h1 class="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3 font-mono">
          <span>CTF & Competitions Board</span>
          <span class="text-[11px] uppercase tracking-wider bg-[#151f30] text-[#9fef00] border border-[#9fef00]/30 px-3 py-1 rounded-full font-bold">
            Lifecycle Hub
          </span>
        </h1>
        <p class="text-slate-400 text-sm mt-1">
          Discover hackathons, CTFs, workshops, submit registration proof, and view team achievements.
        </p>
      </div>

      <!-- Right: Live IST Clock & Actions -->
      <div class="flex items-center gap-3">
        <!-- Real-Time Ticking IST Clock -->
        <div class="bg-[#090d16] border border-cyan-500/40 px-3.5 py-2 rounded-xl flex items-center gap-2.5 font-mono shadow-md shadow-cyan-500/5">
          <div class="relative flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
          </div>
          <div>
            <span class="text-[9px] text-slate-400 uppercase tracking-widest block font-bold leading-none mb-0.5">LIVE IST CLOCK</span>
            <span class="text-xs sm:text-sm font-extrabold text-cyan-400 tracking-wider leading-tight">{{ liveTimeFormatted }}</span>
          </div>
        </div>

        <button 
          v-if="authStore.isTeacher" 
          @click="showAnnounceModal = true" 
          class="btn-htb text-xs py-2.5 px-5 font-mono font-bold flex items-center justify-center gap-2 shadow-lg shadow-[#9fef00]/10 shrink-0"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          <span>Announce Event</span>
        </button>
      </div>
    </div>

    <!-- Category Filter Bar & Search -->
    <div class="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4 border-b border-[#1f293d] pb-4">
      <!-- Category Tabs -->
      <div class="flex flex-wrap items-center gap-2">
        <button 
          v-for="cat in categories" 
          :key="cat" 
          @click="activeCategory = cat; fetchCompetitions()"
          :class="[
            'px-4 py-2 text-xs font-mono font-bold uppercase rounded-lg transition-all duration-200 flex items-center gap-1.5',
            activeCategory === cat 
              ? 'bg-[#9fef00] text-black shadow-lg shadow-[#9fef00]/20 scale-105' 
              : 'bg-[#151f30] text-slate-400 hover:text-white hover:bg-slate-800'
          ]"
        >
          <span>{{ cat }}</span>
        </button>
      </div>

      <!-- Search Input -->
      <div class="relative w-full lg:w-72">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search event title..." 
          class="w-full bg-[#0c1117] border border-[#1f293d] focus:border-[#9fef00] rounded-lg px-3.5 py-2 pl-9 text-xs text-white placeholder-slate-500 font-mono transition-colors outline-none"
        />
        <svg class="w-4 h-4 text-slate-500 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </div>
    </div>

    <!-- Filter Control Bar -->
    <div class="glass-panel p-4 grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono">
      <div>
        <label class="block text-[11px] font-bold text-slate-400 uppercase mb-1.5">Status Filter</label>
        <select v-model="filterStatus" @change="fetchCompetitions" class="input-field text-xs py-2 bg-[#090d16] border-slate-700">
          <option value="all">All Statuses</option>
          <option value="upcoming">Upcoming</option>
          <option value="ongoing">Ongoing (Live)</option>
          <option value="ended">Ended</option>
        </select>
      </div>

      <div>
        <label class="block text-[11px] font-bold text-slate-400 uppercase mb-1.5">Priority Filter</label>
        <select v-model="filterPriority" @change="fetchCompetitions" class="input-field text-xs py-2 bg-[#090d16] border-slate-700">
          <option value="all">All Priorities</option>
          <option value="high">High Priority</option>
          <option value="medium">Medium Priority</option>
          <option value="normal">Normal Priority</option>
        </select>
      </div>

      <div>
        <label class="block text-[11px] font-bold text-slate-400 uppercase mb-1.5">My Involvement</label>
        <select v-model="filterInvolvement" @change="fetchCompetitions" class="input-field text-xs py-2 bg-[#090d16] border-slate-700">
          <option value="all">All Involvement</option>
          <option value="applied">Applied (Any)</option>
          <option value="verified">Verified Participant</option>
          <option value="not_applied">Not Applied</option>
        </select>
      </div>
    </div>

    <!-- Competitions Grid -->
    <div v-if="loading" class="text-center py-16 text-slate-500 font-mono text-sm">
      <div class="inline-block animate-spin w-6 h-6 border-2 border-[#9fef00] border-t-transparent rounded-full mb-2"></div>
      <div>Loading events grid...</div>
    </div>

    <div v-else-if="filteredCompetitions.length === 0" class="glass-panel p-16 text-center text-slate-400 space-y-3 font-mono">
      <svg class="w-12 h-12 text-slate-600 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
      </svg>
      <p class="font-bold text-base text-white">No competitions match filters</p>
      <p class="text-xs text-slate-500 max-w-sm mx-auto">Try selecting 'All' categories or adjusting your status/priority filters.</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="comp in filteredCompetitions" 
        :key="comp.id" 
        class="glass-panel rounded-2xl overflow-hidden flex flex-col justify-between transition-all duration-300 hover:border-[#9fef00]/60 hover:shadow-2xl hover:shadow-[#9fef00]/10 group relative border border-[#1f293d]"
      >
        <div>
          <!-- Poster Header Image with Dynamic Aesthetic Gradient & Badges -->
          <div 
            class="relative w-full h-44 overflow-hidden border-b border-[#1f293d] flex items-center justify-center"
            :style="getCardBannerStyle(comp)"
          >
            <!-- Overlay Gradient for contrast -->
            <div class="absolute inset-0 bg-gradient-to-t from-[#111927] via-transparent to-black/60"></div>

            <!-- Custom Category Icon/Artwork if no poster image -->
            <div v-if="!comp.poster_image || comp.poster_image === '/logo.png'" class="relative z-10 text-center p-4 space-y-1">
              <span class="text-3xl opacity-80 filter drop-shadow">
                {{ getCategoryEmoji(comp.category) }}
              </span>
              <span class="block text-[11px] font-mono font-extrabold uppercase tracking-widest text-slate-300/80">
                {{ comp.category || 'EVENT' }} GAUNTLET
              </span>
            </div>

            <!-- Top Left: Category Pill -->
            <div class="absolute top-3 left-3 z-20">
              <span class="text-[10px] font-mono font-bold uppercase px-2.5 py-1 rounded-md bg-black/70 backdrop-blur-md text-white border border-white/20 shadow">
                {{ comp.category || 'GAUNTLET' }}
              </span>
            </div>

            <!-- Top Right: Computed Status Badge -->
            <div class="absolute top-3 right-3 z-20">
              <span 
                :class="[
                  'text-[10px] font-mono font-bold uppercase px-2.5 py-1 rounded-md shadow-md backdrop-blur-md border flex items-center gap-1.5',
                  comp.computed_status === 'ended' ? 'bg-slate-900/90 text-slate-400 border-slate-700' :
                  comp.computed_status === 'ongoing' ? 'bg-emerald-950/90 text-[#9fef00] border-[#9fef00]/50 animate-pulse' :
                  'bg-cyan-950/90 text-[#00f0ff] border-[#00f0ff]/50'
                ]"
              >
                <span :class="[
                  'w-1.5 h-1.5 rounded-full',
                  comp.computed_status === 'ended' ? 'bg-slate-500' :
                  comp.computed_status === 'ongoing' ? 'bg-[#9fef00]' : 'bg-[#00f0ff]'
                ]"></span>
                {{ comp.computed_status || 'UPCOMING' }}
              </span>
            </div>
          </div>

          <!-- Card Content Body -->
          <div class="p-5 space-y-3 font-mono">
            <!-- Header & Priority Badge -->
            <div class="flex items-start justify-between gap-2">
              <h3 @click="openEventDetails(comp)" class="text-base font-extrabold text-white leading-snug group-hover:text-[#9fef00] transition-colors line-clamp-1 cursor-pointer hover:underline" title="Click for complete details">
                {{ comp.title }}
              </h3>
              <span :class="getPriorityBadgeClass(comp.priority)" class="text-[10px] font-bold uppercase px-2 py-0.5 rounded border shrink-0">
                {{ comp.priority }}
              </span>
            </div>

            <!-- Description -->
            <p @click="openEventDetails(comp)" class="text-slate-400 text-xs line-clamp-2 leading-relaxed h-9 cursor-pointer hover:text-slate-200" title="Click for complete details">
              {{ comp.description || 'No detailed description available for this event.' }}
            </p>

            <!-- Complete Details Trigger Button -->
            <button @click="openEventDetails(comp)" class="w-full text-left text-[11px] text-cyan-400 hover:text-cyan-300 font-bold font-mono py-1 flex items-center justify-between group-hover:translate-x-0.5 transition-all">
              <span class="flex items-center gap-1.5">
                <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <span>View Complete Details & Overview</span>
              </span>
              <span>&rarr;</span>
            </button>

            <!-- External Link -->
            <div v-if="comp.external_link" class="pt-0.5">
              <a :href="comp.external_link" target="_blank" class="text-[11px] text-cyan-400 hover:text-cyan-300 hover:underline inline-flex items-center gap-1.5">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                </svg>
                <span>Registration / Portal Link</span>
              </a>
            </div>

            <!-- Structured Date Timeline Grid: a true 2-column grid (label | value)
                 instead of per-row flex, so labels and values each form a clean
                 aligned column regardless of "Starts"/"Ends"/"Deadline" length. -->
            <div class="text-xs bg-[#080c14] rounded-xl border border-[#1f293d]/80 font-mono overflow-hidden">
              <div class="grid grid-cols-[auto_1fr] items-center gap-x-3 gap-y-2 p-3">
                <span class="text-slate-500 flex items-center gap-1.5 whitespace-nowrap">
                  <svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                  </svg>
                  Starts
                </span>
                <span class="text-slate-200 font-semibold text-right tabular-nums">{{ formatDate(comp.starts_at) }}</span>

                <span class="text-slate-500 flex items-center gap-1.5 whitespace-nowrap">
                  <svg class="w-4 h-4 text-rose-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                  </svg>
                  Ends
                </span>
                <span class="text-slate-200 font-semibold text-right tabular-nums">{{ formatDate(comp.ends_at) }}</span>

                <template v-if="comp.application_deadline">
                  <div class="col-span-2 border-t border-slate-800/80 -mx-3 mt-1"></div>
                  <span class="text-amber-400 flex items-center gap-1.5 whitespace-nowrap">
                    <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    Deadline
                  </span>
                  <span class="text-amber-400 font-bold text-right tabular-nums">{{ formatDate(comp.application_deadline) }}</span>
                </template>
              </div>
            </div>

            <!-- User Involvement Badge Bar -->
            <div class="flex items-center justify-between pt-1 gap-2">
              <span class="text-xs text-slate-500 font-mono uppercase shrink-0">My Status</span>
              <span :class="getInvolvementBadgeClass(comp.user_involvement)" class="text-[11px] uppercase px-2.5 py-0.5 rounded font-bold border text-right whitespace-nowrap">
                {{ formatInvolvement(comp.user_involvement) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Card Footer Actions -->
        <div class="p-5 pt-0 space-y-2 font-mono">
          <!-- Club Event Specific Action: Feedback (No proof submission required) -->
          <template v-if="comp.category === 'club' || comp.category === 'Club'">
            <button 
              @click="openFeedbackModal(comp)" 
              class="w-full bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 text-xs py-2 rounded-xl font-bold flex items-center justify-center gap-1.5 transition-all shadow"
            >
              <svg class="w-4 h-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
              <span>Event Feedback & Rating</span>
            </button>
          </template>

          <!-- Standard Competition Action: Proof Submission -->
          <template v-else>
            <button 
              v-if="comp.user_involvement === 'not_applied'" 
              @click="openApplyModal(comp)" 
              class="w-full btn-neon-cyan text-xs py-2 rounded-xl font-bold"
            >
              I'm Applying (Submit Proof)
            </button>

            <button 
              v-else 
              @click="openApplyModal(comp)" 
              class="w-full bg-slate-800 text-[#9fef00] hover:bg-slate-700 text-xs py-2 rounded-xl border border-slate-700 font-bold"
            >
              Update Registration Proof
            </button>
          </template>

          <!-- Teacher & Admin Control Buttons -->
          <div v-if="authStore.isTeacher" class="space-y-1.5 pt-1 border-t border-slate-800/80">
            <button 
              v-if="comp.category === 'club' || comp.category === 'Club'"
              @click="openAttendanceModal(comp)" 
              class="w-full bg-amber-950/80 hover:bg-amber-900 text-amber-300 border border-amber-500/50 text-[11px] font-bold py-1.5 rounded-lg flex items-center justify-center gap-1.5 transition-all"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
              </svg>
              <span>Attendance & Roster</span>
            </button>

            <div class="grid grid-cols-4 gap-1.5">
              <button 
                @click="openVerificationQueue(comp)" 
                class="bg-purple-950/80 hover:bg-purple-900 text-purple-300 border border-purple-600/40 text-[11px] font-bold py-1.5 rounded-lg transition-all"
              >
                Queue
              </button>
              <button 
                @click="openWrapupModal(comp)" 
                class="bg-cyan-950/80 hover:bg-cyan-900 text-cyan-300 border border-cyan-600/40 text-[11px] font-bold py-1.5 rounded-lg transition-all"
              >
                Wrap-up
              </button>
              <button 
                @click="openEditModal(comp)" 
                class="bg-amber-950/80 hover:bg-amber-900 text-amber-300 border border-amber-600/40 text-[11px] font-bold py-1.5 rounded-lg transition-all flex items-center justify-center gap-1"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
                <span>Edit</span>
              </button>
              <button 
                @click="confirmDeleteCompetition(comp)" 
                class="bg-rose-950/80 hover:bg-rose-900 text-rose-300 border border-rose-600/40 text-[11px] font-bold py-1.5 rounded-lg transition-all flex items-center justify-center gap-1"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
                <span>Delete</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal 0: Comprehensive Event Details Popup -->
    <div v-if="showDetailsModal" class="fixed inset-0 bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4 z-50 animate-fade-in">
      <div class="glass-panel max-w-2xl w-full rounded-2xl overflow-hidden border-2 border-slate-700/80 shadow-2xl space-y-0 max-h-[90vh] flex flex-col">
        
        <!-- Header Banner with Poster Image or Category Gradient -->
        <div class="h-44 w-full relative p-6 flex flex-col justify-between overflow-hidden shrink-0" :style="getCardBannerStyle(selectedComp)">
          <div class="absolute inset-0 bg-gradient-to-t from-[#111927] via-[#111927]/60 to-transparent"></div>
          
          <div class="relative z-10 flex items-center justify-between">
            <span class="px-3 py-1 rounded-full text-sm font-mono font-extrabold uppercase bg-black/60 backdrop-blur border border-white/20 text-white flex items-center gap-1.5 shadow">
              <span>{{ getCategoryEmoji(selectedComp?.category) }}</span>
              <span>{{ selectedComp?.category?.toUpperCase() || 'EVENT' }}</span>
            </span>
            <button @click="showDetailsModal = false" class="w-8 h-8 rounded-full bg-black/60 hover:bg-black text-slate-300 hover:text-white border border-white/20 flex items-center justify-center font-mono font-bold text-base transition-all">✕</button>
          </div>

          <div class="relative z-10 space-y-1.5">
            <div class="flex items-center gap-2">
              <span :class="getPriorityBadgeClass(selectedComp?.priority)" class="text-xs font-mono font-extrabold uppercase px-2 py-0.5 rounded border">
                {{ selectedComp?.priority }} PRIORITY
              </span>
              <span :class="selectedComp?.computed_status === 'ended' ? 'bg-slate-900 text-slate-400 border-slate-700' : selectedComp?.computed_status === 'ongoing' ? 'bg-emerald-950 text-[#9fef00] border-[#9fef00]' : 'bg-cyan-950 text-[#00f0ff] border-[#00f0ff]'" class="text-xs font-mono font-bold uppercase px-2 py-0.5 rounded border">
                {{ selectedComp?.computed_status || 'UPCOMING' }}
              </span>
            </div>
            <h2 class="text-2xl font-black text-white font-mono leading-tight drop-shadow-md">{{ selectedComp?.title }}</h2>
          </div>
        </div>

        <!-- Scrollable Modal Content Body (10 Detailed Sections) -->
        <div class="p-6 space-y-5 overflow-y-auto font-mono text-sm text-slate-300 flex-1">

          <!-- 1. Full Description -->
          <div class="space-y-1.5 bg-[#090d16] p-4 rounded-xl border border-slate-800/80">
            <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <span>📜</span>
              <span>Complete Event Overview & Description</span>
            </h4>
            <p class="text-slate-200 text-sm leading-relaxed whitespace-pre-line">
              {{ selectedComp?.description || 'No detailed overview supplied for this competition.' }}
            </p>
          </div>

          <!-- 2. Detailed IST Timeline Grid (Starts, Ends, Deadline) -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div class="bg-[#090d16] p-3.5 rounded-xl border border-emerald-500/30 space-y-1.5">
              <span class="text-[11px] text-slate-400 uppercase block font-bold">1. Event Starts (IST)</span>
              <p class="text-sm font-bold text-emerald-400">{{ formatDate(selectedComp?.starts_at) }}</p>
            </div>
            <div class="bg-[#090d16] p-3.5 rounded-xl border border-rose-500/30 space-y-1.5">
              <span class="text-[11px] text-slate-400 uppercase block font-bold">2. Event Ends (IST)</span>
              <p class="text-sm font-bold text-rose-400">{{ formatDate(selectedComp?.ends_at) }}</p>
            </div>
            <div class="bg-[#090d16] p-3.5 rounded-xl border border-amber-500/30 space-y-1.5">
              <span class="text-[11px] text-slate-400 uppercase block font-bold">3. Application Deadline</span>
              <p class="text-sm font-bold text-amber-400">{{ formatDate(selectedComp?.application_deadline) || 'No hard deadline' }}</p>
            </div>
          </div>

          <!-- 3. Key Details Metadata Grid -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3 bg-[#090d16] p-4 rounded-xl border border-slate-800">
            <div class="space-y-1">
              <span class="text-[11px] text-slate-500 block uppercase">Category</span>
              <span class="text-sm text-white font-bold uppercase">{{ selectedComp?.category }}</span>
            </div>
            <div class="space-y-1">
              <span class="text-[11px] text-slate-500 block uppercase">Priority</span>
              <span class="text-sm text-white font-bold uppercase">{{ selectedComp?.priority }}</span>
            </div>
            <div class="space-y-1">
              <span class="text-[11px] text-slate-500 block uppercase">My Status</span>
              <span class="text-sm text-cyan-400 font-bold uppercase">{{ formatInvolvement(selectedComp?.user_involvement) }}</span>
            </div>
            <div class="space-y-1">
              <span class="text-[11px] text-slate-500 block uppercase">Attendees / Scanned</span>
              <span class="text-sm text-emerald-400 font-bold">{{ selectedComp?.attendee_count || 0 }} Members</span>
            </div>
          </div>

          <!-- 4. Registration & Portal External Link -->
          <div v-if="selectedComp?.external_link" class="bg-cyan-950/40 p-3.5 rounded-xl border border-cyan-500/40 flex items-center justify-between gap-3">
            <div class="min-w-0 flex-1">
              <span class="text-xs text-cyan-300 uppercase block font-bold">Official External Portal / Link</span>
              <p class="text-sm text-slate-300 font-mono truncate">{{ selectedComp?.external_link }}</p>
            </div>
            <a :href="selectedComp?.external_link" target="_blank" class="btn-neon-cyan text-xs py-2 px-4 rounded-lg font-bold shrink-0">
              Open Portal ↗
            </a>
          </div>

        </div>

        <!-- Modal Footer Actions -->
        <div class="p-4 bg-[#090d16] border-t border-slate-800/80 flex items-center justify-between font-mono shrink-0">
          <button @click="showDetailsModal = false" class="text-slate-400 hover:text-white text-xs px-4 py-2">Close</button>
          
          <div class="flex items-center gap-2">
            <!-- Student Action -->
            <button 
              v-if="selectedComp?.category === 'club' || selectedComp?.category === 'Club'"
              @click="showDetailsModal = false; openFeedbackModal(selectedComp)" 
              class="bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 text-xs py-2 px-4 rounded-lg font-bold"
            >
              ⭐ Event Feedback & Rating
            </button>
            <button 
              v-else
              @click="showDetailsModal = false; openApplyModal(selectedComp)" 
              class="btn-neon-cyan text-xs py-2 px-4 rounded-lg font-bold"
            >
              Apply / Submit Proof
            </button>

            <!-- Teacher/Admin Action -->
            <button 
              v-if="authStore.isTeacher" 
              @click="showDetailsModal = false; openAttendanceModal(selectedComp)" 
              class="bg-amber-400 text-black font-bold text-xs py-2 px-4 rounded-lg"
            >
              Teacher Scanner HUD
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- Modal 1: Student Application Proof -->

    <!-- Modal 1: Student Application Proof -->
    <div v-if="showApplyModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="glass-panel max-w-lg w-full p-6 space-y-4">
        <h3 class="text-lg font-bold text-white">Upload Registration Proof</h3>
        <p class="text-xs text-slate-400">
          Upload a screenshot of your external registration confirmation or team ticket for <strong class="text-white">{{ selectedComp?.title }}</strong>.
        </p>

        <div class="space-y-3">
          <input type="file" @change="handleFileUpload" accept="image/*" class="input-field text-xs py-2" />
          <div v-if="uploading" class="text-xs text-cyan-400 font-mono">Uploading & scanning with ClamAV...</div>
          <div v-if="uploadedScreenshotUrl" class="w-full h-36 rounded overflow-hidden bg-slate-900 border border-slate-700">
            <img :src="uploadedScreenshotUrl" alt="Proof" class="w-full h-full object-contain" />
          </div>
        </div>

        <div class="flex justify-end gap-3 pt-2">
          <button @click="showApplyModal = false" class="text-xs text-slate-400 hover:text-white px-3 py-2 font-mono">Cancel</button>
          <button @click="submitApplicationProof" :disabled="!uploadedScreenshotUrl || submitting" class="btn-neon-cyan text-xs py-2 px-5">
            Submit Application
          </button>
        </div>
      </div>
    </div>

    <!-- Modal 2: Teacher Announce Competition -->
    <div v-if="showAnnounceModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="glass-panel max-w-xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-bold text-white">Announce New Competition</h3>
        
        <form @submit.prevent="submitAnnounce" class="space-y-4 text-xs">
          <div>
            <label class="block font-mono text-slate-400 mb-1">Title *</label>
            <input v-model="newComp.title" required class="input-field" placeholder="e.g. DEF CON CTF Quals" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block font-mono text-slate-400 mb-1">Category</label>
              <select v-model="newComp.category" class="input-field">
                <option value="ctf">CTF</option>
                <option value="hackathon">Hackathon</option>
                <option value="workshop">Workshop</option>
                <option value="club">Club Event (with QR Attendance)</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label class="block font-mono text-slate-400 mb-1">Priority</label>
              <select v-model="newComp.priority" class="input-field">
                <option value="high">High (Red)</option>
                <option value="medium">Medium (Amber)</option>
                <option value="normal">Normal (Gray)</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block font-mono text-slate-400 mb-1">Description *</label>
            <textarea v-model="newComp.description" rows="3" required class="input-field" placeholder="Overview of the competition..."></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block font-mono text-slate-400 mb-1">Starts At *</label>
              <input v-model="newComp.starts_at" type="datetime-local" required class="input-field" />
            </div>

            <div>
              <label class="block font-mono text-slate-400 mb-1">Ends At *</label>
              <input v-model="newComp.ends_at" type="datetime-local" required :min="newComp.starts_at" class="input-field" />
            </div>
          </div>

          <div>
            <label class="block font-mono text-slate-400 mb-1">Application Deadline</label>
            <input v-model="newComp.application_deadline" type="datetime-local" :max="newComp.starts_at" class="input-field" />
          </div>
          <p v-if="announceError" class="text-rose-400 text-xs font-bold">{{ announceError }}</p>

          <div>
            <label class="block font-mono text-slate-400 mb-1">External Registration Link</label>
            <input v-model="newComp.external_link" type="url" class="input-field" placeholder="https://..." />
          </div>

          <div class="space-y-2">
            <label class="block font-mono text-slate-400 mb-1">Event Poster / Cover Image</label>
            <div class="flex items-center gap-3">
              <label class="cursor-pointer bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-3 py-2 rounded-lg text-xs font-mono font-bold flex items-center gap-2 transition-all">
                <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                <span>{{ posterUploading ? 'Uploading Poster...' : '📁 Upload Poster Image' }}</span>
                <input type="file" @change="uploadPosterFile" accept="image/*" class="hidden" :disabled="posterUploading" />
              </label>
              <span class="text-slate-500 text-[11px] font-mono">or paste URL below</span>
            </div>
            <input v-model="newComp.poster_image" type="text" class="input-field" placeholder="https://... or uploaded image URL" />
            <div v-if="newComp.poster_image" class="mt-2 relative w-36 h-20 rounded-lg overflow-hidden border border-slate-700 bg-slate-900">
              <img :src="newComp.poster_image" class="w-full h-full object-cover" />
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-3 border-t border-slate-800">
            <button type="button" @click="showAnnounceModal = false" class="text-xs text-slate-400 hover:text-white px-3 py-2 font-mono">Cancel</button>
            <button type="submit" class="btn-neon-violet text-xs py-2 px-5">Publish Competition</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal 3: Verification Queue -->
    <div v-if="showQueueModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="glass-panel max-w-4xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <h3 class="text-lg font-bold text-white">Verification Queue: {{ selectedComp?.title }}</h3>
          <button @click="showQueueModal = false" class="text-slate-400 hover:text-white font-mono">✕</button>
        </div>

        <div v-if="queueList.length === 0" class="py-8 text-center text-slate-500 font-mono text-xs">
          No application submissions in queue.
        </div>

        <div v-else class="space-y-4">
          <div v-for="app in queueList" :key="app.id" class="p-4 bg-slate-900/90 rounded-lg border border-slate-800 grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
            <!-- Left: Applicant details -->
            <div class="space-y-2">
              <div class="flex items-center gap-2">
                <span class="font-bold text-white text-sm">{{ app.applicant_full_name }}</span>
                <span class="text-xs text-slate-400">(@{{ app.applicant_username }})</span>
              </div>
              <p class="text-xs text-slate-400 font-mono">Applied: {{ formatDate(app.applied_at) }}</p>
              <div>
                <span :class="app.application_status === 'verified' ? 'text-emerald-400' : 'text-amber-400'" class="text-xs font-mono font-bold uppercase">
                  Status: {{ app.application_status }}
                </span>
              </div>

              <div class="flex gap-2 pt-2">
                <button @click="verifyApp(app.id, 'verified')" class="btn-neon-cyan text-xs py-1 px-3">Approve</button>
                <button @click="verifyApp(app.id, 'rejected')" class="bg-red-950 hover:bg-red-900 text-red-300 border border-red-600/40 text-xs py-1 px-3 rounded font-mono">Reject</button>
              </div>
            </div>

            <!-- Right: Side-by-side Screenshot -->
            <div class="w-full h-44 bg-slate-950 rounded border border-slate-800 overflow-hidden">
              <a :href="app.application_screenshot" target="_blank" class="block w-full h-full">
                <img :src="app.application_screenshot" alt="Screenshot Proof" class="w-full h-full object-contain" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal 4: Post-Event Wrap-up -->
    <div v-if="showWrapupModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="glass-panel max-w-3xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <h3 class="text-lg font-bold text-white">Post-Event Wrap-up: {{ selectedComp?.title }}</h3>
          <button @click="showWrapupModal = false" class="text-slate-400 hover:text-white font-mono">✕</button>
        </div>

        <div class="space-y-4 text-xs">
          <div>
            <label class="block font-mono text-slate-400 mb-1">Event Summary Notes</label>
            <textarea v-model="wrapupData.summary_notes" rows="2" class="input-field" placeholder="Describe the team performance and achievements..."></textarea>
          </div>

          <h4 class="font-bold text-slate-200 border-b border-slate-800 pb-1">Verified Participants Results & Certificates</h4>

          <div v-for="(p, idx) in wrapupParticipants" :key="p.id" class="p-3 bg-slate-900 rounded border border-slate-800 space-y-2">
            <div class="flex justify-between items-center font-bold text-slate-100">
              <span>{{ p.applicant_full_name }} (@{{ p.applicant_username }})</span>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block font-mono text-slate-400 mb-1">Result</label>
                <select v-model="p.result" class="input-field text-xs py-1">
                  <option value="participated">Participated</option>
                  <option value="winner">Winner (Auto-Certificate)</option>
                  <option value="runner_up">Runner Up (Auto-Certificate)</option>
                  <option value="not_selected">Not Selected</option>
                </select>
              </div>

              <div>
                <label class="block font-mono text-slate-400 mb-1">Placement Label</label>
                <input v-model="p.placement_label" class="input-field text-xs py-1" placeholder="e.g. 1st Place / Top 5" />
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-3 border-t border-slate-800">
            <button @click="showWrapupModal = false" class="text-xs text-slate-400 hover:text-white px-3 py-2 font-mono">Cancel</button>
            <button @click="submitWrapup" class="btn-neon-violet text-xs py-2 px-5">Submit Wrap-up</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal 5: Event Attendance Roster & Feedback Modal -->
    <div v-if="showAttendanceModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="glass-panel max-w-4xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto font-mono">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <div>
            <span class="text-[10px] font-mono uppercase bg-amber-950 text-amber-400 border border-amber-500/40 px-2.5 py-0.5 rounded font-bold">
              CLUB EVENT MANAGEMENT
            </span>
            <h3 class="text-lg font-bold text-white mt-1 font-mono">Event Details: {{ selectedComp?.title }}</h3>
          </div>
          <button @click="showAttendanceModal = false" class="text-slate-400 hover:text-white font-mono text-lg">✕</button>
        </div>

        <!-- Attendance / Feedback Toggle Tabs -->
        <div class="flex items-center gap-2 border-b border-slate-800 pb-3 text-xs">
          <button 
            @click="activeAttendanceTab = 'roster'"
            :class="[
              'px-4 py-2 rounded-lg font-bold transition-all flex items-center gap-2',
              activeAttendanceTab === 'roster' ? 'bg-amber-400 text-black shadow-md' : 'text-slate-400 hover:text-white bg-[#0c1117]'
            ]"
          >
            <span>📋 Attendance Roster</span>
            <span class="bg-black/30 text-current px-2 py-0.5 rounded text-[10px]">{{ attendanceList.length }}</span>
          </button>
          <button 
            @click="activeAttendanceTab = 'feedback'"
            :class="[
              'px-4 py-2 rounded-lg font-bold transition-all flex items-center gap-2',
              activeAttendanceTab === 'feedback' ? 'bg-amber-400 text-black shadow-md' : 'text-slate-400 hover:text-white bg-[#0c1117]'
            ]"
          >
            <span>⭐ Member Feedback & Ratings</span>
            <span class="bg-black/30 text-current px-2 py-0.5 rounded text-[10px]">
              {{ eventAvgRating > 0 ? eventAvgRating + ' ★ (' + eventTotalRatings + ')' : '0 Reviews' }}
            </span>
          </button>
        </div>

        <!-- TAB 1: ATTENDANCE ROSTER -->
        <div v-if="activeAttendanceTab === 'roster'" class="space-y-4">
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-slate-900/80 p-3.5 rounded-lg border border-slate-800 text-xs">
            <div>
              <span class="text-slate-300">Total Scanned Attendees: <strong class="text-amber-400 text-sm font-bold">{{ attendanceList.length }}</strong></span>
            </div>

            <button 
              @click="exportAttendanceCsv(selectedComp.id)" 
              class="btn-htb text-xs py-2 px-4 bg-amber-400 hover:bg-amber-300 text-black font-extrabold flex items-center gap-2 shadow"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
              </svg>
              <span>Export Attendance CSV</span>
            </button>
          </div>

          <div v-if="attendanceLoading" class="py-12 text-center text-slate-500 text-xs">
            Loading attendance records...
          </div>

          <div v-else-if="attendanceList.length === 0" class="py-12 text-center text-slate-500 text-xs">
            No attendance records scanned yet for this event.
          </div>

          <div v-else class="overflow-x-auto border border-slate-800 rounded-lg">
            <table class="w-full text-left text-xs">
              <thead class="bg-[#0c1117] text-slate-400 uppercase text-[10px] border-b border-slate-800">
                <tr>
                  <th class="p-3">Member</th>
                  <th class="p-3">Member ID</th>
                  <th class="p-3">Scanned At</th>
                  <th class="p-3">Approved By</th>
                  <th class="p-3">Remark</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-800 bg-[#111927]">
                <tr v-for="att in attendanceList" :key="att.id" class="hover:bg-slate-800/50">
                  <td class="p-3">
                    <div class="flex items-center gap-2">
                      <img :src="att.user_avatar_url || '/logo.png'" alt="Avatar" class="w-6 h-6 rounded-full object-cover border border-slate-700" />
                      <div>
                        <span class="font-bold text-white block">{{ att.user_full_name }}</span>
                        <span class="text-[10px] text-slate-400">@{{ att.user_username }}</span>
                      </div>
                    </div>
                  </td>
                  <td class="p-3 text-amber-300 font-bold">{{ att.user_member_id || 'N/A' }}</td>
                  <td class="p-3 text-slate-300">{{ formatDate(att.scanned_at) }}</td>
                  <td class="p-3 text-slate-400">{{ att.scanned_by_name }}</td>
                  <td class="p-3 text-slate-300 italic">{{ att.remark || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- TAB 2: MEMBER FEEDBACK & RATINGS -->
        <div v-else-if="activeAttendanceTab === 'feedback'" class="space-y-4">
          <div class="bg-slate-900/80 p-4 rounded-lg border border-slate-800 flex items-center justify-between text-xs">
            <div>
              <span class="text-slate-400 block uppercase font-bold text-[10px]">Average Event Satisfaction Rating</span>
              <div class="flex items-center gap-2 mt-1">
                <span class="text-2xl font-extrabold text-amber-400">{{ eventAvgRating }}</span>
                <div class="flex text-amber-400 text-sm">
                  <span v-for="s in 5" :key="s">{{ s <= Math.round(eventAvgRating) ? '★' : '☆' }}</span>
                </div>
                <span class="text-slate-400 text-xs">({{ eventTotalRatings }} total reviews)</span>
              </div>
            </div>
          </div>

          <div v-if="eventFeedbackList.length === 0" class="py-12 text-center text-slate-500 text-xs">
            No member feedback submitted for this event yet.
          </div>

          <div v-else class="space-y-3">
            <div v-for="fb in eventFeedbackList" :key="fb.id" class="p-4 bg-[#111927] rounded-xl border border-slate-800 space-y-2 text-xs">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <img :src="fb.user_avatar_url || '/logo.png'" class="w-6 h-6 rounded-full border border-slate-700 object-cover" />
                  <div>
                    <span class="font-bold text-white">{{ fb.user_full_name }}</span>
                    <span class="text-[10px] text-slate-400 ml-1.5">@{{ fb.user_username }}</span>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <div class="flex text-amber-400 text-xs">
                    <span v-for="s in 5" :key="s">{{ s <= fb.rating ? '★' : '☆' }}</span>
                  </div>
                  <span class="text-[10px] text-slate-400">{{ formatDate(fb.created_at) }}</span>
                </div>
              </div>
              <p class="text-slate-300 leading-relaxed bg-[#080c14] p-3 rounded-lg border border-slate-800/60 italic">
                "{{ fb.feedback_text || 'No written comments provided.' }}"
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Modal 6: Member Club Event Feedback Modal -->
    <div v-if="showFeedbackModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="glass-panel max-w-lg w-full p-6 space-y-4 font-mono">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <div>
            <span class="text-[10px] uppercase bg-amber-950 text-amber-400 border border-amber-500/40 px-2.5 py-0.5 rounded font-bold">
              CLUB EVENT FEEDBACK
            </span>
            <h3 class="text-lg font-bold text-white mt-1">{{ selectedComp?.title }}</h3>
          </div>
          <button @click="showFeedbackModal = false" class="text-slate-400 hover:text-white text-lg">✕</button>
        </div>

        <div class="space-y-4 text-xs">
          <div>
            <label class="block font-bold text-slate-300 uppercase mb-2">1. Your Overall Rating</label>
            <div class="flex items-center gap-2">
              <button 
                v-for="star in 5" 
                :key="star" 
                type="button" 
                @click="feedbackRating = star"
                class="text-2xl transition-transform hover:scale-125 focus:outline-none"
              >
                <span v-if="star <= feedbackRating" class="text-amber-400">★</span>
                <span v-else class="text-slate-700">☆</span>
              </button>
              <span class="text-amber-400 font-bold text-sm ml-2">{{ feedbackRating }}/5 Stars</span>
            </div>
          </div>

          <div>
            <label class="block font-bold text-slate-300 uppercase mb-1">2. Your Comments & Suggestions</label>
            <textarea 
              v-model="feedbackText" 
              rows="3" 
              class="input-field w-full text-xs font-mono bg-[#0c1117] border-slate-700" 
              placeholder="What did you learn? How was the speaker, venue, or presentation? Share your feedback..."
            ></textarea>
          </div>

          <div v-if="feedbackSuccess" class="p-3 bg-emerald-950/90 border border-emerald-500 text-emerald-300 rounded-lg text-xs font-bold flex items-center gap-2">
            <svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
            </svg>
            <span>{{ feedbackSuccess }}</span>
          </div>
          <div v-if="feedbackError" class="p-3 bg-rose-950/90 border border-rose-500 text-rose-300 rounded-lg text-xs font-bold flex items-center gap-2">
            <svg class="w-4 h-4 text-rose-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <span>{{ feedbackError }}</span>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="showFeedbackModal = false" class="text-slate-400 hover:text-white px-3 py-2">Cancel</button>
            <button 
              type="button" 
              @click="submitEventFeedback" 
              :disabled="feedbackSubmitting"
              class="btn-htb py-2 px-5 bg-amber-400 hover:bg-amber-300 text-black font-extrabold shadow"
            >
              {{ feedbackSubmitting ? 'Submitting...' : 'Submit Event Feedback' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Edit Event / Competition -->
    <div v-if="showEditModal" class="fixed inset-0 bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4 z-50 animate-fade-in overflow-y-auto">
      <div class="glass-panel max-w-2xl w-full p-6 space-y-4 font-mono rounded-2xl border-2 border-amber-500/40 my-8">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <div class="flex items-center gap-2">
            <span class="text-xs uppercase bg-amber-500/20 text-amber-400 border border-amber-500/40 px-2.5 py-0.5 rounded font-bold">
              EDIT EVENT / COMPETITION
            </span>
            <h3 class="text-lg font-bold text-white">#{{ editingForm.id }}</h3>
          </div>
          <button @click="showEditModal = false" class="text-slate-400 hover:text-white text-lg">✕</button>
        </div>

        <form @submit.prevent="submitEditCompetition" class="space-y-4 text-xs">
          <div>
            <label class="block font-bold text-slate-300 uppercase mb-1">Title *</label>
            <input v-model="editingForm.title" type="text" required class="input-field w-full bg-[#090d16] border-slate-700" placeholder="e.g. CyberXploit CTF 2026" />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block font-bold text-slate-300 uppercase mb-1">Category</label>
              <select v-model="editingForm.category" class="input-field w-full bg-[#090d16] border-slate-700">
                <option value="ctf">CTF</option>
                <option value="hackathon">Hackathon</option>
                <option value="workshop">Workshop</option>
                <option value="club">Club Event</option>
                <option value="webinar">Webinar</option>
                <option value="bootcamp">Bootcamp</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label class="block font-bold text-slate-300 uppercase mb-1">Priority</label>
              <select v-model="editingForm.priority" class="input-field w-full bg-[#090d16] border-slate-700">
                <option value="high">High Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="normal">Normal Priority</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label class="block font-bold text-slate-300 uppercase mb-1">Starts At *</label>
              <input v-model="editingForm.starts_at" type="datetime-local" required class="input-field w-full bg-[#090d16] border-slate-700" />
            </div>
            <div>
              <label class="block font-bold text-slate-300 uppercase mb-1">Ends At *</label>
              <input v-model="editingForm.ends_at" type="datetime-local" required :min="editingForm.starts_at" class="input-field w-full bg-[#090d16] border-slate-700" />
            </div>
            <div>
              <label class="block font-bold text-slate-300 uppercase mb-1">Registration Deadline</label>
              <input v-model="editingForm.application_deadline" type="datetime-local" :max="editingForm.starts_at" class="input-field w-full bg-[#090d16] border-slate-700" />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block font-bold text-slate-300 uppercase mb-1">Portal / External Registration Link</label>
              <input v-model="editingForm.external_link" type="url" class="input-field w-full bg-[#090d16] border-slate-700" placeholder="https://..." />
            </div>
            <div>
              <label class="block font-bold text-slate-300 uppercase mb-1">Poster Image URL</label>
              <input v-model="editingForm.poster_image" type="url" class="input-field w-full bg-[#090d16] border-slate-700" placeholder="https://..." />
            </div>
          </div>

          <div>
            <label class="block font-bold text-slate-300 uppercase mb-1">Description</label>
            <textarea v-model="editingForm.description" rows="4" class="input-field w-full bg-[#090d16] border-slate-700" placeholder="Describe the event goals, rules, venue, or prizes..."></textarea>
          </div>

          <div v-if="editError" class="p-3 bg-rose-950/90 border border-rose-500 text-rose-300 rounded-lg text-xs font-bold flex items-center gap-2">
            <svg class="w-4 h-4 text-rose-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <span>{{ editError }}</span>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="showEditModal = false" class="text-slate-400 hover:text-white px-3 py-2">Cancel</button>
            <button 
              type="submit" 
              :disabled="editSubmitting"
              class="btn-htb py-2 px-6 bg-amber-400 hover:bg-amber-300 text-black font-extrabold shadow"
            >
              {{ editSubmitting ? 'Saving Changes...' : 'Save Competition Edits' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const categories = ['All', 'CTF', 'Hackathon', 'Workshop', 'Club', 'Other']
const activeCategory = ref('All')
const searchQuery = ref('')

const filterStatus = ref('all')
const filterPriority = ref('all')
const filterInvolvement = ref('all')

const competitions = ref([])
const loading = ref(false)

const showEditModal = ref(false)
const editSubmitting = ref(false)
const editError = ref('')

const editingForm = ref({
  id: null,
  title: '',
  description: '',
  category: 'ctf',
  priority: 'normal',
  starts_at: '',
  ends_at: '',
  application_deadline: '',
  external_link: '',
  poster_image: ''
})

const toIsoLocal = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return ''
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const mins = String(d.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${mins}`
}

const openEditModal = (comp) => {
  editError.value = ''
  editingForm.value = {
    id: comp.id,
    title: comp.title || '',
    description: comp.description || '',
    category: (comp.category || 'ctf').toLowerCase(),
    priority: (comp.priority || 'normal').toLowerCase(),
    starts_at: toIsoLocal(comp.starts_at),
    ends_at: toIsoLocal(comp.ends_at),
    application_deadline: toIsoLocal(comp.application_deadline),
    external_link: comp.external_link || '',
    poster_image: comp.poster_image || ''
  }
  showEditModal.value = true
}

const submitEditCompetition = async () => {
  editError.value = ''
  if (editingForm.value.ends_at <= editingForm.value.starts_at) {
    editError.value = 'Ends At must be after Starts At'
    return
  }
  if (editingForm.value.application_deadline && editingForm.value.application_deadline > editingForm.value.starts_at) {
    editError.value = 'Application Deadline must be on or before Starts At'
    return
  }
  editSubmitting.value = true
  try {
    const payload = {
      title: editingForm.value.title,
      description: editingForm.value.description,
      category: editingForm.value.category,
      priority: editingForm.value.priority,
      starts_at: editingForm.value.starts_at,
      ends_at: editingForm.value.ends_at,
      application_deadline: editingForm.value.application_deadline || null,
      external_link: editingForm.value.external_link,
      poster_image: editingForm.value.poster_image
    }
    await axios.put(`/api/competitions/${editingForm.value.id}`, payload)
    showEditModal.value = false
    await fetchCompetitions()
  } catch (err) {
    editError.value = err.response?.data?.error || 'Failed to update competition'
  } finally {
    editSubmitting.value = false
  }
}

const filteredCompetitions = computed(() => {
  if (!searchQuery.value.trim()) return competitions.value
  const q = searchQuery.value.toLowerCase().trim()
  return competitions.value.filter(c => 
    (c.title || '').toLowerCase().includes(q) ||
    (c.category || '').toLowerCase().includes(q) ||
    (c.description || '').toLowerCase().includes(q)
  )
})

const getCategoryEmoji = (category) => {
  const cat = (category || '').toLowerCase()
  if (cat.includes('ctf')) return '⚡'
  if (cat.includes('hackathon')) return '🚀'
  if (cat.includes('workshop')) return '⚙️'
  if (cat.includes('club')) return '🛡️'
  return '🏆'
}

const getCardBannerStyle = (comp) => {
  const cat = (comp.category || '').toLowerCase()
  if (comp.poster_image && comp.poster_image !== '/logo.png') {
    return { backgroundImage: `url(${comp.poster_image})`, backgroundSize: 'cover', backgroundPosition: 'center' }
  }
  if (cat.includes('club')) {
    return { background: 'linear-gradient(135deg, #1c1300 0%, #3d2800 50%, #0d0800 100%)' }
  }
  if (cat.includes('ctf')) {
    return { background: 'linear-gradient(135deg, #051a10 0%, #0e3b22 50%, #03100a 100%)' }
  }
  if (cat.includes('hackathon')) {
    return { background: 'linear-gradient(135deg, #041829 0%, #093456 50%, #020d17 100%)' }
  }
  if (cat.includes('workshop')) {
    return { background: 'linear-gradient(135deg, #19062b 0%, #370e5c 50%, #0e0319 100%)' }
  }
  return { background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #090d16 100%)' }
}

const confirmDeleteCompetition = async (comp) => {
  if (!confirm(`Are you sure you want to delete "${comp.title}"? This action cannot be undone.`)) return
  try {
    await axios.delete(`/api/competitions/${comp.id}`)
    await fetchCompetitions()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete event')
  }
}

const showDetailsModal = ref(false)
const posterUploading = ref(false)

const openEventDetails = (comp) => {
  if (!comp) return
  selectedComp.value = comp
  showDetailsModal.value = true
}

const uploadPosterFile = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  posterUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('feature', 'competitions')

    const res = await axios.post('/api/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    if (res.data && res.data.url) {
      newComp.value.poster_image = res.data.url
    }
  } catch (err) {
    alert('Failed to upload poster image: ' + (err.response?.data?.error || err.message))
  } finally {
    posterUploading.value = false
  }
}

const showApplyModal = ref(false)
const showAnnounceModal = ref(false)
const showQueueModal = ref(false)
const showWrapupModal = ref(false)
const showAttendanceModal = ref(false)
const attendanceList = ref([])
const attendanceLoading = ref(false)

const selectedComp = ref(null)
const uploading = ref(false)
const submitting = ref(false)
const uploadedScreenshotUrl = ref('')

const queueList = ref([])
const wrapupParticipants = ref([])
const wrapupData = ref({ summary_notes: '' })

const newComp = ref({
  title: '',
  description: '',
  category: 'ctf',
  priority: 'normal',
  starts_at: '',
  ends_at: '',
  application_deadline: '',
  external_link: '',
  poster_image: ''
})
const announceError = ref('')

const fetchCompetitions = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/competitions', {
      params: {
        category: activeCategory.value,
        status: filterStatus.value,
        priority: filterPriority.value,
        involvement: filterInvolvement.value
      }
    })
    competitions.value = res.data.competitions || []
  } catch (err) {
    console.error('Failed to load competitions:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCompetitions()
})

const formatDate = (isoStr) => {
  if (!isoStr) return 'N/A'
  try {
    return new Date(isoStr).toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
  } catch (e) {
    return isoStr
  }
}

const getPriorityBorderClass = (priority) => {
  if (priority === 'high') return 'border-l-4 border-l-red-500'
  if (priority === 'medium') return 'border-l-4 border-l-amber-500'
  return 'border-l-4 border-l-slate-500'
}

const getPriorityBadgeClass = (priority) => {
  if (priority === 'high') return 'bg-red-950/80 text-red-400 border-red-600/40'
  if (priority === 'medium') return 'bg-amber-950/80 text-amber-400 border-amber-600/40'
  return 'bg-slate-800 text-slate-300 border-slate-700'
}

const getInvolvementBadgeClass = (status) => {
  if (status === 'verified') return 'bg-emerald-950/80 text-emerald-400 border-emerald-600/40'
  if (status === 'pending_verification') return 'bg-amber-950/80 text-amber-400 border-amber-600/40'
  if (status === 'rejected') return 'bg-red-950/80 text-red-400 border-red-600/40'
  return 'bg-slate-900 text-slate-400 border-slate-800'
}

const formatInvolvement = (status) => {
  if (status === 'pending_verification') return 'Pending Verification'
  if (status === 'verified') return 'Verified Participant'
  if (status === 'rejected') return 'Rejected'
  return 'Not Applied'
}

const openApplyModal = (comp) => {
  selectedComp.value = comp
  uploadedScreenshotUrl.value = comp.user_participation?.application_screenshot || ''
  showApplyModal.value = true
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  uploading.value = true
  const formData = new FormData()
  formData.append('file', file)
  formData.append('feature', 'competitions')

  try {
    const res = await axios.post('/api/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    uploadedScreenshotUrl.value = res.data.url
  } catch (err) {
    alert(err.response?.data?.error || "couldn't be verified as a valid file")
  } finally {
    uploading.value = false
  }
}

const submitApplicationProof = async () => {
  if (!selectedComp.value || !uploadedScreenshotUrl.value) return
  submitting.value = true

  try {
    await axios.post(`/api/competitions/${selectedComp.value.id}/apply`, {
      application_screenshot: uploadedScreenshotUrl.value
    })
    showApplyModal.value = false
    await fetchCompetitions()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to submit application')
  } finally {
    submitting.value = false
  }
}

const submitAnnounce = async () => {
  announceError.value = ''
  if (newComp.value.ends_at && newComp.value.starts_at && newComp.value.ends_at <= newComp.value.starts_at) {
    announceError.value = 'Ends At must be after Starts At'
    return
  }
  if (newComp.value.application_deadline && newComp.value.starts_at && newComp.value.application_deadline > newComp.value.starts_at) {
    announceError.value = 'Application Deadline must be on or before Starts At'
    return
  }
  try {
    await axios.post('/api/competitions', newComp.value)
    showAnnounceModal.value = false
    newComp.value = { title: '', description: '', category: 'ctf', priority: 'normal', starts_at: '', ends_at: '', application_deadline: '', external_link: '' }
    await fetchCompetitions()
  } catch (err) {
    announceError.value = err.response?.data?.error || 'Failed to announce competition'
  }
}

const openVerificationQueue = async (comp) => {
  selectedComp.value = comp
  try {
    const res = await axios.get(`/api/competitions/${comp.id}/applications`)
    queueList.value = res.data.applications || []
    showQueueModal.value = true
  } catch (err) {
    alert('Failed to load queue')
  }
}

const verifyApp = async (appId, status) => {
  try {
    await axios.post(`/api/competitions/${selectedComp.value.id}/applications/${appId}/verify`, { status })
    await openVerificationQueue(selectedComp.value)
    await fetchCompetitions()
  } catch (err) {
    alert('Verification update failed')
  }
}

const openWrapupModal = async (comp) => {
  selectedComp.value = comp
  try {
    const res = await axios.get(`/api/competitions/${comp.id}/applications`)
    wrapupParticipants.value = res.data.applications.map(a => ({
      participation_id: a.id,
      applicant_full_name: a.applicant_full_name,
      applicant_username: a.applicant_username,
      result: a.result || 'participated',
      placement_label: a.placement_label || ''
    }))
    wrapupData.value.summary_notes = comp.wrapup_notes || ''
    showWrapupModal.value = true
  } catch (err) {
    alert('Failed to load wrapup details')
  }
}

const submitWrapup = async () => {
  try {
    await axios.post(`/api/competitions/${selectedComp.value.id}/wrapup`, {
      summary_notes: wrapupData.value.summary_notes,
      participants: wrapupParticipants.value
    })
    showWrapupModal.value = false
    await fetchCompetitions()
  } catch (err) {
    alert('Wrap-up submission failed')
  }
}

const activeAttendanceTab = ref('roster')
const eventFeedbackList = ref([])
const eventAvgRating = ref(0)
const eventTotalRatings = ref(0)

const showFeedbackModal = ref(false)
const feedbackRating = ref(5)
const feedbackText = ref('')
const feedbackSubmitting = ref(false)
const feedbackSuccess = ref('')
const feedbackError = ref('')

const openFeedbackModal = async (comp) => {
  selectedComp.value = comp
  showFeedbackModal.value = true
  feedbackSuccess.value = ''
  feedbackError.value = ''
  try {
    const res = await axios.get(`/api/competitions/${comp.id}/feedback`)
    if (res.data.user_feedback) {
      feedbackRating.value = res.data.user_feedback.rating
      feedbackText.value = res.data.user_feedback.feedback_text || ''
    } else {
      feedbackRating.value = 5
      feedbackText.value = ''
    }
  } catch (err) {
    console.error('Failed to load user feedback', err)
  }
}

const submitEventFeedback = async () => {
  if (!selectedComp.value) return
  feedbackSubmitting.value = true
  feedbackSuccess.value = ''
  feedbackError.value = ''
  try {
    const res = await axios.post(`/api/competitions/${selectedComp.value.id}/feedback`, {
      rating: feedbackRating.value,
      feedback_text: feedbackText.value
    })
    feedbackSuccess.value = res.data.message || 'Feedback submitted successfully!'
    setTimeout(() => {
      showFeedbackModal.value = false
    }, 1200)
  } catch (err) {
    feedbackError.value = err.response?.data?.error || 'Failed to submit feedback'
  } finally {
    feedbackSubmitting.value = false
  }
}

const loadEventFeedbackRoster = async (compId) => {
  try {
    const res = await axios.get(`/api/competitions/${compId}/feedback`)
    eventFeedbackList.value = res.data.feedbacks || []
    eventAvgRating.value = res.data.avg_rating || 0
    eventTotalRatings.value = res.data.total_ratings || 0
  } catch (err) {
    console.error('Failed to load event feedback roster', err)
  }
}

const openAttendanceModal = async (comp) => {
  selectedComp.value = comp
  activeAttendanceTab.value = 'roster'
  showAttendanceModal.value = true
  attendanceLoading.value = true
  try {
    const res = await axios.get(`/api/competitions/${comp.id}/attendance`)
    attendanceList.value = res.data.attendees || []
    await loadEventFeedbackRoster(comp.id)
  } catch (err) {
    alert('Failed to load event attendance roster')
  } finally {
    attendanceLoading.value = false
  }
}

const exportAttendanceCsv = (compId) => {
  window.open(`/api/competitions/${compId}/attendance/export`, '_blank')
}

// ==================== LIVE IST CLOCK TIMER ====================
const liveTimeFormatted = ref('')
let clockTimer = null

const updateLiveClock = () => {
  const now = new Date()
  liveTimeFormatted.value = now.toLocaleTimeString('en-IN', {
    timeZone: 'Asia/Kolkata',
    hour12: true,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}

onMounted(() => {
  fetchCompetitions()
  updateLiveClock()
  clockTimer = setInterval(updateLiveClock, 1000)
})

onUnmounted(() => {
  if (clockTimer) clearInterval(clockTimer)
})
</script>
