// This file should be replaced by tailwind.config.js for compatibility.
// See tailwind.config.js for the working config.

import type { Config } from 'tailwindcss';
import typography from '@tailwindcss/typography';

export default {
	content: [
		'./index.html',
		'./src/**/*.{html,js,vue,ts,jsx,tsx}',
	],
	plugins: [
		typography,
	],
} as Config;