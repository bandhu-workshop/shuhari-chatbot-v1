import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // Same-origin in dev, so lib/api.ts can keep its relative `/api/v1` default and
    // never learn the backend host. Mirrors what nginx does under `just stack`.
    proxy: { "/api": "http://localhost:8000" },
  },
});
