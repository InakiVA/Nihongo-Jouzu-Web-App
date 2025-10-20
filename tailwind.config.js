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
      keyframes: {
        fadeinout: {
          '0%': { opacity: '0' },
          '10%': { opacity: '1' },
          '90%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
      },
      animation: {
        fadeinout: 'fadeinout 3s ease-in-out forwards',
      },
    },
  },
};
