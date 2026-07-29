<template>
  <div id="app-root" class="min-h-screen bg-[#0b0e14] text-slate-100 font-sans">
    <AppLayout v-if="authStore.isAuthenticated && !isPublicRoute">
      <router-view />
    </AppLayout>
    <router-view v-else />
    <ChatWindow v-if="authStore.isAuthenticated && authStore.publicSettings?.general_chat_enabled !== false" />
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import ChatWindow from './components/ChatWindow.vue'
import AppLayout from './components/AppLayout.vue'
import { initHeartbeat } from './services/heartbeat'

const authStore = useAuthStore()
const route = useRoute()

const PUBLIC_ROUTES = ['landing', 'login', 'register', 'forgot-password', 'reset-password', 'verify-id-card', 'setup-admin']

const isPublicRoute = computed(() => {
  return PUBLIC_ROUTES.includes(route.name) || route.path.startsWith('/verify/')
})

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
