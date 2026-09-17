import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The backend runs on :8000; proxy /api to it during development.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
