import { computed } from 'vue'
import { useI18n } from '~/composables/useI18n'

function hasTimezoneInfo(s) {
  return /([zZ]|[+\-]\d{2}:\d{2})$/.test(String(s).trim())
}

export function normalizeIso(value) {
  if (!value) return value
  const s = String(value).trim()
  return hasTimezoneInfo(s) ? s : `${s}Z`
}

export function useDateFormat() {
  const { locale, t } = useI18n()

  const formatter = computed(() => {
    const lang = locale?.value || 'de'
    return new Intl.DateTimeFormat(lang, {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  })

  function formatDateTime(value) {
    if (!value) return ''
    const d = new Date(normalizeIso(value))
    if (Number.isNaN(d.getTime())) return String(value)
    return formatter.value.format(d)
  }

  function formatRelative(iso) {
    if (!iso) return ''

    const date = new Date(normalizeIso(iso))
    if (Number.isNaN(date.getTime())) return String(iso)

    const diffMin = Math.floor((Date.now() - date.getTime()) / 60000)

    if (diffMin < 1) return t('time.justNow')
    if (diffMin < 60) return t('time.minutesAgo', { n: diffMin })

    const diffH = Math.floor(diffMin / 60)
    if (diffH < 24) return t('time.hoursAgo', { n: diffH })

    const diffD = Math.floor(diffH / 24)
    return t('time.daysAgo', { n: diffD })
  }

  return { formatDateTime, formatRelative, normalizeIso }
}