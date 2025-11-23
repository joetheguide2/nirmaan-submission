import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist'
  },
  // Update this to your Railway backend URL
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify('https://nirmaan-submission-production.up.railway.app')
  }
})