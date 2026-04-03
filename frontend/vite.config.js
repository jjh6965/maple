import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(() => {
  const backendTarget =
    process.env.VITE_BACKEND_TARGET ||
    process.env.VITE_API_URL ||
    "http://localhost:8000";

  return {
    plugins: [react()],

    server: {
      host: "0.0.0.0",
      port: 5173,
      proxy: {
        "/auth": {
          target: backendTarget,
          changeOrigin: true,
          secure: false,
        },
        "/api": {
          target: backendTarget,
          changeOrigin: true,
          secure: false,
        },
        "/socket.io": {
          target: backendTarget,
          ws: true,
          changeOrigin: true,
          secure: false,
        },
      },
    },
  };
});
