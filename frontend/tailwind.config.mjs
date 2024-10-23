import daisyui from "daisyui";

export default {
  content: ["./index.html", "./src/**/*.{js,ts}"],

  theme: {
    fontFamily: {
      sans: ['"Gill Sans"', 'sans-serif'],
    },
  },

  // always include in css output, regardless JIT
  safelist: [
    'alert-warning',
    'alert-success',
    'alert-error',
    'alert-info',
  ],

  plugins: [daisyui],
  daisyui: {
    logs: false,
  }
};
