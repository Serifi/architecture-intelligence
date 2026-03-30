<template>
  <div class="flex flex-col rounded-xl border border-slate-200 bg-white p-4" :class="{ 'pointer-events-none opacity-50': loading }">
    <DataTable :value="items" class="text-sm" resizable-columns paginator :rows="5" :rowsPerPageOptions="[5, 10, 20, 50]">
      <Column field="decisionID" :header="t('overview.table.id')" style="width: 6rem" sortable />
      <Column field="title" :header="t('overview.table.title')" sortable />

      <Column :header="t('overview.table.status')" style="width: 12rem">
        <template #body="{ data }">
          <Tag v-if="statusMap[data.statusID]" :value="statusMap[data.statusID].name" :style="{
              backgroundColor: statusMap[data.statusID].color || '#e5e7eb',
              borderColor: statusMap[data.statusID].color || '#e5e7eb'
            }" class="border !text-xs text-slate-900"/>
        </template>
      </Column>

      <Column :header="t('overview.table.lastUpdated')" style="width: 14rem">
        <template #body="{ data }">
          <span class="text-xs text-slate-500">
            {{ formatDate(data.lastUpdated) }}
          </span>
        </template>
      </Column>

      <Column header="" style="width: 4rem">
        <template #body="{ data }">
          <button type="button" @click="openDecision(data.decisionID)"
                  class="inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white text-slate-600 hover:bg-slate-50">
            <i class="pi pi-arrow-right text-xs" />
          </button>
        </template>
      </Column>
    </DataTable>

    <div v-if="loading" class="mt-2 text-xs text-slate-400">
      {{ t('overview.loading.decisions') }}
    </div>
  </div>
</template>

<script setup>
import { useI18n } from '~/composables/useI18n'

defineProps({
  items: { type: Array, default: () => [] },
  statusMap: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  formatDate: { type: Function, required: true },
  openDecision: { type: Function, required: true },
})

const { t } = useI18n()
</script>