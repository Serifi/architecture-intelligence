import { defineStore } from 'pinia'
import { api, apiUrl } from '~/utils/api'
import { runStoreRequest } from '~/utils/requester'
import { useNotify } from '~/composables/useNotify'
import { errorMessage } from '~/utils/messages'

export const useStatusStore = defineStore('status', {
    state: () => ({
        statuses: [],
        loading: false,
        error: null,
    }),

    getters: {
        sortedStatuses(state) {
            const list = [...(state.statuses || [])]
            return list.sort((a, b) => {
                const posA = a?.position ?? 0
                const posB = b?.position ?? 0
                if (posA === posB) return (a?.statusID ?? 0) - (b?.statusID ?? 0)
                return posA - posB
            })
        },
    },

    actions: {
        async fetchStatuses() {
            return runStoreRequest(
                this,
                async () => {
                    const res = await api.get(apiUrl('/statuses/'))
                    this.statuses = res.data || []
                    return this.statuses
                },
                {
                    errorKey: 'notify.statuses.fetchError',
                    errorFallback: 'Failed to load statuses',
                },
            )
        },

        setLocalStatuses(newList) {
            this.statuses = newList || []
        },

        async saveStatuses(updatedStatuses) {
            const notify = useNotify()
            this.error = null

            const current = this.statuses || []
            const next = updatedStatuses || []

            const currentIds = new Set(current.filter((s) => s?.statusID != null).map((s) => s.statusID))
            const nextIds = new Set(next.filter((s) => s?.statusID != null).map((s) => s.statusID))
            const toDelete = [...currentIds].filter((id) => !nextIds.has(id))

            const fail = (err, key, fallback) => {
                const msg = errorMessage(err) ?? notify.t(key, fallback)
                this.error = msg
                notify.error({ message: msg, key, fallback })
                throw err
            }

            try {
                for (const id of toDelete) {
                    try {
                        await api.delete(apiUrl(`/statuses/${id}`))
                    } catch (err) {
                        fail(err, 'notify.statuses.deleteError', 'Request failed')
                    }
                }

                for (const s of next) {
                    const payload = {
                        name: s.name,
                        color: s.color,
                        position: s.position,
                    }

                    try {
                        if (s.statusID != null) await api.put(apiUrl(`/statuses/${s.statusID}`), payload)
                        else await api.post(apiUrl('/statuses/'), payload)
                    } catch (err) {
                        fail(err, 'notify.statuses.saveError', 'Request failed')
                    }
                }

                await this.fetchStatuses()

                notify.success({
                    key: 'notify.statuses.saveSuccess',
                    fallback: 'Statuses updated successfully',
                })

                return true
            } catch {
                return false
            }
        },
    },
})