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
        "neutral-light": "var(--color-neutral-light)",
        "neutral-main": "var(--color-neutral-main)",
        "neutral-secondary": "var(--color-neutral-secondary)",
        "neutral-dark": "var(--color-neutral-dark)",

        "accent-light": "var(--color-accent-light)",
        "accent-main": "var(--color-accent-main)",
        "accent-dark": "var(--color-accent-dark)",

        "secondary-light": "var(--color-secondary-light)",
        "secondary-main": "var(--color-secondary-main)",
        "secondary-dark": "var(--color-secondary-dark)",

        "include": "var(--color-include)",
        "exclude": "var(--color-exclude)",
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
