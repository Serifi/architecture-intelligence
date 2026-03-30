<template>
  <section class="flex flex-col gap-4">
    <h1 class="text-2xl font-semibold text-slate-900">
      {{ suggestion?.title || fallbackTitle }}
    </h1>

    <div class="grid grid-cols-1 gap-4">
      <article v-for="field in fields" :key="field.fieldID" class="flex flex-col rounded-lg border border-slate-200 bg-white p-4">
        <header class="mb-2 flex items-center gap-2">
          <h2 class="text-sm font-semibold text-slate-900">
            {{ field.name }}
          </h2>
          <span v-if="field.isRequired" class="text-[10px] uppercase tracking-wide text-rose-500">*</span>
        </header>

        <p v-if="fieldValueMap[field.fieldID]" class="mt-1 whitespace-pre-line text-sm text-slate-700">
          {{ fieldValueMap[field.fieldID] }}
        </p>
        <p v-else class="mt-1 text-sm italic text-slate-400">
          {{ emptyLabel }}
        </p>
      </article>
    </div>

    <div class="flex justify-end gap-3 pt-2">
      <Button icon="pi-plus" :label="addLabel" variant="blue" :disabled="creating || !suggestion" @click="$emit('add')"/>
      <Button icon="pi-clone" :label="compareLabel" variant="green" :disabled="!canGenerate || aiAlternativesLoading || !suggestion" @click="$emit('alternatives')"/>
      <Button icon="pi-trash" :label="discardLabel" variant="red" @click="$emit('discard')"/>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useNotify } from '~/composables/useNotify'
import Button from '~/components/Button.vue'

const props = defineProps({
  suggestion: { type: Object, default: null },
  template: { type: Object, default: null },
  fieldValueMap: { type: Object, default: () => ({}) },
  creating: { type: Boolean, default: false },
  canGenerate: { type: Boolean, default: false },
  aiAlternativesLoading: { type: Boolean, default: false },
})

defineEmits(['add', 'alternatives', 'discard'])

const notify = useNotify()

const fields = computed(() => (props.template?.fields && Array.isArray(props.template.fields) ? props.template.fields : []))

const fallbackTitle = computed(() => notify.t('create.suggestion.fallbackTitle', 'Architekturvorschlag'))
const emptyLabel = computed(() => notify.t('create.suggestion.emptyField', 'Leer'))
const addLabel = computed(() => notify.t('create.actions.add', 'Architekturentscheidung hinzufügen'))
const compareLabel = computed(() => notify.t('create.actions.compare', 'Vorschläge vergleichen'))
const discardLabel = computed(() => notify.t('create.actions.discard', 'Löschen'))
</script>