import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/start': 'http://localhost:8000',
      '/reset': 'http://localhost:8000',
      '/stop': 'http://localhost:8000',
      '/viewer': {
        target: 'http://localhost:3001',
        rewrite: (path) => path.replace(/^\/viewer/, ''),
      },
      '/inventory': {
        target: 'http://localhost:3002',
        rewrite: (path) => path.replace(/^\/inventory/, ''),
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    }
  }
})
