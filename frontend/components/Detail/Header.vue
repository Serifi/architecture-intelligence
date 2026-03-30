<template>
  <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between lg:gap-6">
    <div class="flex w-full flex-col gap-2">
      <div class="flex items-center gap-3">
        <Icon icon="pi-arrow-left" @click="emit('back')" />

        <div class="min-w-0 flex-1">
          <input v-if="isEditing" :value="title" type="text" spellcheck="false"
                 class="block w-full min-w-0 text-2xl font-semibold text-slate-900 bg-transparent border-0 outline-none ring-0 focus:outline-none focus:ring-0 p-0"
                 :placeholder="t('detail.header.titlePlaceholder', 'Titel eingeben...')"
                 @input="emit('update:title', $event.target.value)"/>

          <h1 v-else class="text-2xl font-semibold text-slate-900">
            {{ titleText }}
          </h1>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-3 text-xs text-slate-500">
        <span v-if="statusName" class="inline-flex items-center gap-1 rounded-full bg-slate-200 px-2 py-1 text-[11px] font-medium text-slate-700">
          <span class="h-1.5 w-1.5 rounded-full bg-emerald-500" />
          {{ statusName }}
        </span>

        <span v-if="decision">
          {{ t('detail.header.idPrefix', 'ID:') }} {{ decision?.decisionID }}
        </span>
        <span v-if="decision">
          {{ t('detail.header.createdPrefix', 'Erstellt:') }} {{ formatDateTime(decision?.createdAt) }}
        </span>
        <span v-if="decision">
          {{ t('detail.header.updatedPrefix', 'Aktualisiert:') }} {{ formatDateTime(decision?.lastUpdated) }}
        </span>
        <span v-if="decision">
          {{ t('detail.header.requiredHint', '* Pflichtfeld') }}
        </span>
      </div>
    </div>

    <div class="flex flex-wrap items-center justify-end gap-3 lg:flex-nowrap">
      <Button :icon="historyButtonIcon" :label="historyButtonLabel" variant="white" @click="emit('toggle-history')"/>
      <Button :icon="isEditing ? 'pi-save' : 'pi-pencil'" :label="isEditing ? t('detail.header.save', 'Speichern') : t('detail.header.edit', 'Bearbeiten')"
              variant="blue" :disabled="disableSave" @click="emit('edit-or-save')"/>
      <Button icon="pi-trash" :label="t('detail.header.delete', 'Löschen')" variant="red" @click="emit('delete')"/>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNotify } from '~/composables/useNotify'
import { useDateFormat } from '~/composables/useDateFormat'
import Button from '~/components/Button.vue'
import Icon from "../Icon.vue"

const props = defineProps({
  decision: { type: Object, default: null },
  statusName: { type: String, default: null },
  isEditing: { type: Boolean, default: false },
  showHistory: { type: Boolean, default: false },
  disableSave: { type: Boolean, default: false },

  title: { type: String, default: '' },
})

const emit = defineEmits(['update:title', 'back', 'toggle-history', 'edit-or-save', 'delete'])

const notify = useNotify()
const t = (key, fallback, params) => notify.t(key, fallback, params)
const { formatDateTime } = useDateFormat()

const historyButtonLabel = computed(() =>
    props.showHistory ? t('detail.header.fields', 'Felder') : t('detail.header.history', 'History'),
)

const historyButtonIcon = computed(() => (props.showHistory ? 'pi-list' : 'pi-history'))

const titleText = computed(() => {
  const title = String(props.decision?.title ?? '').trim()
  return title.length ? title : t('detail.header.loadingTitle', 'Lade Entscheidung ...')
})
</script>