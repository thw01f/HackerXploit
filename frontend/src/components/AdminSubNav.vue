<template>
  <div class="glass-panel p-2 overflow-x-auto border-b border-slate-800 mb-6">
    <div class="flex items-center space-x-1 min-w-max">
      <router-link 
        to="/admin" 
        exact
        class="admin-nav-tab"
        active-class="admin-nav-tab-active"
      >
        <span>👥 User Accounts</span>
      </router-link>

      <router-link 
        to="/admin/profile-fields" 
        class="admin-nav-tab"
        active-class="admin-nav-tab-active"
      >
        <span>📋 Custom Profile Fields</span>
      </router-link>

      <router-link 
        to="/admin/security" 
        class="admin-nav-tab"
        active-class="admin-nav-tab-active"
      >
        <span>🛡️ Security & Sessions</span>
      </router-link>

      <router-link 
        to="/admin/admins" 
        class="admin-nav-tab"
        active-class="admin-nav-tab-active"
      >
        <span>👑 Manage Admins (Root)</span>
      </router-link>

      <router-link 
        to="/admin/settings" 
        class="admin-nav-tab"
        active-class="admin-nav-tab-active"
      >
        <span>⚙️ Domain & Password Settings</span>
      </router-link>

      <router-link 
        to="/admin/backups" 
        class="admin-nav-tab"
        active-class="admin-nav-tab-active"
      >
        <span>💾 Backups</span>
      </router-link>

      <router-link 
        to="/admin/audit-logs" 
        class="admin-nav-tab"
        active-class="admin-nav-tab-active"
      >
        <span>📊 Audit Logs</span>
      </router-link>

      <router-link 
        to="/admin/inbox-logs" 
        class="admin-nav-tab"
        active-class="admin-nav-tab-active"
      >
        <span>📥 Inbox Log</span>
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
  padding: 0.6rem 1rem;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
  display: inline-flex;
  items-center: center;
  gap: 0.375rem;
  border: 1px solid transparent;
}

.admin-nav-tab:hover {
  color: #00f0ff;
  background-color: rgba(0, 240, 255, 0.08);
  border-color: rgba(0, 240, 255, 0.2);
}

.admin-nav-tab-active {
  color: #9fef00 !important;
  background-color: rgba(159, 239, 0, 0.12) !important;
  border-color: rgba(159, 239, 0, 0.4) !important;
  box-shadow: 0 0 10px rgba(159, 239, 0, 0.15);
}
</style>
