<template>
  <span :class="['inline-flex items-center rounded-full border px-2 py-[2px] text-[10px] font-medium leading-none whitespace-nowrap', config.classes]" v-bind="$attrs">
    {{ config.label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '~/composables/useI18n'

const props = defineProps({
  priority: { type: String, required: true },
})

const { t } = useI18n()

const CONFIG = {
  low: { key: 'projects.priority.low', fallback: 'Low', classes: 'bg-yellow-50 border-yellow-300 text-yellow-800' },
  medium: { key: 'projects.priority.medium', fallback: 'Medium', classes: 'bg-orange-50 border-orange-300 text-orange-800' },
  high: { key: 'projects.priority.high', fallback: 'High', classes: 'bg-red-50 border-red-300 text-red-700' },
  critical: { key: 'projects.priority.critical', fallback: 'Critical', classes: 'bg-red-100 border-red-400 text-red-900' },
}

const DEFAULT = { key: 'common.unknown', fallback: 'Unknown', classes: 'bg-gray-50 border-gray-300 text-gray-600' }

const config = computed(() => {
  const key = String(props.priority || '').toLowerCase()
  const base = CONFIG[key] || DEFAULT
  return { ...base, label: t(base.key, base.fallback) }
})
</script>