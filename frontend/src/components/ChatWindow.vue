<template>
  <div ref="chatContainerRef" class="fixed bottom-6 right-6 z-50">
    <!-- Toggle Button -->
    <button 
      @click.stop="chatStore.isOpen = !chatStore.isOpen"
      class="btn-neon-cyan p-3.5 rounded-full shadow-2xl flex items-center space-x-2 border border-cyan-400/50"
    >
      <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
      <span class="font-mono text-xs font-bold uppercase hidden sm:inline">Live Chat</span>
    </button>

    <!-- Chat Modal Window -->
    <div v-if="chatStore.isOpen" class="fixed bottom-20 right-6 w-96 h-[500px] glass-panel p-4 flex flex-col justify-between border border-cyan-500/30 shadow-2xl rounded-2xl">
      <!-- Header & Channel Selector -->
      <div class="border-b border-slate-800 pb-3 flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <span class="font-bold text-sm text-white font-mono"># {{ chatStore.activeChannel }}</span>
        </div>
        <span class="text-[11px] font-mono text-cyan-400">{{ chatStore.onlineCount }} online</span>
      </div>

      <!-- Channel Tabs -->
      <div class="flex space-x-1 py-2 border-b border-slate-800 text-xs">
        <button 
          v-for="ch in ['general', 'ctf_team', 'announcements']" 
          :key="ch"
          @click="chatStore.joinChannel(ch)"
          class="px-2.5 py-1 rounded font-mono text-[11px] transition-colors"
          :class="chatStore.activeChannel === ch ? 'bg-cyan-950 text-cyan-300 font-bold border border-cyan-500/30' : 'text-slate-400 hover:text-white'"
        >
          #{{ ch }}
        </button>
      </div>

      <!-- Messages Feed -->
      <div class="flex-1 overflow-y-auto space-y-3 py-3 pr-1">
        <div v-for="msg in chatStore.messages" :key="msg.id" class="flex items-start space-x-2 text-xs">
          <img :src="msg.sender_avatar || defaultAvatarSvg" @error="(e) => e.target.src = defaultAvatarSvg" class="w-7 h-7 rounded-full object-cover border border-slate-700 mt-0.5" />
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-200">{{ msg.sender_username }}</span>
              <div class="flex items-center space-x-2">
                <span class="text-[9px] text-slate-500 font-mono">{{ new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', hour12: prefs.is12h.value}) }}</span>
                <button 
                  v-if="authStore.isTeacher && !msg.is_deleted" 
                  @click="chatStore.softDeleteMessage(msg.id)"
                  class="text-[9px] text-red-400 hover:underline font-mono"
                  title="Soft-delete message"
                >
                  del
                </button>
              </div>
            </div>
            <p :class="msg.is_deleted ? 'text-slate-500 italic' : 'text-slate-300'" class="mt-0.5 break-words">
              {{ msg.content }}
            </p>
          </div>
        </div>
      </div>

      <!-- Input Form -->
      <form @submit.prevent="handleSend" class="pt-2 border-t border-slate-800 flex items-center space-x-2">
        <input 
          v-model="newMessage" 
          type="text" 
          placeholder="Type message..." 
          class="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
        />
        <button type="submit" class="btn-neon-cyan py-1.5 px-3 text-xs">Send</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useChatStore } from '../stores/chat'
import { usePreferences } from '../stores/preferences'

const authStore = useAuthStore()
const chatStore = useChatStore()
const prefs = usePreferences()
const newMessage = ref('')
const chatContainerRef = ref(null)

const defaultAvatarSvg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'><rect width='100' height='100' fill='%230b0e14'/><circle cx='50' cy='38' r='20' fill='%231f293d' stroke='%239fef00' stroke-width='2'/><path d='M20,85 C20,62 35,55 50,55 C65,55 80,62 80,85 Z' fill='%231f293d' stroke='%239fef00' stroke-width='2'/></svg>"

const handleClickOutside = (event) => {
  if (chatStore.isOpen && chatContainerRef.value && !chatContainerRef.value.contains(event.target)) {
    chatStore.isOpen = false
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    chatStore.initSocket()
  }
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const handleSend = () => {
  if (!newMessage.value.trim()) return
  chatStore.sendMessage(newMessage.value)
  newMessage.value = ''
}
</script>
