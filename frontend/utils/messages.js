export function backendMessage(data) {
    if (!data) return null
    if (typeof data === 'string') return data
    if (typeof data !== 'object') return null
    return data.message ?? data.detail ?? null
}

export function errorMessage(err) {
    return backendMessage(err?.response?.data) ?? (err?.message ? String(err.message) : null)
}