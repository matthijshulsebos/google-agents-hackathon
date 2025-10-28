/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2563EB',
          light: '#3B82F6',
          dark: '#1E40AF',
        },
        critical: {
          bg: '#FEE2E2',
          text: '#DC2626',
        },
        warning: {
          bg: '#FEF3C7',
          text: '#D97706',
        },
        success: {
          bg: '#D1FAE5',
          text: '#059669',
        },
        info: {
          bg: '#EDE9FE',
          text: '#7C3AED',
        },
      },
    },
  },
  plugins: [],
}
