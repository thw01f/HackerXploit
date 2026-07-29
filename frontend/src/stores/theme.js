import { ref, watchEffect } from 'vue'

const isDark = ref(localStorage.getItem('hx_theme') !== 'light')

const applyTheme = () => {
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    document.documentElement.classList.remove('light')
  } else {
    document.documentElement.classList.add('light')
    document.documentElement.classList.remove('dark')
  }
  localStorage.setItem('hx_theme', isDark.value ? 'dark' : 'light')
}

// Initial application
applyTheme()

export function useTheme() {
  const toggleTheme = () => {
    isDark.value = !isDark.value
    applyTheme()
  }

  return {
    isDark,
    toggleTheme
  }
}
