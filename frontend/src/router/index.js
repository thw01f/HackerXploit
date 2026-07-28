import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import LandingView from '../views/LandingView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import AcademyView from '../views/AcademyView.vue'
import CourseDetailView from '../views/CourseDetailView.vue'
import CompetitionsView from '../views/CompetitionsView.vue'
import OpportunitiesView from '../views/OpportunitiesView.vue'
import ProfileView from '../views/ProfileView.vue'
import AdminView from '../views/AdminView.vue'
import AdminSecurityView from '../views/AdminSecurityView.vue'
import AdminAdminsView from '../views/AdminAdminsView.vue'

const routes = [
  { path: '/', name: 'landing', component: LandingView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
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
    path: '/academy/course/:id', 
    name: 'course-detail', 
    component: CourseDetailView, 
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

  if (to.meta.rootOnly && !authStore.isRootAdmin) {
    return next({ name: 'dashboard' })
  }

  if (to.meta.roles && !to.meta.roles.includes(authStore.userRole)) {
    return next({ name: 'dashboard' })
  }

  next()
})

export default router
