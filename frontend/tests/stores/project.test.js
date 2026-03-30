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

describe('Project Store', () => {
    beforeEach(() => {
        setActivePinia(createPinia())
        vi.clearAllMocks()
    })

    it('fetchProjects sets projects state on success', async () => {
        const store = useProjectStore()
        const mockProjects = [{ projectID: 1, name: 'Project 1', position: 0 }]
        api.get.mockResolvedValue({ data: mockProjects })

        await store.fetchProjects()

        expect(store.projects).toEqual(mockProjects)
        expect(api.get).toHaveBeenCalledWith('/projects/', expect.anything())
    })

    it('createProject adds new project to state', async () => {
        const store = useProjectStore()
        const newProject = { name: 'New Project' }
        const responseProject = { projectID: 2, name: 'New Project', position: 1 }
        api.post.mockResolvedValue({ data: responseProject })

        await store.createProject(newProject)

        expect(store.projects).toContainEqual(responseProject)
    })

    it('sortedProjects getter returns projects ordered by position', () => {
        const store = useProjectStore()
        store.projects = [
            { projectID: 1, position: 2 },
            { projectID: 2, position: 0 },
            { projectID: 3, position: 1 }
        ]

        const sorted = store.sortedProjects
        expect(sorted[0].projectID).toBe(2)
        expect(sorted[1].projectID).toBe(3)
        expect(sorted[2].projectID).toBe(1)
    })

    it('deleteProject removes project from state', async () => {
        const store = useProjectStore()
        store.projects = [{ projectID: 1 }, { projectID: 2 }]
        api.delete.mockResolvedValue({ data: { message: 'Deleted' } })

        await store.deleteProject(1)

        expect(store.projects).toHaveLength(1)
        expect(store.projects[0].projectID).toBe(2)
    })
})
