import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In development, forward /api calls to the Flask server on port 5000.
// The test block configures Vitest to run component tests in a browser-like DOM.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/api": "http://127.0.0.1:5000" },
  },
  test: {
    environment: "jsdom",
    include: ["src/**/*.test.{js,jsx}"],
  },
});
