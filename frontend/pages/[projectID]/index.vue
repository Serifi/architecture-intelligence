<template>
  <div class="flex min-h-screen flex-col bg-slate-100 font-sans text-gray-800">
    <Header :subtitle="project?.name || ''" />

    <main class="mx-auto flex w-full max-w-[96rem] flex-1 flex-col gap-6 p-4 md:p-8">
      <Bar :project-name="project?.name || ''" v-model:search="searchTerm" :table="showTableView"
           @back="goHome" @toggle-view="toggleTableView" @manage-statuses="onManageStatuses"
           @attach-files="onAttachFiles" @create-decision="onCreateDecision"/>

      <div class="h-[64vh] w-full">
        <Board v-if="!showTableView" :status-rows="statusRows" :first-status-id="firstStatusId"
               :loading="decisionsLoading || statusesLoading" :get-decisions="decisionsForStatus"
               :format-date="formatDateTime" :on-drop="onDrop" :on-drag-start="onDragStart"
               :on-drag-end="onDragEnd" :open-decision="openDecision"/>

        <Table v-else :items="filteredDecisions" :status-map="statusMap"
               :loading="decisionsLoading || statusesLoading" :format-date="formatDateTime"
               :open-decision="openDecision"/>
      </div>
    </main>

    <Upload v-model="showAttachDialog" :project-id="projectId" />
    <Status v-model="showStatusDialog" :statuses="sortedStatuses" @save="onSaveStatuses" @error="notifyError"/>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'

import Header from '~/components/Header.vue'
import Bar from '~/components/Overview/Bar.vue'
import Board from '~/components/Overview/Board.vue'
import Table from '~/components/Overview/Table.vue'
import Upload from '~/components/Overview/Upload.vue'
import Status from '~/components/Overview/Status.vue'

import { useProjectStore } from '~/stores/project'
import { useDecisionStore } from '~/stores/decision'
import { useStatusStore } from '~/stores/status'
import { useNotify } from '~/composables/useNotify'
import { useI18n } from '~/composables/useI18n'
import { useDateFormat } from '~/composables/useDateFormat'
import { errorMessage } from '~/utils/messages'

const { t } = useI18n()
const { formatDateTime } = useDateFormat()

const route = useRoute()
const router = useRouter()

const notify = useNotify()
const notifyError = (msg) => notify.error({ message: String(msg || '') })

const projectId = computed(() => Number(route.params.projectID))

const projectsStore = useProjectStore()
const { activeProject } = storeToRefs(projectsStore)

const decisionsStore = useDecisionStore()
const { decisions, loading: decisionsLoadingRef } = storeToRefs(decisionsStore)

const statusesStore = useStatusStore()
const { statuses, loading: statusesLoadingRef } = storeToRefs(statusesStore)

const searchTerm = ref('')
const draggedDecisionId = ref(null)
const showTableView = ref(false)
const showAttachDialog = ref(false)
const showStatusDialog = ref(false)

const project = computed(() => activeProject.value)
const decisionsLoading = computed(() => Boolean(decisionsLoadingRef.value))
const statusesLoading = computed(() => Boolean(statusesLoadingRef.value))

const sortedStatuses = computed(() => statusesStore.sortedStatuses)

const statusMap = computed(() => {
  const map = {}
  for (const s of statuses.value || []) map[s.statusID] = s
  return map
})

const firstStatusId = computed(() => sortedStatuses.value?.[0]?.statusID ?? null)

const filteredDecisions = computed(() => {
  const term = searchTerm.value.toLowerCase().trim()
  const list = decisions.value || []
  if (!term) return list
  return list.filter((d) => String(d.title || '').toLowerCase().includes(term))
})

function decisionsForStatus(statusId, isFirstColumn) {
  return filteredDecisions.value.filter((d) => {
    if (d.statusID === statusId) return true
    return Boolean(isFirstColumn) && d.statusID == null
  })
}

const statusRows = computed(() => {
  const items = sortedStatuses.value || []
  if (!items.length) return []

  const maxCols = 4
  if (items.length <= maxCols) return [items]

  const rows = []
  for (let i = 0; i < items.length; i += maxCols) rows.push(items.slice(i, i + maxCols))

  if (rows.length > 1 && rows[rows.length - 1].length === 1) {
    const last = rows.pop()
    rows[rows.length - 1] = rows[rows.length - 1].slice(0, -1)
    rows.push([...rows[rows.length - 1].slice(-1), ...last])
  }

  return rows
})

onMounted(async () => {
  await projectsStore.fetchProjectById(projectId.value)
  await Promise.all([statusesStore.fetchStatuses(), decisionsStore.fetchDecisions(projectId.value)])
})

function goHome() {
  router.push('/')
}

function toggleTableView() {
  showTableView.value = !showTableView.value
}

function onAttachFiles() {
  showAttachDialog.value = true
}

function onManageStatuses() {
  showStatusDialog.value = true
}

function onCreateDecision() {
  router.push(`/${projectId.value}/create`)
}

function openDecision(decisionId) {
  router.push(`/${projectId.value}/${decisionId}`)
}

function onDragStart(decisionId) {
  draggedDecisionId.value = decisionId
}

function onDragEnd() {
  draggedDecisionId.value = null
}

async function onDrop(targetStatusId) {
  if (!draggedDecisionId.value) return

  const decisionId = draggedDecisionId.value
  draggedDecisionId.value = null

  const before = (decisions.value || []).find((d) => d.decisionID === decisionId)
  const prevStatusId = before?.statusID ?? null

  const nextStatusId = targetStatusId ?? null
  if (prevStatusId === nextStatusId) return

  const statusObj = (statuses.value || []).find((s) => s.statusID === nextStatusId) || null
  const nextStatusName = statusObj?.name ?? null
  const prevStatusName = before?.statusName ?? null

  decisionsStore.setLocalStatus(decisionId, nextStatusId, nextStatusName)

  try {
    await decisionsStore.updateDecisionStatus(decisionId, nextStatusId)
  } catch (e) {
    decisionsStore.setLocalStatus(decisionId, prevStatusId, prevStatusName)
    notify.error({
      message: errorMessage(e) ?? t('overview.errors.updateDecisionStatus', 'Status konnte nicht aktualisiert werden.'),
    })
  }
}

function toPastelHex(raw) {
  const cleaned = String(raw || '').replace('#', '').trim()
  const base = cleaned.length === 3 ? cleaned.split('').map((c) => c + c).join('') : cleaned.padStart(6, '0').slice(0, 6)

  let r = parseInt(base.slice(0, 2), 16)
  let g = parseInt(base.slice(2, 4), 16)
  let b = parseInt(base.slice(4, 6), 16)

  const avg = (r + g + b) / 3
  if (avg >= 215) return `#${base.toLowerCase()}`

  const mix = 255
  const factor = 0.85
  r = Math.round(r * (1 - factor) + mix * factor)
  g = Math.round(g * (1 - factor) + mix * factor)
  b = Math.round(b * (1 - factor) + mix * factor)

  const toHex = (v) => v.toString(16).padStart(2, '0')
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`
}

async function onSaveStatuses({ items, reassignments }) {
  const normalized = (items || []).map((s, idx) => ({
    statusID: s.statusID || null,
    name: s.name,
    color: toPastelHex(s.colorRaw || 'e5e7eb'),
    position: idx,
  }))

  const ok = await statusesStore.saveStatuses(normalized)
  if (!ok) return

  for (const item of reassignments || []) {
    await decisionsStore.reassignDecisions(item.fromStatusId, item.toStatusId)
  }

  showStatusDialog.value = false
}
</script>

<style>
.p-datatable .p-datatable-thead > tr > th {
  background-color: #FFFFFF !important;
}
</style>