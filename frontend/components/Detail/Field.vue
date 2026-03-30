<template>
  <section class="mt-2 flex flex-col gap-4">
    <div class="rounded-lg border border-slate-200 bg-white p-5">
      <div class="mb-1 flex items-center gap-2">
        <div class="text-sm font-semibold text-slate-900">
          {{ template.name }}
        </div>
      </div>

      <p v-if="template.description" class="mt-2 whitespace-pre-line text-sm text-slate-700">
        {{ template.description }}
      </p>
    </div>

    <Divider :label="t('detail.template.fieldsTitle', 'Felder')" />

    <div class="grid grid-cols-1 gap-4">
      <article v-for="field in template.fields" :key="field.fieldID" class="flex flex-col rounded-lg border bg-white p-4"
               :class="fieldBorderClass(field)" @click="emit('field-click', field.fieldID)">
        <header class="mb-2 flex items-center gap-2">
          <h2 class="text-sm font-semibold text-slate-900">
            {{ field.name }}
          </h2>
          <span v-if="field.isRequired" class="text-[10px] uppercase tracking-wide text-rose-500">
            *
          </span>
        </header>

        <div class="mt-1 flex-1 whitespace-pre-line text-sm text-slate-700">
          <template v-if="isEditing">
            <textarea :value="String(values[field.fieldID] ?? '')" rows="1"
                      class="m-0 h-full w-full resize-none border-none bg-transparent p-0 text-sm leading-normal text-slate-700 focus:outline-none focus:ring-0"
                      :placeholder="t('detail.template.placeholder', 'Text einfügen...')"
                      @input="onInput(field.fieldID, $event.target.value)"/>
          </template>

          <template v-else>
            <p v-if="fieldValueMap[field.fieldID]" class="m-0 whitespace-pre-line text-sm text-slate-700">
              {{ fieldValueMap[field.fieldID] }}
            </p>

            <p v-else class="m-0 text-sm italic text-slate-400">
              {{ t('detail.template.none', 'Keine Angabe') }}
            </p>
          </template>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import Divider from '~/components/Divider.vue'
import { useNotify } from '~/composables/useNotify'

const props = defineProps({
  template: { type: Object, required: true },
  fieldValueMap: { type: Object, default: () => ({}) },
  values: { type: Object, default: () => ({}) },
  isEditing: { type: Boolean, default: false },
  activeFieldId: { type: [Number, String, null], default: null },
})

const emit = defineEmits(['update:values', 'field-click'])

const notify = useNotify()
const t = (key, fallback, params) => notify.t(key, fallback, params)

function onInput(fieldId, value) {
  emit('update:values', { ...props.values, [fieldId]: value })
}

function fieldBorderClass(field) {
  if (!props.isEditing) return 'border-slate-200'

  const v = String(props.values[field.fieldID] ?? '').trim()
  const missingRequired = Boolean(field.isRequired) && v.length === 0

  if (missingRequired) return 'border-red-400'
  if (props.activeFieldId === field.fieldID) return 'border-sky-500 ring-1 ring-sky-200'
  return 'border-slate-200'
}
</script>