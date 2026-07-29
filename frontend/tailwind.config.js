/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cyber-dark': '#0b0e14',
        'cyber-surface': '#111927',
        'cyber-card': '#151f30',
        'cyber-border': '#1f293d',
        'htb-green': '#9fef00',
        'cyber-cyan': '#00f0ff',
      },
      fontFamily: {
        sans: ['Inter', 'Outfit', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      }
    },
  },
  plugins: [],
}
