import { vi } from 'vitest'
import { config } from '@vue/test-utils'

const mockT = (key, fallback) => fallback || key

global.navigateTo = vi.fn()
global.useNuxtApp = () => ({
    $i18n: {
        t: mockT,
        locale: { value: 'en' },
    },
    $toast: {
        add: vi.fn(),
    },
})

config.global.mocks = {
    $t: mockT,
    t: mockT,
}

config.global.provide = {
    t: mockT,
}

global.console = {
    ...console,
    warn: vi.fn(),
    error: vi.fn(),
}
