<template>
  <div class="glass-panel p-2 overflow-x-auto border-b border-slate-800 mb-6 rounded-xl bg-[#0c1117]/80 backdrop-blur-md">
    <div class="flex items-center space-x-1.5 min-w-max">
      <router-link 
        to="/admin" 
        exact
        class="admin-nav-tab flex items-center gap-1.5"
        active-class="admin-nav-tab-active"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 100 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
        </svg>
        <span>User Accounts</span>
      </router-link>

      <router-link 
        to="/admin/profile-fields" 
        class="admin-nav-tab flex items-center gap-1.5"
        active-class="admin-nav-tab-active"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        <span>Custom Profile Fields</span>
      </router-link>

      <router-link 
        to="/admin/security" 
        class="admin-nav-tab flex items-center gap-1.5"
        active-class="admin-nav-tab-active"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
        </svg>
        <span>Security & Sessions</span>
      </router-link>

      <router-link 
        to="/admin/admins" 
        class="admin-nav-tab flex items-center gap-1.5"
        active-class="admin-nav-tab-active"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/>
        </svg>
        <span>Manage Admins (Root)</span>
      </router-link>

      <router-link 
        to="/admin/settings" 
        class="admin-nav-tab flex items-center gap-1.5"
        active-class="admin-nav-tab-active"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        <span>Domain & Password Settings</span>
      </router-link>

      <router-link 
        to="/admin/backups" 
        class="admin-nav-tab flex items-center gap-1.5"
        active-class="admin-nav-tab-active"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/>
        </svg>
        <span>Backups</span>
      </router-link>

      <router-link 
        to="/admin/audit-logs" 
        class="admin-nav-tab flex items-center gap-1.5"
        active-class="admin-nav-tab-active"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
        </svg>
        <span>Audit Logs</span>
      </router-link>

      <router-link 
        to="/admin/inbox-logs" 
        class="admin-nav-tab flex items-center gap-1.5"
        active-class="admin-nav-tab-active"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
        </svg>
        <span>Inbox Log</span>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.admin-nav-tab {
  font-family: 'Fira Code', monospace;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  padding: 0.45rem 0.85rem;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  border: 1px solid transparent;
  white-space: nowrap;
}

.admin-nav-tab:hover {
  color: #00f0ff;
  background-color: rgba(0, 240, 255, 0.1);
  border-color: rgba(0, 240, 255, 0.3);
}

.admin-nav-tab-active {
  color: #9fef00 !important;
  background-color: rgba(159, 239, 0, 0.12) !important;
  border-color: rgba(159, 239, 0, 0.4) !important;
  box-shadow: 0 0 8px rgba(159, 239, 0, 0.15);
}
</style>
