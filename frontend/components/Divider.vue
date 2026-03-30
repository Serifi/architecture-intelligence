<template>
  <div class="my-4 flex items-center gap-3">
    <div class="flex-1 border-t border-slate-200" />
    <span class="text-[11px] uppercase tracking-wide text-slate-400">
      {{ label }}
    </span>
    <div class="flex-1 border-t border-slate-200" />
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
})
</script>