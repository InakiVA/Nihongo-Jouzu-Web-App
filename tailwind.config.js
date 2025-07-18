console.log("TAILWIND CONFIG CARGADO");

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/css/**/*.css",
    "./**/*.{py,html,js}",
  ],
  theme: {
    extend: {
      colors: {
        main: "#008f89",
        light: "#c9f7f5",
        dark: "#2a3c4b",
        darkest: "#1c2731",
      },
    },
  },
};
