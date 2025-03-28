import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'build',
    sourcemap: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      },
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'three'],
          ui: ['@mui/material', '@emotion/react', '@emotion/styled']
        }
      }
    },
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: process.env.NODE_ENV === 'production',
        drop_debugger: true
      }
    }
  },
  server: {
    port: 3000,
    open: true,
    host: true,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // Ensure backend is running on this port
        changeOrigin: true
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@styles': resolve(__dirname, 'src/styles'),
      '@backend': resolve(__dirname, 'src/backend')
    }
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'three', '@mui/material'],
    exclude: ['electron']
  },
  esbuild: {
    jsxInject: `import React from 'react'`
  }
})