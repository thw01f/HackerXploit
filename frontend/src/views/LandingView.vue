<template>
  <!-- Authenticated User Intro Page View (Uses AppLayout Sidebar) -->
  <AppLayout v-if="authStore.isAuthenticated">
    <div class="max-w-7xl mx-auto py-6 sm:py-10 flex-1 flex flex-col justify-center w-full space-y-12">
      
      <!-- Top Announcement Tag -->
      <div class="text-center mb-2">
        <div class="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-[#151f30] border border-[#9fef00]/40 text-[#9fef00] text-xs font-mono shadow-lg">
          <span class="w-2 h-2 rounded-full bg-[#9fef00]"></span>
          <span>SYSTEM READY // OFFICIAL CYBERSECURITY PLATFORM</span>
        </div>
      </div>

      <!-- Main Heading & Hero Text -->
      <div class="text-center space-y-6 max-w-4xl mx-auto">
        <h1 class="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight leading-snug font-mono">
          PRACTICE OFFENSIVE SECURITY.<br />
          <span class="text-[#9fef00] underline decoration-[#9fef00]/40 underline-offset-8">
            HACK. COMPETE. WIN.
          </span>
        </h1>

        <p class="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed">
          Welcome to <strong class="text-white font-mono">HackerXploit</strong> — the premier collegiate cybersecurity platform. Real-world CTF arenas, hands-on academy modules, and verified member credentials.
        </p>

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
          <router-link to="/dashboard" class="btn-htb text-xs sm:text-sm py-3 px-8 w-full sm:w-auto font-mono">
            🚀 GO TO DASHBOARD
          </router-link>
          <a href="http://arena.hackerxploit.org" target="_blank" class="btn-ghost text-xs sm:text-sm py-3 px-8 w-full sm:w-auto font-mono text-[#00f0ff] border-[#00f0ff]/30 hover:border-[#00f0ff]">
            ⚡ LAUNCH CTF ARENA &rarr;
          </a>
        </div>
      </div>

      <!-- Interactive Terminal Mockup Box -->
      <div class="max-w-3xl mx-auto w-full glass-panel overflow-hidden border border-[#1f293d] shadow-2xl">
        <div class="bg-[#090d16] px-4 py-2.5 border-b border-[#1f293d] flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="w-3 h-3 rounded-full bg-red-500/80 inline-block"></span>
            <span class="w-3 h-3 rounded-full bg-amber-500/80 inline-block"></span>
            <span class="w-3 h-3 rounded-full bg-emerald-500/80 inline-block"></span>
          </div>
          <span class="text-xs font-mono text-slate-400">hackerxploit-shell ~ v2.4.0</span>
          <span class="text-xs font-mono text-[#9fef00]">STATUS: ONLINE</span>
        </div>
        <div class="p-6 font-mono text-xs sm:text-sm text-slate-300 space-y-2 bg-[#0b0e14]">
          <p><span class="text-[#9fef00]">root@hx-box:~#</span> ./init_platform.sh --domain club.hackerxploit.org</p>
          <p class="text-slate-400">[+] Authenticating OAuth2 identity provider... [OK]</p>
          <p class="text-slate-400">[+] Loading Academy modules: Web Exploitation, Reverse Engineering, Cryptography... [OK]</p>
          <p class="text-slate-400">[+] Synchronizing CTFd Shadow Accounts & Leaderboard Scoreboard... [OK]</p>
          <p class="text-[#00f0ff] font-bold">[SUCCESS] Operator Session Initialized. Welcome back, Agent.</p>
        </div>
      </div>

      <!-- Feature Grid (Symmetric 3 Columns) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <div class="glass-panel p-6 border-l-4 border-l-[#9fef00] hover:translate-y-[-2px] transition-all">
          <div class="w-10 h-10 rounded-lg bg-[#151f30] border border-[#9fef00]/40 flex items-center justify-center text-[#9fef00] font-mono font-bold mb-4">
            01
          </div>
          <h3 class="text-lg font-bold text-white font-mono mb-2">HackerXploit Academy</h3>
          <p class="text-slate-400 text-xs leading-relaxed">
            Medium-style hands-on courses covering Web Exploitation, Reverse Engineering, Forensics, Binary Exploitation, and Cloud Hacking.
          </p>
        </div>

        <div class="glass-panel p-6 border-l-4 border-l-[#00f0ff] hover:translate-y-[-2px] transition-all">
          <div class="w-10 h-10 rounded-lg bg-[#151f30] border border-[#00f0ff]/40 flex items-center justify-center text-[#00f0ff] font-mono font-bold mb-4">
            02
          </div>
          <h3 class="text-lg font-bold text-white font-mono mb-2">Integrated CTF Arena</h3>
          <p class="text-slate-400 text-xs leading-relaxed">
            Compete on our official CTFd infrastructure using unified OAuth2 single sign-on across all subdomains.
          </p>
        </div>

        <div class="glass-panel p-6 border-l-4 border-l-amber-400 hover:translate-y-[-2px] transition-all">
          <div class="w-10 h-10 rounded-lg bg-[#151f30] border border-amber-400/40 flex items-center justify-center text-amber-400 font-mono font-bold mb-4">
            03
          </div>
          <h3 class="text-lg font-bold text-white font-mono mb-2">Career & Defense Ops</h3>
          <p class="text-slate-400 text-xs leading-relaxed">
            Access cybersecurity job/internship boards, skill-matching, official competition wrap-up certificates, and virtual 3D ID cards.
          </p>
        </div>

      </div>

      <Footer />
    </div>
  </AppLayout>

  <!-- Guest / Unauthenticated Landing View -->
  <div v-else class="min-h-screen flex flex-col justify-between bg-[#0b0e14]">
    <Navbar />

    <!-- Hero Section -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-16 flex-1 flex flex-col justify-center w-full">
      
      <!-- Top Announcement Tag -->
      <div class="text-center mb-6 pt-4">
        <div class="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-[#151f30] border border-[#9fef00]/40 text-[#9fef00] text-xs font-mono shadow-lg">
          <span class="w-2 h-2 rounded-full bg-[#9fef00]"></span>
          <span>SYSTEM READY // OFFICIAL CYBERSECURITY PLATFORM</span>
        </div>
      </div>

      <!-- Main Heading & Hero Text -->
      <div class="text-center space-y-6 max-w-4xl mx-auto">
        <h1 class="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight leading-snug font-mono">
          PRACTICE OFFENSIVE SECURITY.<br />
          <span class="text-[#9fef00] underline decoration-[#9fef00]/40 underline-offset-8">
            HACK. COMPETE. WIN.
          </span>
        </h1>

        <p class="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed">
          Welcome to <strong class="text-white font-mono">HackerXploit</strong> — the premier collegiate cybersecurity platform. Real-world CTF arenas, hands-on academy modules, and verified member credentials.
        </p>

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
          <router-link to="/register" class="btn-htb text-xs sm:text-sm py-3 px-8 w-full sm:w-auto font-mono">
            🚀 JOIN THE CLUB
          </router-link>
          <a href="http://arena.hackerxploit.org" target="_blank" class="btn-ghost text-xs sm:text-sm py-3 px-8 w-full sm:w-auto font-mono text-[#00f0ff] border-[#00f0ff]/30 hover:border-[#00f0ff]">
            ⚡ LAUNCH CTF ARENA &rarr;
          </a>
        </div>
      </div>

      <!-- Interactive Terminal Mockup Box -->
      <div class="mt-14 max-w-3xl mx-auto w-full glass-panel overflow-hidden border border-[#1f293d] shadow-2xl">
        <div class="bg-[#090d16] px-4 py-2.5 border-b border-[#1f293d] flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="w-3 h-3 rounded-full bg-red-500/80 inline-block"></span>
            <span class="w-3 h-3 rounded-full bg-amber-500/80 inline-block"></span>
            <span class="w-3 h-3 rounded-full bg-emerald-500/80 inline-block"></span>
          </div>
          <span class="text-xs font-mono text-slate-400">hackerxploit-shell ~ v2.4.0</span>
          <span class="text-xs font-mono text-[#9fef00]">STATUS: ONLINE</span>
        </div>
        <div class="p-6 font-mono text-xs sm:text-sm text-slate-300 space-y-2 bg-[#0b0e14]">
          <p><span class="text-[#9fef00]">root@hx-box:~#</span> ./init_platform.sh --domain club.hackerxploit.org</p>
          <p class="text-slate-400">[+] Authenticating OAuth2 identity provider... [OK]</p>
          <p class="text-slate-400">[+] Loading Academy modules: Web Exploitation, Reverse Engineering, Cryptography... [OK]</p>
          <p class="text-slate-400">[+] Synchronizing CTFd Shadow Accounts & Leaderboard Scoreboard... [OK]</p>
          <p class="text-[#00f0ff] font-bold">[SUCCESS] Operator Session Initialized. Welcome back, Agent.</p>
        </div>
      </div>

      <!-- Feature Grid (Symmetric 3 Columns) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
        
        <div class="glass-panel p-6 border-l-4 border-l-[#9fef00] hover:translate-y-[-2px] transition-all">
          <div class="w-10 h-10 rounded-lg bg-[#151f30] border border-[#9fef00]/40 flex items-center justify-center text-[#9fef00] font-mono font-bold mb-4">
            01
          </div>
          <h3 class="text-lg font-bold text-white font-mono mb-2">HackerXploit Academy</h3>
          <p class="text-slate-400 text-xs leading-relaxed">
            Medium-style hands-on courses covering Web Exploitation, Reverse Engineering, Forensics, Binary Exploitation, and Cloud Hacking.
          </p>
        </div>

        <div class="glass-panel p-6 border-l-4 border-l-[#00f0ff] hover:translate-y-[-2px] transition-all">
          <div class="w-10 h-10 rounded-lg bg-[#151f30] border border-[#00f0ff]/40 flex items-center justify-center text-[#00f0ff] font-mono font-bold mb-4">
            02
          </div>
          <h3 class="text-lg font-bold text-white font-mono mb-2">Integrated CTF Arena</h3>
          <p class="text-slate-400 text-xs leading-relaxed">
            Compete on our official CTFd infrastructure using unified OAuth2 single sign-on across all subdomains.
          </p>
        </div>

        <div class="glass-panel p-6 border-l-4 border-l-amber-400 hover:translate-y-[-2px] transition-all">
          <div class="w-10 h-10 rounded-lg bg-[#151f30] border border-amber-400/40 flex items-center justify-center text-amber-400 font-mono font-bold mb-4">
            03
          </div>
          <h3 class="text-lg font-bold text-white font-mono mb-2">Career & Defense Ops</h3>
          <p class="text-slate-400 text-xs leading-relaxed">
            Access cybersecurity job/internship boards, skill-matching, official competition wrap-up certificates, and virtual 3D ID cards.
          </p>
        </div>

      </div>

    </main>

    <Footer />
  </div>
</template>

<script setup>
import AppLayout from '../components/AppLayout.vue'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
</script>
