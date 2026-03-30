<template>
  <div class="flex justify-between gap-4">
    <div class="min-w-0 flex-1">
      <div class="flex min-w-0 items-center gap-2">
        <i :class="['pi', iconClass, 'shrink-0 leading-none text-gray-500']" />
        <div class="flex min-w-0 items-center gap-2">
          <span class="truncate font-semibold text-blue-700 hover:underline">
            {{ project.name }}
          </span>
          <Priority :priority="project.priority" class="shrink-0" />
        </div>
      </div>
    </div>

    <div class="mt-1 flex shrink-0 cursor-grab items-start text-gray-300 hover:text-gray-400 active:cursor-grabbing"
         @mousedown.stop @touchstart.stop>
      <i class="pi pi-bars leading-none" />
    </div>
  </div>

  <p class="mt-2 break-words text-sm leading-relaxed text-gray-600">
    {{ descriptionText }}
  </p>
</template>

<script setup>
import { computed } from 'vue'
import Priority from '~/components/Project/Priority.vue'
import { useI18n } from '~/composables/useI18n'

const props = defineProps({
  project: { type: Object, required: true },
})

const { t } = useI18n()

const iconClass = computed(() => {
  const raw = String(props.project.icon || '').trim()
  return raw ? `pi-${raw}` : 'pi-folder'
})

const descriptionText = computed(() => {
  const text = String(props.project.description || '').trim()
  return text || t('projects.card.noDescription')
})
</script>