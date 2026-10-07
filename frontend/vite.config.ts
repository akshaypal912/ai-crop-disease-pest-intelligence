import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  server: {
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'caramel-retread-halved.ngrok-free.dev',
    ],
    proxy: {
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/predict': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/assistant': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/translate': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
