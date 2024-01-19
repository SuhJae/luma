import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import {resolve} from 'path'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    build: {
        // Use a relative path for outDir
        outDir: resolve(__dirname, '../backend/app/static'),
        // This will empty the outDir folder before building
        emptyOutDir: true,
    },
    server: {
        proxy: {
            '/api/v1': {
                target: 'http://localhost:8000', // FastAPI server
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api\/v1/, '')
            }
        }
    }
})
