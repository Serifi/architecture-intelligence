<template>
  <Dialog v-model:visible="visible" modal closable :header="t('overview.status.title')" style="width: 64rem">
    <div class="divide-y divide-slate-200">
      <div v-for="status in editable" :key="status.statusID ?? `temp-${status._localKey}`" class="flex cursor-move items-center gap-3 py-2 first:pt-0 last:pb-0"
           draggable="true" @dragstart="onStatusDragStart(statusKey(status))" @dragover.prevent @drop="onStatusDrop(statusKey(status))">
        <ColorPicker v-model="status._colorRaw" format="hex" class="inline-block overflow-hidden rounded-md" />

        <InputText v-model="status.name" class="flex-1 bg-transparent !border-none !shadow-none focus:!outline-none focus:!ring-0"
                   :placeholder="t('overview.status.namePlaceholder')"/>

        <div class="ml-2 flex items-center gap-4">
          <button type="button" class="p-1" @click.stop="onDeleteStatus(status)">
            <i class="pi pi-trash cursor-pointer text-sm text-red-500" />
          </button>
          <span class="flex items-center text-slate-400">
            <i class="pi pi-bars" />
          </span>
        </div>
      </div>
    </div>

    <div class="mt-3 border-t border-slate-200 pt-3">
      <button type="button" @click="onAddStatus" class="flex h-10 w-full items-center justify-center rounded-lg
      text-xs font-medium text-slate-500 transition-colors hover:text-sky-600 cursor-pointer">
        <i class="pi pi-plus mr-2" />
        {{ t('overview.status.add') }}
      </button>
    </div>

    <template #footer>
      <div class="flex w-full items-center gap-3">
        <Message v-if="hasDuplicateStatusNames" severity="error" :closable="false">
          {{ t('overview.status.duplicateError') }}
        </Message>

        <div class="ms-auto flex gap-3">
          <Button :label="t('common.cancel')" severity="secondary" text @click="visible = false" />
          <Button :label="t('common.save')" severity="primary" :disabled="hasDuplicateStatusNames" @click="onSave" />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useVModel } from '~/composables/useVModel'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  statuses: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue', 'save', 'error'])

const { t } = useI18n()
const visible = useVModel(props, 'modelValue', emit)

const editable = ref([])
const draggedKey = ref(null)
const tempKey = ref(-1)
const deletedStatusReassignments = ref([])

watch(
    () => visible.value,
    (isOpen) => {
      if (isOpen) initFromProps()
      else deletedStatusReassignments.value = []
    },
    { immediate: true },
)

watch(
    () => props.statuses,
    () => {
      if (visible.value) initFromProps()
    },
)

function initFromProps() {
  editable.value = (props.statuses || []).map((s, idx) => ({
    statusID: s.statusID ?? null,
    name: s.name ?? '',
    position: s.position ?? idx,
    color: s.color || '#e5e7eb',
    _colorRaw: String(s.color || '#e5e7eb').replace('#', ''),
    _localKey: s.statusID ?? `local-${idx}`,
  }))
  deletedStatusReassignments.value = []
  draggedKey.value = null
}

function statusKey(status) {
  return status.statusID ?? status._localKey
}

const hasDuplicateStatusNames = computed(() => {
  const seen = new Set()
  for (const s of editable.value) {
    const name = String(s?.name || '').trim().toLowerCase()
    if (!name) continue
    if (seen.has(name)) return true
    seen.add(name)
  }
  return false
})

function onStatusDragStart(key) {
  draggedKey.value = key
}

function onStatusDrop(targetKey) {
  const fromKey = draggedKey.value
  if (!fromKey || fromKey === targetKey) return

  const fromIndex = editable.value.findIndex((s) => statusKey(s) === fromKey)
  const toIndex = editable.value.findIndex((s) => statusKey(s) === targetKey)
  if (fromIndex === -1 || toIndex === -1) return

  const [moved] = editable.value.splice(fromIndex, 1)
  editable.value.splice(toIndex, 0, moved)
  editable.value = editable.value.map((s, idx) => ({ ...s, position: idx }))
  draggedKey.value = null
}

function onAddStatus() {
  const key = tempKey.value--
  editable.value.push({
    statusID: null,
    name: t('overview.status.defaultName', 'Status'),
    position: editable.value.length,
    color: '#e5e7eb',
    _colorRaw: 'e5e7eb',
    _localKey: key,
  })
}

function onDeleteStatus(status) {
  if (editable.value.length <= 1) {
    emit('error', t('overview.status.minOne', 'Es muss mindestens ein Status vorhanden bleiben.'))
    return
  }

  const key = statusKey(status)
  const idx = editable.value.findIndex((s) => statusKey(s) === key)
  if (idx === -1) return

  if (status.statusID != null) {
    const neighbor = editable.value[idx - 1] || editable.value[idx + 1]
    if (neighbor?.statusID != null) {
      deletedStatusReassignments.value.push({
        fromStatusId: status.statusID,
        toStatusId: neighbor.statusID,
      })
    }
  }

  editable.value.splice(idx, 1)
  editable.value = editable.value.map((s, i) => ({ ...s, position: i }))
}

function onSave() {
  if (hasDuplicateStatusNames.value) return

  const items = editable.value.map((s, idx) => ({
    statusID: s.statusID ?? null,
    name: s.name,
    position: idx,
    colorRaw: s._colorRaw || 'e5e7eb',
  }))

  emit('save', { items, reassignments: deletedStatusReassignments.value })
  deletedStatusReassignments.value = []
}
</script>