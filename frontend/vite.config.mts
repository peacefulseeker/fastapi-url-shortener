import { defineConfig } from "vite";
import checker from "vite-plugin-checker";

export default defineConfig({
  server: {
    port: 5555,
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
});
