import { defineStore } from 'pinia'
import { api, apiUrl } from '~/utils/api'
import { runStoreRequest } from '~/utils/requester'
import { backendMessage, errorMessage } from '~/utils/messages'
import { useNotify } from '~/composables/useNotify'

export const useHistoryStore = defineStore('history', {
    state: () => ({
        entries: [],
        loading: false,
        error: null,
    }),

    actions: {
        async fetchHistory(decisionId) {
            return runStoreRequest(
                this,
                async () => {
                    const res = await api.get(apiUrl('/decision-history'), {
                        params: { decision_id: decisionId },
                    })
                    this.entries = res.data || []
                    return this.entries
                },
                {
                    errorKey: 'notify.history.fetchError',
                    errorFallback: 'History konnte nicht geladen werden.',
                },
            )
        },

        async deleteEntry(historyId) {
            const notify = useNotify()
            this.error = null

            try {
                const res = await api.delete(apiUrl(`/decision-history/${historyId}`))

                notify.success({
                    message: backendMessage(res.data),
                    key: 'notify.history.deleteSuccess',
                    fallback: 'History-Eintrag wurde erfolgreich gelöscht.',
                })

                this.entries = (this.entries || []).filter((e) => e?.historyID !== historyId)
                return res.data
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.history.deleteError', 'History-Eintrag konnte nicht gelöscht werden.')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.history.deleteError',
                    fallback: 'History-Eintrag konnte nicht gelöscht werden.',
                })

                throw err
            }
        },
    },
})