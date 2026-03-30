<template>
  <button type="button" :disabled="disabled" @click="$emit('click', $event)"
          class="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-slate-300 bg-white cursor-pointer
               text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60" :icon="null">
    <i :class="['pi', icon, 'text-sm']" />
  </button>
</template>

<script setup>
defineProps({
  icon: { type: String, required: true },
  disabled: { type: Boolean, default: false },
})

defineEmits(['click'])
</script>