<template>
  <div id="app-root" class="min-h-screen bg-cyber-dark text-slate-100 font-sans">
    <router-view />
    <ChatWindow v-if="authStore.isAuthenticated" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import ChatWindow from './components/ChatWindow.vue'

const authStore = useAuthStore()

onMounted(() => {
  if (authStore.token) {
    authStore.fetchMe()
  }
})
</script>
