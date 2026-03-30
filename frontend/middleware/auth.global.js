import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware((to) => {
    const auth = useAuthStore()
    const isAuthRoute = to.path === '/auth'
    const isLoggedIn = Boolean(auth.user)

    if (!isLoggedIn && !isAuthRoute) return navigateTo('/auth')
    if (isLoggedIn && isAuthRoute) return navigateTo('/')

    return undefined
})