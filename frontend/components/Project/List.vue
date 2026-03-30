<template>
  <div class="w-full">
    <div class="grid w-full grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4"
         :class="{ 'min-h-[320px] place-content-center': !projects.length }">
      <Card v-for="p in projects" :key="p.projectID" :project="p"
            :is-drag-over="dragOverId === p.projectID" :hover-color="hoverColor[p.projectID]"
            @drag-start="$emit('drag-start', $event)" @drop="$emit('drop', $event)"
            @hover-border="$emit('hover-border', $event)" @hover-leave="$emit('hover-leave', $event)"
            @request-delete="$emit('request-delete', $event)" @request-edit="$emit('request-edit', $event)"
            @dragover.prevent="$emit('drag-over', p.projectID)" @click="$emit('card-click', p.projectID)"/>

      <div class="group relative flex cursor-pointer items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50
                  p-8 transition-[border-color,background-color,box-shadow] duration-150 hover:border-blue-600 hover:bg-blue-50 hover:shadow-lg"
           :class="{ 'col-span-full mx-auto w-full max-w-2xl px-8 py-6': !projects.length }"
           @click="$emit('add-click')">
        <div class="flex flex-col items-center gap-2 text-center font-sans text-gray-500">
          <div v-if="!projects.length" class="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-400">
            {{ $t('projects.empty.title') }}
          </div>
          <p v-if="!projects.length" class="mb-2 text-[0.8rem] text-slate-500">
            {{ $t('projects.empty.text') }}
          </p>

          <i class="pi pi-plus text-[1.1rem] text-gray-500 transition-colors duration-150 group-hover:text-blue-600" />
          <div class="text-[0.8rem] font-medium text-gray-500 transition-colors duration-150 group-hover:text-blue-600">
            {{ $t('projects.add') }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Card from '~/components/Project/Card.vue'

defineProps({
  projects: { type: Array, default: () => [] },
  dragOverId: { type: [Number, String, null], default: null },
  hoverColor: { type: Object, default: () => ({}) },
})

defineEmits([
  'card-click',
  'drag-start',
  'drag-over',
  'drop',
  'hover-border',
  'hover-leave',
  'request-delete',
  'request-edit',
  'add-click',
])
</script>