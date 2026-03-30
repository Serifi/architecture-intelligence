<template>
  <Dialog v-model:visible="visible" modal closable style="width: 64rem" :header="dialogTitle">
    <div class="grid gap-4 text-sm text-gray-700">
      <div class="grid gap-4 sm:grid-cols-3">
        <label class="grid gap-2 text-xs font-medium text-gray-700 sm:col-span-2">
          {{ t('projects.form.name') }}
          <InputText v-model="form.name" class="w-full" :placeholder="t('common.placeholder.text')" />
        </label>

        <label class="grid gap-2 text-xs font-medium text-gray-700">
          {{ t('projects.form.priority') }}
          <Select v-model="form.priority" class="w-full" :options="priorityOptions" optionLabel="label" optionValue="value" />
        </label>
      </div>

      <label class="grid gap-2 text-xs font-medium text-gray-700">
        {{ t('projects.form.description') }}
        <Textarea v-model="form.description" rows="3" class="w-full" :placeholder="t('common.placeholder.text')" />
      </label>

      <div class="grid gap-4 sm:grid-cols-3">
        <div class="grid gap-2 text-xs font-medium text-gray-700 sm:col-span-2">
          {{ t('projects.form.icon') }}
          <div class="flex w-full items-center rounded-md border border-gray-300 bg-white px-2">
            <span class="inline-flex h-8 w-8 items-center justify-center">
              <i :class="['pi', iconClass, 'text-gray-700']" />
            </span>
            <InputText v-model="form.icon" class="w-full !border-0 focus:!outline-none focus:!ring-0" :placeholder="t('common.placeholder.text')"/>
          </div>
        </div>

        <div class="grid gap-2 text-xs font-medium text-gray-700">
          {{ t('projects.form.color') }}
          <div class="flex w-full items-center gap-3 rounded-md border border-gray-300 bg-white px-3 py-1.5">
            <ColorPicker v-model="colorRaw" format="hex" class="inline-block overflow-hidden rounded-md" />
            <span class="text-gray-700">#{{ (colorRaw || '').toUpperCase() }}</span>
          </div>
        </div>
      </div>

      <div class="grid gap-2 text-xs font-medium text-gray-700">
        <span>{{ t('projects.form.tags') }}</span>

        <div class="flex flex-wrap gap-2">
          <span v-for="(tag, idx) in tags" :key="`${modeKey}-${idx}`" class="inline-flex items-center gap-1 rounded-full border
          border-slate-300/60 bg-slate-50 px-2 py-[3px] text-[10.5px] font-medium leading-[1.2] text-gray-600">
            {{ tag }}
            <i class="pi pi-times cursor-pointer text-xs text-gray-400 hover:text-gray-700" @click="removeTag(idx)" />
          </span>
        </div>

        <InputText v-model="tagInput" class="w-full" :placeholder="t('projects.form.tagPlaceholder')" @keydown.enter.prevent="addTag"/>
      </div>
    </div>

    <template #footer>
      <div class="flex w-full items-center gap-3">
        <Message v-if="showNameConflict" severity="error" :closable="false">
          {{ t('projects.form.nameConflict') }}
        </Message>

        <div class="ms-auto flex gap-3">
          <Button :label="t('common.cancel')" severity="secondary" text @click="visible = false" />
          <Button :label="confirmLabel" severity="primary" :disabled="!isValid" @click="onConfirm" />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useProjectStore } from '~/stores/project'
import { useI18n } from '~/composables/useI18n'
import { useVModel } from '~/composables/useVModel'

const props = defineProps({
  visible: { type: Boolean, default: false },
  project: { type: Object, default: null },
})

const emit = defineEmits(['update:visible', 'create', 'save'])

const { t } = useI18n()
const projectsStore = useProjectStore()

const visible = useVModel(props, 'visible', emit)

const isEdit = computed(() => Boolean(props.project))
const modeKey = computed(() => (isEdit.value ? 'edit' : 'create'))

const dialogTitle = computed(() => (isEdit.value ? t('projects.form.titleEdit') : t('projects.form.titleCreate')))
const confirmLabel = computed(() => (isEdit.value ? t('common.save') : t('common.create')))

const form = ref({
  id: null,
  name: '',
  description: '',
  priority: 'medium',
  icon: 'folder',
})

const colorRaw = ref('2563EB')
const tagInput = ref('')
const tags = ref([])

const priorityOptions = computed(() => [
  { label: t('projects.priority.low'), value: 'low' },
  { label: t('projects.priority.medium'), value: 'medium' },
  { label: t('projects.priority.high'), value: 'high' },
  { label: t('projects.priority.critical'), value: 'critical' },
])

const iconClass = computed(() => {
  const raw = String(form.value.icon || '').trim()
  return raw ? `pi-${raw}` : 'pi-folder'
})

const normalizedName = computed(() => String(form.value.name || '').trim().toLowerCase())

const isNameUnique = computed(() => {
  if (!normalizedName.value) return true

  return !(projectsStore.projects || []).some((p) => {
    const existing = String(p?.name || '').trim().toLowerCase()
    return p?.projectID !== form.value.id && existing === normalizedName.value
  })
})

const showNameConflict = computed(() => normalizedName.value.length > 0 && !isNameUnique.value)
const isValid = computed(() => normalizedName.value.length > 0 && isNameUnique.value)

watch(
    () => visible.value,
    (isOpen) => {
      if (isOpen) initForm()
    },
)

watch(
    () => props.project,
    () => {
      if (visible.value) initForm()
    },
)

function initForm() {
  const p = props.project

  if (p) {
    form.value = {
      id: p.projectID ?? null,
      name: p.name || '',
      description: p.description || '',
      priority: p.priority || 'medium',
      icon: p.icon || 'folder',
    }
    colorRaw.value = String(p.color || '#2563EB').replace('#', '')
    tags.value = Array.isArray(p.tags) ? [...p.tags] : []
    tagInput.value = ''
    return
  }

  form.value = { id: null, name: '', description: '', priority: 'medium', icon: 'folder' }
  colorRaw.value = '2563EB'
  tags.value = []
  tagInput.value = ''
}

function addTag() {
  const value = tagInput.value.trim()
  if (!value) return
  if (!tags.value.includes(value)) tags.value.push(value)
  tagInput.value = ''
}

function removeTag(idx) {
  tags.value.splice(idx, 1)
}

function onConfirm() {
  if (!isValid.value) return

  const payload = {
    name: form.value.name,
    description: form.value.description,
    priority: form.value.priority,
    icon: form.value.icon,
    color: `#${colorRaw.value || '2563EB'}`,
    tags: [...tags.value],
  }

  if (isEdit.value && form.value.id) emit('save', { id: form.value.id, data: payload })
  else emit('create', payload)
}
</script>