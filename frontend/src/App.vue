<template>
  <div id="app-root" class="min-h-screen bg-cyber-dark text-slate-100 font-sans">
    <router-view />
    <ChatWindow v-if="authStore.isAuthenticated" />
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useAuthStore } from './stores/auth'
import ChatWindow from './components/ChatWindow.vue'
import { initHeartbeat } from './services/heartbeat'

const authStore = useAuthStore()

onMounted(() => {
  if (authStore.token) {
    authStore.fetchMe()
    initHeartbeat(authStore)
  }
})

watch(() => authStore.token, (newToken) => {
  if (newToken) {
    initHeartbeat(authStore)
  }
})
</script>

