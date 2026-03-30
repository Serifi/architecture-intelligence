import { defineNuxtConfig } from 'nuxt/config'
import Lara from '@primevue/themes/lara'
import { definePreset } from '@primevue/themes'

export default defineNuxtConfig({
    ssr: false,
    telemetry: false,
    compatibilityDate: '2025-11-02',

    modules: ['@pinia/nuxt', '@nuxtjs/tailwindcss', '@primevue/nuxt-module'],

    pinia: { storesDirs: ['app/stores/**'] },

    app: {
        head: {
            title: 'Architecture Intelligence',
            meta: [
                { name: 'viewport', content: 'width=device-width, initial-scale=1' },
                {
                    name: 'description',
                    content:
                        'Webanwendung zur KI-gestützten Erfassung, Auswertung und Dokumentation von Architekturentscheidungen',
                },
            ],
            link: [
                { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
                {
                    rel: 'stylesheet',
                    href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap',
                },
            ],
        },
    },

    css: ['primeicons/primeicons.css'],

    postcss: { plugins: { '@tailwindcss/postcss': {}, autoprefixer: {} } },

    tailwindcss: { viewer: false },

    vite: {
        css: {
            preprocessorOptions: { scss: { api: 'modern' } },
        },
    },

    primevue: {
        autoImport: true,
        usePrimeVue: true,
        transpile: true,
        options: {
            theme: {
                ripple: true,
                preset: definePreset(Lara, {
                    semantic: {
                        primary: {
                            50: '{blue.50}',
                            100: '{blue.100}',
                            200: '{blue.200}',
                            300: '{blue.300}',
                            400: '{blue.400}',
                            500: '{blue.500}',
                            600: '{blue.600}',
                            700: '{blue.700}',
                            800: '{blue.800}',
                            900: '{blue.900}',
                            950: '{blue.950}',
                        },
                    },
                }),
                options: { darkModeSelector: '.p-dark', cssLayer: false },
            },
        },
    },
})