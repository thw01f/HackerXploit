import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'
import router from './router'
import './index.css'

if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
  axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
}

// Session identity travels via the HttpOnly session_token cookie only —
// the SPA never reads or sends the raw token itself.
axios.defaults.withCredentials = true

const app = createApp(App)

app.use(createPinia())
app.use(router)

const sentryDsn = import.meta.env.VITE_SENTRY_DSN
if (sentryDsn) {
  import('@sentry/vue').then((Sentry) => {
    Sentry.init({
      app,
      dsn: sentryDsn,
      integrations: [Sentry.browserTracingIntegration({ router })],
      tracesSampleRate: 0.2
    })
  }).catch(() => {})
}

app.mount('#app')
