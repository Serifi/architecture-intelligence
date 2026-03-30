import {defineStore} from 'pinia'
import {api, apiUrl} from '~/utils/api'
import {backendMessage, errorMessage} from '~/utils/messages'
import {useNotify} from '~/composables/useNotify'
import {useAuthStore} from '~/stores/auth'

function normalizeFieldValues(source, fallback = []) {
    const list = Array.isArray(source?.fieldValues)
        ? source.fieldValues
        : Array.isArray(source?.fields)
            ? source.fields
            : fallback

    return (list || []).map((f) => ({
        fieldID: f.fieldID,
        value: f.value ?? '',
    }))
}

export const useDecisionStore = defineStore('decision', {
    state: () => ({
        decisions: [],
        aiSuggestion: null,
        aiAlternatives: [],
        loading: false,
        aiLoading: false,
        aiAlternativesLoading: false,
        chatLoading: false,
        error: null,
    }),

    getters: {
        decisionsByStatus(state) {
            return (statusIdOrNull, searchTerm = '') => {
                const term = String(searchTerm || '').toLowerCase().trim()

                return (state.decisions || []).filter((d) => {
                    const matchesStatus =
                        statusIdOrNull == null ? d?.statusID == null : d?.statusID === statusIdOrNull

                    const matchesSearch =
                        !term || String(d?.title || '').toLowerCase().includes(term)

                    return matchesStatus && matchesSearch
                })
            }
        },
    },

    actions: {
        requireUserId() {
            const notify = useNotify()
            const userId = useAuthStore().user?.userID ?? null
            if (userId) return userId

            const msg = notify.t('notify.auth.notLoggedIn', 'Kein Benutzer angemeldet.')
            this.error = msg
            notify.error({key: 'notify.auth.notLoggedIn', fallback: 'Kein Benutzer angemeldet.'})
            throw new Error(msg)
        },

        async fetchDecisions(projectId) {
            const notify = useNotify()
            const userId = useAuthStore().user?.userID ?? null

            this.loading = true
            this.error = null

            try {
                if (!userId) {
                    this.decisions = []
                    return this.decisions
                }

                const res = await api.get(apiUrl('/decisions/'), {
                    params: {project_id: projectId, user_id: userId},
                })

                this.decisions = (res.data || []).map((d) => ({
                    decisionID: d.decisionID,
                    title: d.title,
                    lastUpdated: d.lastUpdated,
                    statusID: d.status?.statusID ?? d.statusID ?? null,
                    statusName: d.status?.name ?? d.statusName ?? null,
                }))

                return this.decisions
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.decisions.fetchError', 'Failed to load decisions')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.decisions.fetchError',
                    fallback: 'Failed to load decisions',
                })

                return []
            } finally {
                this.loading = false
            }
        },

        async fetchDecision(decisionId) {
            const notify = useNotify()
            this.loading = true
            this.error = null

            try {
                const res = await api.get(apiUrl(`/decisions/${decisionId}`))
                return res.data
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.decisions.fetchOneError', 'Failed to load decision')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.decisions.fetchOneError',
                    fallback: 'Failed to load decision',
                })

                throw err
            } finally {
                this.loading = false
            }
        },

        async updateDecisionFields(decisionId, fieldValues, options = {}) {
            const notify = useNotify()
            this.error = null

            try {
                const userId = this.requireUserId()

                const payload = {
                    fieldValues,
                    userID: userId,
                }

                if (options?.title != null) payload.title = String(options.title)

                const res = await api.put(apiUrl(`/decisions/${decisionId}`), payload)

                notify.success({
                    message: backendMessage(res.data),
                    key: 'notify.decisions.updateFieldsSuccess',
                    fallback: 'Architecture decision was updated successfully.',
                })

                return res.data?.decision ?? res.data
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.decisions.updateFieldsError', 'Failed to update decision fields')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.decisions.updateFieldsError',
                    fallback: 'Failed to update decision fields',
                })

                throw err
            }
        },

        setLocalStatus(decisionId, statusId, statusName = null) {
            const idx = (this.decisions || []).findIndex((d) => d?.decisionID === decisionId)
            if (idx === -1) return
            this.decisions[idx] = {...this.decisions[idx], statusID: statusId, statusName}
        },

        async updateDecisionStatus(decisionId, statusId) {
            const notify = useNotify()
            this.error = null

            try {
                const userId = useAuthStore().user?.userID ?? null

                const res = await api.put(apiUrl(`/decisions/${decisionId}`), {
                    statusID: statusId,
                    userID: userId,
                })

                notify.success({
                    message: backendMessage(res.data),
                    key: 'notify.decisions.updateStatusSuccess',
                    fallback: 'Architecture decision was updated successfully.',
                })

                return res.data?.decision ?? res.data
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.decisions.updateStatusError', 'Failed to update decision status')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.decisions.updateStatusError',
                    fallback: 'Failed to update decision status',
                })

                throw err
            }
        },

        async deleteDecision(decisionId) {
            const notify = useNotify()
            this.error = null

            try {
                const userId = useAuthStore().user?.userID ?? null

                await api.delete(apiUrl(`/decisions/${decisionId}`), {
                    params: {user_id: userId},
                })

                notify.success({
                    key: 'notify.decisions.deleteSuccess',
                    fallback: 'Architecture decision was deleted successfully.',
                })

                this.decisions = (this.decisions || []).filter((d) => d?.decisionID !== decisionId)
                return true
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.decisions.deleteError', 'Failed to delete architecture decision')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.decisions.deleteError',
                    fallback: 'Failed to delete architecture decision',
                })

                throw err
            }
        },

        async reassignDecisions(fromStatusId, toStatusId) {
            if (fromStatusId == null || toStatusId == null) return

            const userId = useAuthStore().user?.userID ?? null
            const affected = (this.decisions || []).filter((d) => d?.statusID === fromStatusId)

            this.decisions = (this.decisions || []).map((d) =>
                d?.statusID === fromStatusId ? {...d, statusID: toStatusId} : d,
            )

            await Promise.allSettled(
                affected.map((d) =>
                    api.put(apiUrl(`/decisions/${d.decisionID}`), {
                        statusID: toStatusId,
                        userID: userId,
                    }),
                ),
            )
        },

        async generateDecisionWithAI({projectId, templateId, prompt}) {
            const notify = useNotify()
            this.aiLoading = true
            this.error = null

            try {
                const res = await api.post(apiUrl('/decisions/ai/suggestion'), {
                    projectID: projectId,
                    templateID: templateId,
                    prompt,
                })

                const raw = res.data || {}
                const resolvedTemplateId = raw.templateID != null ? raw.templateID : templateId

                this.aiSuggestion = {
                    templateID: resolvedTemplateId,
                    title:
                        raw.title ||
                        notify.t('notify.decisions.ai.defaultTitle', 'AI-generierte Architekturentscheidung'),
                    fieldValues: normalizeFieldValues(raw),
                    prompt,
                }

                this.aiAlternatives = []

                notify.success({
                    message: backendMessage(res.data),
                    key: 'notify.decisions.ai.success',
                    fallback: 'Architekturvorschlag wurde erfolgreich generiert.',
                })

                return this.aiSuggestion
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.decisions.ai.error', 'Failed to generate architecture decision with AI')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.decisions.ai.error',
                    fallback: 'Failed to generate architecture decision with AI',
                })

                throw err
            } finally {
                this.aiLoading = false
            }
        },

        async generateAlternativeDecisionsWithAI(requestPayload) {
            const notify = useNotify()
            this.aiAlternativesLoading = true
            this.error = null

            try {
                const res = await api.post(apiUrl('/decisions/ai/alternatives'), requestPayload)

                const raw = res.data || {}
                const alternativesRaw = raw.alternatives || raw.alternativeSuggestions || []
                const prompt = requestPayload?.prompt ?? requestPayload?.base?.prompt ?? ''

                this.aiAlternatives = (alternativesRaw || []).map((alt) => {
                    const tplId = alt.templateID != null ? alt.templateID : requestPayload?.templateID

                    return {
                        templateID: tplId,
                        title:
                            alt.title ||
                            notify.t('notify.decisions.ai.altDefaultTitle', 'Alternative Architekturentscheidung'),
                        fieldValues: normalizeFieldValues(alt),
                        prompt,
                    }
                })

                notify.success({
                    message: backendMessage(res.data),
                    key: 'notify.decisions.ai.altSuccess',
                    fallback: 'Alternative Architekturvorschläge wurden erfolgreich generiert.',
                })

                return this.aiAlternatives
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t(
                        'notify.decisions.ai.altError',
                        'Failed to generate alternative architecture decisions with AI',
                    )

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.decisions.ai.altError',
                    fallback: 'Failed to generate alternative architecture decisions with AI',
                })

                throw err
            } finally {
                this.aiAlternativesLoading = false
            }
        },

        async createDecisionFromSuggestion({projectId, suggestion, templateId}) {
            const notify = useNotify()
            this.error = null

            function isDuplicateTitleError(err) {
                const status = err?.response?.status ?? null
                const raw =
                    err?.response?.data?.message ??
                    err?.response?.data?.error ??
                    err?.response?.data ??
                    err?.message ??
                    ''

                const msg = String(raw || '').toLowerCase()

                return (
                    status === 409 ||
                    msg.includes('already exists') ||
                    msg.includes('exists already') ||
                    msg.includes('duplicate') ||
                    msg.includes('unique') ||
                    msg.includes('conflict')
                )
            }

            function withSuffix(base, n) {
                const t = String(base || '').trim()
                return n <= 1 ? t : `${t} ${n}`
            }

            try {
                const userId = this.requireUserId()

                const effectiveTemplateId =
                    templateId || suggestion?.templateID || suggestion?.template?.templateID

                if (!effectiveTemplateId) {
                    const msg = notify.t(
                        'notify.decisions.templateMissing',
                        'TemplateID fehlt für die Architekturentscheidung.',
                    )
                    this.error = msg
                    notify.error({
                        key: 'notify.decisions.templateMissing',
                        fallback: 'TemplateID fehlt für die Architekturentscheidung.',
                    })
                    throw new Error(msg)
                }

                const baseTitle =
                    suggestion?.title ||
                    notify.t('notify.decisions.defaultCreateTitle', 'Architekturentscheidung – {qa}', {
                        qa: suggestion?.qualityAttribute || notify.t('notify.decisions.noTitle', 'ohne Titel'),
                    })

                const maxAttempts = 50
                let lastErr = null

                for (let attempt = 1; attempt <= maxAttempts; attempt++) {
                    const title = withSuffix(baseTitle, attempt)

                    try {
                        const res = await api.post(apiUrl('/decisions/'), {
                            projectID: projectId,
                            templateID: effectiveTemplateId,
                            title,
                            fieldValues: normalizeFieldValues(suggestion, suggestion?.fieldValues || []),
                            userID: userId,
                        })

                        const decision = res.data?.decision ?? res.data

                        notify.success({
                            message: backendMessage(res.data),
                            key: 'notify.decisions.createSuccess',
                            fallback: 'Architekturentscheidung wurde erstellt.',
                        })

                        if (decision?.decisionID) {
                            this.decisions.push({
                                decisionID: decision.decisionID,
                                title: decision.title,
                                lastUpdated: decision.lastUpdated,
                                statusID: decision.status?.statusID ?? decision.statusID ?? null,
                                statusName: decision.status?.name ?? decision.statusName ?? null,
                            })
                        }

                        return decision
                    } catch (err) {
                        lastErr = err
                        if (isDuplicateTitleError(err) && attempt < maxAttempts) {
                            continue
                        }
                        throw err
                    }
                }

                throw lastErr || new Error('Create decision failed.')
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t(
                        'notify.decisions.createError',
                        'Failed to create architecture decision from suggestion',
                    )

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.decisions.createError',
                    fallback: 'Failed to create architecture decision from suggestion',
                })

                throw err
            }
        },

        async chatAboutDecision(projectId, messages, suggestion = null) {
            const notify = useNotify()
            this.chatLoading = true
            this.error = null

            try {
                const payload = {projectID: projectId, messages}
                if (suggestion) payload.suggestion = suggestion

                const res = await api.post(apiUrl('/decisions/ai/chat'), payload)
                if (typeof res.data === 'string') return res.data
                return res.data?.reply ?? ''
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.decisions.chatError', 'Chat mit Architekturentscheidung fehlgeschlagen.')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.decisions.chatError',
                    fallback: 'Chat mit Architekturentscheidung fehlgeschlagen.',
                })

                throw err
            } finally {
                this.chatLoading = false
            }
        },

        clearSuggestion() {
            this.aiSuggestion = null
            this.aiAlternatives = []
        },

        clearAlternatives() {
            this.aiAlternatives = []
        },
    },
})