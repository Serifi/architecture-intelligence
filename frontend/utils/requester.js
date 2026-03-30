import { useNotify } from '~/composables/useNotify'
import { errorMessage } from '~/utils/messages'

export async function runStoreRequest(store, fn, { errorKey, errorFallback } = {}) {
    const notify = useNotify()

    store.error = null
    store.loading = true

    try {
        return await fn()
    } catch (err) {
        const msg = errorMessage(err) ?? notify.t(errorKey, errorFallback || '')
        store.error = msg

        notify.error({
            message: msg,
            key: errorKey,
            fallback: errorFallback,
        })

        throw err
    } finally {
        store.loading = false
    }
}