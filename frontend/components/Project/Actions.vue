<template>
  <div class="absolute bottom-2.5 right-2.5 flex gap-2.5">
    <i class="pi pi-pencil cursor-pointer text-base leading-none text-blue-600 hover:text-blue-800" @click.stop="emit('edit')" />
    <i class="pi pi-trash cursor-pointer text-base leading-none text-red-600 hover:text-red-800" @click.stop="emit('delete')" />
  </div>
</template>

<script setup>
const emit = defineEmits(['edit', 'delete'])
</script>