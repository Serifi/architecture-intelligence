<template>
  <div class="flex min-h-screen flex-col bg-slate-100 text-gray-800 font-sans">
    <Header :subtitle="project?.name || ''" />

    <main class="mx-auto flex w-full max-w-[96rem] flex-1 flex-col gap-6 p-8">
      <SecondaryHeader :decision="decision" :status-name="statusName" :is-editing="isEditing" :show-history="showHistory"
                       :disable-save="isEditing && hasRequiredError" :title="editableTitle" @update:title="editableTitle = $event"
                       @back="goBackToDecisions" @toggle-history="toggleHistory" @edit-or-save="onEditOrSave"
                       @delete="deleteDialogVisible = true"/>

      <Divider :label="showHistory ? t('detail.divider.history', 'History') : t('detail.divider.template', 'Template')" />

      <Field v-if="!showHistory && template" :template="template" :field-value-map="fieldValueMap"
             :is-editing="isEditing" :active-field-id="activeFieldId" v-model:values="editableValues" @field-click="onFieldClick"/>

      <History v-else-if="showHistory" :entries="historyEntries" :format-date="formatDateTime" :normalize-iso="normalizeIso" @delete-entry="onDeleteHistoryEntry"/>

    </main>

    <Deletion v-model="deleteDialogVisible" :decision="decision" :loading="deleteLoading" @confirm="confirmDelete" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'

import Header from '~/components/Header.vue'
import SecondaryHeader from '~/components/Detail/Header.vue'
import Field from '~/components/Detail/Field.vue'
import History from '~/components/Detail/History.vue'
import Deletion from '~/components/Detail/Deletion.vue'
import Divider from '~/components/Divider.vue'

import { useProjectStore } from '~/stores/project'
import { useHistoryStore } from '~/stores/history'
import { useDecisionStore } from '~/stores/decision'
import { useAuthStore } from '~/stores/auth'
import { useNotify } from '~/composables/useNotify'
import { useDateFormat, normalizeIso } from '~/composables/useDateFormat'
import { api, apiUrl } from '~/utils/api'
import { errorMessage } from '~/utils/messages'

const route = useRoute()
const router = useRouter()

const { formatDateTime } = useDateFormat()
const notify = useNotify()
const t = (key, fallback = '', params) => notify.t(key, fallback, params)

const auth = useAuthStore()

const projectsStore = useProjectStore()
const { activeProject } = storeToRefs(projectsStore)
const project = computed(() => activeProject.value)

const historyStore = useHistoryStore()
const { entries: historyEntries } = storeToRefs(historyStore)

const decisionsStore = useDecisionStore()

const projectId = computed(() => Number(route.params.projectID))
const decisionId = computed(() => Number(route.params.decisionID))

const decision = ref(null)
const template = ref(null)

const loading = ref(false)
const error = ref(null)

const deleteDialogVisible = ref(false)
const deleteLoading = ref(false)

const showHistory = ref(false)

const isEditing = ref(false)
const editableTitle = ref('')
const editableValues = ref({})
const activeFieldId = ref(null)

const statusName = computed(() => {
  const d = decision.value
  return d ? (d.status?.name ?? d.statusName ?? null) : null
})

const fieldValueMap = computed(() => {
  const map = {}
  const list = decision.value?.fieldValues
  if (!Array.isArray(list)) return map
  for (const fv of list) map[fv.fieldID] = fv.value
  return map
})

const hasRequiredError = computed(() => {
  if (!isEditing.value) return false
  const tpl = template.value
  if (!tpl || !Array.isArray(tpl.fields)) return false

  const missingRequiredField = tpl.fields.some((field) => {
    if (!field?.isRequired) return false
    const v = String(editableValues.value[field.fieldID] ?? '').trim()
    return v.length === 0
  })

  const missingTitle = String(editableTitle.value || '').trim().length === 0

  return missingRequiredField || missingTitle
})

onMounted(async () => {
  await loadAll()
})

async function loadAll() {
  try {
    loading.value = true
    error.value = null

    if (!Number.isFinite(decisionId.value)) {
      error.value = t('detail.errors.invalidUrlDecisionId', 'Ungültige URL – keine gültige Entscheidungs-ID.')
      return
    }

    if (!activeProject.value || activeProject.value.projectID !== projectId.value) {
      await projectsStore.fetchProjectById(projectId.value)
    }

    const decisionRes = await decisionsStore.fetchDecision(decisionId.value)
    decision.value = decisionRes
    editableTitle.value = String(decisionRes?.title ?? '')

    const templateId = decisionRes?.templateID ?? decisionRes?.template?.templateID ?? null
    if (templateId != null) {
      const res = await api.get(apiUrl(`/templates/${templateId}`))
      template.value = res.data
    } else {
      template.value = null
    }
  } catch (e) {
    error.value = errorMessage(e) ?? t('detail.errors.loadDecisionFailed', 'Fehler beim Laden der Architekturentscheidung.')
  } finally {
    loading.value = false
  }
}

function goBackToDecisions() {
  router.push(Number.isFinite(projectId.value) ? `/${projectId.value}` : '/')
}

async function toggleHistory() {
  if (!showHistory.value) {
    try {
      if (Number.isFinite(decisionId.value)) await historyStore.fetchHistory(decisionId.value)
    } catch (e) {
      notify.error({ message: errorMessage(e) ?? t('notify.history.fetchError', 'History konnte nicht geladen werden.') })
    }
    showHistory.value = true
    return
  }

  showHistory.value = false
}

function initEditableValues() {
  const tpl = template.value
  const values = {}

  editableTitle.value = String(decision.value?.title ?? '').trim()
  if (tpl && Array.isArray(tpl.fields)) {
    for (const field of tpl.fields) values[field.fieldID] = String(fieldValueMap.value[field.fieldID] ?? '')
  }

  editableTitle.value = String(decision.value?.title ?? '')
  editableValues.value = values
  activeFieldId.value = null
}

function onFieldClick(fieldId) {
  if (!isEditing.value) return
  activeFieldId.value = fieldId
}

async function onEditOrSave() {
  if (!isEditing.value) {
    initEditableValues()
    isEditing.value = true
    return
  }

  if (hasRequiredError.value) return
  await saveDecisionEdits()
}

async function saveDecisionEdits() {
  const d = decision.value
  const tpl = template.value
  if (!d || !tpl || !Array.isArray(tpl.fields)) return

  const userId = auth.user?.userID
  if (!userId) {
    error.value = t('detail.errors.notLoggedIn', 'Kein Benutzer angemeldet.')
    return
  }

  const titlePayload = String(editableTitle.value ?? '').trim()

  const fieldValuesPayload = tpl.fields.map((field) => ({
    fieldID: field.fieldID,
    value: String(editableValues.value[field.fieldID] ?? ''),
  }))

  try {
    const updated = await decisionsStore.updateDecisionFields(decisionId.value, fieldValuesPayload, { title: titlePayload })
    const newValues = updated?.fieldValues

    decision.value = {
      ...d,
      title: String(editableTitle.value ?? '').trim(),
      fieldValues: Array.isArray(newValues) ? newValues : fieldValuesPayload,
    }

    isEditing.value = false
    activeFieldId.value = null
  } catch (e) {
    error.value = decisionsStore.error ?? errorMessage(e) ?? t('detail.errors.saveFailed', 'Fehler beim Speichern der Änderungen.')
  }
}

async function confirmDelete() {
  if (!decision.value) return
  deleteLoading.value = true

  try {
    await decisionsStore.deleteDecision(decisionId.value)
    deleteDialogVisible.value = false
    router.push(Number.isFinite(projectId.value) ? `/${projectId.value}` : '/')
  } catch (e) {
    notify.error({ message: errorMessage(e) ?? t('notify.decisions.deleteError', 'Löschen fehlgeschlagen.') })
  } finally {
    deleteLoading.value = false
  }
}

async function onDeleteHistoryEntry(historyId) {
  try {
    await historyStore.deleteEntry(historyId)
  } catch (e) {
    notify.error({ message: errorMessage(e) ?? t('notify.history.deleteError', 'History-Eintrag konnte nicht gelöscht werden.') })
  }
}
</script>