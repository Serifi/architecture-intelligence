const keyFor = (id) => `store-${id}`

function safeParse(json) {
    try {
        return JSON.parse(json)
    } catch {
        return null
    }
}

export default defineNuxtPlugin((nuxtApp) => {
    nuxtApp.$pinia.use(({ store }) => {
        const key = keyFor(store.$id)

        try {
            const stored = sessionStorage.getItem(key)
            const parsed = stored ? safeParse(stored) : null
            if (parsed && typeof parsed === 'object') store.$patch(parsed)
        } catch {}

        store.$subscribe((_mutation, state) => {
            try {
                sessionStorage.setItem(key, JSON.stringify(state))
            } catch {}
        })
    })
})