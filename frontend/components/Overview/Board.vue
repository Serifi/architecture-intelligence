<template>
  <div class="h-full overflow-x-auto">
    <div class="flex h-full flex-col gap-4" :class="{ 'pointer-events-none opacity-50': loading }">
      <div v-for="row in statusRows" :key="row.map((s) => s.statusID).join('-')" class="flex flex-col gap-4 md:grid md:gap-4"
           :style="{ gridTemplateColumns: `repeat(${row.length}, minmax(18rem, 1fr))` }">
        <div v-for="status in row" :key="status.statusID" class="flex flex-col rounded-xl border bg-white"
             :style="{ borderColor: status.color || '#e5e7eb' }">
          <div class="mb-3 flex items-center justify-between rounded-t-xl px-4 py-2" :style="{ backgroundColor: status.color || '#e5e7eb' }">
            <h2 class="text-sm font-semibold text-slate-900">
              {{ status.name }}
            </h2>
            <span class="text-xs text-slate-800/80">
              {{ decisionsFor(status.statusID, status.statusID === firstStatusId).length }}
            </span>
          </div>

          <div class="flex-1 overflow-y-auto px-4 pb-4 pt-1" @dragover.prevent @dragenter.prevent @drop="onDrop(status.statusID)">
            <div v-for="d in decisionsFor(status.statusID, status.statusID === firstStatusId)" :key="d.decisionID"
                 class="mb-3 cursor-pointer rounded-lg border border-slate-200 bg-white px-4 py-3 shadow-sm transition active:scale-[0.99]"
                 draggable="true" @dragstart="onDragStart(d.decisionID)" @dragend="onDragEnd" @click="openDecision(d.decisionID)">
              <div class="mb-1 flex items-baseline gap-1">
                <span class="text-[10px] uppercase tracking-wide text-slate-400">
                  #{{ d.decisionID }}
                </span>
                <span class="truncate text-sm font-semibold text-slate-900" :title="d.title">
                  {{ d.title }}
                </span>
              </div>

              <div class="text-[11px] text-slate-400">
                {{ t('overview.board.lastUpdated') }} {{ formatDate(d.lastUpdated) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="mt-4 text-xs text-slate-400">
      {{ t('overview.loading.decisions') }}
    </div>
  </div>
</template>

<script setup>
import { useI18n } from '~/composables/useI18n'

const props = defineProps({
  statusRows: { type: Array, default: () => [] },
  firstStatusId: { type: [Number, String, null], default: null },
  loading: { type: Boolean, default: false },
  getDecisions: { type: Function, required: true },
  formatDate: { type: Function, required: true },
  onDrop: { type: Function, required: true },
  onDragStart: { type: Function, required: true },
  onDragEnd: { type: Function, required: true },
  openDecision: { type: Function, required: true },
})

const { t } = useI18n()

const decisionsFor = (statusId, isFirst) => props.getDecisions(statusId, isFirst)
</script>