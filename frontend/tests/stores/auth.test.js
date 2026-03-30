import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../../stores/auth'
import { api } from '../../utils/api'

vi.mock('../../utils/api', () => ({
    api: {
        get: vi.fn(),
        post: vi.fn()
    },
    apiUrl: (path) => path
}))

vi.mock('../../composables/useNotify', () => ({
    useNotify: () => ({
        t: (k, fallback) => fallback || k,
        success: vi.fn(),
        error: vi.fn()
    })
}))

describe('Auth Store', () => {
    beforeEach(() => {
        setActivePinia(createPinia())
        vi.clearAllMocks()
    })

    it('login sets user and token on success', async () => {
        const store = useAuthStore()
        const mockUser = { userID: 1, username: 'admin' }
        const mockToken = 'fake-jwt-token'

        api.post.mockResolvedValue({
            data: { user: mockUser, token: mockToken }
        })

        await store.login({ email: 'admin', password: 'password' })

        expect(store.user).toEqual(mockUser)
        expect(store.token).toBe(mockToken)
        expect(store.user).not.toBeNull()
    })

    it('logout clears user and token', () => {
        const store = useAuthStore()
        store.user = { userID: 1 }
        store.token = 'abc'

        store.logout()

        expect(store.user).toBeNull()
        expect(store.token).toBeNull()
    })
})
