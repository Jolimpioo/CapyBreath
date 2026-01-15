/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        capy: {
          primary: '#8B7355',    // Marrom capivara
          secondary: '#C4A57B',  // Bege claro
          accent: '#4A7C59',     // Verde água
          light: '#F5E6D3',      // Creme
          dark: '#5C4A3A',       // Marrom escuro
        }
      },
    },
  },
  plugins: [],
}