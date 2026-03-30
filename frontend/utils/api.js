import axios from 'axios'

export const api = axios.create()

const RAW_BASE = 'http://localhost:8000'

export function apiBase() {
    return String(RAW_BASE).replace(/\/+$/, '')
}

export function apiUrl(path) {
    const p = String(path || '')
    const normalized = p.startsWith('/') ? p : `/${p}`
    return `${apiBase()}${normalized}`
}