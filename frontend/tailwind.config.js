/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: '#0F172A',
        cyber: '#2563EB',
        accent: '#22D3EE',
        surface: 'rgba(15,23,42,0.75)',
        card: 'rgba(30,41,59,0.7)',
        border: 'rgba(148,163,184,0.2)',
        critical: '#EF4444',
        high: '#F97316',
        medium: '#EAB308',
        low: '#22C55E',
      },
      boxShadow: {
        glass: '0 10px 40px rgba(0,0,0,0.35)',
        glow: '0 0 25px rgba(34,211,238,0.35)',
      },
      backdropBlur: {
        xs: '2px',
      },
      backgroundImage: {
        'mesh': 'radial-gradient(circle at 20% 20%, rgba(34,211,238,0.08), transparent 25%), radial-gradient(circle at 80% 0%, rgba(37,99,235,0.12), transparent 25%), radial-gradient(circle at 60% 80%, rgba(239,68,68,0.08), transparent 25%)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'fade-in': 'fade-in 0.6s ease both',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'fade-in': {
          '0%': { opacity: 0, transform: 'translateY(6px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        }
      }
    },
  },
  plugins: [],
}
