import { useNuxtApp } from '#app'

export function useI18n() {
    const nuxtApp = useNuxtApp()

    return {
        t: nuxtApp.$t,
        locale: nuxtApp.$locale,
        setLocale: nuxtApp.$setLocale,
    }
}