<template>
  <Dialog v-model:visible="visible" modal closable style="width: 64rem"
          :header="t('detail.deletion.title', 'Architekturentscheidung löschen?')">
    <div class="text-sm leading-relaxed text-gray-700">
      <p class="m-0">
        {{ t('detail.deletion.text.before', 'Soll die Architekturentscheidung') }}
        <span class="font-semibold text-gray-900">
          #{{ decision?.decisionID }} – {{ decision?.title }}
        </span>
        {{ t('detail.deletion.text.after', 'wirklich entfernt werden? Diese Aktion kann nicht rückgängig gemacht werden.') }}
      </p>
    </div>

    <template #footer>
      <div class="flex justify-end gap-3">
        <Button :label="t('detail.deletion.cancel', 'Abbrechen')" severity="secondary" text @click="visible = false"/>
        <Button :label="t('detail.deletion.confirm', 'Löschen')" severity="danger" :loading="loading" @click="emit('confirm')"/>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { useNotify } from '~/composables/useNotify'
import { useVModel } from '~/composables/useVModel'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  decision: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'confirm'])

const visible = useVModel(props, 'modelValue', emit)
const notify = useNotify()
const t = (key, fallback, params) => notify.t(key, fallback, params)
</script>