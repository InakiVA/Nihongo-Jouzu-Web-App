const daisyui = require("daisyui");

module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/css/**/*.css",
    "./**/*.{py,html,js}",
  ],
  safelist: [
    'bg-dark',
    'bg-darkest',
    'text-dark',
    'text-darkest',
  ],
  theme: {
    extend: {
      colors: {
      },
    },
  },
};
