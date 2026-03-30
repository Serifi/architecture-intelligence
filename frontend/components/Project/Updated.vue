<template>
  <div class="mt-4 text-xs font-normal leading-none text-gray-400">
    {{ prefix }} {{ label }}
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useDateFormat } from '~/composables/useDateFormat'

const props = defineProps({
  lastUpdated: { type: String, default: null },
})

const { t } = useI18n()
const { formatRelative } = useDateFormat()

const prefix = computed(() => t('projects.updatedPrefix'))

const now = ref(Date.now())
let timer = null

onMounted(() => {
  timer = setInterval(() => {
    now.value = Date.now()
  }, 60_000)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})

const label = computed(() => formatRelative(props.lastUpdated, now.value))
</script>