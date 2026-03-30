<template>
  <section class="flex flex-col gap-3">
    <Divider :label="title" />

    <section class="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4">
      <div class="h-128 space-y-3 overflow-y-auto rounded-md border border-slate-100 p-3 text-sm">
        <p v-if="messages.length === 0" class="text-slate-400">
          {{ emptyHint }}
        </p>

        <div v-for="(msg, idx) in messages" :key="idx" class="flex flex-col gap-1">
          <div v-if="msg.role === 'user'" class="max-w-[80%] self-end rounded-lg bg-sky-600 px-3 py-2 text-white">
            {{ msg.content }}
          </div>
          <div v-else class="max-w-[80%] self-start whitespace-pre-line rounded-lg bg-slate-100 px-3 py-2 text-slate-800">
            {{ msg.content }}
          </div>
        </div>
      </div>

      <form class="mt-2 flex gap-2" @submit.prevent="$emit('send')">
        <InputText v-model="m" class="flex-1 text-sm" :placeholder="ph"/>
        <Button type="submit" icon="pi-send" :label="sendLabel" variant="blue" :disabled="!canSend || loading"/>
      </form>
    </section>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useNotify } from '~/composables/useNotify'
import Divider from '~/components/Divider.vue'
import Button from '~/components/Button.vue'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  message: { type: String, default: '' },
  canSend: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:message', 'send'])

const notify = useNotify()

const title = computed(() => notify.t('create.chat.title', 'Chat'))
const emptyHint = computed(() =>
    notify.t(
        'create.chat.empty',
        'Fragen zum generierten Vorschlag stellen, zum Beispiel: „Welche unmittelbaren Risiken ergeben sich aus dieser Architekturentscheidung?“',
    ),
)

const ph = computed(() => notify.t('create.chat.placeholder', 'Text eingeben...'))
const sendLabel = computed(() => notify.t('create.chat.send', 'Senden'))

const m = computed({
  get: () => props.message,
  set: (v) => emit('update:message', v),
})
</script>