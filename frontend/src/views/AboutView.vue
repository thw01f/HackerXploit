<template>
  <div class="max-w-5xl mx-auto space-y-8 pb-12">

    <!-- Page Title Header -->
    <div class="glass-panel p-8 relative overflow-hidden bg-gradient-to-r from-[#0d1525] via-[#111927] to-[#090d16] border-l-4 border-l-[#9fef00]">
      <div class="relative z-10">
        <span class="px-3 py-1 rounded bg-[#9fef00]/10 border border-[#9fef00]/30 text-[#9fef00] font-mono text-xs font-bold uppercase tracking-wider">
          ABOUT THE PLATFORM
        </span>
        <h1 class="text-3xl font-extrabold mt-2 font-mono">
          <span class="text-white">Hacker</span><span class="text-red-500">Xploit</span>
        </h1>
        <p class="text-slate-300 text-sm mt-1.5 max-w-2xl leading-relaxed">
          The collegiate cybersecurity club platform - real-world CTF arenas, hands-on academy modules, and verified member credentials, all under one unified sign-on.
        </p>
      </div>
    </div>

    <!-- Core Features -->
    <div class="glass-panel p-6 space-y-6">
      <h2 class="text-lg font-bold text-white font-mono border-b border-slate-800 pb-3">What's on this platform</h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="border-l-4 border-l-[#9fef00] pl-4 space-y-1">
          <h3 class="text-sm font-bold text-white font-mono">Academy</h3>
          <p class="text-xs text-slate-400 leading-relaxed">Hands-on courses across Web Exploitation, Reverse Engineering, Forensics, Binary Exploitation, and Cloud Security, with progress tracking and completion certificates.</p>
        </div>

        <div class="border-l-4 border-l-[#00f0ff] pl-4 space-y-1">
          <h3 class="text-sm font-bold text-white font-mono">CTF Arena</h3>
          <p class="text-xs text-slate-400 leading-relaxed">Compete on the official CTFd infrastructure at arena.hackerxploit.org using unified OAuth2 single sign-on - no separate account needed.</p>
        </div>

        <div class="border-l-4 border-l-amber-400 pl-4 space-y-1">
          <h3 class="text-sm font-bold text-white font-mono">Competitions & Club Events</h3>
          <p class="text-xs text-slate-400 leading-relaxed">Apply to competitions and hackathons, submit post-event completion reports, and check in to club events via QR badge scan.</p>
        </div>

        <div class="border-l-4 border-l-purple-400 pl-4 space-y-1">
          <h3 class="text-sm font-bold text-white font-mono">Opportunities</h3>
          <p class="text-xs text-slate-400 leading-relaxed">A skill-matched job and internship board surfacing roles relevant to your listed skills.</p>
        </div>

        <div class="border-l-4 border-l-rose-400 pl-4 space-y-1">
          <h3 class="text-sm font-bold text-white font-mono">Digital ID Card</h3>
          <p class="text-xs text-slate-400 leading-relaxed">A virtual member badge with a QR verification pass, live event participation status, and a permanent Badge ID.</p>
        </div>

        <div class="border-l-4 border-l-slate-400 pl-4 space-y-1">
          <h3 class="text-sm font-bold text-white font-mono">Chat & Inbox</h3>
          <p class="text-xs text-slate-400 leading-relaxed">Real-time general chat with the club, plus a scoped broadcast inbox for official announcements and updates.</p>
        </div>
      </div>
    </div>

    <!-- Identity & Trust -->
    <div class="glass-panel p-6 space-y-3">
      <h2 class="text-lg font-bold text-white font-mono border-b border-slate-800 pb-3">Identity & membership</h2>
      <p class="text-xs text-slate-400 leading-relaxed">
        Membership is verified through SRM email address and Registration Number at signup, with new registrations reviewed by teachers or admins before approval.
        Every approved member gets a permanent, unique Badge ID displayed on their Digital ID Card and used across competition records and attendance exports.
      </p>
    </div>

    <!-- Footer note -->
    <div class="text-center text-xs text-slate-500 font-mono pt-2">
      Have a question we didn't cover? Reach out via
      <router-link to="/contact" class="text-[#00f0ff] hover:underline">Contact Support</router-link>.
    </div>

  </div>
</template>
