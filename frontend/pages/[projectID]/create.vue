<template>
  <div class="flex min-h-screen flex-col bg-slate-100 font-sans text-gray-800">
    <Header :subtitle="project?.name || ''" />

    <main class="mx-auto flex w-full max-w-[96rem] flex-1 flex-col gap-6 p-8">
      <Bar :title="t('create.title', 'Architekturentscheidungen')"
           :can-generate="canGenerate" :loading="aiLoading"
           @back="goBack" @generate="onGenerateWithAI"/>

      <Form v-model:prompt="qualityAttribute" v-model:template-id="selectedTemplateId"
            :options="templateOptions" :loading="templatesLoading"
            :label-prompt="t('create.form.prompt', 'Prompt (optional)')"
            :label-template="t('create.form.template', 'Vorlage')"
            :ph-prompt="t('common.placeholder.text', 'Text einfügen...')"
            :ph-template="t('create.form.templatePlaceholder', 'Auswahl treffen...')"/>

      <section class="flex flex-1 flex-col gap-4">
        <div class="flex items-center gap-3">
          <div class="h-px flex-1 bg-slate-200" />
          <span class="text-[11px] uppercase tracking-wide text-slate-400">
            {{ t('create.suggestion.divider', 'Vorschlag') }}
          </span>
          <div class="h-px flex-1 bg-slate-200" />
        </div>

        <div v-if="aiLoading" class="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
          {{ t('create.suggestion.thinking', 'Thinking ...') }}
        </div>

        <div v-else-if="!aiSuggestion" class="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">
          {{ t('create.suggestion.empty.before', 'Prompt und Vorlage auswählen und') }}
          <span class="font-medium">
            {{ t('create.suggestion.empty.cta', '„Architekturvorschlag erstellen“') }}
          </span>
          {{ t('create.suggestion.empty.after', 'anklicken.') }}
        </div>

        <div v-else class="flex flex-col gap-6">
          <Suggestion :suggestion="aiSuggestion" :template="suggestionTemplate" :field-value-map="suggestionFieldValueMap"
                      :creating="creating" :can-generate="canGenerate" :ai-alternatives-loading="aiAlternativesLoading"
                      @add="onAddDecision" @alternatives="onGenerateAlternatives" @discard="onDiscardSuggestion"/>

          <Alternatives :visible="alternativesVisible" :loading="aiAlternativesLoading" :items="aiAlternatives"
                        :field-meta="fieldMetaById" @select="onSelectAlternative"/>

          <Chat v-model:message="currentMessage" :messages="messages" :loading="chatLoading"
                :can-send="canSendChat" @send="onSendChat"/>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'

import Header from '~/components/Header.vue'
import Bar from '~/components/Creation/Bar.vue'
import Form from '~/components/Creation/Form.vue'
import Suggestion from '~/components/Creation/Suggestion.vue'
import Alternatives from '~/components/Creation/Alternatives.vue'
import Chat from '~/components/Creation/Chat.vue'

import { useProjectStore } from '~/stores/project'
import { useDecisionStore } from '~/stores/decision'
import { useNotify } from '~/composables/useNotify'
import { api, apiUrl } from '~/utils/api'
import { errorMessage } from '~/utils/messages'

const route = useRoute()
const router = useRouter()

const notify = useNotify()
const t = (key, fallback, params) => notify.t(key, fallback, params)

const projectId = computed(() => Number(route.params.projectID))

const projectsStore = useProjectStore()
const { activeProject } = storeToRefs(projectsStore)
const project = computed(() => activeProject.value)

const decisionsStore = useDecisionStore()
const {
  aiSuggestion,
  aiLoading,
  aiAlternatives,
  aiAlternativesLoading,
  chatLoading,
} = storeToRefs(decisionsStore)

const templates = ref([])
const templatesLoading = ref(false)

const qualityAttribute = ref('')
const selectedTemplateId = ref(null)
const creating = ref(false)
const alternativesVisible = ref(false)

const messages = ref([])
const currentMessage = ref('')

const templateOptions = computed(() =>
    (templates.value || []).map((tpl) => ({
      label: tpl.name,
      value: tpl.templateID,
    })),
)

const suggestionTemplate = computed(() => {
  const s = aiSuggestion.value
  if (!s) return null
  if (s.template) return s.template
  const id = s.templateID
  if (id == null) return null
  return (templates.value || []).find((tpl) => tpl.templateID === id) || null
})

const suggestionFieldValueMap = computed(() => {
  const s = aiSuggestion.value
  const map = {}
  const list = s?.fieldValues || []
  if (!Array.isArray(list)) return map
  for (const fv of list) map[fv.fieldID] = fv.value
  return map
})

const fieldMetaById = computed(() => {
  const map = {}
  const tpl = suggestionTemplate.value
  const fields = tpl?.fields
  if (!Array.isArray(fields)) return map
  for (const f of fields) map[f.fieldID] = f
  return map
})

const canGenerate = computed(() => Boolean(selectedTemplateId.value) && !templatesLoading.value)
const canSendChat = computed(() => currentMessage.value.trim().length > 0)

onMounted(async () => {
  try {
    if (!Number.isNaN(projectId.value)) {
      if (!activeProject.value || activeProject.value.projectID !== projectId.value) {
        await projectsStore.fetchProjectById(projectId.value)
      }
    }

    templatesLoading.value = true
    const res = await api.get(apiUrl('/templates/'))
    templates.value = res.data || []
  } catch (e) {
    notify.error({
      message: errorMessage(e) ?? t('create.errors.templates', 'Vorlagen konnten nicht geladen werden.'),
    })
  } finally {
    templatesLoading.value = false
  }
})

function goBack() {
  if (!Number.isNaN(projectId.value)) router.push(`/${projectId.value}`)
  else router.push('/')
}

async function onGenerateWithAI() {
  if (!canGenerate.value || aiLoading.value) return
  if (Number.isNaN(projectId.value)) {
    notify.error({ message: t('create.errors.projectId', 'Ungültige Projekt-ID in der URL.') })
    return
  }

  try {
    alternativesVisible.value = false
    await decisionsStore.generateDecisionWithAI({
      projectId: projectId.value,
      templateId: selectedTemplateId.value,
      prompt: qualityAttribute.value.trim(),
    })
  } catch {}
}

async function onGenerateAlternatives() {
  if (!canGenerate.value || aiAlternativesLoading.value || !aiSuggestion.value) return
  if (Number.isNaN(projectId.value)) {
    notify.error({ message: t('create.errors.projectId', 'Ungültige Projekt-ID in der URL.') })
    return
  }

  const tpl = suggestionTemplate.value
  if (!tpl) {
    notify.error({ message: t('create.errors.templateMissing', 'Keine gültige Vorlage für den Vorschlag gefunden.') })
    return
  }

  try {
    const prompt = qualityAttribute.value.trim()

    const baseFields = (tpl.fields || []).map((field) => ({
      fieldID: field.fieldID,
      name: field.name,
      isRequired: field.isRequired,
      value: suggestionFieldValueMap.value[field.fieldID] || '',
    }))

    const payload = {
      projectID: projectId.value,
      templateID: selectedTemplateId.value,
      prompt,
      base: {
        projectID: projectId.value,
        templateID: selectedTemplateId.value,
        prompt,
        title: aiSuggestion.value.title || prompt || 'Architekturentscheidung',
        fields: baseFields,
      },
    }

    alternativesVisible.value = true
    await decisionsStore.generateAlternativeDecisionsWithAI(payload)
  } catch {}
}

async function onAddDecision() {
  if (!aiSuggestion.value) return
  if (Number.isNaN(projectId.value)) {
    notify.error({ message: t('create.errors.projectId', 'Ungültige Projekt-ID in der URL.') })
    return
  }

  try {
    creating.value = true

    const created = await decisionsStore.createDecisionFromSuggestion({
      projectId: projectId.value,
      suggestion: aiSuggestion.value,
      templateId: selectedTemplateId.value,
    })

    decisionsStore.clearSuggestion()
    alternativesVisible.value = false

    if (created?.decisionID) router.push(`/${projectId.value}/${created.decisionID}`)
    else router.push(`/${projectId.value}`)
  } catch {} finally {
    creating.value = false
  }
}

function onSelectAlternative(index) {
  const alt = aiAlternatives.value?.[index]
  if (!alt) return

  const currentMain = aiSuggestion.value || null
  const remaining = (aiAlternatives.value || []).filter((_, i) => i !== index)
  const newAlternatives = currentMain ? [...remaining, currentMain] : remaining

  decisionsStore.$patch({
    aiSuggestion: alt,
    aiAlternatives: newAlternatives,
  })
}

function onDiscardSuggestion() {
  decisionsStore.clearSuggestion()
  alternativesVisible.value = false

  notify.success({
    message: t('create.success.discarded', 'Architekturvorschlag wurde verworfen.'),
  })
}

async function onSendChat() {
  const text = currentMessage.value.trim()
  if (!text) return

  messages.value.push({ role: 'user', content: text })
  currentMessage.value = ''

  if (Number.isNaN(projectId.value)) {
    notify.error({ message: t('create.errors.projectId', 'Ungültige Projekt-ID in der URL.') })
    return
  }

  try {
    const historyForBackend = messages.value.map((m) => ({ role: m.role, content: m.content }))

    let suggestionForChat = null
    const s = aiSuggestion.value
    if (s) {
      const rawFieldValues = Array.isArray(s.fieldValues) ? s.fieldValues : Array.isArray(s.fields) ? s.fields : []

      const fieldsForChat = rawFieldValues.map((fv) => ({
        fieldID: fv.fieldID,
        name: fieldMetaById.value[fv.fieldID]?.name || `Feld ${fv.fieldID}`,
        isRequired: fieldMetaById.value[fv.fieldID]?.isRequired ?? false,
        value: fv.value || '',
      }))

      suggestionForChat = {
        title: s.title || (qualityAttribute.value.trim() || 'Architekturentscheidung'),
        statusName: null,
        fields: fieldsForChat,
      }
    }

    const reply = await decisionsStore.chatAboutDecision(projectId.value, historyForBackend, suggestionForChat)

    if (reply && String(reply).length > 0) {
      messages.value.push({ role: 'assistant', content: String(reply) })
    }
  } catch {}
}
</script>