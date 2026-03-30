import { defineStore } from 'pinia'
import { api, apiUrl } from '~/utils/api'
import { runStoreRequest } from '~/utils/requester'
import { backendMessage, errorMessage } from '~/utils/messages'
import { useNotify } from '~/composables/useNotify'
import { useAuthStore } from '~/stores/auth'

export const useProjectStore = defineStore('project', {
    state: () => ({
        projects: [],
        activeProject: null,
        loading: false,
        error: null,
    }),

    getters: {
        sortedProjects(state) {
            return [...(state.projects || [])].sort(
                (a, b) => (a?.position ?? 0) - (b?.position ?? 0),
            )
        },
    },

    actions: {
        userId() {
            return useAuthStore().user?.userID ?? null
        },

        async fetchProjects() {
            return runStoreRequest(
                this,
                async () => {
                    const userId = this.userId()
                    if (!userId) {
                        this.projects = []
                        return this.projects
                    }

                    const res = await api.get(apiUrl('/projects/'), {
                        params: { user_id: userId },
                    })
                    this.projects = res.data || []
                    return this.projects
                },
                {
                    errorKey: 'notify.projects.fetchError',
                    errorFallback: 'Failed to load projects',
                },
            )
        },

        async fetchProjectById(id) {
            return runStoreRequest(
                this,
                async () => {
                    const notify = useNotify()
                    const userId = this.userId()

                    if (!userId) {
                        this.activeProject = null
                        this.error = notify.t('notify.auth.notAuthenticated', 'User not authenticated')
                        return null
                    }

                    const res = await api.get(apiUrl(`/projects/${id}`), {
                        params: { user_id: userId },
                    })

                    this.activeProject = res.data
                    return this.activeProject
                },
                {
                    errorKey: 'notify.projects.fetchOneError',
                    errorFallback: 'Failed to load project',
                },
            )
        },

        reorderProjects(newOrder) {
            this.projects = (newOrder || []).map((p, idx) => ({ ...p, position: idx }))
        },

        async persistOrder() {
            const notify = useNotify()
            const userId = this.userId()

            const payload = this.sortedProjects.map((p, idx) => ({
                projectID: p.projectID,
                position: idx,
            }))

            try {
                await api.put(
                    apiUrl('/projects/reorder'),
                    { items: payload },
                    { params: { user_id: userId } },
                )
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.projects.reorderError', 'Projects could not be reordered.')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.projects.reorderError',
                    fallback: 'Projects could not be reordered.',
                })

                throw err
            }
        },

        async createProject(payload) {
            const notify = useNotify()
            const userId = this.userId()
            this.error = null

            try {
                const res = await api.post(
                    apiUrl('/projects/'),
                    { ...payload, userID: userId },
                    { params: { user_id: userId } },
                )

                const created = res.data?.project ?? res.data
                this.projects.push(created)

                notify.success({
                    message: backendMessage(res.data),
                    key: 'notify.projects.createSuccess',
                    fallback: 'Project created successfully.',
                })

                return created
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.projects.createError', 'Project cannot be created.')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.projects.createError',
                    fallback: 'Project cannot be created.',
                })

                throw err
            }
        },

        async updateProject(id, payload) {
            const notify = useNotify()
            const userId = this.userId()
            this.error = null

            try {
                const res = await api.put(apiUrl(`/projects/${id}`), payload, {
                    params: { user_id: userId },
                })

                const updated = res.data?.project ?? res.data

                const idx = this.projects.findIndex((p) => p?.projectID === id)
                if (idx !== -1) this.projects[idx] = updated
                if (this.activeProject?.projectID === id) this.activeProject = updated

                notify.success({
                    message: backendMessage(res.data),
                    key: 'notify.projects.updateSuccess',
                    fallback: 'Project updated successfully.',
                })

                return updated
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.projects.updateError', 'Project cannot be updated.')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.projects.updateError',
                    fallback: 'Project cannot be updated.',
                })

                throw err
            }
        },

        async deleteProject(id) {
            const notify = useNotify()
            const userId = this.userId()
            this.error = null

            try {
                const res = await api.delete(apiUrl(`/projects/${id}`), {
                    params: { user_id: userId },
                })

                this.projects = (this.projects || []).filter((p) => p?.projectID !== id)
                if (this.activeProject?.projectID === id) this.activeProject = null

                notify.success({
                    message: backendMessage(res.data),
                    key: 'notify.projects.deleteSuccess',
                    fallback: 'Project deleted successfully.',
                })

                return res.data
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.projects.deleteError', 'Project cannot be deleted.')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.projects.deleteError',
                    fallback: 'Project cannot be deleted.',
                })

                throw err
            }
        },
    },
})