<template>
  <div class="flex items-center gap-4">
    <Icon icon="pi-arrow-left" @click="$emit('back')" />

    <h1 class="flex-shrink-0 text-2xl font-semibold text-slate-900">
      {{ title }}
    </h1>

    <div class="flex-1" />

    <Button icon="pi-sparkles" :label="genLabel" variant="blue" :disabled="!canGenerate || loading" @click="$emit('generate')"/>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNotify } from '~/composables/useNotify'
import Icon from '~/components/Icon.vue'
import Button from '~/components/Button.vue'

defineProps({
  title: { type: String, required: true },
  canGenerate: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
})

defineEmits(['back', 'generate'])

const notify = useNotify()
const genLabel = computed(() => notify.t('create.actions.generate', 'Architekturvorschlag erstellen'))
</script>