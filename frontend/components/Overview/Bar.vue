<template>
  <div class="flex flex-col gap-4 md:flex-row md:items-center">
    <div class="flex items-center gap-4">
      <Icon icon="pi-arrow-left" @click="emit('back')" />

      <h1 class="flex-shrink-0 text-2xl font-semibold text-slate-900">
        {{ t('overview.title') }}
      </h1>

      <div class="ms-auto flex items-center gap-2 md:hidden">
        <Icon :icon="table ? 'pi-th-large' : 'pi-table'" @click="emit('toggle-view')" />
        <Icon icon="pi-sliders-h" @click="emit('manage-statuses')" />
        <Icon icon="pi-paperclip" @click="emit('attach-files')" />
      </div>
    </div>

    <div class="w-full md:flex-1">
      <div class="relative w-full md:max-w-xl md:mx-auto">
        <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-sm text-slate-400" />
        <input
            v-model="localSearch"
            type="text"
            :placeholder="t('overview.search.placeholder')"
            class="w-full rounded-lg border border-slate-300 bg-white px-4 py-2 pl-9 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
      </div>
    </div>

    <div class="hidden items-center gap-2 md:flex">
      <Icon :icon="table ? 'pi-th-large' : 'pi-table'" @click="emit('toggle-view')" />
      <Icon icon="pi-sliders-h" @click="emit('manage-statuses')" />
      <Icon icon="pi-paperclip" @click="emit('attach-files')" />
    </div>

    <div class="w-full md:w-auto">
      <Button variant="blue" icon="pi-plus" :label="t('overview.actions.createSuggestion')" class="w-full md:w-auto" @click="emit('create-decision')"/>
    </div>
  </div>
</template>

<script setup>
import Icon from '~/components/Icon.vue'
import Button from '~/components/Button.vue'
import { useI18n } from '~/composables/useI18n'
import { useVModel } from '~/composables/useVModel'

const props = defineProps({
  projectName: { type: String, default: '' },
  search: { type: String, default: '' },
  table: { type: Boolean, default: false },
})

const emit = defineEmits([
  'update:search',
  'back',
  'toggle-view',
  'manage-statuses',
  'attach-files',
  'create-decision',
])

const { t } = useI18n()

const localSearch = useVModel(
    props,
    'search',
    (_eventName, value) => emit('update:search', value),
)
</script>