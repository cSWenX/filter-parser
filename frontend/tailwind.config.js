/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        }
      },
      fontFamily: {
        sans: ['system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      }
    },
  },
  plugins: [],
  // 云部署优化：确保重要样式不被清除
  safelist: [
    'bg-white',
    'border-r',
    'border-gray-200',
    'flex',
    'flex-col',
    'w-64',
    'p-6',
    'text-xl',
    'font-bold',
    'text-gray-900',
    'text-sm',
    'text-gray-600',
    'mt-1',
    'flex-1',
    'p-4',
    'space-y-2',
    'w-full',
    'items-start',
    'rounded-lg',
    'text-left',
    'transition-colors',
    'duration-200',
    'bg-primary-50',
    'text-primary-700',
    'border',
    'border-primary-200',
    'hover:bg-gray-50',
    'hover:text-gray-900',
    'w-5',
    'h-5',
    'mt-0.5',
    'mr-3',
    'flex-shrink-0',
    'text-primary-600',
    'text-gray-400',
    'font-medium',
    'text-primary-900',
    'border-t',
    'text-xs',
    'text-gray-500',
    'min-h-screen',
    'bg-gray-50'
  ]
}