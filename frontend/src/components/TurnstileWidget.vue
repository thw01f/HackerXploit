<template>
  <div ref="containerRef"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  siteKey: { type: String, required: true },
  theme: { type: String, default: 'dark' } // Turnstile only supports 'light'/'dark', not this app's 'system'
})

const emit = defineEmits(['verified', 'expired', 'error'])

const containerRef = ref(null)
let widgetId = null

// Cloudflare's script is loaded once and shared across every widget instance
// on the page (e.g. if both a login and a register form somehow mount at
// once) - re-injecting <script> tags per-widget would re-run the loader
// and can leave window.turnstile in an inconsistent state.
let scriptLoadPromise = null
const loadTurnstileScript = () => {
  if (window.turnstile) return Promise.resolve()
  if (scriptLoadPromise) return scriptLoadPromise

  scriptLoadPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js'
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Failed to load Cloudflare Turnstile'))
    document.head.appendChild(script)
  })
  return scriptLoadPromise
}

const renderWidget = () => {
  if (!containerRef.value || !window.turnstile) return
  widgetId = window.turnstile.render(containerRef.value, {
    sitekey: props.siteKey,
    theme: props.theme,
    callback: (token) => emit('verified', token),
    'expired-callback': () => emit('expired'),
    'error-callback': () => emit('error')
  })
}

onMounted(async () => {
  try {
    await loadTurnstileScript()
    renderWidget()
  } catch (e) {
    emit('error')
  }
})

onBeforeUnmount(() => {
  if (widgetId && window.turnstile) {
    window.turnstile.remove(widgetId)
  }
})

// The site key can arrive asynchronously (fetched from the backend after
// this component already mounted with an empty placeholder) - re-render
// once a real key shows up instead of staying stuck unrendered.
watch(() => props.siteKey, (newKey, oldKey) => {
  if (newKey && newKey !== oldKey && window.turnstile) {
    if (widgetId) window.turnstile.remove(widgetId)
    renderWidget()
  }
})

// Turnstile doesn't support a live theme switch on an already-rendered
// widget - if the user flips light/dark mode while this page is open, the
// only way to reflect it is to tear down and re-render.
watch(() => props.theme, () => {
  if (widgetId && window.turnstile) {
    window.turnstile.remove(widgetId)
    renderWidget()
  }
})

defineExpose({
  reset: () => {
    if (widgetId && window.turnstile) window.turnstile.reset(widgetId)
  }
})
</script>
