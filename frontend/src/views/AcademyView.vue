<template>
  <div class="space-y-8 font-sans selection:bg-[#00f0ff] selection:text-black">
      
      <!-- TryHackMe-Style Hero Header Banner -->
      <div class="glass-panel p-8 md:p-10 rounded-3xl bg-[#0d1420]/90 border border-[#1f293d] shadow-2xl relative overflow-hidden">
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-8 relative z-10">
          <div class="space-y-3 max-w-2xl">
            <span class="text-xs font-mono font-bold text-[#00f0ff] uppercase tracking-wider bg-[#00f0ff]/10 px-3 py-1 rounded-full border border-[#00f0ff]/30">
              LEARN & HACK
            </span>
            <h1 class="text-3xl md:text-5xl font-extrabold text-white tracking-tight font-serif leading-tight">
              Cyber Security Learning Paths
            </h1>
            <p class="text-slate-300 text-sm md:text-base leading-relaxed">
              Discover real-world offensive & defensive cybersecurity modules, live classes, and structured roadmaps.
            </p>
            <div class="flex items-center gap-6 pt-2 font-mono text-xs md:text-sm">
              <div class="flex items-center space-x-2">
                <span class="text-lg font-bold text-white">{{ clubStore.courses?.length || 0 }}</span>
                <span class="text-slate-400">Active Paths & Modules</span>
              </div>
              <span class="text-slate-600">•</span>
              <div class="flex items-center space-x-2">
                <span class="text-lg font-bold text-white">{{ liveClasses?.length || 0 }}</span>
                <span class="text-slate-400">Scheduled Live Sessions</span>
              </div>
            </div>
          </div>

          <!-- Studio Authoring & Management Actions -->
          <div class="flex flex-wrap items-center gap-3 font-mono">
            <button 
              v-if="authStore.isTeacher" 
              @click="openCreatePathModal" 
              class="btn-htb text-xs py-3 px-5 font-bold uppercase tracking-wider shadow-lg flex items-center justify-center space-x-2"
            >
              <svg class="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              <span>Create Path / Module</span>
            </button>

            <router-link
              v-if="authStore.isTeacher"
              to="/academy/write"
              class="bg-[#161b22] hover:bg-[#21262d] text-slate-200 border border-[#30363d] text-xs py-3 px-5 font-bold rounded-xl transition-all flex items-center justify-center space-x-2"
            >
              <svg class="w-4 h-4 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
              <span>Content Studio</span>
            </router-link>

            <router-link
              v-if="authStore.isTeacher"
              to="/academy/roadmap-studio"
              class="bg-[#161b22] hover:bg-[#21262d] text-slate-200 border border-[#30363d] text-xs py-3 px-5 font-bold rounded-xl transition-all flex items-center justify-center space-x-2"
            >
              <svg class="w-4 h-4 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
              </svg>
              <span>Roadmap Studio</span>
            </router-link>

            <router-link
              v-if="authStore.isTeacher"
              to="/academy/certification-studio"
              class="bg-[#161b22] hover:bg-[#21262d] text-slate-200 border border-[#30363d] text-xs py-3 px-5 font-bold rounded-xl transition-all flex items-center justify-center space-x-2"
            >
              <svg class="w-4 h-4 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span>Certification Studio</span>
            </router-link>

            <button
              v-if="authStore.isTeacher"
              @click="showLiveModal = true" 
              class="btn-neon-cyan text-xs py-3 px-5 font-bold uppercase tracking-wider flex items-center justify-center space-x-2"
            >
              <svg class="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
              </svg>
              <span>Live Class</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Sub-Navigation Tabs Bar -->
      <div class="flex items-center space-x-3 border-b border-[#1f293d] pb-4 overflow-x-auto font-mono">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-7 py-3.5 rounded-xl text-base font-bold transition-all flex items-center space-x-2 whitespace-nowrap',
            activeTab === tab.id
              ? 'bg-[#9fef00]/15 text-[#9fef00] border border-[#9fef00]/40 shadow-[0_0_12px_rgba(159,239,0,0.15)]'
              : 'text-slate-400 hover:text-white hover:bg-[#151f30]'
          ]"
        >
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- TAB: PATHS -->
      <div v-if="activeTab === 'paths'" class="space-y-6">
        
        <!-- Search & Filter Controls -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 font-mono">
          <div class="md:col-span-2 relative flex items-center">
            <div class="absolute left-3.5 pointer-events-none text-slate-400 flex items-center justify-center">
              <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
            </div>
            <input 
              v-model="pathSearch" 
              type="text" 
              placeholder="Search learning paths & modules..." 
              class="input-field w-full text-xs !pl-11 py-3 bg-[#0d1420]" 
            />
          </div>

          <div>
            <select v-model="difficultyFilter" class="input-field w-full text-xs py-3 bg-[#0d1420] text-slate-300">
              <option value="All">Difficulty: All</option>
              <option value="Easy">Easy</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
          </div>

          <div>
            <select v-model="statusFilter" class="input-field w-full text-xs py-3 bg-[#0d1420] text-slate-300">
              <option value="All">Status: All</option>
              <option value="published">Published</option>
              <option value="draft">Draft</option>
            </select>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="filteredPaths.length === 0" class="glass-panel p-16 text-center text-slate-400 space-y-4 rounded-3xl bg-[#0d1420]">
          <div class="flex justify-center text-[#9fef00]">
            <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
            </svg>
          </div>
          <h3 class="text-lg font-bold text-white font-serif">No Learning Paths Found</h3>
          <p class="text-xs text-slate-400 max-w-md mx-auto font-mono">
            There are currently no matching learning paths. Teachers and Admins can create new paths or write notes using the studio.
          </p>
          <button v-if="authStore.isTeacher" @click="openCreatePathModal" class="btn-htb text-xs py-2 px-5 font-mono uppercase font-bold">
            + Create First Path
          </button>
        </div>

        <!-- Learning Path Cards Grid -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div 
            v-for="path in filteredPaths" 
            :key="path.id"
            class="glass-panel rounded-2xl bg-[#0d1420] border transition-all duration-300 flex flex-col justify-between overflow-hidden group hover:scale-[1.02]"
            :class="path.enrollment?.is_completed ? 'border-[#9fef00]/50 hover:border-[#9fef00]' : 'border-[#1f293d] hover:border-[#00f0ff]'"
          >
            <!-- Card Image Artwork & Badges -->
            <div class="relative h-48 bg-[#0b0e14] overflow-hidden cursor-pointer" @click="navigateToCourse(path.slug)">
              <img
                :src="path.cover_image || '/default-cover.svg'"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div class="absolute inset-0 bg-gradient-to-t from-[#0d1420] via-transparent to-black/30"></div>

              <!-- Top Left Badge Tag -->
              <span v-if="path.enrollment?.is_completed" class="absolute top-3 left-3 bg-[#9fef00] text-black text-[10px] font-mono font-extrabold px-2.5 py-0.5 rounded uppercase tracking-wider shadow-md flex items-center gap-1">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
                Completed
              </span>
              <span v-else-if="path.is_new" class="absolute top-3 left-3 bg-[#9fef00] text-black text-[10px] font-mono font-extrabold px-2.5 py-0.5 rounded uppercase tracking-wider shadow-md">
                NEW 2026
              </span>

              <!-- Top Right Management Actions for Admins & Teachers -->
              <div v-if="authStore.isTeacher" class="absolute top-3 right-3 flex items-center space-x-1.5 bg-[#0b0e14]/90 p-1 rounded-lg border border-[#1f293d] backdrop-blur-sm z-10">
                <button @click.stop="moveCourseLeft(idx)" title="Move Left" class="text-xs p-1 bg-[#151f30] hover:bg-[#1f293d] text-[#9fef00] rounded font-bold font-mono">
                  &larr;
                </button>
                <button @click.stop="moveCourseRight(idx)" title="Move Right" class="text-xs p-1 bg-[#151f30] hover:bg-[#1f293d] text-[#9fef00] rounded font-bold font-mono">
                  &rarr;
                </button>
                <button @click.stop="openEditPathModal(path)" title="Edit Path" class="text-xs px-2 py-1 bg-[#151f30] hover:bg-[#1f293d] text-[#00f0ff] rounded font-mono font-bold flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 210.382H3v-3.572L16.732 3.732z"/>
                  </svg>
                  <span>Edit</span>
                </button>
                <button @click.stop="deletePath(path.id)" title="Delete Path" class="text-xs p-1.5 bg-rose-950/80 hover:bg-rose-900 text-rose-300 rounded font-mono font-bold flex items-center">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Card Content Body -->
            <div class="p-5 space-y-4 flex-1 flex flex-col justify-between cursor-pointer" @click="navigateToCourse(path.slug)">
              <div class="space-y-2">
                <div class="flex items-center justify-between font-mono text-[10px]">
                  <span class="text-[#00f0ff] uppercase font-bold tracking-wider">{{ path.difficulty || 'Easy' }}</span>
                  <span class="text-slate-500 font-bold">{{ path.modules_count || 0 }} Modules</span>
                </div>
                <h3 class="text-lg font-bold text-white group-hover:text-[#00f0ff] transition-colors leading-snug">
                  {{ path.title }}
                </h3>
                <p class="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                  {{ path.description }}
                </p>
                <div v-if="path.enrollment" class="space-y-1 pt-1">
                  <div class="flex items-center justify-between text-[10px] font-mono">
                    <span class="text-slate-500 font-bold uppercase">Progress</span>
                    <span :class="path.enrollment.is_completed ? 'text-[#9fef00]' : 'text-[#00f0ff]'" class="font-bold">{{ Math.round(path.enrollment.progress_percent) }}%</span>
                  </div>
                  <div class="w-full bg-[#1f293d] h-1.5 rounded-full overflow-hidden">
                    <div class="bg-gradient-to-r from-[#00f0ff] to-[#9fef00] h-full transition-all duration-500" :style="{ width: `${path.enrollment.progress_percent}%` }"></div>
                  </div>
                </div>
              </div>

              <div class="pt-3 border-t border-[#1f293d] flex items-center justify-between font-mono text-xs">
                <span class="text-slate-400 text-[11px]">Author: {{ path.author_name || 'HackerXploit Staff' }}</span>
                <span class="text-[#9fef00] font-bold group-hover:underline">{{ pathCtaLabel(path) }} &rarr;</span>
              </div>
            </div>

          </div>
        </div>

      </div>

      <!-- TAB: ROADMAP -->
      <div v-if="activeTab === 'roadmap'" class="space-y-6 font-mono">
        <div class="glass-panel p-6 bg-[#0d1420] border border-[#1f293d] rounded-2xl space-y-4">
          <div class="flex items-center justify-between flex-wrap gap-3">
            <div class="flex items-center space-x-2.5 min-w-0">
              <svg class="w-5 h-5 text-[#9fef00] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
              </svg>
              <!-- Roadmap picker - lets teachers/students switch between every
                   roadmap created in Roadmap Studio, not just the default one -->
              <select
                v-if="roadmapsList.length > 1"
                v-model="selectedRoadmapSlug"
                class="input-field bg-[#0b0e14] text-lg font-bold text-white py-1.5 pl-2 pr-8 max-w-full"
              >
                <option v-for="rm in roadmapsList" :key="rm.slug" :value="rm.slug">{{ rm.title }}</option>
              </select>
              <h3 v-else class="text-lg font-bold text-white truncate">{{ roadmapsList[0]?.title || 'Cybersecurity Learning Roadmap' }}</h3>
            </div>
            <router-link v-if="authStore.isTeacher" to="/academy/roadmap-studio" class="bg-[#161b22] hover:bg-[#21262d] text-slate-200 border border-[#30363d] text-xs py-2 px-4 font-bold rounded-xl transition-all flex items-center gap-1.5">
              <svg class="w-4 h-4 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
              <span>Roadmap Studio</span>
            </router-link>
          </div>
        </div>

        <div class="h-[calc(100vh-320px)] min-h-[500px] rounded-2xl overflow-hidden border border-[#21262d] shadow-2xl relative">
          <InteractiveRoadmapGraph :roadmapSlug="selectedRoadmapSlug" />
        </div>
      </div>

      <!-- TAB: CERTIFICATIONS -->
      <div v-if="activeTab === 'certifications'" class="space-y-6 font-mono">
        <div class="glass-panel p-6 bg-[#0d1420] border border-[#1f293d] rounded-2xl space-y-4">
          <div class="flex items-center justify-between flex-wrap gap-3">
            <div class="flex items-center space-x-2.5 min-w-0">
              <svg class="w-5 h-5 text-[#9fef00] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <select
                v-if="certCategories.length > 1"
                v-model="selectedCertCategorySlug"
                class="input-field bg-[#0b0e14] text-lg font-bold text-white py-1.5 pl-2 pr-8 max-w-full"
              >
                <option v-for="cat in certCategories" :key="cat.slug" :value="cat.slug">{{ cat.title }}</option>
              </select>
              <h3 v-else-if="certCategories.length === 1" class="text-lg font-bold text-white truncate">{{ certCategories[0].title }}</h3>
              <h3 v-else class="text-lg font-bold text-white truncate">Certifications</h3>
            </div>
            <router-link v-if="authStore.isTeacher" to="/academy/certification-studio" class="bg-[#161b22] hover:bg-[#21262d] text-slate-200 border border-[#30363d] text-xs py-2 px-4 font-bold rounded-xl transition-all flex items-center gap-1.5">
              <svg class="w-4 h-4 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
              <span>Certification Studio</span>
            </router-link>
          </div>
          <p class="text-xs text-slate-400">Industry certifications grouped into progression flowcharts - exam links and provider info curated by the team.</p>
        </div>

        <!-- Empty State -->
        <div v-if="certCategories.length === 0" class="glass-panel p-16 text-center text-slate-400 space-y-4 rounded-3xl bg-[#0d1420]">
          <div class="flex justify-center text-[#9fef00]">
            <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <h3 class="text-lg font-bold text-white font-serif">No Certification Categories Yet</h3>
          <p class="text-xs text-slate-400 max-w-md mx-auto font-mono">
            Teachers and Admins can create categories and build certification flowcharts in the Certification Studio.
          </p>
          <router-link v-if="authStore.isTeacher" to="/academy/certification-studio" class="btn-htb text-xs py-2 px-5 font-mono uppercase font-bold inline-block">
            Open Certification Studio
          </router-link>
        </div>

        <!-- Flowchart Viewer -->
        <div v-else class="h-[600px] rounded-2xl overflow-hidden border border-[#21262d] shadow-2xl relative">
          <CertificationFlowViewer :categorySlug="selectedCertCategorySlug" />
        </div>
      </div>

      <!-- TAB: MODULES - flat list of individual modules (chapters) across
           every path, distinct from the "Learning Paths" tab which lists
           whole paths. This used to just re-render the same path cards
           again under a different label ("Module Folder"/"Start Module"),
           which was pure duplication. -->
      <div v-if="activeTab === 'modules'" class="space-y-6 font-mono">
        <div v-if="!modulesList.length" class="glass-panel p-12 text-center text-slate-500 text-xs rounded-2xl">
          No modules available.
        </div>
        <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          <router-link
            v-for="mod in modulesList"
            :key="mod.id"
            :to="`/academy/course/${mod.course_slug}/module/${mod.id}`"
            class="rounded-2xl overflow-hidden bg-[#0d1420] border border-[#1f293d] hover:border-[#00f0ff]/50 transition-all group flex flex-col"
          >
            <div class="h-40 w-full overflow-hidden relative flex-shrink-0">
              <img :src="mod.cover_image" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
              <span v-if="mod.status === 'draft'" class="absolute top-2 left-2 bg-amber-500 text-black text-[10px] font-mono font-extrabold px-2 py-0.5 rounded uppercase tracking-wider shadow-md">Draft</span>
            </div>
            <div class="p-3 space-y-1.5 flex-1 flex flex-col">
              <span class="text-[10px] uppercase text-[#9fef00] font-bold">{{ mod.difficulty || 'Easy' }}</span>
              <h3 class="text-sm font-bold text-white group-hover:text-[#00f0ff] transition-colors line-clamp-2 leading-snug">{{ mod.title }}</h3>
              <p class="text-[11px] text-slate-500 truncate flex-1">{{ mod.course_title }}</p>
              <div class="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                <span>{{ mod.notes_count }} notes</span>
                <span>{{ mod.read_time_minutes }} min</span>
              </div>
            </div>
          </router-link>
        </div>
      </div>

      <!-- TAB: LIVE CLASSES -->
      <div v-if="activeTab === 'live'" class="space-y-6 font-mono">
        <div v-if="liveClasses.length === 0" class="glass-panel p-12 text-center text-slate-500 text-xs rounded-2xl">
          No live classes currently scheduled.
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-for="lc in liveClasses" :key="lc.id" class="glass-panel p-6 bg-[#0d1420] border border-[#1f293d] rounded-2xl flex flex-col justify-between space-y-4">
            <div class="space-y-3">
              <div class="flex justify-between items-start">
                <span class="text-xs font-bold text-[#9fef00] bg-[#9fef00]/10 px-2.5 py-0.5 rounded border border-[#9fef00]/30 uppercase flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-[#9fef00]"></span> Scheduled Live
                </span>
                <span class="text-xs text-slate-400">{{ formatDate(lc.scheduled_at) }}</span>
              </div>

              <!-- Thumbnail artwork -->
              <img :src="lc.thumbnail_url || '/default-cover.svg'" class="w-full h-40 object-cover rounded-xl border border-[#1f293d]" />

              <h3 class="text-lg font-bold text-white">{{ lc.title }}</h3>
              <p class="text-xs text-slate-300 leading-relaxed">{{ lc.description }}</p>
            </div>

            <div class="pt-4 border-t border-[#1f293d] flex justify-between items-center">
              <div v-if="authStore.isTeacher" class="flex items-center space-x-2">
                <button @click="openEditLiveModal(lc)" class="text-xs text-[#00f0ff] hover:underline font-bold">Edit</button>
                <button @click="deleteLiveClass(lc.id)" class="text-xs text-rose-400 hover:underline font-bold">Cancel</button>
              </div>
              <a :href="lc.meeting_link" target="_blank" class="btn-neon-cyan text-xs py-2 px-5 font-bold ml-auto flex items-center gap-2">
                <svg class="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                </svg>
                <span>Join Live Class</span>
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Create / Edit Path Modal for Admins & Teachers -->
      <div v-if="showPathModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm font-mono">
        <div class="w-full max-w-lg glass-panel p-6 rounded-2xl border border-[#1f293d] bg-[#0d1420]">
          <h3 class="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
            <span>{{ isEditingPath ? 'Edit Path / Module' : 'Create Path / Module' }}</span>
          </h3>
          <form @submit.prevent="handleSavePath" class="space-y-4">
            <div>
              <label class="block text-xs text-slate-400 uppercase mb-1">Path Title <span class="text-rose-400">*</span></label>
              <input v-model="pathForm.title" type="text" placeholder="e.g. Web Application Security" required class="input-field text-xs w-full py-2" />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-slate-400 uppercase mb-1">Difficulty</label>
                <select v-model="pathForm.difficulty" class="input-field text-xs w-full py-2 bg-[#0b0e14] text-slate-300">
                  <option value="Easy">Easy</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                </select>
              </div>

              <div>
                <label class="block text-xs text-slate-400 uppercase mb-1">Status</label>
                <select v-model="pathForm.status" class="input-field text-xs w-full py-2 bg-[#0b0e14] text-slate-300">
                  <option value="published">Published</option>
                  <option value="draft">Draft</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-xs text-slate-400 uppercase mb-1">Cover Image / Thumbnail URL</label>
              <div class="flex items-center gap-2">
                <input v-model="pathForm.cover_image" type="text" placeholder="/uploads/courses/cover.png or https://..." class="input-field text-xs flex-1 py-2" />
                <button type="button" @click="triggerCoverUpload" :disabled="coverUploading" class="btn-ghost text-xs py-2 px-3 text-[#00f0ff] border border-[#00f0ff]/40 hover:bg-[#00f0ff]/10 flex-shrink-0 font-bold">
                  {{ coverUploading ? 'Uploading...' : 'Upload Image' }}
                </button>
                <input ref="coverFileInput" type="file" accept="image/*" class="hidden" @change="handleCoverUpload" />
              </div>
            </div>

            <div>
              <label class="block text-xs text-slate-400 uppercase mb-1">Description</label>
              <textarea v-model="pathForm.description" rows="3" placeholder="Overview of learning path..." class="input-field text-xs w-full py-2"></textarea>
            </div>

            <div class="flex items-center space-x-2">
              <input v-model="pathForm.is_new" type="checkbox" id="is_new_chk" class="rounded border-[#1f293d]" />
              <label for="is_new_chk" class="text-xs text-slate-300">Highlight with NEW 2026 Badge</label>
            </div>

            <div class="flex justify-end space-x-3 pt-4 border-t border-[#1f293d]">
              <button type="button" @click="showPathModal = false" class="btn-ghost text-xs py-2 px-4">Cancel</button>
              <button type="submit" class="btn-htb text-xs py-2 px-5 font-bold uppercase">{{ isEditingPath ? 'Update Path' : 'Publish Path' }}</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Schedule / Edit Live Class Modal for Teachers -->
      <div v-if="showLiveModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm font-mono">
        <div class="w-full max-w-lg glass-panel p-6 rounded-2xl border border-[#1f293d] bg-[#0d1420]">
          <h3 class="text-xl font-bold text-white mb-4">{{ isEditingLive ? 'Edit Live Class' : 'Schedule Live Class' }}</h3>
          <form @submit.prevent="handleScheduleLive" class="space-y-4">
            <div>
              <label class="block text-xs text-slate-400 uppercase mb-1">Session Title <span class="text-rose-400">*</span></label>
              <input v-model="newLive.title" type="text" placeholder="e.g. Kerberoasting Deep Dive" required class="input-field text-xs w-full py-2" />
            </div>

            <div>
              <label class="block text-xs text-slate-400 uppercase mb-1">Meeting Link <span class="text-rose-400">*</span></label>
              <input v-model="newLive.meeting_link" type="url" placeholder="https://meet.google.com/xyz" required class="input-field text-xs w-full py-2" />
            </div>

            <div>
              <label class="block text-xs text-slate-400 uppercase mb-1">Thumbnail Artwork URL</label>
              <div class="flex items-center gap-2">
                <input v-model="newLive.thumbnail_url" type="text" placeholder="/uploads/courses/cover.png or https://..." class="input-field text-xs flex-1 py-2" />
                <button type="button" @click="triggerLiveCoverUpload" :disabled="liveCoverUploading" class="btn-ghost text-xs py-2 px-3 text-[#00f0ff] border border-[#00f0ff]/40 hover:bg-[#00f0ff]/10 flex-shrink-0 font-bold">
                  {{ liveCoverUploading ? 'Uploading...' : 'Upload Image' }}
                </button>
                <input ref="liveCoverFileInput" type="file" accept="image/*" class="hidden" @change="handleLiveCoverUpload" />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-slate-400 uppercase mb-1">Date & Time</label>
                <input v-model="newLive.scheduled_at" type="datetime-local" required class="input-field text-xs w-full py-2 bg-[#0b0e14]" />
              </div>
              <div>
                <label class="block text-xs text-slate-400 uppercase mb-1">Duration (Minutes)</label>
                <input v-model="newLive.duration_minutes" type="number" placeholder="60" class="input-field text-xs w-full py-2" />
              </div>
            </div>

            <div>
              <label class="block text-xs text-slate-400 uppercase mb-1">Description / Agenda</label>
              <textarea v-model="newLive.description" rows="3" placeholder="Session details..." class="input-field text-xs w-full py-2"></textarea>
            </div>

            <div class="flex justify-end space-x-3 pt-4 border-t border-[#1f293d]">
              <button type="button" @click="showLiveModal = false" class="btn-ghost text-xs py-2 px-4">Cancel</button>
              <button type="submit" class="btn-neon-cyan text-xs py-2 px-5 font-bold">{{ isEditingLive ? 'Update Live Class' : 'Publish Live Class' }}</button>
            </div>
          </form>
        </div>
      </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useClubStore } from '../stores/club'
import { usePreferences } from '../stores/preferences'
import InteractiveRoadmapGraph from '../components/InteractiveRoadmapGraph.vue'
import CertificationFlowViewer from '../components/CertificationFlowViewer.vue'

const router = useRouter()
const authStore = useAuthStore()
const clubStore = useClubStore()
const prefs = usePreferences()

const activeTab = ref('roadmap')
const pathSearch = ref('')
const difficultyFilter = ref('All')
const statusFilter = ref('All')

const tabs = [
  { id: 'roadmap', label: 'Roadmap' },
  { id: 'certifications', label: 'Certifications' },
  { id: 'paths', label: 'Learning Paths' },
  { id: 'modules', label: 'Modules' },
  { id: 'live', label: 'Live Classes' }
]

// Roadmaps created in Roadmap Studio only ever showed up inside the Studio
// itself - this tab used to hardcode roadmapSlug="cyber-security" for the
// graph canvas, so any other roadmap a teacher created was invisible
// everywhere else in the app.
const roadmapsList = ref([])
const selectedRoadmapSlug = ref('cyber-security')

const fetchRoadmapsList = async () => {
  try {
    const res = await axios.get('/api/roadmaps', { withCredentials: true })
    roadmapsList.value = res.data
    if (res.data.length && !res.data.some(r => r.slug === selectedRoadmapSlug.value)) {
      selectedRoadmapSlug.value = res.data[0].slug
    }
  } catch (e) {
    console.error('Failed to load roadmaps', e)
  }
}

const liveClasses = ref([])
const showLiveModal = ref(false)
const isEditingLive = ref(false)
const editingLiveId = ref(null)
const newLive = ref({ title: '', meeting_link: '', thumbnail_url: '', scheduled_at: '', duration_minutes: 60, description: '' })
const liveCoverUploading = ref(false)
const liveCoverFileInput = ref(null)

const showPathModal = ref(false)
const isEditingPath = ref(false)
const editingPathId = ref(null)
const pathForm = ref({ title: '', description: '', difficulty: 'Easy', cover_image: '', is_new: true, status: 'published' })

const coverUploading = ref(false)
const coverFileInput = ref(null)

const triggerCoverUpload = () => {
  if (coverFileInput.value) coverFileInput.value.click()
}

const handleCoverUpload = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return

  coverUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('feature', 'courses')

    const res = await axios.post('/api/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      withCredentials: true
    })

    if (res.data && res.data.url) {
      pathForm.value.cover_image = res.data.url
    }
  } catch (err) {
    alert('Failed to upload thumbnail: ' + (err.response?.data?.error || err.message))
  } finally {
    coverUploading.value = false
  }
}

const moveCourseLeft = async (idx) => {
  if (idx <= 0) return
  const courses = [...clubStore.courses]
  const temp = courses[idx]
  courses[idx] = courses[idx - 1]
  courses[idx - 1] = temp
  clubStore.courses = courses
}

const moveCourseRight = async (idx) => {
  if (idx >= clubStore.courses.length - 1) return
  const courses = [...clubStore.courses]
  const temp = courses[idx]
  courses[idx] = courses[idx + 1]
  courses[idx + 1] = temp
  clubStore.courses = courses
}

const filteredPaths = computed(() => {
  let list = clubStore.courses || []
  if (pathSearch.value.trim()) {
    const q = pathSearch.value.toLowerCase()
    list = list.filter(p => p.title.toLowerCase().includes(q) || (p.description && p.description.toLowerCase().includes(q)))
  }
  if (difficultyFilter.value !== 'All') {
    list = list.filter(p => (p.difficulty || 'Easy').toLowerCase() === difficultyFilter.value.toLowerCase())
  }
  if (statusFilter.value !== 'All') {
    list = list.filter(p => p.status === statusFilter.value)
  }
  return list
})

const navigateToCourse = (slug) => {
  if (slug) router.push(`/academy/course/${slug}`)
}

const pathCtaLabel = (path) => {
  if (!path.enrollment) return 'Start Path'
  if (path.enrollment.is_completed) return 'Review Path'
  return 'Continue Path'
}

const openCreatePathModal = () => {
  isEditingPath.value = false
  editingPathId.value = null
  pathForm.value = { title: '', description: '', difficulty: 'Easy', cover_image: '', is_new: true, status: 'published' }
  showPathModal.value = true
}

const openEditPathModal = (path) => {
  isEditingPath.value = true
  editingPathId.value = path.id
  pathForm.value = {
    title: path.title,
    description: path.description,
    difficulty: path.difficulty || 'Easy',
    cover_image: path.cover_image || '',
    is_new: path.is_new !== false,
    status: path.status || 'published'
  }
  showPathModal.value = true
}

const handleSavePath = async () => {
  if (!pathForm.value.title.trim()) return
  try {
    if (isEditingPath.value && editingPathId.value) {
      await axios.put(`/api/academy/courses/${editingPathId.value}`, pathForm.value, { withCredentials: true })
      showPathModal.value = false
      await clubStore.fetchCourses()
    } else {
      const res = await axios.post('/api/academy/courses', pathForm.value, { withCredentials: true })
      showPathModal.value = false
      await clubStore.fetchCourses()
      // Jump straight to the new path's overview page - that's where modules
      // now get added, instead of leaving the teacher stranded on the empty
      // card grid with no obvious next step.
      router.push(`/academy/course/${res.data.slug}`)
    }
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to save path')
  }
}

const deletePath = async (courseId) => {
  if (!confirm('Delete this path and all associated chapters?')) return
  try {
    await axios.delete(`/api/academy/courses/${courseId}`, { withCredentials: true })
    await clubStore.fetchCourses()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete path')
  }
}

// Certifications now live inside categories, each rendered as a flowchart
// (built in Certification Studio) - this tab just picks which category to
// view, it no longer edits certifications directly.
const certCategories = ref([])
const selectedCertCategorySlug = ref('')

const fetchCertCategories = async () => {
  try {
    const res = await axios.get('/api/certification-categories', { withCredentials: true })
    certCategories.value = res.data
    if (res.data.length && !res.data.some(c => c.slug === selectedCertCategorySlug.value)) {
      selectedCertCategorySlug.value = res.data[0].slug
    }
  } catch (err) {
    console.error('Failed to fetch certification categories', err)
  }
}

const modulesList = ref([])

const fetchModulesList = async () => {
  try {
    const res = await axios.get('/api/academy/modules', { withCredentials: true })
    modulesList.value = res.data.modules || []
  } catch (err) {
    console.error('Failed to fetch modules', err)
  }
}

const fetchLiveClasses = async () => {
  try {
    const res = await axios.get('/api/academy/live-classes', { withCredentials: true })
    liveClasses.value = res.data.live_classes || []
  } catch (err) {
    console.error('Failed to fetch live classes', err)
  }
}

// datetime-local inputs hold a bare "wall clock" string with no timezone -
// it means whatever the browser's local time zone says, not UTC. Sending
// that straight to the backend made it store the scheduler's local digits
// AS IF they were UTC, so anyone viewing the session in a different time
// zone (or even the scheduler themselves, once correctly parsed) saw the
// wrong time. Convert explicitly at both boundaries instead.
const utcIsoToLocalInputValue = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const localInputValueToUtcIso = (localStr) => {
  return localStr ? new Date(localStr).toISOString() : null
}

const openEditLiveModal = (lc) => {
  isEditingLive.value = true
  editingLiveId.value = lc.id
  newLive.value = {
    title: lc.title,
    meeting_link: lc.meeting_link,
    thumbnail_url: lc.thumbnail_url || '',
    scheduled_at: utcIsoToLocalInputValue(lc.scheduled_at),
    duration_minutes: lc.duration_minutes || 60,
    description: lc.description || ''
  }
  showLiveModal.value = true
}

const triggerLiveCoverUpload = () => {
  if (liveCoverFileInput.value) liveCoverFileInput.value.click()
}

const handleLiveCoverUpload = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return

  liveCoverUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('feature', 'courses')

    const res = await axios.post('/api/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      withCredentials: true
    })

    if (res.data && res.data.url) {
      newLive.value.thumbnail_url = res.data.url
    }
  } catch (err) {
    alert('Failed to upload thumbnail: ' + (err.response?.data?.error || err.message))
  } finally {
    liveCoverUploading.value = false
  }
}

const handleScheduleLive = async () => {
  if (!newLive.value.title.trim() || !newLive.value.meeting_link.trim()) return
  try {
    const payload = { ...newLive.value, scheduled_at: localInputValueToUtcIso(newLive.value.scheduled_at) }
    if (isEditingLive.value && editingLiveId.value) {
      await axios.put(`/api/academy/live-classes/${editingLiveId.value}`, payload, { withCredentials: true })
    } else {
      await axios.post('/api/academy/live-classes', payload, { withCredentials: true })
    }
    showLiveModal.value = false
    newLive.value = { title: '', meeting_link: '', thumbnail_url: '', scheduled_at: '', duration_minutes: 60, description: '' }
    await fetchLiveClasses()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to save live class')
  }
}

const deleteLiveClass = async (id) => {
  if (!confirm('Cancel this live class session?')) return
  try {
    await axios.delete(`/api/academy/live-classes/${id}`, { withCredentials: true })
    await fetchLiveClasses()
  } catch (err) {
    alert('Failed to cancel session')
  }
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: prefs.is12h.value })
}

onMounted(() => {
  clubStore.fetchCourses()
  fetchLiveClasses()
  fetchRoadmapsList()
  fetchCertCategories()
  fetchModulesList()
})
</script>
