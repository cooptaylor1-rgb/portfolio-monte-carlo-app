/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand Colors
        primary: {
          navy: '#0F3B63',
          'navy-light': '#1F4F7C',
          'navy-dark': '#082539',
        },
        accent: {
          gold: '#B49759',
          'gold-light': '#C4A76A',
          'gold-dark': '#9A834D',
        },
        // Background Palette (Dark Mode)
        background: {
          base: '#0A0C10',
          elevated: '#12141A',
          hover: '#1A1D24',
          border: '#262A33',
        },
        // Text Colors
        text: {
          primary: '#FFFFFF',
          secondary: '#B4B9C2',
          tertiary: '#6F767D',
          disabled: '#4A5057',
        },
        // Semantic Colors
        status: {
          success: {
            base: '#10B981',
            light: '#34D399',
            dark: '#059669',
          },
          warning: {
            base: '#F59E0B',
            light: '#FBBF24',
            dark: '#D97706',
          },
          error: {
            base: '#EF4444',
            light: '#F87171',
            dark: '#DC2626',
          },
          info: {
            base: '#3B82F6',
            light: '#60A5FA',
            dark: '#2563EB',
          },
        },
        // Chart Colors
        chart: {
          equity: '#4CA6E8',
          fixed: '#7AC18D',
          cash: '#D7B46A',
          projection: '#7AA6C4',
          p90: '#059669',
          p75: '#10B981',
          p50: '#B49759',
          p25: '#F59E0B',
          p10: '#DC2626',
        },
        // Legacy aliases for backwards compatibility
        success: '#10B981',
        warning: '#F59E0B',
        danger: '#EF4444',
        'brand-gold': '#B49759',
        'brand-gold-dark': '#9A834D',
        surface: {
          900: '#0A0C10',
          800: '#12141A',
          700: '#1A1D24',
          600: '#262A33',
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
        'sm': '6px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgb(0 0 0 / 0.3)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.3), 0 2px 4px -2px rgb(0 0 0 / 0.2)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.4), 0 4px 6px -4px rgb(0 0 0 / 0.3)',
        'xl': '0 20px 25px -5px rgb(0 0 0 / 0.4), 0 8px 10px -6px rgb(0 0 0 / 0.3)',
        'glow': '0 0 20px rgb(180 151 89 / 0.3)',
        'glow-strong': '0 0 30px rgb(180 151 89 / 0.5)',
      },
      transitionDuration: {
        'fast': '150ms',
        'default': '200ms',
        'slow': '300ms',
      },
      maxWidth: {
        'container': '1440px',
      },
    },
  },
  plugins: [],
}
