import { useNuxtApp } from '#app'

function applyParams(text, params) {
    if (!text || !params) return text
    let out = String(text)
    for (const [k, v] of Object.entries(params)) {
        out = out.replaceAll(`{${k}}`, String(v))
    }
    return out
}

export function useNotify() {
    const nuxtApp = useNuxtApp()
    const toast = nuxtApp.vueApp?.config?.globalProperties?.$toast

    if (!toast || typeof toast.add !== 'function') {
        throw new Error('PrimeVue ToastService is not available.')
    }

    const translate = typeof nuxtApp.$t === 'function' ? nuxtApp.$t : null

    function t(key, fallback = '', params) {
        const translated = translate ? translate(key, params) : null
        const chosen = translated && translated !== key ? translated : (fallback || key)
        return applyParams(chosen, params)
    }

    function add(severity, options = {}) {
        const {
            message,
            key,
            fallback,
            params,
            summary,
            summaryKey,
            summaryFallback,
            life,
        } = options

        const resolvedSummary =
            summary ??
            (summaryKey ? t(summaryKey, summaryFallback || '', params) : (summaryFallback || ''))

        const resolvedDetail =
            message ??
            (key ? t(key, fallback || '', params) : (fallback || ''))

        toast.add({
            severity,
            summary: resolvedSummary,
            detail: resolvedDetail,
            life: typeof life === 'number' ? life : undefined,
        })
    }

    function success(options = {}) {
        add('success', {
            summaryKey: options.summaryKey ?? 'notify.summary.success',
            summaryFallback: options.summaryFallback ?? 'Erfolg',
            life: options.life ?? 3000,
            ...options,
        })
    }

    function error(options = {}) {
        add('error', {
            summaryKey: options.summaryKey ?? 'notify.summary.error',
            summaryFallback: options.summaryFallback ?? 'Fehler',
            life: options.life ?? 5000,
            ...options,
        })
    }

    const CRUD = {
        create: {
            okKey: 'notify.crud.create.success',
            okFallback: '{entity} wurde erfolgreich erstellt.',
            errKey: 'notify.crud.create.error',
            errFallback: '{entity}: Fehler beim Erstellen.',
        },
        update: {
            okKey: 'notify.crud.update.success',
            okFallback: '{entity} wurde erfolgreich aktualisiert.',
            errKey: 'notify.crud.update.error',
            errFallback: '{entity}: Fehler beim Aktualisieren.',
        },
        delete: {
            okKey: 'notify.crud.delete.success',
            okFallback: '{entity} wurde erfolgreich gelöscht.',
            errKey: 'notify.crud.delete.error',
            errFallback: '{entity}: Fehler beim Löschen.',
        },
        other: {
            okKey: 'notify.crud.other.success',
            okFallback: '{entity} wurde erfolgreich ausgeführt.',
            errKey: 'notify.crud.other.error',
            errFallback: '{entity}: Fehler bei der Aktion.',
        },
    }

    function successCrud(action, entityLabel = 'Eintrag', backendMsg = null) {
        const cfg = CRUD[action] || CRUD.other
        const detail = backendMsg ?? t(cfg.okKey, cfg.okFallback, { entity: entityLabel })

        success({
            message: detail,
            summaryKey: 'notify.crud.summary.success',
            summaryFallback: 'Aktion erfolgreich',
        })
    }

    function errorCrud(action, entityLabel = 'Eintrag', backendMsg = null, technical = null) {
        const cfg = CRUD[action] || CRUD.other
        const base = backendMsg ?? t(cfg.errKey, cfg.errFallback, { entity: entityLabel })
        const detail = technical ? `${base} (${technical})` : base
        error({ message: detail })
    }

    async function withCrudToast(promise, options = {}) {
        const { action = 'update', entityLabel = 'Eintrag', successMessage = null } = options

        try {
            const res = await promise
            successCrud(action, entityLabel, successMessage)
            return res
        } catch (e) {
            const technical =
                e && typeof e === 'object' && 'message' in e ? String(e.message) : null
            errorCrud(action, entityLabel, null, technical)
            throw e
        }
    }

    return { t, success, error, successCrud, errorCrud, withCrudToast }
}