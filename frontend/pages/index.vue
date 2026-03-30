<template>
  <div class="flex min-h-screen flex-col bg-slate-100 font-sans text-gray-800">
    <Header />

    <main class="mx-auto flex w-full max-w-[96rem] p-8">
      <List :projects="localOrder" :drag-over-id="dragOverId" :hover-color="hoverColor"
          @drag-start="onDragStart" @drag-over="onDragOver" @drop="onDrop"
          @request-delete="openDeleteDialog" @request-edit="openEditDialog"
          @hover-border="setHoverBorder" @hover-leave="clearHoverBorder"
          @card-click="goToDetails" @add-click="openCreateDialog"/>
    </main>

    <Deletion v-model:visible="deleteDialogVisible" :project="projectToDelete" @confirm="confirmDelete" />
    <Form v-model:visible="createDialogVisible" @create="handleCreate" />
    <Form v-model:visible="editDialogVisible" :project="editingProject" @save="handleEdit" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useProjectStore } from '~/stores/project'

import Header from '~/components/Header.vue'
import List from '~/components/Project/List.vue'
import Deletion from '~/components/Project/Deletion.vue'
import Form from '~/components/Project/Form.vue'

const router = useRouter()

const projectsStore = useProjectStore()
const { sortedProjects } = storeToRefs(projectsStore)

const localOrder = ref([])
const dragStartId = ref(null)
const dragOverId = ref(null)
const hoverColor = ref({})

const deleteDialogVisible = ref(false)
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)

const projectToDelete = ref(null)
const editingProject = ref(null)

const isDragging = computed(() => dragStartId.value != null)

onMounted(async () => {
  await projectsStore.fetchProjects()
  localOrder.value = [...sortedProjects.value]
})

watch(sortedProjects, (val) => {
  if (!isDragging.value) localOrder.value = [...val]
})

function goToDetails(id) {
  router.push(`/${id}`)
}

function onDragStart(id) {
  dragStartId.value = id
}

function onDragOver(id) {
  dragOverId.value = id
}

function onDrop(targetId) {
  const fromId = dragStartId.value
  dragStartId.value = null
  dragOverId.value = null

  if (fromId == null || targetId == null || fromId === targetId) return

  const next = [...localOrder.value]
  const fromIndex = next.findIndex((p) => p.projectID === fromId)
  const toIndex = next.findIndex((p) => p.projectID === targetId)
  if (fromIndex === -1 || toIndex === -1) return

  const [moved] = next.splice(fromIndex, 1)
  next.splice(toIndex, 0, moved)

  localOrder.value = next
  projectsStore.reorderProjects(next)
  void projectsStore.persistOrder()
}

function setHoverBorder({ id, color }) {
  hoverColor.value = { ...hoverColor.value, [id]: color || '#3b82f6' }
}

function clearHoverBorder(id) {
  const { [id]: _removed, ...rest } = hoverColor.value
  hoverColor.value = rest
}

function openDeleteDialog(project) {
  projectToDelete.value = project
  deleteDialogVisible.value = true
}

async function confirmDelete() {
  const project = projectToDelete.value
  if (!project) return

  try {
    await projectsStore.deleteProject(project.projectID)
    deleteDialogVisible.value = false
    projectToDelete.value = null
    localOrder.value = [...sortedProjects.value]
  } catch {}
}

function openCreateDialog() {
  editingProject.value = null
  editDialogVisible.value = false
  deleteDialogVisible.value = false
  createDialogVisible.value = true
}

function openEditDialog(project) {
  editingProject.value = { ...project }
  createDialogVisible.value = false
  deleteDialogVisible.value = false
  editDialogVisible.value = true
}

async function handleCreate(payload) {
  try {
    await projectsStore.createProject({
      name: payload.name,
      description: payload.description || null,
      priority: payload.priority,
      position: sortedProjects.value.length,
      icon: payload.icon || null,
      color: payload.color,
      tags: payload.tags?.length ? [...payload.tags] : null,
    })

    localOrder.value = [...sortedProjects.value]
    createDialogVisible.value = false
  } catch {}
}

async function handleEdit({ id, data }) {
  try {
    await projectsStore.updateProject(id, {
      name: data.name,
      description: data.description || null,
      priority: data.priority,
      icon: data.icon || null,
      color: data.color,
      tags: data.tags?.length ? [...data.tags] : null,
    })

    localOrder.value = [...sortedProjects.value]
    editDialogVisible.value = false
    editingProject.value = null
  } catch {}
}
</script>