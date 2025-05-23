const typography = require('@tailwindcss/typography');

module.exports = {
  content: [
    './index.html',
    './src/**/*.{html,js,vue,ts,jsx,tsx}',
  ],
  plugins: [
    typography,
  ],
}; 