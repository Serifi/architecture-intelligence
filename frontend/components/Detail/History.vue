<template>
  <section class="mt-2 flex flex-col gap-3">
    <div class="mb-2 flex items-center gap-3 text-[11px] text-slate-500">
      <div class="w-56">
        <IconField class="w-full">
          <InputIcon class="pi pi-search text-[11px] text-slate-400" />
          <InputText v-model="search" type="text" :placeholder="t('detail.history.searchPlaceholder', 'Suche...')"
                     class="w-full !h-8 !py-0 !text-[11px]"/>
        </IconField>
      </div>

      <Select v-model="timeFilter" :options="timeOptions" optionLabel="label" optionValue="value" showClear
              :placeholder="t('detail.history.timeRangePlaceholder', 'Zeitraum')" class="ms-auto h-8 w-64 text-[11px]"
              :pt="{ label: { class: '!pt-1.5 !text-[11px] flex items-center' } }"/>

      <Select v-if="typeOptions.length" v-model="typeFilter" :options="typeOptions" optionLabel="label" optionValue="value"
              showClear :placeholder="t('detail.history.typePlaceholder', 'Typ')" class="h-8 w-64 text-[11px]"
              :pt="{ label: { class: '!pt-1.5 !text-[11px] flex items-center' } }"/>
    </div>

    <div v-if="!filteredEntries.length" class="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-500">
      {{ t('detail.history.empty', 'History ist leer.') }}
    </div>

    <ul v-else class="space-y-3">
      <li v-for="entry in filteredEntries" :key="entry.historyID"
          class="flex justify-between gap-3 rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-700">
        <div>
          <div class="mb-1 text-xs text-slate-400">
            {{ formatDate(entry.createdAt) }}
          </div>
          <div class="font-medium">
            {{ entry.message || typeLabel(entry.eventType) || entry.eventType }}
          </div>
        </div>

        <button type="button" class="self-start flex items-center gap-1 text-xs text-slate-400 hover:text-red-500 cursor-pointer"
                @click="emit('delete-entry', entry.historyID)">
          <i class="pi pi-trash text-xs" />
        </button>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useNotify } from '~/composables/useNotify'

const props = defineProps({
  entries: { type: Array, default: () => [] },
  formatDate: { type: Function, required: true },
  normalizeIso: { type: Function, required: true },
})

const emit = defineEmits(['delete-entry'])

const notify = useNotify()
const t = (key, fallback, params) => notify.t(key, fallback, params)

const search = ref('')
const timeFilter = ref(null)
const typeFilter = ref(null)

const timeOptions = computed(() => [
  { label: t('detail.history.timeRanges.24h', '24 Stunden'), value: '24h' },
  { label: t('detail.history.timeRanges.7d', '7 Tage'), value: '7d' },
  { label: t('detail.history.timeRanges.30d', '30 Tage'), value: '30d' },
])

const eventTypeKeyMap = {
  CREATED: 'created',
  STATUS_CHANGED: 'statusChanged',
  FIELD_CHANGED: 'fieldChanged',
}

function typeKey(eventType) {
  if (!eventType) return 'unknown'
  return eventTypeKeyMap[eventType] || 'unknown'
}

function typeLabel(eventType) {
  if (!eventType) return ''
  return t(`detail.history.types.${typeKey(eventType)}`, eventType)
}

const typeOptions = computed(() => {
  const set = new Set()
  for (const e of props.entries || []) {
    if (e?.eventType) set.add(e.eventType)
  }
  return [...set].map((v) => ({ value: v, label: typeLabel(v) || v }))
})

const filteredEntries = computed(() => {
  const term = String(search.value || '').toLowerCase().trim()
  const now = Date.now()
  const dayMs = 24 * 60 * 60 * 1000

  const maxAgeMs =
      timeFilter.value === '24h'
          ? 1 * dayMs
          : timeFilter.value === '7d'
              ? 7 * dayMs
              : timeFilter.value === '30d'
                  ? 30 * dayMs
                  : null

  return (props.entries || []).filter((entry) => {
    if (!entry) return false

    if (typeFilter.value && entry.eventType !== typeFilter.value) return false

    if (maxAgeMs != null) {
      const created = new Date(props.normalizeIso(entry.createdAt)).getTime()
      if (!Number.isNaN(created) && now - created > maxAgeMs) return false
    }

    if (!term) return true

    const msg = String(entry.message || '').toLowerCase()
    const evtRaw = String(entry.eventType || '').toLowerCase()
    const evtLabel = String(typeLabel(entry.eventType) || '').toLowerCase()

    return msg.includes(term) || evtRaw.includes(term) || evtLabel.includes(term)
  })
})
</script>