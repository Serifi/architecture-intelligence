import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useProjectStore } from '../../stores/project'
import { api } from '../../utils/api'

vi.mock('../../utils/api', () => ({
    api: {
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn()
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

vi.mock('../../stores/auth', () => ({
    useAuthStore: () => ({
        user: { userID: 1 }
    })
}))

describe('Project Store - Existing Features Bug Detection', () => {
    beforeEach(() => {
        setActivePinia(createPinia())
        vi.clearAllMocks()
    })

    it('should handle empty response from API correctly', async () => {
        const store = useProjectStore()
        api.get.mockResolvedValue({ data: null })

        await store.fetchProjects()

        expect(Array.isArray(store.projects)).toBe(true)
        expect(store.projects).toEqual([])
    })

    it('should maintain project order after multiple operations', async () => {
        const store = useProjectStore()

        store.projects = [
            { projectID: 3, name: 'C', position: 2 },
            { projectID: 1, name: 'A', position: 0 },
            { projectID: 2, name: 'B', position: 1 }
        ]

        const sorted = store.sortedProjects

        expect(sorted[0].projectID).toBe(1)
        expect(sorted[1].projectID).toBe(2)
        expect(sorted[2].projectID).toBe(3)
    })

    it('should handle projects with null position', async () => {
        const store = useProjectStore()

        store.projects = [
            { projectID: 2, name: 'B', position: 5 },
            { projectID: 1, name: 'A', position: null },
            { projectID: 3, name: 'C', position: undefined }
        ]

        const sorted = store.sortedProjects

        expect(sorted[0].position ?? 0).toBe(0)
        expect(sorted[1].position ?? 0).toBe(0)
        expect(sorted[2].position).toBe(5)
    })

    it('should not mutate original projects array in sortedProjects', async () => {
        const store = useProjectStore()

        const original = [
            { projectID: 2, name: 'B', position: 1 },
            { projectID: 1, name: 'A', position: 0 }
        ]

        store.projects = original

        const sorted = store.sortedProjects

        expect(store.projects[0].projectID).toBe(2)
        expect(store.projects[1].projectID).toBe(1)

        expect(sorted[0].projectID).toBe(1)
        expect(sorted[1].projectID).toBe(2)
    })

    it('should clear projects when user is not authenticated', async () => {
        const store = useProjectStore()

        vi.spyOn(store, 'userId').mockReturnValue(null)

        store.projects = [{ projectID: 1, name: 'Old' }]

        await store.fetchProjects()

        expect(store.projects).toEqual([])
        expect(api.get).not.toHaveBeenCalled()
    })
})
