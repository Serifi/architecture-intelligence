import { defineStore } from 'pinia'
import { api, apiUrl } from '~/utils/api'
import { backendMessage, errorMessage } from '~/utils/messages'
import { useNotify } from '~/composables/useNotify'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        token: null,
        loading: false,
        error: null,
    }),

    actions: {
        async register({ email, password }) {
            const notify = useNotify()
            this.loading = true
            this.error = null

            try {
                const res = await api.post(apiUrl('/users/'), { email, password })
                const user = res.data?.user ?? res.data

                this.user = user
                this.token = res.data?.token ?? null

                notify.success({
                    message: backendMessage(res.data),
                    key: 'notify.auth.register.success',
                    fallback: 'Registrierung erfolgreich.',
                })

                return user
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.auth.register.error', 'Registrierung fehlgeschlagen.')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.auth.register.error',
                    fallback: 'Registrierung fehlgeschlagen.',
                })

                throw err
            } finally {
                this.loading = false
            }
        },

        async login({ email, password }) {
            const notify = useNotify()
            this.loading = true
            this.error = null

            try {
                const res = await api.post(apiUrl('/users/login'), { email, password })
                const user = res.data?.user ?? res.data

                this.user = user
                this.token = res.data?.token ?? null

                notify.success({
                    message: backendMessage(res.data),
                    key: 'notify.auth.login.success',
                    fallback: 'Erfolgreich angemeldet.',
                })

                return user
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.auth.login.error', 'Anmeldung fehlgeschlagen.')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.auth.login.error',
                    fallback: 'Anmeldung fehlgeschlagen.',
                })

                throw err
            } finally {
                this.loading = false
            }
        },

        async updateUser({ email, password }) {
            const notify = useNotify()

            if (!this.user) {
                notify.error({ key: 'notify.auth.notLoggedIn', fallback: 'Kein Benutzer angemeldet.' })
                return null
            }

            this.loading = true
            this.error = null

            const payload = { email }
            if (password) payload.password = password

            try {
                const res = await api.put(apiUrl(`/users/${this.user.userID}`), payload)
                const updated = res.data?.user ?? res.data

                this.user = updated

                notify.success({
                    message: backendMessage(res.data),
                    key: 'notify.auth.profileUpdated',
                    fallback: 'Profil aktualisiert.',
                })

                return updated
            } catch (err) {
                const msg =
                    errorMessage(err) ??
                    notify.t('notify.auth.profileUpdateError', 'Profil konnte nicht aktualisiert werden.')

                this.error = msg
                notify.error({
                    message: msg,
                    key: 'notify.auth.profileUpdateError',
                    fallback: 'Profil konnte nicht aktualisiert werden.',
                })

                throw err
            } finally {
                this.loading = false
            }
        },

        logout() {
            this.user = null
            this.token = null
            this.error = null
        },
    },
})