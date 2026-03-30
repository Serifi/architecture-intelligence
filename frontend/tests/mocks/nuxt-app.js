import { ref } from 'vue'
import { vi } from 'vitest'

const mockT = (key, fallback) => fallback || key

const mockNuxtApp = {
    $i18n: {
        t: mockT,
        locale: ref('en'),
    },
    $toast: {
        add: vi.fn(),
    },
    $t: mockT,
    $locale: ref('en'),
    $setLocale: vi.fn(),
}

export function useNuxtApp() {
    return mockNuxtApp
}

export function useRouter() {
    return {
        push: vi.fn(),
        replace: vi.fn(),
        go: vi.fn(),
        back: vi.fn(),
        forward: vi.fn(),
        currentRoute: ref({ path: '/', query: {}, params: {} }),
    }
}

export function useRoute() {
    return {
        path: '/',
        query: {},
        params: {},
        hash: '',
        fullPath: '/',
        matched: [],
        meta: {},
        name: undefined,
    }
}

export function navigateTo(to, options) {
    return Promise.resolve()
}

export function defineNuxtComponent(options) {
    return options
}

export function useRuntimeConfig() {
    return {
        public: {
            apiBase: 'http://localhost:8000',
        },
    }
}
