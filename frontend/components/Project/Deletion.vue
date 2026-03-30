<template>
  <Dialog v-model:visible="visible" modal closable style="width: 64rem" :header="t('projects.delete.title')">
    <div class="flex items-center gap-6 text-sm leading-relaxed text-gray-700">
      <i class="pi pi-exclamation-triangle !text-[36px] text-red-500" />
      <p class="m-0">
        {{ t('projects.delete.text.before') }}
        <span class="font-semibold text-gray-900">{{ project?.name }}</span>
        {{ t('projects.delete.text.after') }}
      </p>
    </div>

    <template #footer>
      <div class="flex justify-end gap-3">
        <Button :label="t('common.cancel')" severity="secondary" text @click="visible = false" />
        <Button :label="t('common.delete')" severity="danger" @click="emit('confirm')" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { useI18n } from '~/composables/useI18n'
import { useVModel } from '~/composables/useVModel'

const props = defineProps({
  visible: { type: Boolean, default: false },
  project: { type: Object, default: null },
})

const emit = defineEmits(['update:visible', 'confirm'])

const { t } = useI18n()
const visible = useVModel(props, 'visible', emit)
</script>