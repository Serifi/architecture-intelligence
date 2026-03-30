export const useNuxtApp = () => ({
    $t: (key) => key,
    $locale: { value: 'en' },
    $setLocale: () => { },
    vueApp: {
        config: {
            globalProperties: {
                $toast: {
                    add: () => { }
                }
            }
        }
    }
})
