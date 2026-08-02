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
              <span>Modules Studio</span>
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
      <div class="flex items-center space-x-2 border-b border-[#1f293d] pb-3 overflow-x-auto font-mono">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 whitespace-nowrap',
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
            class="glass-panel rounded-2xl bg-[#0d1420] border border-[#1f293d] hover:border-[#00f0ff] transition-all duration-300 flex flex-col justify-between overflow-hidden group hover:scale-[1.02]"
          >
            <!-- Card Image Artwork & Badges -->
            <div class="relative h-48 bg-[#0b0e14] overflow-hidden cursor-pointer" @click="navigateToCourse(path.slug)">
              <img 
                :src="path.cover_image || '/uploads/courses/default_cover.png'" 
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
              />
              <div class="absolute inset-0 bg-gradient-to-t from-[#0d1420] via-transparent to-black/30"></div>

              <!-- Top Left Badge Tag -->
              <span v-if="path.is_new" class="absolute top-3 left-3 bg-[#9fef00] text-black text-[10px] font-mono font-extrabold px-2.5 py-0.5 rounded uppercase tracking-wider shadow-md">
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
                  <span class="text-slate-500 font-bold">{{ path.chapters_count || 0 }} Chapters</span>
                </div>
                <h3 class="text-lg font-bold text-white group-hover:text-[#00f0ff] transition-colors leading-snug">
                  {{ path.title }}
                </h3>
                <p class="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                  {{ path.description }}
                </p>
              </div>

              <div class="pt-3 border-t border-[#1f293d] flex items-center justify-between font-mono text-xs">
                <span class="text-slate-400 text-[11px]">Author: {{ path.author_name || 'HackerXploit Staff' }}</span>
                <span class="text-[#9fef00] font-bold group-hover:underline">Start Path &rarr;</span>
              </div>
            </div>

          </div>
        </div>

      </div>

      <!-- TAB: ROADMAP -->
      <div v-if="activeTab === 'roadmap'" class="space-y-6 font-mono">
        <div class="glass-panel p-6 bg-[#0d1420] border border-[#1f293d] rounded-2xl space-y-4">
          <div class="flex items-center space-x-2.5">
            <svg class="w-5 h-5 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
            </svg>
            <h3 class="text-lg font-bold text-white">Cybersecurity Learning Roadmap</h3>
          </div>
          <p class="text-xs text-slate-400">Structured pathways generated dynamically from published academy courses.</p>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
            <div 
              v-for="(course, idx) in clubStore.courses" 
              :key="course.id" 
              class="p-5 rounded-xl bg-[#0b0e14] border border-[#1f293d] space-y-3 cursor-pointer hover:border-[#00f0ff] transition-all"
              @click="navigateToCourse(course.slug)"
            >
              <span class="text-xs font-bold text-[#00f0ff] uppercase bg-[#00f0ff]/10 px-2.5 py-1 rounded border border-[#00f0ff]/30">Phase {{ idx + 1 }}</span>
              <h4 class="font-bold text-white text-sm">{{ course.title }}</h4>
              <p class="text-xs text-slate-400 line-clamp-2">{{ course.description }}</p>
              <div class="text-xs text-[#00f0ff]">{{ course.chapters_count || 1 }} Chapters &bull; {{ course.difficulty || 'Easy' }}</div>
            </div>

            <div v-if="!clubStore.courses?.length" class="col-span-3 text-center py-8 text-slate-500 text-xs">
              No active courses in roadmap yet.
            </div>
          </div>
        </div>
      </div>

      <!-- TAB: MODULES (Course Catalog) -->
      <div v-if="activeTab === 'modules'" class="space-y-6 font-mono">
        <div v-if="!clubStore.courses?.length" class="glass-panel p-12 text-center text-slate-500 text-xs rounded-2xl">
          No modules available.
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="course in clubStore.courses" :key="course.id" class="glass-panel p-6 flex flex-col justify-between hover:border-[#9fef00]/50 transition-all bg-[#0d1420] border border-[#1f293d] rounded-2xl">
            <div>
              <div class="flex items-center justify-between mb-3">
                <span class="text-[10px] uppercase bg-[#151f30] text-[#9fef00] px-2.5 py-0.5 rounded border border-[#9fef00]/30">
                  {{ course.difficulty || 'Easy' }}
                </span>
                <span class="text-xs text-slate-400">{{ course.chapters_count || 0 }} Chapters</span>
              </div>
              <h3 class="text-lg font-bold text-white mb-2">{{ course.title }}</h3>
              <p class="text-slate-300 text-xs line-clamp-3 mb-6 leading-relaxed">{{ course.description }}</p>
            </div>

            <div class="pt-4 border-t border-[#1f293d] flex items-center justify-between">
              <span class="text-xs text-slate-400">{{ course.status }}</span>
              <router-link :to="`/academy/course/${course.slug}`" class="btn-htb text-xs py-1.5 px-4">
                Start Module &rarr;
              </router-link>
            </div>
          </div>
      </div>

        <!-- ================= VISUAL FLOWCHART CANVAS ================= -->
        <div v-if="roadmapViewMode === 'flowchart'" class="space-y-10 overflow-x-auto pb-8">
          
          <!-- ROOT NODE: START HERE -->
          <div class="flex flex-col items-center justify-center space-y-4">
            <div class="px-8 py-3.5 rounded-2xl bg-gradient-to-r from-[#00f0ff]/20 via-[#9fef00]/20 to-purple-500/20 border-2 border-[#00f0ff] shadow-[0_0_20px_rgba(0,240,255,0.3)] text-center font-mono">
              <div class="text-[10px] text-[#9fef00] font-extrabold uppercase tracking-widest">START HERE</div>
              <div class="text-lg font-extrabold text-white tracking-tight">Cyber Security Roadmap</div>
            </div>

            <!-- Down Arrow Connector -->
            <svg class="w-6 h-8 text-[#00f0ff] animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 14l-7 7m0 0l-7-7m7 7V3"/>
            </svg>
          </div>

          <!-- STEP 1: FUNDAMENTALS STAGE -->
          <div class="max-w-5xl mx-auto space-y-4 p-6 rounded-3xl bg-[#080c14]/90 border border-[#1f293d] relative">
            <div class="text-center font-mono">
              <span class="px-3 py-1 rounded-full bg-[#9fef00]/10 text-[#9fef00] border border-[#9fef00]/30 text-xs font-bold uppercase tracking-wider">
                STEP 1: IT & Security Foundations
              </span>
            </div>

            <!-- Horizontal Flow Nodes Grid -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
              <div 
                v-for="node in getPhaseNodes('phase-1').filter(n => n.type === 'fundamental')" 
                :key="node.id"
                @click="selectedRoadmapNode = node"
                class="glass-panel p-4 rounded-2xl border border-[#9fef00]/40 bg-[#0d1420] hover:border-[#9fef00] hover:shadow-[0_0_15px_rgba(159,239,0,0.25)] transition-all cursor-pointer group text-center space-y-2"
              >
                <span class="text-[10px] font-mono bg-[#9fef00]/10 text-[#9fef00] px-2 py-0.5 rounded font-bold uppercase">
                  {{ node.difficulty }}
                </span>
                <h4 class="text-sm font-bold text-white group-hover:text-[#9fef00] font-mono leading-snug">
                  {{ node.title }}
                </h4>
                <p class="text-slate-400 text-[11px] line-clamp-2">{{ node.shortDescription }}</p>
                <div class="text-[10px] font-mono text-slate-500 pt-1 border-t border-[#1f293d]">
                  Inspect Node &rarr;
                </div>
              </div>
            </div>
          </div>

          <!-- Down Arrow Connector -->
          <div class="flex justify-center">
            <svg class="w-6 h-8 text-[#9fef00]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 14l-7 7m0 0l-7-7m7 7V3"/>
            </svg>
          </div>

          <!-- STEP 2: CORE GENERAL SECURITY & CERTIFICATION -->
          <div class="max-w-3xl mx-auto space-y-4 p-6 rounded-3xl bg-[#080c14]/90 border border-[#1f293d] text-center">
            <span class="px-3 py-1 rounded-full bg-amber-400/10 text-amber-400 border border-amber-400/30 text-xs font-bold uppercase font-mono tracking-wider">
              STEP 2: Baseline Security Certification
            </span>

            <div class="flex justify-center pt-2">
              <div 
                v-for="node in getPhaseNodes('phase-1').filter(n => n.type === 'certification')" 
                :key="node.id"
                @click="selectedRoadmapNode = node"
                class="glass-panel p-5 rounded-2xl border border-amber-400/50 bg-[#0d1420] hover:border-amber-400 hover:shadow-[0_0_20px_rgba(251,191,36,0.3)] transition-all cursor-pointer group text-center space-y-2 w-full max-w-md"
              >
                <div class="flex items-center justify-between font-mono text-[10px]">
                  <span class="bg-amber-400/20 text-amber-400 px-2 py-0.5 rounded font-bold">GLOBAL CERTIFICATION</span>
                  <span class="text-slate-400">SY0-701</span>
                </div>
                <h4 class="text-base font-extrabold text-white group-hover:text-amber-400 font-mono">
                  {{ node.title }}
                </h4>
                <p class="text-slate-300 text-xs leading-relaxed">{{ node.shortDescription }}</p>
              </div>
            </div>
          </div>

          <!-- SPLIT BRANCH FLOW CONNECTOR (3 SPECIALIZATION PATHS) -->
          <div class="space-y-4 pt-4">
            <div class="text-center font-mono">
              <span class="px-4 py-1.5 rounded-2xl bg-[#00f0ff]/10 text-[#00f0ff] border border-[#00f0ff]/40 text-xs font-extrabold uppercase tracking-widest">
                STEP 3: CHOOSE YOUR SPECIALIZATION PATHWAY
              </span>
            </div>

            <!-- SVG Branch Lines -->
            <div class="hidden md:block w-full max-w-5xl mx-auto h-8 relative">
              <svg class="w-full h-full text-[#1f293d]" fill="none" stroke="currentColor">
                <line x1="50%" y1="0" x2="50%" y2="100%" stroke="#00f0ff" stroke-width="2"/>
                <line x1="16%" y1="100%" x2="84%" y2="100%" stroke="#1f293d" stroke-width="2"/>
              </svg>
            </div>

            <!-- 3 SPECIALIZED BRANCH COLUMNS -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-7xl mx-auto items-start">
              
              <!-- BRANCH 1: OFFENSIVE SECURITY (RED TEAM) -->
              <div class="glass-panel p-5 rounded-3xl bg-[#0d1420] border-2 border-rose-500/40 space-y-4 relative overflow-hidden">
                <div class="absolute top-0 right-0 w-24 h-24 bg-rose-500/10 rounded-full blur-2xl pointer-events-none"></div>

                <div class="flex items-center space-x-2 font-mono pb-3 border-b border-[#1f293d]">
                  <span class="text-lg">⚔️</span>
                  <div>
                    <h3 class="text-base font-extrabold text-rose-400 font-serif">Red Team Pathway</h3>
                    <p class="text-[10px] text-slate-400">Offensive Penetration Testing</p>
                  </div>
                </div>

                <!-- Sequential Flow Stack -->
                <div class="space-y-3">
                  <div 
                    v-for="(node, nIdx) in getOffensiveNodes()" 
                    :key="node.id"
                    @click="selectedRoadmapNode = node"
                    class="p-3.5 rounded-xl border border-rose-500/30 bg-[#080c14] hover:border-rose-500 hover:shadow-[0_0_12px_rgba(244,63,94,0.2)] transition-all cursor-pointer group space-y-1.5"
                  >
                    <div class="flex items-center justify-between font-mono text-[10px]">
                      <span class="text-rose-400 font-bold">NODE 0{{ nIdx + 1 }}</span>
                      <span class="text-slate-400">{{ node.difficulty }}</span>
                    </div>
                    <h4 class="text-xs font-bold text-white group-hover:text-rose-300 font-mono">
                      {{ node.title }}
                    </h4>
                    <p class="text-slate-400 text-[11px] line-clamp-1 font-sans">{{ node.shortDescription }}</p>
                  </div>
                </div>
              </div>

              <!-- BRANCH 2: DEFENSIVE SECURITY (BLUE TEAM) -->
              <div class="glass-panel p-5 rounded-3xl bg-[#0d1420] border-2 border-[#00f0ff]/40 space-y-4 relative overflow-hidden">
                <div class="absolute top-0 right-0 w-24 h-24 bg-[#00f0ff]/10 rounded-full blur-2xl pointer-events-none"></div>

                <div class="flex items-center space-x-2 font-mono pb-3 border-b border-[#1f293d]">
                  <span class="text-lg">🛡️</span>
                  <div>
                    <h3 class="text-base font-extrabold text-[#00f0ff] font-serif">Blue Team Pathway</h3>
                    <p class="text-[10px] text-slate-400">SOC, Forensics & Defense</p>
                  </div>
                </div>

                <!-- Sequential Flow Stack -->
                <div class="space-y-3">
                  <div 
                    v-for="(node, nIdx) in getDefensiveNodes()" 
                    :key="node.id"
                    @click="selectedRoadmapNode = node"
                    class="p-3.5 rounded-xl border border-[#00f0ff]/30 bg-[#080c14] hover:border-[#00f0ff] hover:shadow-[0_0_12px_rgba(0,240,255,0.2)] transition-all cursor-pointer group space-y-1.5"
                  >
                    <div class="flex items-center justify-between font-mono text-[10px]">
                      <span class="text-[#00f0ff] font-bold">NODE 0{{ nIdx + 1 }}</span>
                      <span class="text-slate-400">{{ node.difficulty }}</span>
                    </div>
                    <h4 class="text-xs font-bold text-white group-hover:text-[#00f0ff] font-mono">
                      {{ node.title }}
                    </h4>
                    <p class="text-slate-400 text-[11px] line-clamp-1 font-sans">{{ node.shortDescription }}</p>
                  </div>
                </div>
              </div>

              <!-- BRANCH 3: CLOUD & DEVSECOPS -->
              <div class="glass-panel p-5 rounded-3xl bg-[#0d1420] border-2 border-purple-400/40 space-y-4 relative overflow-hidden">
                <div class="absolute top-0 right-0 w-24 h-24 bg-purple-500/10 rounded-full blur-2xl pointer-events-none"></div>

                <div class="flex items-center space-x-2 font-mono pb-3 border-b border-[#1f293d]">
                  <span class="text-lg">☁️</span>
                  <div>
                    <h3 class="text-base font-extrabold text-purple-400 font-serif">Cloud & DevSecOps</h3>
                    <p class="text-[10px] text-slate-400">Infrastructure & CI/CD Security</p>
                  </div>
                </div>

                <!-- Sequential Flow Stack -->
                <div class="space-y-3">
                  <div 
                    v-for="(node, nIdx) in getCloudNodes()" 
                    :key="node.id"
                    @click="selectedRoadmapNode = node"
                    class="p-3.5 rounded-xl border border-purple-400/30 bg-[#080c14] hover:border-purple-400 hover:shadow-[0_0_12px_rgba(192,132,252,0.2)] transition-all cursor-pointer group space-y-1.5"
                  >
                    <div class="flex items-center justify-between font-mono text-[10px]">
                      <span class="text-purple-400 font-bold">NODE 0{{ nIdx + 1 }}</span>
                      <span class="text-slate-400">{{ node.difficulty }}</span>
                    </div>
                    <h4 class="text-xs font-bold text-white group-hover:text-purple-300 font-mono">
                      {{ node.title }}
                    </h4>
                    <p class="text-slate-400 text-[11px] line-clamp-1 font-sans">{{ node.shortDescription }}</p>
                  </div>
                </div>
              </div>

            </div>
          </div>

          <!-- STEP 4: EXECUTIVE MASTERY & APEX CERTS -->
          <div class="max-w-4xl mx-auto space-y-4 p-6 rounded-3xl bg-[#080c14]/90 border border-[#1f293d] text-center">
            <div class="font-mono">
              <span class="px-4 py-1.5 rounded-2xl bg-amber-400/10 text-amber-400 border border-amber-400/40 text-xs font-extrabold uppercase tracking-widest">
                STEP 4: APEX CERTIFICATIONS & EXECUTIVE MASTERY
              </span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div 
                v-for="node in getApexCertNodes()" 
                :key="node.id"
                @click="selectedRoadmapNode = node"
                class="glass-panel p-5 rounded-2xl border border-amber-400/40 bg-[#0d1420] hover:border-amber-400 hover:shadow-[0_0_15px_rgba(251,191,36,0.25)] transition-all cursor-pointer group text-left space-y-2"
              >
                <div class="flex items-center justify-between font-mono text-[10px]">
                  <span class="bg-amber-400/20 text-amber-400 px-2 py-0.5 rounded font-bold">APEX CERTIFICATION</span>
                  <span class="text-purple-400 font-bold">{{ node.difficulty }}</span>
                </div>
                <h4 class="text-sm font-extrabold text-white group-hover:text-amber-400 font-mono">
                  {{ node.title }}
                </h4>
                <p class="text-slate-300 text-xs line-clamp-2 leading-relaxed">{{ node.shortDescription }}</p>
              </div>
            </div>
          </div>

        </div>

        <!-- ================= GRID LIST VIEW ================= -->
        <div v-else class="relative pl-6 md:pl-10 space-y-12 border-l-2 border-[#1f293d]/80 ml-2 md:ml-4">
          <div 
            v-for="(phase, pIdx) in filteredRoadmapPhases" 
            :key="phase.id"
            class="relative space-y-6"
          >
            <div class="absolute -left-[31px] md:-left-[47px] top-0 w-8 h-8 rounded-full bg-[#0d1420] border-2 border-[#00f0ff] text-[#00f0ff] flex items-center justify-center font-mono font-bold text-xs shadow-[0_0_12px_rgba(0,240,255,0.4)]">
              {{ pIdx + 1 }}
            </div>

            <div class="space-y-1 pt-0.5">
              <div class="flex items-center space-x-3">
                <h3 class="text-xl font-extrabold text-white font-serif tracking-tight">
                  {{ phase.title }}
                </h3>
                <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-[#151f30] text-[#9fef00] border border-[#1f293d]">
                  {{ phase.subtitle }}
                </span>
              </div>
              <p class="text-slate-400 text-xs font-sans leading-relaxed">{{ phase.description }}</p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 items-stretch">
              <div 
                v-for="node in phase.nodes" 
                :key="node.id"
                @click="selectedRoadmapNode = node"
                :class="[
                  'glass-panel p-5 rounded-2xl border transition-all duration-300 group cursor-pointer flex flex-col justify-between relative overflow-hidden bg-[#0d1420]',
                  getRoadmapBorderClass(node.type)
                ]"
              >
                <div class="space-y-3 relative z-10">
                  <div class="flex items-center justify-between font-mono text-[10px]">
                    <span :class="getRoadmapTypeBadgeClass(node.type)" class="px-2 py-0.5 rounded font-bold uppercase border">
                      {{ node.type }}
                    </span>
                    <span :class="getRoadmapDifficultyBadgeClass(node.difficulty)" class="px-2 py-0.5 rounded font-semibold">
                      {{ node.difficulty }}
                    </span>
                  </div>

                  <div>
                    <h4 class="text-sm font-bold text-white group-hover:text-[#00f0ff] transition-colors leading-snug font-mono">
                      {{ node.title }}
                    </h4>
                    <p class="text-slate-400 text-xs line-clamp-2 mt-1 font-sans leading-relaxed">
                      {{ node.shortDescription }}
                    </p>
                  </div>
                </div>

                <div class="pt-3 mt-3 border-t border-[#1f293d]/80 flex items-center justify-between text-xs font-mono text-slate-500 group-hover:text-[#00f0ff]">
                  <span class="text-[11px]">Inspect Details</span>
                  <span class="font-bold group-hover:translate-x-1 transition-transform">&rarr;</span>
                </div>
              </div>
            </div>
          </div>
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
              <img :src="lc.thumbnail_url || '/uploads/courses/default_cover.png'" class="w-full h-40 object-cover rounded-xl border border-[#1f293d]" />

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
                  {{ coverUploading ? 'Uploading...' : '📁 Upload Image' }}
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
              <input v-model="newLive.thumbnail_url" type="text" placeholder="/uploads/courses/cover.png" class="input-field text-xs w-full py-2" />
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

      <!-- Roadmap Node Explainer Modal -->

      <!-- TAB: ROADMAP (Interactive Data-Driven Node Graph) -->
      <div v-if="activeTab === 'roadmap'" class="h-[calc(100vh-160px)] rounded-2xl overflow-hidden border border-[#21262d] shadow-2xl relative">
        <InteractiveRoadmapGraph roadmapSlug="cyber-security" />
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

const router = useRouter()
const authStore = useAuthStore()
const clubStore = useClubStore()
const prefs = usePreferences()

const activeTab = ref('paths')
const pathSearch = ref('')
const difficultyFilter = ref('All')
const statusFilter = ref('All')

// Roadmap State & Data
const roadmapSearch = ref('')
const activeRoadmapCat = ref('all')
const selectedRoadmapNode = ref(null)
const roadmapViewMode = ref('flowchart')

const getPhaseNodes = (phaseId) => {
  const phase = roadmapPhasesData.find(p => p.id === phaseId)
  return phase ? phase.nodes : []
}

const getOffensiveNodes = () => {
  const allNodes = []
  roadmapPhasesData.forEach(p => {
    p.nodes.forEach(n => {
      if (n.type === 'offensive') allNodes.push(n)
    })
  })
  return allNodes
}

const getDefensiveNodes = () => {
  const allNodes = []
  roadmapPhasesData.forEach(p => {
    p.nodes.forEach(n => {
      if (n.type === 'defensive') allNodes.push(n)
    })
  })
  return allNodes
}

const getCloudNodes = () => {
  const allNodes = []
  roadmapPhasesData.forEach(p => {
    p.nodes.forEach(n => {
      if (n.type === 'cloud') allNodes.push(n)
    })
  })
  return allNodes
}

const getApexCertNodes = () => {
  const allNodes = []
  roadmapPhasesData.forEach(p => {
    p.nodes.forEach(n => {
      if (n.type === 'certification' && n.id !== 'comptia-secplus') allNodes.push(n)
    })
  })
  return allNodes
}

const roadmapCategories = [
  { id: 'all', label: 'All Tracks', icon: '🌐' },
  { id: 'fundamental', label: 'IT Fundamentals', icon: '💻' },
  { id: 'offensive', label: 'Offensive Security (Red)', icon: '⚔️' },
  { id: 'defensive', label: 'Defensive Security (Blue)', icon: '🛡️' },
  { id: 'cloud', label: 'Cloud & Engineering', icon: '☁️' },
  { id: 'certification', label: 'Certifications Pathway', icon: '📜' },
]

const roadmapPhasesData = [
  {
    id: 'phase-1',
    title: 'Phase 1: IT & Fundamental Skills',
    subtitle: 'Foundation Layer',
    description: 'Master hardware components, operating systems, wireless protocols, CTF practice arenas, and entry-level certifications.',
    nodes: [
      {
        id: 'hardware-os',
        type: 'fundamental',
        title: 'Hardware & OS Fundamentals',
        difficulty: 'Beginner',
        estimatedTime: '2 - 3 Weeks',
        shortDescription: 'Computer Hardware Components, Connection Types, OS-Independent Troubleshooting, Windows, Linux, MacOS.',
        fullDescription: 'Understand physical computer architecture, motherboard buses, RAM, storage interfaces, peripherals, and OS-independent diagnostic workflows across Windows, Linux, and MacOS.',
        skills: ['Hardware Components & Buses', 'Connection Types & Interfaces', 'OS-Independent Troubleshooting', 'Popular Suites (iCloud, Google, MS Office)', 'CRUD Operations on Files & CLI'],
        prerequisites: 'Basic Computer Usage',
        certifications: 'CompTIA A+',
        careerRoles: 'IT Support Specialist, Helpdesk Technician',
        salaryInsight: '$55,000 - $70,000 / year'
      },
      {
        id: 'wireless-local',
        type: 'fundamental',
        title: 'Local & Wireless Technologies',
        difficulty: 'Beginner',
        estimatedTime: '2 Weeks',
        shortDescription: 'NFC, WiFi, Bluetooth, Infrared, and wireless communication standards.',
        fullDescription: 'Learn how short-range and local wireless radio protocols transmit data, how handshakes occur, and how to identify vulnerability patterns in wireless access points.',
        skills: ['WiFi (802.11 Standards)', 'Bluetooth Security & Pairing', 'NFC & RFID Mechanics', 'Infrared Communications', 'Wireless Access Point Config'],
        prerequisites: 'Hardware Fundamentals',
        certifications: 'CompTIA Network+',
        careerRoles: 'Wireless Network Technician',
        salaryInsight: '$60,000 - $75,000 / year'
      },
      {
        id: 'ctf-arenas',
        type: 'fundamental',
        title: 'CTF Platforms & Practice Arenas',
        difficulty: 'Beginner',
        estimatedTime: 'Continuous',
        shortDescription: 'HackTheBox, TryHackMe, VulnHub, picoCTF, SANS Holiday Hack Challenge.',
        fullDescription: 'Hands-on practice platforms designed to build offensive and defensive problem-solving skills through gamified challenge rooms and vulnerable machines.',
        skills: ['HackTheBox Lab Navigation', 'TryHackMe Learning Paths', 'picoCTF Beginner Challenges', 'VulnHub Local VM Hacking', 'SANS Holiday Hack Challenges'],
        prerequisites: 'Linux CLI, Networking Basics',
        certifications: 'Practical CTF Badges',
        careerRoles: 'CTF Player, Cyber Researcher',
        salaryInsight: 'Skill Builder'
      },
      {
        id: 'beginner-certs',
        type: 'certification',
        title: 'Beginner Certifications Track',
        difficulty: 'Beginner',
        estimatedTime: '4 - 8 Weeks',
        shortDescription: 'CompTIA A+, CompTIA Linux+, CompTIA Network+, CCNA, CompTIA Security+.',
        fullDescription: 'Validate core competency in hardware, Linux system administration, Cisco routing/switching, and foundational security controls recognized by enterprise employers globally.',
        skills: ['CompTIA A+ (Core 1 & 2)', 'CompTIA Linux+ (XK0-005)', 'CompTIA Network+ (N10-008)', 'Cisco CCNA (200-301)', 'CompTIA Security+ (SY0-701)'],
        prerequisites: 'IT Fundamentals',
        certifications: 'CompTIA A+, Linux+, Network+, CCNA, Security+',
        careerRoles: 'Junior Systems Admin, Junior SOC Analyst',
        salaryInsight: '$70,000 - $90,000 / year'
      }
    ]
  },
  {
    id: 'phase-2',
    title: 'Phase 2: Networking & Infrastructure Knowledge',
    subtitle: 'Network Layer',
    description: 'Understand the OSI model, IP subnetting, network services, topologies, virtualization technologies, and authentication.',
    nodes: [
      {
        id: 'osi-subnetting',
        type: 'fundamental',
        title: 'OSI Model & IP Subnetting',
        difficulty: 'Intermediate',
        estimatedTime: '3 Weeks',
        shortDescription: '7-Layer OSI model, IPv4/IPv6, CIDR, Subnet Masks, Public vs Private IP, Gateway & Loopback.',
        fullDescription: 'Master the 7 layers of the OSI model and packet encapsulation. Calculate subnets, CIDR notation, default gateways, and local loopback interfaces.',
        skills: ['OSI 7-Layer Model & Encapsulation', 'IPv4 & IPv6 Addressing', 'CIDR & Subnet Masking', 'Public vs Private Ranges', 'Localhost & Loopback Mechanics'],
        prerequisites: 'Basic Computer Networking',
        certifications: 'CompTIA Network+, Cisco CCNA',
        careerRoles: 'Network Administrator, Systems Engineer',
        salaryInsight: '$75,000 - $95,000 / year'
      },
      {
        id: 'network-services-topologies',
        type: 'fundamental',
        title: 'Network Services & Topologies',
        difficulty: 'Intermediate',
        estimatedTime: '2 - 3 Weeks',
        shortDescription: 'DHCP, DNS, NTP, IPAM, Star/Ring/Mesh/Bus topologies, Routers, Switches, VPNs, MAN/LAN/WAN.',
        fullDescription: 'Understand structural network layouts (Star, Mesh, Bus) and core services providing automated IP configuration (DHCP), domain resolution (DNS), and time synchronization (NTP).',
        skills: ['DHCP & DNS Resolution', 'NTP & IPAM Services', 'Star, Mesh, Bus Topologies', 'Routers, Switches & VLANs', 'VPN Tunnels & WAN Connections'],
        prerequisites: 'OSI Model & IP Subnetting',
        certifications: 'CCNA',
        careerRoles: 'Network Engineer, Infrastructure Specialist',
        salaryInsight: '$80,000 - $100,000 / year'
      },
      {
        id: 'virtualization-tech',
        type: 'fundamental',
        title: 'Virtualization & Hypervisors',
        difficulty: 'Intermediate',
        estimatedTime: '2 Weeks',
        shortDescription: 'VMWare, VirtualBox, ESXi, Proxmox, Type-1 & Type-2 Hypervisors, Guest vs Host OS.',
        fullDescription: 'Learn virtual machine provisioning, hypervisor abstractions, hardware passthrough, and sandbox creation on VMWare, Proxmox, and ESXi environments.',
        skills: ['Type-1 Hypervisors (ESXi, Proxmox)', 'Type-2 Hypervisors (VirtualBox, VMWare Workstation)', 'Guest OS vs Host OS Isolation', 'Virtual Switch & NAT Networking', 'VM Snapshotting & Storage'],
        prerequisites: 'Linux & Windows Admin',
        certifications: 'VMware VCP, Proxmox Certified',
        careerRoles: 'Virtualization Admin, Cloud Operations',
        salaryInsight: '$85,000 - $105,000 / year'
      },
      {
        id: 'troubleshooting-auth',
        type: 'fundamental',
        title: 'Network Diagnostic Tools & Auth Methodologies',
        difficulty: 'Intermediate',
        estimatedTime: '3 Weeks',
        shortDescription: 'nslookup, iptables, ipconfig, netstat, ping, dig, arp, nmap, route, tcpdump, Kerberos, LDAP, SSO, RADIUS.',
        fullDescription: 'Master CLI utilities for network diagnostics and traffic analysis alongside enterprise authentication protocols like Kerberos, Active Directory LDAP, SSO, and RADIUS.',
        skills: ['Packet Captures (tcpdump, Wireshark)', 'Port Scanning & Routes (nmap, route)', 'DNS Diagnostics (nslookup, dig)', 'Kerberos & LDAP Authentication', 'SSO & RADIUS Federation'],
        prerequisites: 'OSI Model & Network Services',
        certifications: 'CompTIA Security+, Network+',
        careerRoles: 'Network Security Analyst, Identity Engineer',
        salaryInsight: '$85,000 - $110,000 / year'
      }
    ]
  },
  {
    id: 'phase-3',
    title: 'Phase 3: Core Security Concepts & Defense Frameworks',
    subtitle: 'Security Layer',
    description: 'Master the CIA Triad, Defense in Depth, Zero Trust, Incident Response, Cryptography, and Security Frameworks.',
    nodes: [
      {
        id: 'cia-defense-indepth',
        type: 'defensive',
        title: 'Core Concepts & Defense in Depth',
        difficulty: 'Intermediate',
        estimatedTime: '3 Weeks',
        shortDescription: 'CIA Triad, Defense in Depth, Zero Trust, Cyber Kill Chain, MFA, IDS/IPS, Honeypots, OSINT.',
        fullDescription: 'Study core security architecture models: Confidentiality/Integrity/Availability (CIA Triad), layered security controls, Zero Trust micro-segmentation, and intrusion detection systems.',
        skills: ['CIA Triad & Non-repudiation', 'Defense in Depth Controls', 'Zero Trust Architecture', 'IDS/IPS Configuration', 'OSINT & Threat Intel Gathering'],
        prerequisites: 'Networking Knowledge',
        certifications: 'CompTIA Security+, CySA+',
        careerRoles: 'Security Engineer, Risk Analyst',
        salaryInsight: '$90,000 - $115,000 / year'
      },
      {
        id: 'cryptography-pki',
        type: 'defensive',
        title: 'Cryptography & PKI',
        difficulty: 'Intermediate',
        estimatedTime: '3 Weeks',
        shortDescription: 'Salting, Hashing, Key Exchange, Public vs Private Keys, PKI, Certificate Authorities, Obfuscation.',
        fullDescription: 'Understand symmetric and asymmetric encryption (AES, RSA, ECC), cryptographic hashing algorithms (SHA-256, bcrypt salting), Diffie-Hellman key exchange, and Public Key Infrastructure.',
        skills: ['Symmetric vs Asymmetric Encryption', 'Hashing & Salting Mechanics', 'PKI & Certificate Authorities', 'Diffie-Hellman Key Exchange', 'Code Obfuscation Techniques'],
        prerequisites: 'Math & IT Foundations',
        certifications: 'CompTIA Security+',
        careerRoles: 'Cryptographer, Security Architect',
        salaryInsight: '$95,000 - $125,000 / year'
      },
      {
        id: 'frameworks-standards',
        type: 'defensive',
        title: 'Security Frameworks & Standards',
        difficulty: 'Intermediate',
        estimatedTime: '2 - 3 Weeks',
        shortDescription: 'MITRE ATT&CK, Cyber Kill Chain, Diamond Model, ISO 27001, NIST RMF, CIS Controls.',
        fullDescription: 'Align security operations with industry frameworks: MITRE ATT&CK matrix for adversary tactics, NIST Risk Management Framework (RMF), and ISO 27001 compliance standards.',
        skills: ['MITRE ATT&CK Mapping', 'NIST Cybersecurity Framework (CSF)', 'ISO/IEC 27001 Controls', 'CIS Critical Security Controls', 'Diamond Model of Intrusion'],
        prerequisites: 'Security Fundamentals',
        certifications: 'CISA, CISM',
        careerRoles: 'Compliance Officer, Security Auditor',
        salaryInsight: '$100,000 - $130,000 / year'
      },
      {
        id: 'siem-incident-response',
        type: 'defensive',
        title: 'SIEM, Log Sources & Incident Response',
        difficulty: 'Intermediate',
        estimatedTime: '4 Weeks',
        shortDescription: 'SIEM/SOAR (Splunk), Event logs, syslogs, Netflow, Incident Response Lifecycle (Preparation -> Lessons Learned).',
        fullDescription: 'Analyze security event logs across Windows Sysmon, Linux Syslog, and NetFlow using SIEM/SOAR platforms. Execute the 6 phases of Incident Response.',
        skills: ['SIEM & SOAR Orchestration', 'Event Logs & Syslog Parsing', 'NetFlow & Packet Capture Logs', '6 Incident Response Stages', 'Threat Classification & APT Triage'],
        prerequisites: 'Troubleshooting Tools',
        certifications: 'CompTIA CySA+, Blue Team Level 1',
        careerRoles: 'SOC Analyst L2, Incident Responder',
        salaryInsight: '$90,000 - $120,000 / year'
      }
    ]
  },
  {
    id: 'phase-4',
    title: 'Phase 4: Offensive Security & Exploitation (Red Team)',
    subtitle: 'Offensive Layer',
    description: 'Master penetration testing rules, web application hacking, privilege escalation, Active Directory attacks, and red team certs.',
    nodes: [
      {
        id: 'web-owasp-attacks',
        type: 'offensive',
        title: 'Web Application Attacks & OWASP',
        difficulty: 'Advanced',
        estimatedTime: '4 - 5 Weeks',
        shortDescription: 'SQL Injection, XSS, CSRF, Directory Traversal, Replay Attacks, Burp Suite Pro.',
        fullDescription: 'Exploit critical web vulnerabilities listed in the OWASP Top 10. Intercept and tamper with requests using Burp Suite, perform blind/error-based SQL injection, and exploit stored/reflected XSS.',
        skills: ['SQL Injection (SQLi)', 'Cross-Site Scripting (XSS)', 'Cross-Site Request Forgery (CSRF)', 'Directory Traversal & LFI/RFI', 'Burp Suite Pro Exploitation'],
        prerequisites: 'Web Architecture',
        certifications: 'eJPT, GWAPT, BSCP',
        careerRoles: 'Web Application Penetration Tester',
        salaryInsight: '$95,000 - $130,000 / year'
      },
      {
        id: 'privesc-ad-hacking',
        type: 'offensive',
        title: 'Privilege Escalation & Active Directory',
        difficulty: 'Advanced',
        estimatedTime: '5 - 6 Weeks',
        shortDescription: 'Linux SUID, Windows Token Impersonation, Kerberoasting, BloodHound, Pass-the-Hash.',
        fullDescription: 'Gain root or NT AUTHORITY\\SYSTEM access on compromised hosts and perform Active Directory domain takeovers using Kerberoasting, AS-REP Roasting, and BloodHound graphs.',
        skills: ['SUID & Capabilities Exploitation', 'Windows Token & Service Hijacking', 'Kerberoasting & AS-REP Roasting', 'BloodHound LDAP Mapping', 'Pass-the-Hash & DCSync'],
        prerequisites: 'Linux CLI, Windows Admin',
        certifications: 'OSCP, CRTO, GPEN',
        careerRoles: 'Red Team Operator, Senior Pentester',
        salaryInsight: '$120,000 - $160,000 / year'
      },
      {
        id: 'attack-types-social-engineering',
        type: 'offensive',
        title: 'Social Engineering & Attack Vectors',
        difficulty: 'Intermediate',
        estimatedTime: '3 Weeks',
        shortDescription: 'Phishing, Vishing, Smishing, Tailgating, DoS/DDoS, MITM, DNS Poisoning, Evil Twin, Buffer Overflow.',
        fullDescription: 'Understand human and protocol attack vectors: Phishing campaigns, Vishing, Man-in-the-Middle (MITM)ARP poisoning, Rogue Access Points, and low-level memory buffer overflows.',
        skills: ['Phishing & Social Engineering', 'Man-In-The-Middle (MITM) Spoofing', 'Evil Twin & Rogue Access Points', 'DNS Poisoning & Deauth Attacks', 'Memory Leak & Buffer Overflow'],
        prerequisites: 'Security Concepts',
        certifications: 'CEH, CompTIA PenTest+',
        careerRoles: 'Ethical Hacker, Security Consultant',
        salaryInsight: '$90,000 - $125,000 / year'
      },
      {
        id: 'advanced-offensive-certs',
        type: 'certification',
        title: 'Advanced Red Team Certifications',
        difficulty: 'Advanced',
        estimatedTime: '8 - 12 Weeks',
        shortDescription: 'CEH, GPEN, GWAPT, GIAC, OSCP, CREST.',
        fullDescription: 'Validate elite hands-on offensive capabilities through 24-hour practical labs and challenge networks required by elite penetration testing consultancies worldwide.',
        skills: ['Certified Ethical Hacker (CEH)', 'GIAC Penetration Tester (GPEN)', 'Offensive Security Certified Professional (OSCP)', 'CREST Registered Penetration Tester', 'GIAC Web Application Pentester (GWAPT)'],
        prerequisites: 'eJPT, OWASP, AD Hacking',
        certifications: 'CEH, GPEN, GWAPT, OSCP, CREST',
        careerRoles: 'Lead Red Team Specialist, Offensive Security Principal',
        salaryInsight: '$130,000 - $175,000 / year'
      }
    ]
  },
  {
    id: 'phase-5',
    title: 'Phase 5: Defensive Operations & Forensics (Blue Team)',
    subtitle: 'Defensive Layer',
    description: 'Master incident response tools, threat hunting, digital forensics, malware analysis, OS hardening, and blue team certs.',
    nodes: [
      {
        id: 'ir-discovery-tools',
        type: 'defensive',
        title: 'Incident Response & Discovery Tools',
        difficulty: 'Intermediate',
        estimatedTime: '4 Weeks',
        shortDescription: 'nmap, wireshark, winhex, memdump, FTK Imager, autopsy, tail, grep, cat, dd, hping.',
        fullDescription: 'Master forensic data extraction and discovery tools for live memory analysis, disk imaging with FTK Imager, network packet dissection in Wireshark, and log filtering.',
        skills: ['FTK Imager Disk Acquisition', 'Autopsy Digital Forensics Suite', 'RAM Memory Analysis (memdump, Volatility)', 'Wireshark & Hex Dissection (winhex)', 'Linux Forensic Commands (grep, tail, dd)'],
        prerequisites: 'SIEM & Troubleshooting Tools',
        certifications: 'BTL1, GCFA',
        careerRoles: 'Forensic Investigator, Incident Response Specialist',
        salaryInsight: '$100,000 - $135,000 / year'
      },
      {
        id: 'threat-analysis-tools',
        type: 'defensive',
        title: 'Threat Intel & Sandbox Analysis',
        difficulty: 'Intermediate',
        estimatedTime: '3 Weeks',
        shortDescription: 'VirusTotal, Joe Sandbox, any.run, urlvoid, urlscan, WHOIS, Threat Classification.',
        fullDescription: 'Analyze suspicious files, URLs, and domains using cloud sandbox environments (Any.run, Joe Sandbox), WHOIS records, and reputation APIs to classify APT threats.',
        skills: ['VirusTotal Malware Scoring', 'Interactive Sandboxing (Any.run)', 'Joe Sandbox Behavioral Analysis', 'Domain & IP Reputation Lookup', 'Threat Intelligence Feeds'],
        prerequisites: 'Security Concepts',
        certifications: 'CompTIA CySA+',
        careerRoles: 'Threat Intelligence Analyst, Malware Researcher',
        salaryInsight: '$95,000 - $130,000 / year'
      },
      {
        id: 'hardening-secure-protocols',
        type: 'defensive',
        title: 'OS Hardening & Secure Protocols',
        difficulty: 'Intermediate',
        estimatedTime: '3 Weeks',
        shortDescription: 'MAC/NAC, Group Policy, ACLs, FTP vs SFTP, SSL vs TLS, DNSSEC, LDAPS, EDR, DLP, Firewalls.',
        fullDescription: 'Implement host and network hardening: Group Policy Objects (GPOs), Access Control Lists (ACLs), Endpoint Detection and Response (EDR), and migrate unsecure protocols to encrypted equivalents.',
        skills: ['Group Policy & Registry Hardening', 'EDR & DLP Deployment', 'Next-Gen Firewall & HIPS Rules', 'Secure Protocol Migration (SFTP, TLS, LDAPS)', 'MAC & NAC Access Control'],
        prerequisites: 'Networking Knowledge',
        certifications: 'CompTIA Security+, GSEC',
        careerRoles: 'Security Administrator, Systems Hardening Specialist',
        salaryInsight: '$90,000 - $120,000 / year'
      },
      {
        id: 'defensive-certs',
        type: 'certification',
        title: 'Advanced Blue Team Certifications',
        difficulty: 'Advanced',
        estimatedTime: '6 - 10 Weeks',
        shortDescription: 'CompTIA CySA+, GSEC, BTL1, BTL2, GIAC Certified Forensic Analyst (GCFA).',
        fullDescription: 'Validate advanced defensive expertise in threat hunting, SOC operations, digital forensics, and enterprise incident response.',
        skills: ['CompTIA Cybersecurity Analyst (CySA+)', 'GIAC Security Essentials (GSEC)', 'Blue Team Level 1 & 2 (BTL1/BTL2)', 'GIAC Certified Forensic Analyst (GCFA)'],
        prerequisites: 'SIEM, IR Tools, Hardening',
        certifications: 'CySA+, GSEC, BTL1, BTL2, GCFA',
        careerRoles: 'Senior SOC Lead, Incident Response Manager',
        salaryInsight: '$120,000 - $160,000 / year'
      }
    ]
  },
  {
    id: 'phase-6',
    title: 'Phase 6: Cloud Security & Programming Mastery',
    subtitle: 'Cloud & Code Layer',
    description: 'Master cloud security architecture (AWS/Azure/GCP), serverless, IaC, and security scripting in Python, Go, Bash, PowerShell.',
    nodes: [
      {
        id: 'cloud-models-services',
        type: 'cloud',
        title: 'Cloud Models & Infrastructure Security',
        difficulty: 'Advanced',
        estimatedTime: '4 - 5 Weeks',
        shortDescription: 'IaaS, PaaS, SaaS, Public/Private/Hybrid, AWS, GCP, Azure, S3, Infrastructure as Code, Serverless.',
        fullDescription: 'Understand cloud security architecture across AWS, Azure, and GCP. Audit IAM policies, secure S3 cloud storage buckets, configure Infrastructure as Code (Terraform), and protect serverless functions.',
        skills: ['AWS, Azure & GCP Security Controls', 'Cloud Service Models (IaaS, PaaS, SaaS)', 'IAM Policy Auditing & Hardening', 'Infrastructure as Code (IaC) Scanning', 'S3 & Cloud Storage Encryption'],
        prerequisites: 'Networking & Virtualization',
        certifications: 'AWS Security Specialty, CCSP',
        careerRoles: 'Cloud Security Engineer, DevSecOps Engineer',
        salaryInsight: '$130,000 - $175,000 / year'
      },
      {
        id: 'programming-skills',
        type: 'cloud',
        title: 'Security Programming & Scripting',
        difficulty: 'Intermediate',
        estimatedTime: '4 - 6 Weeks',
        shortDescription: 'Python, Go, JavaScript, C++, Bash, PowerShell.',
        fullDescription: 'Develop security automation scripts, custom exploit modules, and log parsing tools using Python, Go, Bash, and PowerShell.',
        skills: ['Python Security Scripting & Scapy', 'Go Network Tools & Concurrency', 'Bash Shell Automation', 'PowerShell Administration & Cmdlets', 'JavaScript & C++ Basics'],
        prerequisites: 'Linux & Windows CLI',
        certifications: 'Python/Go Developer Certs',
        careerRoles: 'Security Tooling Engineer, DevSecOps Developer',
        salaryInsight: '$110,000 - $150,000 / year'
      }
    ]
  },
  {
    id: 'phase-7',
    title: 'Phase 7: Resources, Compliance & Executive Leadership',
    subtitle: 'Mastery & Leadership Layer',
    description: 'Master GTFOBins, WADComs, executive governance, stakeholder communication, and apex certifications (CISSP/CISM).',
    nodes: [
      {
        id: 'security-resources',
        type: 'fundamental',
        title: 'Living Off the Land & Quick References',
        difficulty: 'Intermediate',
        estimatedTime: 'Continuous',
        shortDescription: 'GTFOBins, WADComs, LOLBAS, roadmap.sh.',
        fullDescription: 'Utilize Living Off The Land binaries (LOLBAS), GTFOBins for Linux privilege escalation, WADComs for Active Directory commands, and community roadmap references.',
        skills: ['GTFOBins Linux Binary Bypasses', 'WADComs Active Directory Commands', 'LOLBAS Windows Utility Exploitation', 'roadmap.sh Community Learning Paths'],
        prerequisites: 'Linux & Windows Admin',
        certifications: 'Practical Mastery',
        careerRoles: 'Senior Security Analyst',
        salaryInsight: 'Skill Reference'
      },
      {
        id: 'apex-executive-certs',
        type: 'certification',
        title: 'Executive Leadership & Apex Certifications',
        difficulty: 'Expert',
        estimatedTime: '10 - 14 Weeks',
        shortDescription: 'CISSP, CISA, CISM, Stakeholder Communication (HR, Legal, Compliance, Management).',
        fullDescription: 'Prepare for enterprise leadership roles (CISO, Director of Security). Master security governance, risk assessment, legal regulatory compliance, and obtain the CISSP/CISM credentials.',
        skills: ['CISSP 8 Security Domains', 'CISM Security Governance & Strategy', 'CISA Information Systems Auditing', 'Regulatory Compliance & Legal', 'Executive & Stakeholder Management'],
        prerequisites: '5+ Years Industry Experience',
        certifications: 'CISSP, CISA, CISM',
        careerRoles: 'Chief Information Security Officer (CISO), VP of Cyber Security',
        salaryInsight: '$160,000 - $250,000+ / year'
      }
    ]
  }
]

const filteredRoadmapPhases = computed(() => {
  return roadmapPhasesData.map(phase => {
    const nodes = phase.nodes.filter(node => {
      const matchesCategory = activeRoadmapCat.value === 'all' || node.type === activeRoadmapCat.value
      const q = roadmapSearch.value.toLowerCase().trim()
      if (!q) return matchesCategory

      const matchesSearch = 
        node.title.toLowerCase().includes(q) ||
        node.shortDescription.toLowerCase().includes(q) ||
        node.skills.some(s => s.toLowerCase().includes(q)) ||
        node.certifications.toLowerCase().includes(q)

      return matchesCategory && matchesSearch
    })

    return { ...phase, nodes }
  }).filter(phase => phase.nodes.length > 0)
})

const getRoadmapBorderClass = (type) => {
  switch (type) {
    case 'offensive':
      return 'hover:border-rose-500/60 hover:shadow-[0_0_15px_rgba(244,63,94,0.15)]'
    case 'defensive':
      return 'hover:border-[#00f0ff]/60 hover:shadow-[0_0_15px_rgba(0,240,255,0.15)]'
    case 'certification':
      return 'hover:border-amber-400/60 hover:shadow-[0_0_15px_rgba(251,191,36,0.15)]'
    case 'cloud':
      return 'hover:border-purple-400/60 hover:shadow-[0_0_15px_rgba(192,132,252,0.15)]'
    default:
      return 'hover:border-[#9fef00]/60 hover:shadow-[0_0_15px_rgba(159,239,0,0.15)]'
  }
}

const getRoadmapTypeBadgeClass = (type) => {
  switch (type) {
    case 'offensive':
      return 'bg-rose-500/10 text-rose-400 border-rose-500/30'
    case 'defensive':
      return 'bg-[#00f0ff]/10 text-[#00f0ff] border-[#00f0ff]/30'
    case 'certification':
      return 'bg-amber-400/10 text-amber-400 border-amber-400/30'
    case 'cloud':
      return 'bg-purple-400/10 text-purple-400 border-purple-400/30'
    default:
      return 'bg-[#9fef00]/10 text-[#9fef00] border-[#9fef00]/30'
  }
}

const getRoadmapDifficultyBadgeClass = (difficulty) => {
  switch (difficulty) {
    case 'Beginner':
      return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
    case 'Intermediate':
      return 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
    case 'Advanced':
      return 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
    case 'Expert':
      return 'bg-purple-500/10 text-purple-400 border border-purple-500/30'
    default:
      return 'bg-slate-800 text-slate-400'
  }
}

const tabs = [
  { id: 'paths', label: 'Learning Paths' },
  { id: 'roadmap', label: 'Roadmap' },
  { id: 'modules', label: 'Modules & Notes' },
  { id: 'live', label: 'Live Classes' }
]

const liveClasses = ref([])
const showLiveModal = ref(false)
const isEditingLive = ref(false)
const editingLiveId = ref(null)
const newLive = ref({ title: '', meeting_link: '', thumbnail_url: '', scheduled_at: '', duration_minutes: 60, description: '' })

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
    formData.append('type', 'course_cover')

    const res = await axios.post('/api/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      withCredentials: true
    })

    if (res.data && res.data.file_url) {
      pathForm.value.cover_image = res.data.file_url
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
    } else {
      await axios.post('/api/academy/courses', pathForm.value, { withCredentials: true })
    }
    showPathModal.value = false
    await clubStore.fetchCourses()
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

const fetchLiveClasses = async () => {
  try {
    const res = await axios.get('/api/academy/live-classes', { withCredentials: true })
    liveClasses.value = res.data.live_classes || []
  } catch (err) {
    console.error('Failed to fetch live classes', err)
  }
}

const openEditLiveModal = (lc) => {
  isEditingLive.value = true
  editingLiveId.value = lc.id
  newLive.value = {
    title: lc.title,
    meeting_link: lc.meeting_link,
    thumbnail_url: lc.thumbnail_url || '',
    scheduled_at: lc.scheduled_at ? lc.scheduled_at.slice(0, 16) : '',
    duration_minutes: lc.duration_minutes || 60,
    description: lc.description || ''
  }
  showLiveModal.value = true
}

const handleScheduleLive = async () => {
  if (!newLive.value.title.trim() || !newLive.value.meeting_link.trim()) return
  try {
    if (isEditingLive.value && editingLiveId.value) {
      await axios.put(`/api/academy/live-classes/${editingLiveId.value}`, newLive.value, { withCredentials: true })
    } else {
      await axios.post('/api/academy/live-classes', newLive.value, { withCredentials: true })
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
})
</script>
