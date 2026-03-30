<template>
  <Dialog v-model:visible="visible" modal closable :header="t('overview.attach.title')" style="width: 64rem">
    <div class="card">
      <FileUpload ref="fileUploadRef" name="file" :multiple="true" :maxFileSize="52428800" :customUpload="true" @uploader="onUpload" @select="onSelect">
        <template #header="{ chooseCallback, uploadCallback, clearCallback, files }">
          <div class="flex flex-1 flex-wrap items-center justify-between gap-4">
            <div class="flex flex-col gap-2">
              <Message v-if="showUploadHint && files?.length" severity="info" :closable="true" @close="showUploadHint = false">
                {{ t('overview.attach.clickToUpload', 'Tipp: Klicke auf das Wolken Symbol, um Dateien hochzuladen.') }}
              </Message>
            </div>

            <div class="ms-auto flex gap-2">
              <Button @click="chooseCallback()" icon="pi pi-paperclip" rounded variant="outlined" severity="secondary" />
              <Button @click="uploadCallback()" icon="pi pi-cloud-upload" rounded variant="outlined" severity="success" :disabled="!files?.length || uploading"/>
              <Button @click="onClear(clearCallback)" icon="pi pi-times" rounded variant="outlined" severity="danger" :disabled="!files?.length || uploading"/>
            </div>
          </div>
        </template>

        <template #content="{ files, uploadedFiles, removeFileCallback }">
          <div class="flex flex-col gap-8 pt-4">
            <div v-if="files?.length">
              <div class="flex flex-wrap gap-4">
                <div v-for="(file, index) in files" :key="file.name + file.type + file.size"
                     class="flex items-center justify-between gap-6 rounded-xl border border-slate-300 p-6">
                  <div class="flex min-w-0 items-center gap-3">
                    <span class="truncate font-semibold">
                      {{ file.name }}
                    </span>
                    <span class="shrink-0 text-sm text-slate-500">
                      {{ formatSize(file.size) }}
                    </span>
                  </div>

                  <Button icon="pi pi-times" @click="removeFileCallback(index)" variant="outlined" rounded severity="danger"/>
                </div>
              </div>
            </div>

            <div v-if="uploadedFiles?.length">
              <div class="flex flex-wrap gap-4">
                <div v-for="file in uploadedFiles" :key="file.name + file.type + file.size"
                     class="flex items-center justify-between gap-6 rounded-xl border border-slate-300 p-6">
                  <div class="flex flex min-w-0 items-center gap-3">
                    <span class="truncate font-semibold">
                      {{ file.name }}
                    </span>
                    <span class="shrink-0 text-sm text-slate-500">
                      {{ formatSize(file.size) }}
                    </span>
                    <Badge :value="t('overview.attach.uploaded')" severity="success" />
                  </div>

                  <div class="shrink-0">
                    <img v-if="file.type?.startsWith('image/')" role="presentation" :alt="file.name" :src="file.objectURL" width="100" height="50"/>
                    <i v-else class="pi pi-file text-4xl" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>

        <template #empty>
          <div class="flex flex-col items-center justify-center">
            <i class="pi pi-cloud-upload !border-2 !rounded-full !p-8 !text-4xl !text-muted-color" />
            <p class="mb-0 mt-6">
              {{ t('overview.attach.empty') }}
            </p>
          </div>
        </template>
      </FileUpload>

      <div class="mt-6">
        <ul class="divide-y divide-slate-200">
          <li v-for="att in attachments" :key="att.attachmentID" class="flex items-center justify-between py-2 text-sm">
            <div class="flex flex-col">
              <span class="font-medium">{{ att.originalFilename }}</span>
              <span class="text-xs text-slate-400">
                {{ formatSize(att.sizeBytes) }} · {{ formatDateTime(att.createdAt) }}
              </span>
            </div>

            <Button icon="pi pi-trash" rounded variant="outlined" severity="danger" :disabled="deleting" @click="onDeleteAttachment(att.attachmentID)"/>
          </li>
        </ul>
      </div>
    </div>
  </Dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { usePrimeVue } from 'primevue/config'
import { useAttachmentStore } from '~/stores/attachment'
import { useDateFormat } from '~/composables/useDateFormat'
import { useI18n } from '~/composables/useI18n'
import { useVModel } from '~/composables/useVModel'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  projectId: { type: Number, required: true },
})

const emit = defineEmits(['update:modelValue'])

const { t } = useI18n()
const visible = useVModel(props, 'modelValue', emit)

const fileUploadRef = ref(null)
const $primevue = usePrimeVue()

const attachmentsStore = useAttachmentStore()
const { sortedAttachments, loading, uploading, deleting } = storeToRefs(attachmentsStore)

const attachments = computed(() => sortedAttachments.value || [])
const attachmentsLoading = computed(() => Boolean(loading.value))

const { formatDateTime } = useDateFormat()

const showUploadHint = ref(false)

watch(
    () => visible.value,
    async (isOpen) => {
      if (!isOpen) return
      if (props.projectId) await attachmentsStore.fetchAttachments(props.projectId)
      showUploadHint.value = false
    },
)

function onSelect(event) {
  showUploadHint.value = Boolean(event?.files?.length)
}

function onClear(clearCallback) {
  clearCallback()
  showUploadHint.value = false
}

async function onUpload(event) {
  const files = event?.files || []
  if (!props.projectId || !files.length) return

  for (const file of files) {
    try {
      await attachmentsStore.uploadAttachment(props.projectId, file)
    } catch {
      break
    }
  }

  fileUploadRef.value?.clear()
  showUploadHint.value = false
}

async function onDeleteAttachment(attachmentId) {
  if (!props.projectId) return
  await attachmentsStore.deleteAttachment(props.projectId, attachmentId)
}

function formatSize(bytes) {
  const sizes = $primevue.config.locale.fileSizeTypes
  const value = Number(bytes || 0)
  if (!value) return `0 ${sizes[0]}`

  const k = 1024
  const i = Math.floor(Math.log(value) / Math.log(k))
  const formatted = Number((value / Math.pow(k, i)).toFixed(1))
  return `${formatted} ${sizes[i]}`
}
</script>