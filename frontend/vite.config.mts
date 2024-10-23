import { defineConfig } from "vite";
import checker from "vite-plugin-checker";

const config = defineConfig({
  server: {
    port: process.env.PORT,
    proxy: {
      "/api": {
        target: `http://localhost:${process.env.BACKEND_PORT}`,
        changeOrigin: true,
        secure: false,
      },
    },
  },
  plugins: [
    checker({
      typescript: true,
    }),
  ],

  build: {
    outDir: "../app/static/frontend/",
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: "index.js",
        assetFileNames: (assetInfo) => {
          if (assetInfo.name === "index.css") {
            return "index.css";
          }
        },
      },
    },
  },
});

export default config;
