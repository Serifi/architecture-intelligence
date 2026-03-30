import { describe, it, expect, vi } from 'vitest'
import { useDateFormat, normalizeIso } from '../../composables/useDateFormat'

vi.mock('../../composables/useI18n', () => ({
    useI18n: () => ({
        locale: { value: 'en' },
        t: (key, params) => {
            if (key === 'time.minutesAgo') return `${params.n} minutes ago`
            if (key === 'time.justNow') return 'Just now'
            return key
        }
    })
}))

describe('useDateFormat Composable', () => {
    it('normalizeIso adds Z if missing', () => {
        expect(normalizeIso('2025-12-26T10:00:00')).toBe('2025-12-26T10:00:00Z')
        expect(normalizeIso('2025-12-26T10:00:00Z')).toBe('2025-12-26T10:00:00Z')
    })

    it('formatRelative returns "Just now" for current time', () => {
        const { formatRelative } = useDateFormat()
        const now = new Date().toISOString()
        expect(formatRelative(now)).toBe('Just now')
    })

    it('formatRelative returns "x minutes ago"', () => {
        const { formatRelative } = useDateFormat()
        const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000).toISOString()
        expect(formatRelative(fiveMinutesAgo)).toBe('5 minutes ago')
    })

    it('formatDateTime returns formatted string', () => {
        const { formatDateTime } = useDateFormat()
        const date = '2025-12-26T10:00:00Z'
        const formatted = formatDateTime(date)

        expect(typeof formatted).toBe('string')
        expect(formatted.length).toBeGreaterThan(5)
    })
})
