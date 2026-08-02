import { ref } from 'vue'

// mode: 'light' | 'dark' | 'system' - the user's explicit preference.
// isDark: the resolved boolean actually applied to the page (follows the OS
// preference live when mode is 'system').
const STORAGE_KEY = 'hx_theme_mode'

const storedMode = localStorage.getItem(STORAGE_KEY)
const mode = ref(['light', 'dark', 'system'].includes(storedMode) ? storedMode : 'system')

const systemPrefersDark = () => window.matchMedia('(prefers-color-scheme: dark)').matches

const resolveIsDark = () => {
  if (mode.value === 'system') return systemPrefersDark()
  return mode.value === 'dark'
}

const isDark = ref(resolveIsDark())

const applyTheme = () => {
  isDark.value = resolveIsDark()
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    document.documentElement.classList.remove('light')
  } else {
    document.documentElement.classList.add('light')
    document.documentElement.classList.remove('dark')
  }
}

// Initial application
applyTheme()

// Live-follow the OS theme while mode is 'system'
if (window.matchMedia) {
  const mql = window.matchMedia('(prefers-color-scheme: dark)')
  const onSystemChange = () => {
    if (mode.value === 'system') applyTheme()
  }
  if (mql.addEventListener) mql.addEventListener('change', onSystemChange)
  else if (mql.addListener) mql.addListener(onSystemChange) // older Safari
}

export function useTheme() {
  const setMode = (newMode) => {
    if (!['light', 'dark', 'system'].includes(newMode)) return
    mode.value = newMode
    localStorage.setItem(STORAGE_KEY, newMode)
    applyTheme()
  }

  const toggleTheme = () => {
    // Quick-access toggle (used by the compact drawer switch): flips between
    // light and dark directly, dropping out of 'system' mode since the user
    // just made an explicit choice.
    setMode(isDark.value ? 'light' : 'dark')
  }

  return {
    mode,
    isDark,
    setMode,
    toggleTheme
  }
}
