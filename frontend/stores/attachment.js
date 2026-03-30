import { defineStore } from 'pinia'
import { api, apiUrl } from '~/utils/api'
import { backendMessage, errorMessage } from '~/utils/messages'
import { useNotify } from '~/composables/useNotify'
import { useAuthStore } from '~/stores/auth'

export const useAttachmentStore = defineStore('attachment', {
    state: () => ({
        attachments: [],
        loading: false,
        uploading: false,
        deleting: false,
        error: null,
    }),

    getters: {
        sortedAttachments(state) {
            return [...(state.attachments || [])].sort((a, b) => {
                const da = new Date(a?.createdAt || 0).getTime()
                const db = new Date(b?.createdAt || 0).getTime()
                return db - da
            })
        },
    },

    actions: {
        requireUserId() {
            const notify = useNotify()
            const userId = useAuthStore().user?.userID ?? null
            if (userId) return userId

            const msg = notify.t('notify.auth.notAuthenticated', 'User not authenticated')
            this.error = msg
            notify.error({ key: 'notify.auth.notAuthenticated', fallback: 'User not authenticated' })
            throw new Error(msg)
        },

        async fetchAttachments(projectId) {
            const notify = useNotify()
            this.loading = true
            this.error = null

            try {
                const userId = useAuthStore().user?.userID ?? null
                if (!userId) {
                    this.attachments = []
                    this.error = notify.t('notify.auth.notAuthenticated', 'User not authenticated')
                    return this.attachments
                }

                const res = await api.get(apiUrl(`/projects/${projectId}/attachments/`), {
                    params: { user_id: userId },
                })

                this.attachments = res.data || []
                return this.attachments
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.attachments.fetchError', 'Failed to load attachments.')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.attachments.fetchError',
                    fallback: 'Failed to load attachments.',
                })
                throw err
            } finally {
                this.loading = false
            }
        },

        async uploadAttachment(projectId, file) {
            const notify = useNotify()
            this.uploading = true
            this.error = null

            try {
                const userId = this.requireUserId()

                const formData = new FormData()
                formData.append('file', file)

                const res = await api.post(apiUrl(`/projects/${projectId}/attachments/`), formData, {
                    params: { user_id: userId },
                    headers: { 'Content-Type': 'multipart/form-data' },
                })

                const created = res.data?.attachment ?? res.data
                if (created) this.attachments.push(created)

                notify.success({
                    message: backendMessage(res.data),
                    key: 'notify.attachments.uploadSuccess',
                    fallback: '"{filename}" wurde erfolgreich hochgeladen.',
                    params: { filename: file?.name ?? '' },
                })

                return created
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.attachments.uploadError', '"{filename}" konnte nicht hochgeladen werden.', {
                        filename: file?.name ?? '',
                    })

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.attachments.uploadError',
                    fallback: '"{filename}" konnte nicht hochgeladen werden.',
                    params: { filename: file?.name ?? '' },
                })

                throw err
            } finally {
                this.uploading = false
            }
        },

        async deleteAttachment(projectId, attachmentId) {
            const notify = useNotify()
            this.deleting = true
            this.error = null

            const attachment = (this.attachments || []).find((a) => a?.attachmentID === attachmentId)
            const filename = attachment?.originalFilename || 'Attachment'

            try {
                const userId = this.requireUserId()

                const res = await api.delete(apiUrl(`/projects/${projectId}/attachments/${attachmentId}`), {
                    params: { user_id: userId },
                })

                this.attachments = (this.attachments || []).filter((a) => a?.attachmentID !== attachmentId)

                notify.success({
                    message: backendMessage(res.data),
                    key: 'notify.attachments.deleteSuccess',
                    fallback: '"{filename}" wurde erfolgreich gelöscht.',
                    params: { filename },
                })

                return res.data
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.attachments.deleteError', '"{filename}" konnte nicht gelöscht werden.', {
                        filename,
                    })

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.attachments.deleteError',
                    fallback: '"{filename}" konnte nicht gelöscht werden.',
                    params: { filename },
                })

                throw err
            } finally {
                this.deleting = false
            }
        },
    },
})