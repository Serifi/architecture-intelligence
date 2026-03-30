<template>
  <section class="flex flex-col gap-4">
    <div class="grid grid-cols-1 items-end gap-4 md:grid-cols-3">
      <label class="flex flex-col gap-1 text-xs font-medium text-slate-700 md:col-span-2">
        {{ labelPrompt }}
        <InputText v-model="p" class="w-full text-sm" :placeholder="phPrompt" />
      </label>

      <label class="flex flex-col gap-1 text-xs font-medium text-slate-700">
        {{ labelTemplate }}
        <Select v-model="tid" :options="options" optionLabel="label" optionValue="value"
                :placeholder="phTemplate" class="w-full text-sm" :disabled="loading"/>
      </label>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  prompt: { type: String, default: '' },
  templateId: { type: [Number, String, null], default: null },
  options: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },

  labelPrompt: { type: String, required: true },
  labelTemplate: { type: String, required: true },
  phPrompt: { type: String, required: true },
  phTemplate: { type: String, required: true },
})

const emit = defineEmits(['update:prompt', 'update:templateId'])

const p = computed({
  get: () => props.prompt,
  set: (v) => emit('update:prompt', v),
})

const tid = computed({
  get: () => props.templateId,
  set: (v) => emit('update:templateId', v),
})
</script>