/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./public/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        customGreen : {
          100: "#349C55",
          200: "#0E7C4A",
        },
        customBlue : {
          100: "#1668BD",
          200: "#2258A5",
        },
        customOrange : {
          100: "#FFB318",
          200: "#FF8B00",
        },
        cgreen : {
          100: "#349C55",
          200: "#0E7C4A",
        },
        cblue : {
          100: "#1668BD",
          200: "#2258A5",
        },
        corange : {
          100: "#FFB318",
          200: "#FF8B00",
        },
        cred : {
          100: "#F8312F",
          200: "#E51400",
        },
      }
    },
  },
  plugins: [],
}

