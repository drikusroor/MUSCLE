import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react()],
  test: {
    include: ['**/*.test.js', '**/*.test.jsx', '**/*.test.ts', '**/*.test.tsx'],
    globals: true,
    environment: 'happy-dom',
    coverage: {
      reportsDirectory: 'public/coverage',
    },
  },
  esbuild: {
    include: /\.[jt]sx?$/,
    exclude: [],
    loader: 'jsx',
  },
  resolve: {
    alias: {
        '@/': '/src/',
    },
},
})
