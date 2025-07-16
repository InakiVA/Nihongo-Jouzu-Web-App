console.log("⚡ TAILWIND CONFIG CARGADO");
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./templates/**/*.html",
    "./static/css/**/*.css",
    "./**/*.{py,html,js}",
  ],
  theme: {
    extend: {
      colors: {
        aqua: "#008f89",
        mint: "#c9f7f5",
        ocean: "#2a3c4b",
        darkocean: "#1c2731",
      },
    },
  },
  plugins: [
    import("daisyui"), // con ESM debes usar import()
  ],
};
