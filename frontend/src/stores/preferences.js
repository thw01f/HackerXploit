import { ref, computed } from 'vue'

// timeFormat: '12h' | '24h' - applies to every clock/timestamp rendered across
// the app. A module-scope singleton (like stores/theme.js) rather than a Pinia
// store, since it's a pure client-rendering preference with no server sync.
const STORAGE_KEY = 'hx_time_format'

const stored = localStorage.getItem(STORAGE_KEY)
const timeFormat = ref(['12h', '24h'].includes(stored) ? stored : '12h')

export function usePreferences() {
  const setTimeFormat = (fmt) => {
    if (!['12h', '24h'].includes(fmt)) return
    timeFormat.value = fmt
    localStorage.setItem(STORAGE_KEY, fmt)
  }

  const is12h = computed(() => timeFormat.value === '12h')

  return {
    timeFormat,
    setTimeFormat,
    is12h
  }
}
