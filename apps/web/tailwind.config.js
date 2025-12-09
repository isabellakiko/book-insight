/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0a0908',
        paper: {
          dark: '#151210',
          DEFAULT: '#1e1a16',
          light: '#2a2520',
          lighter: '#3d3529',
        },
        gold: {
          DEFAULT: '#e6c158',
          dim: '#c9a55c',
          glow: 'rgba(230, 193, 88, 0.4)',
        },
        copper: '#e08850',
        burgundy: '#c45050',
      },
      fontFamily: {
        display: ['Cormorant Garamond', 'Noto Serif SC', 'Georgia', 'serif'],
        body: ['Source Sans 3', 'Noto Sans SC', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        '2xs': '0.6875rem',
      },
      spacing: {
        18: '4.5rem',
        88: '22rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease-out forwards',
        'slide-up': 'slideUp 0.5s ease-out forwards',
        'slide-in': 'slideIn 0.4s ease-out forwards',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(230, 193, 88, 0.2)' },
          '100%': { boxShadow: '0 0 20px rgba(230, 193, 88, 0.4)' },
        },
      },
      boxShadow: {
        'gold-glow': '0 0 20px rgba(230, 193, 88, 0.3)',
        'gold-glow-lg': '0 0 40px rgba(230, 193, 88, 0.4)',
      },
    },
  },
  plugins: [],
}
