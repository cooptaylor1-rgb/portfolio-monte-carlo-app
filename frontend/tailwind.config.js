/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand Colors - Updated for WCAG AA compliance
        primary: {
          navy: '#0F3B63',
          'navy-light': '#1F4F7C',
          'navy-dark': '#082539',
        },
        accent: {
          gold: '#C4A76A',        // Updated
          'gold-light': '#D4B77A', // Updated
          'gold-dark': '#A4875A',  // Updated
        },
        // Background Palette (Dark Mode) - Updated for better contrast
        background: {
          base: '#0F1419',        // Updated
          elevated: '#1A1F26',    // Updated
          hover: '#252B33',       // Updated
          border: '#34393F',      // Updated
        },
        // Text Colors - WCAG AA Compliant
        text: {
          primary: '#FFFFFF',
          secondary: '#C9D1D9',   // Updated
          tertiary: '#8B949E',    // Updated
          disabled: '#6A737D',    // Updated
        },
        // Semantic Colors - Professional and accessible
        status: {
          success: {
            base: '#3FB950',      // Updated
            light: '#56D364',     // Updated
            dark: '#2EA043',      // Updated
          },
          warning: {
            base: '#D29922',      // Updated
            light: '#E3B341',     // Updated
            dark: '#BB8009',      // Updated
          },
          error: {
            base: '#F85149',      // Updated
            light: '#FF7B72',     // Updated
            dark: '#DA3633',      // Updated
          },
          info: {
            base: '#58A6FF',      // Updated
            light: '#79C0FF',     // Updated
            dark: '#388BFD',      // Updated
          },
        },
        // Chart Colors - Color blind friendly
        chart: {
          equity: '#58A6FF',     // Updated
          fixed: '#56D364',      // Updated
          cash: '#D29922',       // Updated
          projection: '#7AA6C4',
          p90: '#56D364',        // Updated
          p75: '#7EE787',        // Updated
          p50: '#D29922',        // Updated
          p25: '#FF9A56',        // Updated
          p10: '#F85149',        // Updated
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Nunito Sans', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Monaco', 'Courier New', 'monospace'],
      },
      fontSize: {
        'display': ['36px', { lineHeight: '44px', letterSpacing: '-0.02em', fontWeight: '700' }],
        'h1': ['32px', { lineHeight: '40px', letterSpacing: '-0.02em', fontWeight: '700' }],
        'h2': ['24px', { lineHeight: '32px', letterSpacing: '-0.01em', fontWeight: '600' }],
        'h3': ['18px', { lineHeight: '28px', letterSpacing: '0', fontWeight: '600' }],
        'h4': ['16px', { lineHeight: '24px', letterSpacing: '0', fontWeight: '600' }],
        'body': ['14px', { lineHeight: '20px', letterSpacing: '0', fontWeight: '400' }],
        'small': ['12px', { lineHeight: '16px', letterSpacing: '0', fontWeight: '400' }],
        'micro': ['11px', { lineHeight: '14px', letterSpacing: '0', fontWeight: '400' }],
      },
      spacing: {
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
        'xl': '32px',
        '2xl': '48px',
        '3xl': '64px',
      },
      borderRadius: {
        'sm': '4px',          // Updated
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        'full': '9999px',     // Added
      },
      boxShadow: {
        'sm': '0 1px 3px 0 rgba(0, 0, 0, 0.5)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.5)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.6)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.7)',
        'glow': '0 0 20px rgba(196, 167, 106, 0.25)',           // Updated
        'glow-strong': '0 0 30px rgba(196, 167, 106, 0.4)',     // Updated
      },
      transitionDuration: {
        'fast': '100ms',      // Updated
        'default': '200ms',
        'slow': '350ms',      // Updated
      },
      maxWidth: {
        'container': '1440px',
        'content': '1200px',
        'narrow': '800px',
      },
      zIndex: {
        '0': '0',
        '10': '10',
        '20': '20',
        '30': '30',
        '40': '40',
        '50': '50',
        'dropdown': '1000',
        'sticky': '1020',
        'modal': '1300',
        'popover': '1400',
        'tooltip': '1500',
      },
      animation: {
        'fade-in': 'fadeIn 200ms ease-in',
        'fade-out': 'fadeOut 200ms ease-out',
        'slide-in-left': 'slideInLeft 250ms ease-out',
        'slide-in-right': 'slideInRight 250ms ease-out',
        'slide-up': 'slideUp 250ms ease-out',
        'scale-in': 'scaleIn 150ms ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        slideInLeft: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
