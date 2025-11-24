/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/frontend/**/*.{js,ts,jsx,tsx,mdx}',
    './src/frontend/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/frontend/components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Alert severity colors
        'alert-critical': '#DC2626',
        'alert-high': '#EA580C',
        'alert-medium': '#CA8A04',
        'alert-low': '#2563EB',

        // Alert severity backgrounds (lighter versions)
        'alert-critical-bg': '#FEE2E2',
        'alert-high-bg': '#FFEDD5',
        'alert-medium-bg': '#FEF9C3',
        'alert-low-bg': '#DBEAFE',

        // Aging bucket colors
        'aging-current': '#16A34A',
        'aging-30': '#84CC16',
        'aging-60': '#EAB308',
        'aging-90': '#F97316',
        'aging-over': '#DC2626',

        // Status colors
        'status-active': '#16A34A',
        'status-inactive': '#6B7280',
        'status-hold': '#DC2626',
        'status-cod': '#8B5CF6',

        // Primary brand colors
        primary: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
          950: '#172554',
        },

        // Neutral colors for UI
        neutral: {
          50: '#FAFAFA',
          100: '#F5F5F5',
          200: '#E5E5E5',
          300: '#D4D4D4',
          400: '#A3A3A3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0A0A0A',
        },

        // Success/Error/Warning colors
        success: {
          50: '#F0FDF4',
          100: '#DCFCE7',
          500: '#22C55E',
          600: '#16A34A',
          700: '#15803D',
        },
        error: {
          50: '#FEF2F2',
          100: '#FEE2E2',
          500: '#EF4444',
          600: '#DC2626',
          700: '#B91C1C',
        },
        warning: {
          50: '#FFFBEB',
          100: '#FEF3C7',
          500: '#F59E0B',
          600: '#D97706',
          700: '#B45309',
        },
        info: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
        },
      },

      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },

      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
      },

      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },

      boxShadow: {
        'card': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        'card-hover': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'modal': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        'dropdown': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
      },

      borderRadius: {
        'sm': '0.25rem',
        'DEFAULT': '0.375rem',
        'md': '0.5rem',
        'lg': '0.75rem',
        'xl': '1rem',
      },

      animation: {
        'critical-pulse': 'critical-pulse 1.5s ease-in-out infinite',
        'icon-pulse': 'icon-pulse 1s ease-in-out infinite',
        'fade-in': 'fade-in 0.2s ease-out',
        'slide-in': 'slide-in 0.3s ease-out',
        'spin-slow': 'spin 2s linear infinite',
      },

      keyframes: {
        'critical-pulse': {
          '0%, 100%': {
            backgroundColor: '#FEE2E2',
            borderColor: '#DC2626',
          },
          '50%': {
            backgroundColor: '#FECACA',
            borderColor: '#B91C1C',
          },
        },
        'icon-pulse': {
          '0%, 100%': {
            transform: 'scale(1)',
            opacity: '1',
          },
          '50%': {
            transform: 'scale(1.2)',
            opacity: '0.8',
          },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-in': {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },

      transitionProperty: {
        'height': 'height',
        'spacing': 'margin, padding',
      },

      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      },
    },
  },
  plugins: [
    // Custom plugin for AR-specific utilities
    function({ addUtilities, addComponents, theme }) {
      // Alert severity utilities
      addUtilities({
        '.alert-critical-pulse': {
          animation: 'critical-pulse 1.5s ease-in-out infinite',
        },
        '.alert-icon-pulse': {
          animation: 'icon-pulse 1s ease-in-out infinite',
        },
      });

      // Badge components
      addComponents({
        '.badge-critical': {
          backgroundColor: theme('colors.alert-critical-bg'),
          color: theme('colors.alert-critical'),
          borderColor: theme('colors.alert-critical'),
        },
        '.badge-high': {
          backgroundColor: theme('colors.alert-high-bg'),
          color: theme('colors.alert-high'),
          borderColor: theme('colors.alert-high'),
        },
        '.badge-medium': {
          backgroundColor: theme('colors.alert-medium-bg'),
          color: theme('colors.alert-medium'),
          borderColor: theme('colors.alert-medium'),
        },
        '.badge-low': {
          backgroundColor: theme('colors.alert-low-bg'),
          color: theme('colors.alert-low'),
          borderColor: theme('colors.alert-low'),
        },
      });
    },
  ],
};
