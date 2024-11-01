import daisyui from "daisyui";

export default {
  content: [
    "./index.html",
    "../app/templates/**/*.html",
    "./src/**/*.{js,ts}",
  ],

  theme: {
    fontFamily: {
      sans: ['"Gill Sans"', 'sans-serif'],
    },
  },

  // always include in css output, regardless JIT
  safelist: [
    {
        pattern: /alert-*/
    }
  ],

  plugins: [daisyui],
  daisyui: {
    logs: false,
    themes: ['light']
  }
};
