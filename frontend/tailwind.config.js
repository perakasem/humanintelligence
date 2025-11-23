/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Earth tone palette
        primary: {
          50: '#fdf8f6',
          100: '#f9ebe5',
          200: '#f3d5c8',
          300: '#e9b8a3',
          400: '#db9275',
          500: '#c97a5c',
          600: '#b5634a',
          700: '#96503d',
          800: '#7a4436',
          900: '#653b30',
        },
        // Sage/olive accent
        accent: {
          50: '#f6f7f4',
          100: '#e9ebe3',
          200: '#d4d8c8',
          300: '#b5bda1',
          400: '#959f7c',
          500: '#7a8561',
          600: '#5f6a4b',
          700: '#4a533c',
          800: '#3d4433',
          900: '#353b2d',
        },
        // Warm stone neutrals
        stone: {
          50: '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c',
          600: '#57534e',
          700: '#44403c',
          800: '#292524',
          900: '#1c1917',
        },
        // Cream background
        cream: {
          50: '#fefdfb',
          100: '#fdf9f3',
          200: '#faf3e8',
          300: '#f5e9d6',
          400: '#eddcc0',
        },
      },
      fontFamily: {
        // Elegant serif for headings
        serif: ['Fraunces', 'Georgia', 'serif'],
        // Clean sans for body
        sans: ['DM Sans', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'display': ['3.5rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'heading': ['2rem', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
      },
      borderRadius: {
        'organic': '1.5rem',
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'warm': '0 4px 20px -2px rgba(101, 59, 48, 0.1)',
      },
    },
  },
  plugins: [],
}
