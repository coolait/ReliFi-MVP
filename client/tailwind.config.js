/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'uber-blue': '#4285F4',
        'lyft-blue': '#4285F4',
        'doordash-yellow': '#FFD700',
        'grubhub-orange': '#FF6B35',
        'ubereats-gray': '#E0E0E0',
      }
    },
  },
  plugins: [],
}
