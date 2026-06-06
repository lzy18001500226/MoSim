import { sentryVitePlugin } from "@sentry/vite-plugin";
import path from "node:path";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// https://vite.dev/config/
export default defineConfig({
  server: {
    proxy: {
      // Forward requests starting with /api to the backend server
      "/api": {
        target: "http://localhost:3001",
        changeOrigin: true,
      },
    },
  },

  plugins: [
    react(),
    tailwindcss(),
    sentryVitePlugin({
      org: "achat",
      project: "web",
      telemetry: false,
    }),
  ],

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },

  build: {
    sourcemap: true,
  },
});
