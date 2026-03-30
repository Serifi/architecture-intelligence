<template>
  <div class="space-y-1">
    <label v-if="label" class="block text-xs font-medium text-slate-600">
      {{ label }}
    </label>

    <Password v-model="model" :feedback="feedback" toggleMask inputClass="w-full" class="w-full" :autocomplete="autocomplete">
      <template v-if="feedback" #header>
        <div class="mb-2 text-xs font-semibold">
          {{ t('auth.password.rules.title') }}
        </div>
      </template>

      <template v-if="feedback" #footer>
        <Divider />
        <ul class="my-2 list-disc pl-4 text-left text-[0.75rem] leading-normal text-slate-500">
          <li>{{ t('auth.password.rules.minLength') }}</li>
          <li>{{ t('auth.password.rules.lowercase') }}</li>
          <li>{{ t('auth.password.rules.uppercase') }}</li>
          <li>{{ t('auth.password.rules.digit') }}</li>
        </ul>
      </template>
    </Password>
  </div>
</template>

<script setup>
import { useI18n } from '~/composables/useI18n'
import { useVModel } from '~/composables/useVModel'

const props = defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: '' },
  feedback: { type: Boolean, default: false },
  autocomplete: { type: String, default: 'off' },
})

const emit = defineEmits(['update:modelValue'])

const model = useVModel(props, 'modelValue', emit)
const { t } = useI18n()
</script>