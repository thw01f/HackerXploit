<template>
  <div id="app-root" class="min-h-screen bg-[#0b0e14] text-slate-100 font-sans">
    <AppLayout v-if="authStore.isAuthenticated && !isPublicRoute">
      <router-view />
    </AppLayout>
    <router-view v-else />
    <!-- !isPublicRoute matters here the same way it does for AppLayout above:
         public pages (landing, login, /verify/:token, ...) must stay clean
         and stand alone even when the viewer happens to have a valid
         session from browsing elsewhere in the app (e.g. an admin checking
         a member's ID card verification page while still logged in) - the
         chat widget was previously gated on isAuthenticated alone, so it
         showed up over the public verification page for anyone signed in. -->
    <ChatWindow v-if="authStore.isAuthenticated && !isPublicRoute && authStore.publicSettings?.general_chat_enabled !== false" />
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

onMounted(async () => {
  if (!authStore.authChecked) {
    await authStore.fetchMe()
  }
  if (authStore.isAuthenticated) {
    initHeartbeat(authStore)
    // Previously only fetched from Sidebar.vue, which only mounts once
    // AppLayout does (authenticated + non-public routes) - until then
    // publicSettings sat at its hardcoded default (general_chat_enabled:
    // true), so the chat widget's admin-disabled check had nothing real to
    // read yet. Fetching it here too makes the toggle authoritative from
    // the moment a session is confirmed, not just after Sidebar happens to
    // mount.
    authStore.fetchPublicSettings()
  }
})

watch(() => authStore.user, (newUser) => {
  if (newUser) {
    initHeartbeat(authStore)
  }
})
</script>
