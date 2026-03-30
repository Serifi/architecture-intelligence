<template>
  <div class="relative flex cursor-pointer flex-col rounded-xl border bg-white p-4 shadow-sm transition-[box-shadow,border-color] duration-150"
       :class="{ 'border-2 bg-blue-50 outline-2 outline-offset-2 outline-blue-500': isDragOver }" :style="borderHoverStyle"
       draggable="true" @dragstart="onDragStart" @dragover.prevent @drop="onDrop"
       @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave">

    <Header :project="project" />
    <Tag :tags="project.tags ?? []" />
    <Updated :last-updated="project.lastUpdated" />
    <Actions v-if="hovered" @edit="emitEdit" @delete="emitDelete" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import Header from '~/components/Project/Header.vue'
import Updated from '~/components/Project/Updated.vue'
import Actions from '~/components/Project/Actions.vue'
import Tag from '~/components/Project/Tag.vue'

const props = defineProps({
  project: { type: Object, required: true },
  isDragOver: { type: Boolean, default: false },
  hoverColor: { type: String, default: null },
})

const emit = defineEmits([
  'drag-start',
  'drop',
  'request-delete',
  'request-edit',
  'hover-border',
  'hover-leave',
])

const hovered = ref(false)

const borderHoverStyle = computed(() => {
  const color = props.hoverColor || props.project.color || '#3b82f6'
  return { borderColor: hovered.value ? color : '#d1d5db' }
})

function onDragStart(e) {
  e.dataTransfer?.setData('text/plain', String(props.project.projectID))
  emit('drag-start', props.project.projectID)
}

function onDrop() {
  emit('drop', props.project.projectID)
}

function emitDelete() {
  emit('request-delete', props.project)
}

function emitEdit() {
  emit('request-edit', props.project)
}

function handleMouseEnter() {
  hovered.value = true
  emit('hover-border', { id: props.project.projectID, color: props.project.color || '#3b82f6' })
}

function handleMouseLeave() {
  hovered.value = false
  emit('hover-leave', props.project.projectID)
}
</script>