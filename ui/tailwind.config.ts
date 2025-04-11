import type { Config } from 'tailwindcss';

export default {
	content: ['./src/**/*.{html,js,vue,ts,jsx,tsx}'],
  purge: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
} as Config;