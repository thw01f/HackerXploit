<template>
  <div class="min-h-screen flex flex-col justify-between">
    <Navbar />

    <!-- Hero Section -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 flex-1 flex flex-col justify-center">
      <div class="text-center space-y-6">
        <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-500/30 text-cyan-300 text-xs font-mono">
          <span class="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
          <span>FALL 2026 RECRUITMENT OPEN</span>
        </div>

        <h1 class="text-5xl md:text-7xl font-extrabold text-white tracking-tight leading-tight">
          Master Cybersecurity.<br />
          <span class="bg-gradient-to-r from-cyan-400 via-teal-300 to-purple-500 bg-clip-text text-transparent">
            Compete. Hack. Lead.
          </span>
        </h1>

        <p class="max-w-2xl mx-auto text-lg text-slate-300">
          Welcome to <strong class="text-white">HackerXploit</strong> — the official collegiate cybersecurity organization. Engage in hands-on CTF competitions, enterprise learning tracks, and defense research.
        </p>

        <div class="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <router-link to="/register" class="btn-neon-cyan text-base py-3 px-8 w-full sm:w-auto">
            Apply For Membership
          </router-link>
          <a href="http://ctf.hackerxploit.org" target="_blank" class="btn-neon-violet text-base py-3 px-8 w-full sm:w-auto">
            Launch CTF Arena
          </a>
        </div>
      </div>

      <!-- Feature Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mt-24">
        <div class="glass-panel p-8 hover:border-cyan-500/40 transition-all">
          <div class="w-12 h-12 rounded-lg bg-cyan-950 border border-cyan-500/40 flex items-center justify-center text-cyan-400 font-bold mb-6">
            01
          </div>
          <h3 class="text-xl font-bold text-white mb-2">HackerXploit Academy</h3>
          <p class="text-slate-400 text-sm">
            Curated hands-on courses covering Web Exploitation, Reverse Engineering, Cryptography, Binary Exploitation, and Cloud Security.
          </p>
        </div>

        <div class="glass-panel p-8 hover:border-purple-500/40 transition-all">
          <div class="w-12 h-12 rounded-lg bg-purple-950 border border-purple-500/40 flex items-center justify-center text-purple-400 font-bold mb-6">
            02
          </div>
          <h3 class="text-xl font-bold text-white mb-2">Integrated CTF Platform</h3>
          <p class="text-slate-400 text-sm">
            Compete on our custom CTFd instance with unified single sign-on authentication across all club domains.
          </p>
        </div>

        <div class="glass-panel p-8 hover:border-teal-500/40 transition-all">
          <div class="w-12 h-12 rounded-lg bg-teal-950 border border-teal-500/40 flex items-center justify-center text-teal-400 font-bold mb-6">
            03
          </div>
          <h3 class="text-xl font-bold text-white mb-2">Career & Defense Ops</h3>
          <p class="text-slate-400 text-sm">
            Exclusive access to cybersecurity internships, collegiate team competitions, research opportunities, and digital member credentials.
          </p>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
</script>
