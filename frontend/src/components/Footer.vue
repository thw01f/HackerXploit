<template>
  <footer class="border-t border-[#1f293d] bg-[#0b0e14] mt-16 py-8 text-slate-400 text-xs font-mono">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-4">
      <!-- min-w-0: without it this row's default min-width (auto, not 0)
           refuses to let the copyright text shrink/wrap below its own
           content width, so on a narrow phone it crowded/overflowed
           against the logo instead of wrapping onto a second line. -->
      <div class="flex items-center space-x-3 min-w-0 text-center md:text-left">
        <img src="/logo.png" class="w-6 h-6 object-contain flex-shrink-0" alt="HackerXploit Logo" />

        <div class="min-w-0">
          <span class="font-bold text-white">HackerXploit Cyber Platform</span> &copy; 2026. Official Collegiate Cybersecurity Org.
        </div>
      </div>
      <div class="flex flex-wrap items-center justify-center gap-6 text-[11px]">
        <a href="https://club.hackerxploit.org" target="_blank" class="text-slate-400 hover:text-[#9fef00] transition-colors">club.hackerxploit.org</a>
        <a href="https://arena.hackerxploit.org" target="_blank" class="text-slate-400 hover:text-[#00f0ff] transition-colors">arena.hackerxploit.org</a>
      </div>
    </div>
  </footer>
</template>
