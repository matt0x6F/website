// This file should be replaced by tailwind.config.js for compatibility.
// See tailwind.config.js for the working config.

import type { Config } from 'tailwindcss';
import typography from '@tailwindcss/typography';

const config: Config = {
	content: [
		'./components/**/*.{vue,js,ts}',
		'./layouts/**/*.{vue,js,ts}',
		'./pages/**/*.{vue,js,ts}',
		'./views/**/*.{vue,js,ts}',
		'./app.vue',
		'./nuxt.config.{js,ts}',
	],
	theme: {
		extend: {
			colors: {
				primary: {
					DEFAULT: '#10b981', // emerald-500
					50:  '#ecfdf5',
					100: '#d1fae5',
					200: '#a7f3d0',
					300: '#6ee7b7',
					400: '#34d399',
					500: '#10b981',
					600: '#059669',
					700: '#047857',
					800: '#065f46',
					900: '#064e3b',
				},
			},
		},
	},
	plugins: [
		typography,
	],
};

export default config;