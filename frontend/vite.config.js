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
    }
})
