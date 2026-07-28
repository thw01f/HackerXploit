import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import LandingView from '../views/LandingView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import SetupAdminView from '../views/SetupAdminView.vue'
import ForgotPasswordView from '../views/ForgotPasswordView.vue'
import ResetPasswordView from '../views/ResetPasswordView.vue'
import DashboardView from '../views/DashboardView.vue'
import AcademyView from '../views/AcademyView.vue'
import AcademyWriteView from '../views/AcademyWriteView.vue'
import CourseDetailView from '../views/CourseDetailView.vue'
import MyCoursesView from '../views/MyCoursesView.vue'
import SearchView from '../views/SearchView.vue'
import CompetitionsView from '../views/CompetitionsView.vue'
import OpportunitiesView from '../views/OpportunitiesView.vue'
import ProfileView from '../views/ProfileView.vue'
import AdminView from '../views/AdminView.vue'
import AdminSecurityView from '../views/AdminSecurityView.vue'
import AdminAdminsView from '../views/AdminAdminsView.vue'
import AdminAuditLogView from '../views/AdminAuditLogView.vue'
import AdminPasswordRequestsView from '../views/AdminPasswordRequestsView.vue'
import AdminProfileFieldsView from '../views/AdminProfileFieldsView.vue'

const routes = [
  { path: '/', name: 'landing', component: LandingView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/setup-admin', name: 'setup-admin', component: SetupAdminView, meta: { requiresAuth: true } },
  { path: '/forgot-password', name: 'forgot-password', component: ForgotPasswordView },
  { path: '/reset-password', name: 'reset-password', component: ResetPasswordView },
  { 
    path: '/dashboard', 
    name: 'dashboard', 
    component: DashboardView, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/academy', 
    name: 'academy', 
    component: AcademyView, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/academy/write', 
    name: 'academy-write', 
    component: AcademyWriteView, 
    meta: { requiresAuth: true, roles: ['teacher', 'admin', 'root_admin'] } 
  },
  { 
    path: '/academy/course/:slug', 
    name: 'course-detail', 
    component: CourseDetailView, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/academy/my-courses', 
    name: 'my-courses', 
    component: MyCoursesView, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/search', 
    name: 'search', 
    component: SearchView, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/competitions', 
    name: 'competitions', 
    component: CompetitionsView, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/opportunities', 
    name: 'opportunities', 
    component: OpportunitiesView, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/profile', 
    name: 'profile', 
    component: ProfileView, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/admin', 
    name: 'admin', 
    component: AdminView, 
    meta: { requiresAuth: true, roles: ['admin', 'root_admin', 'teacher'] } 
  },
  { 
    path: '/admin/security/login-activity', 
    name: 'admin-security', 
    component: AdminSecurityView, 
    meta: { requiresAuth: true, roles: ['admin', 'root_admin'] } 
  },
  { 
    path: '/admin/audit-log', 
    name: 'admin-audit-log', 
    component: AdminAuditLogView, 
    meta: { requiresAuth: true, roles: ['admin', 'root_admin'] } 
  },
  { 
    path: '/admin/password-requests', 
    name: 'admin-password-requests', 
    component: AdminPasswordRequestsView, 
    meta: { requiresAuth: true, roles: ['admin', 'root_admin'] } 
  },
  { 
    path: '/admin/profile-fields', 
    name: 'admin-profile-fields', 
    component: AdminProfileFieldsView, 
    meta: { requiresAuth: true, roles: ['admin', 'root_admin'] } 
  },
  { 
    path: '/admin/manage-admins', 
    name: 'admin-manage', 
    component: AdminAdminsView, 
    meta: { requiresAuth: true, rootOnly: true } 
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  if (authStore.token && !authStore.user) {
    await authStore.fetchMe()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  // Force first-login setup redirect
  if (authStore.user && authStore.user.is_first_login && to.name !== 'setup-admin' && to.name !== 'login') {
    return next({ name: 'setup-admin' })
  }

  if (to.meta.rootOnly && !authStore.isRootAdmin) {
    return next({ name: 'dashboard' })
  }

  if (to.meta.roles && !to.meta.roles.includes(authStore.userRole)) {
    return next({ name: 'dashboard' })
  }

  next()
})

export default router
