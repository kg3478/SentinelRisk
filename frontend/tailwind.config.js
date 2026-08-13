/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#090d16',
        surface: '#111827',
        surfaceCard: '#1f2937',
        borderDark: '#374151',
        brandPrimary: '#6366f1',
        brandAccent: '#818cf8',
        riskLow: '#10b981',
        riskMedium: '#f59e0b',
        riskHigh: '#f97316',
        riskCritical: '#ef4444',
      },
    },
  },
  plugins: [],
}
