import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useDecisionStore } from '../../stores/decision'
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

describe('Decision Store', () => {
    beforeEach(() => {
        setActivePinia(createPinia())
        vi.clearAllMocks()
    })

    it('fetchDecisions loads data into state', async () => {
        const store = useDecisionStore()
        const mockData = [{ decisionID: 1, title: 'Decision 1' }]
        api.get.mockResolvedValue({ data: mockData })

        await store.fetchDecisions(1)

        expect(store.decisions[0].decisionID).toBe(1)
        expect(store.decisions[0].title).toBe('Decision 1')
    })

    it('generateDecisionWithAI calls API and returns suggestion', async () => {
        const store = useDecisionStore()
        const mockSuggestion = { title: 'AI Suggested', fields: [] }
        api.post.mockResolvedValue({ data: mockSuggestion })

        const result = await store.generateDecisionWithAI({ projectId: 1, templateId: 1, prompt: 'test' })

        expect(result).toEqual(store.aiSuggestion)
        expect(api.post).toHaveBeenCalledWith('/decisions/ai/suggestion', expect.objectContaining({
            projectID: 1,
            templateID: 1,
            prompt: 'test'
        }))
    })
})
