/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50:  '#e8f5ed',
          100: '#c8e6d4',
          200: '#a4d4b5',
          300: '#7dc196',
          400: '#5db07b',
          500: '#3d9e61',
          600: '#1B7A3D',  // brand green
          700: '#155f30',
          800: '#0f4523',
          900: '#082b15',
        },
        accent: {
          400: '#FFA726',
          500: '#F57C00',  // brand orange
          600: '#E65100',
        },
        surface: {
          DEFAULT: '#FFFFFF',
          50: '#F8FBF9',
          100: '#F0F7F2',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Noto Sans Devanagari', 'system-ui', 'sans-serif'],
        devanagari: ['Noto Sans Devanagari', 'sans-serif'],
      },
      borderRadius: {
        xl:  '16px',
        '2xl': '24px',
      },
      boxShadow: {
        card: '0 2px 12px rgba(0,0,0,0.08)',
        'card-hover': '0 8px 24px rgba(0,0,0,0.14)',
      },
      minHeight: {
        touch: '48px',
      },
    },
  },
  plugins: [],
}
