import { ref, readonly } from 'vue'
import de from '~/locales/de.json'
import en from '~/locales/en.json'

const STORAGE_KEY = 'locale'
const DEFAULT_LOCALE = 'de'
const MESSAGES = { de, en }
const SUPPORTED = new Set(Object.keys(MESSAGES))

function resolvePath(obj, path) {
    const parts = String(path || '').split('.').filter(Boolean)
    let cur = obj
    for (const p of parts) {
        if (!cur || typeof cur !== 'object' || !(p in cur)) return null
        cur = cur[p]
    }
    return typeof cur === 'string' ? cur : null
}

function format(text, params) {
    if (!text || !params) return text
    let out = text
    for (const [k, v] of Object.entries(params)) {
        out = out.replaceAll(`{${k}}`, String(v))
    }
    return out
}

function readStoredLocale() {
    try {
        const v = localStorage.getItem(STORAGE_KEY)
        return SUPPORTED.has(v) ? v : null
    } catch {
        return null
    }
}

function storeLocale(locale) {
    try {
        localStorage.setItem(STORAGE_KEY, locale)
    } catch {}
}

export default defineNuxtPlugin(() => {
    const initial = readStoredLocale() ?? DEFAULT_LOCALE
    const locale = ref(initial)

    function setLocale(next) {
        const lang = SUPPORTED.has(next) ? next : DEFAULT_LOCALE
        if (locale.value === lang) return
        locale.value = lang
        storeLocale(lang)
    }

    function t(key, params) {
        const primary = resolvePath(MESSAGES[locale.value], key)
        const fallback = resolvePath(MESSAGES[DEFAULT_LOCALE], key)
        const resolved = primary ?? fallback ?? String(key)
        return format(resolved, params)
    }

    return {
        provide: {
            t,
            locale: readonly(locale),
            setLocale,
            i18n: { t, locale: readonly(locale), setLocale },
        },
    }
})