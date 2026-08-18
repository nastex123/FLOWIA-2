import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        obsidian: {
          950: '#030408',
          900: '#06050b',
          800: '#0c0a14',
          700: '#140f22',
        },
        crimson: {
          950: '#4c0519',
          900: '#881337',
          800: '#9f1239',
          700: '#be123c',
          600: '#e11d48',
          500: '#f43f5e',
          400: '#fb7185',
          300: '#fda4af',
          200: '#fecdd3',
          100: '#ffe4e6',
          50: '#fff1f2',
        },
      },
      fontFamily: {
        serif: ['Georgia', 'Palatino Linotype', 'Garamond', 'serif'],
        sans: ['Segoe UI', 'Inter', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
export default config;
