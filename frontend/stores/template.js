import { defineStore } from 'pinia'
import { api, apiUrl } from '~/utils/api'
import { runStoreRequest } from '~/utils/requester'

export const useTemplateStore = defineStore('template', {
    state: () => ({
        templates: [],
        loading: false,
        error: null,
    }),

    actions: {
        async fetchTemplates() {
            return runStoreRequest(
                this,
                async () => {
                    const res = await api.get(apiUrl('/templates/'))
                    this.templates = res.data || []
                    return this.templates
                },
                {
                    errorKey: 'notify.templates.fetchError',
                    errorFallback: 'Templates konnten nicht geladen werden.',
                },
            )
        },
    },
})