import { ref, computed } from 'vue'

// timeFormat: '12h' | '24h' - applies to every clock/timestamp rendered across
// the app. A module-scope singleton (like stores/theme.js) rather than a Pinia
// store, since it's a pure client-rendering preference with no server sync.
const STORAGE_KEY = 'hx_time_format'

const stored = localStorage.getItem(STORAGE_KEY)
const timeFormat = ref(['12h', '24h'].includes(stored) ? stored : '12h')

// fontScale: overall UI text/scaling size. Applied as the root font-size so
// every rem-based Tailwind class (text-sm, p-4, gap-2, ...) scales with it
// app-wide, not just literal font sizes.
const FONT_SCALE_KEY = 'hx_font_scale'
const FONT_SCALE_SIZES = { sm: '87.5%', md: '100%', lg: '112.5%', xl: '125%' }

const storedFontScale = localStorage.getItem(FONT_SCALE_KEY)
const fontScale = ref(Object.keys(FONT_SCALE_SIZES).includes(storedFontScale) ? storedFontScale : 'md')

const applyFontScale = () => {
  document.documentElement.style.fontSize = FONT_SCALE_SIZES[fontScale.value]
}

applyFontScale()

export function usePreferences() {
  const setTimeFormat = (fmt) => {
    if (!['12h', '24h'].includes(fmt)) return
    timeFormat.value = fmt
    localStorage.setItem(STORAGE_KEY, fmt)
  }

  const is12h = computed(() => timeFormat.value === '12h')

  const setFontScale = (scale) => {
    if (!Object.keys(FONT_SCALE_SIZES).includes(scale)) return
    fontScale.value = scale
    localStorage.setItem(FONT_SCALE_KEY, scale)
    applyFontScale()
  }

  return {
    timeFormat,
    setTimeFormat,
    is12h,
    fontScale,
    setFontScale
  }
}
