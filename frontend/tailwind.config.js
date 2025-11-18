/** @type {import('tailwindcss').Config} */
const config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef8ff',
          100: '#cfe7ff',
          500: '#2b72ff',
          600: '#1e53c9',
          900: '#0c1a3a',
        },
      },
    },
  },
  plugins: [],
}

export default config



