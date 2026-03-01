import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite' 

export default defineConfig({
  plugins: [react(), tailwindcss()], // Thêm tailwindcss() vào đây
  clearScreen: false,
  server: {
    port: 5173,
    strictPort: true,
    watch: {
      ignored:["**/src-tauri/**", "**/python-sidecar/**"],
    },
  },
})