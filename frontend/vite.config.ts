import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './',
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    hmr: {
      clientPort: 443,
      protocol: 'wss',
      host: 'd3ucunu1klbp79.cloudfront.net'
    },
    allowedHosts: [
      'd3ucunu1klbp79.cloudfront.net',
      '.cloudfront.net',
      'localhost'
    ]
  }
})
