<template>
  <button type="button" :class="classes" :disabled="disabled" @click="onClick">
    <i v-if="icon" :class="['pi', icon, 'text-xs', label ? 'mr-2' : '']" />
    <span v-if="label">{{ label }}</span>
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon: { type: String, default: '' },
  label: { type: String, default: '' },
  variant: {
    type: String,
    default: 'white',
    validator: (v) => ['white', 'blue', 'green', 'red'].includes(v),
  },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['click'])

const base =
    'inline-flex h-10 items-center justify-center rounded-lg px-4 text-sm font-semibold transition cursor-pointer ' +
    'active:scale-[0.97] disabled:opacity-60 disabled:cursor-not-allowed'

const variants = {
  white: 'border border-slate-300 bg-white text-slate-600 hover:bg-slate-50',
  blue: 'bg-sky-600 text-white hover:bg-sky-700',
  green: 'bg-emerald-600 text-white hover:bg-emerald-700',
  red: 'bg-red-600 text-white hover:bg-red-700',
}

const classes = computed(() => `${base} ${variants[props.variant]}`)

function onClick(e) {
  if (!props.disabled) emit('click', e)
}
</script>