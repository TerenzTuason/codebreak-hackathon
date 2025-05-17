import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: {
          DEFAULT: '#0052CC',
          light: '#4C9AFF',
          dark: '#0747A6'
        },
        secondary: {
          DEFAULT: '#6B7DFF',
          light: '#8B94FF'
        }
      },
      fontFamily: {
        poppins: ['var(--font-poppins)', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(to right bottom, #6B7DFF, #8B94FF)',
      }
    },
  },
  plugins: [],
};
export default config;
