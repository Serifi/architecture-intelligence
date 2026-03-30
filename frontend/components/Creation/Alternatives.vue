<template>
  <section v-if="visible" class="mt-2 flex flex-col gap-3">
    <div class="flex items-center gap-3">
      <div class="h-px flex-1 bg-slate-200" />
      <span class="text-[11px] uppercase tracking-wide text-slate-400">
        {{ title }}
      </span>
      <div class="h-px flex-1 bg-slate-200" />
    </div>

    <p class="text-[11px] text-slate-400">
      {{ hint }}
    </p>

    <div v-if="loading" class="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
      {{ loadingLabel }}
    </div>

    <div v-else-if="!items || items.length === 0" class="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">
      {{ emptyLabel }}
    </div>

    <div v-else class="flex flex-row gap-4">
      <article v-for="(alt, index) in items" :key="index" :class="[
          'flex cursor-pointer flex-col rounded-lg border border-slate-200 bg-white p-4 transition hover:border-sky-400',
          cardWidth(index),]" @click="$emit('select', index)">
        <header class="mb-2 flex items-center gap-2">
          <h3 class="text-sm font-semibold text-slate-900">
            {{ alt.title || `${fallbackAlt} ${index + 1}` }}
          </h3>
        </header>

        <div class="mt-2 flex max-h-64 flex-col gap-2 overflow-y-auto">
          <div v-for="fv in alt.fieldValues || []" :key="fv.fieldID" class="rounded-md border border-slate-100 p-2">
            <div class="text-xs font-semibold text-slate-600">
              {{ fieldMeta[fv.fieldID]?.name || `${fieldFallback} ${fv.fieldID}` }}
            </div>
            <div class="mt-1 whitespace-pre-line text-sm text-slate-700">
              {{ fv.value || dash }}
            </div>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useNotify } from '~/composables/useNotify'

const props = defineProps({
  visible: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  items: { type: Array, default: () => [] },
  fieldMeta: { type: Object, default: () => ({}) },
})

defineEmits(['select'])

const notify = useNotify()

const title = computed(() => notify.t('create.alternatives.title', 'Alternativen'))
const hint = computed(() => notify.t('create.alternatives.hint', 'Klicken, um diese Alternative als Vorschlag zu übernehmen.'))
const loadingLabel = computed(() => notify.t('create.alternatives.loading', 'Alternativen werden generiert ...'))
const emptyLabel = computed(() => notify.t('create.alternatives.empty', 'Bisher wurden keine Alternativvorschläge generiert oder gefunden.'))

const fallbackAlt = computed(() => notify.t('create.alternatives.fallbackAlt', 'Alternative'))
const fieldFallback = computed(() => notify.t('create.alternatives.fieldFallback', 'Feld'))
const dash = computed(() => notify.t('create.alternatives.dash', '—'))

function cardWidth(index) {
  const total = props.items?.length || 0
  if (total === 1) return 'w-full'
  if (total % 2 === 1 && index === total - 1) return 'w-full md:w-full'
  return 'w-full md:w-1/2'
}
</script>