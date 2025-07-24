import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  server: {
    host: true, // so Vite listens to external requests
    allowedHosts: [
      "freeware-april-eng-approach.trycloudflare.com", // your tunnel URL
    ],
    port: 5173, // or whatever port you're using
  },
  plugins: [react()],
});
