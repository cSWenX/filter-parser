import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false, // 云部署优化：关闭sourcemap减少构建体积
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['lucide-react', 'react-hot-toast']
        }
      }
    },
    // 确保CSS正确内联
    cssCodeSplit: false,
    // 云部署优化
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  },
  // 云部署兼容性配置
  base: './', // 使用相对路径，适配各种部署环境
  define: {
    // 避免生产环境中的开发工具
    __DEV__: false
  }
})