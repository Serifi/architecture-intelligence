<template>
  <div v-if="tags.length" class="mt-4 flex flex-wrap gap-2">
    <span v-for="tag in tags" :key="tag" class="inline-flex items-center rounded-full border px-2 py-[2px] text-[10px]
    font-medium leading-none whitespace-nowrap border-slate-300/60 bg-slate-50 text-gray-600">
      {{ tag }}
    </span>
  </div>
</template>

<script setup>
defineProps({
  tags: { type: Array, default: () => [] },
})
</script>