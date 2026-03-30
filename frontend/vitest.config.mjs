import vue from '@vitejs/plugin-vue'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitest/config'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './'),
            '~': path.resolve(__dirname, './'),
            '#app': path.resolve(__dirname, './tests/mocks/nuxt-app.js'),
            '#imports': path.resolve(__dirname, './tests/mocks/nuxt-imports.js'),
        },
    },
    test: {
        globals: true,
        environment: 'jsdom',
        include: ['**/tests/**/*.test.js'],
        setupFiles: ['./tests/setup.js'],
    },
})