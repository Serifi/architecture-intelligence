<template>
  <header class="border-b border-gray-200 bg-white py-3 px-4">
    <div class="mx-auto flex max-w-[96rem] items-start justify-between gap-2">
      <div>
        <h1 class="m-0 text-base font-semibold leading-snug text-gray-900">
          {{ t('header.appTitle') }}
        </h1>
        <p class="text-xs leading-snug text-gray-500">
          {{ subtitleText }}
        </p>
      </div>

      <div class="flex items-start gap-3 text-xs text-gray-500">
        <div v-if="auth.user" class="flex items-center gap-2">
          <div class="relative">
            <button type="button" @click="toggleLangMenu"
                    class="flex items-center gap-2 rounded-lg bg-gray-100 px-3 py-2 text-gray-700 hover:bg-gray-200 cursor-pointer">
              <i class="pi pi-language text-sm" />
            </button>

            <Popover ref="langMenu">
              <div class="flex min-w-[150px] flex-col text-sm">
                <button type="button" @click="setLanguage('de')"
                        class="flex w-full items-center gap-2 px-3 py-2 text-left hover:bg-gray-50 cursor-pointer">
                  <span class="text-base">🇩🇪</span>
                  <span>{{ t('header.language.de') }}</span>
                </button>
                <button type="button" @click="setLanguage('en')"
                        class="flex w-full items-center gap-2 px-3 py-2 text-left hover:bg-gray-50 cursor-pointer">
                  <span class="text-base">🇬🇧</span>
                  <span>{{ t('header.language.en') }}</span>
                </button>
              </div>
            </Popover>
          </div>

          <div class="relative">
            <button type="button" @click="toggleUserMenu"
                    class="flex items-center gap-2 rounded-lg bg-gray-100 px-3 py-2 text-gray-700 hover:bg-gray-200 cursor-pointer">
              <i class="pi pi-user text-sm" />
            </button>

            <Popover ref="userMenu">
              <div class="flex min-w-[150px] flex-col divide-y divide-gray-100 text-sm">
                <button type="button" @click="openSettings"
                        class="flex w-full items-center gap-2 px-3 py-2 text-left hover:bg-gray-50 cursor-pointer">
                  <i class="pi pi-cog text-xs text-gray-500" />
                  <span>{{ t('header.user.settings') }}</span>
                </button>
                <button type="button" @click="logout"
                        class="flex w-full items-center gap-2 px-3 py-2 text-left text-red-500 hover:bg-gray-50 cursor-pointer">
                  <i class="pi pi-sign-out text-xs" />
                  <span>{{ t('header.user.logout') }}</span>
                </button>
              </div>
            </Popover>
          </div>
        </div>
      </div>
    </div>

    <Dialog v-model:visible="showSettings" modal :header="t('header.settings.title')" style="width: 64rem">
      <form class="space-y-4" @submit.prevent="submitSettings">
        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-600">
            {{ t('header.settings.emailLabel') }}
          </label>

          <InputText v-model="formEmail" type="email" class="w-full" autocomplete="email" />

          <p v-if="showEmailError" class="mt-1 text-[0.7rem] text-red-500">
            {{ t('header.settings.emailInvalid') }}
          </p>
        </div>

        <Field v-model="formPassword" :label="t('header.settings.newPassword')" :feedback="true" autocomplete="new-password" />

        <div class="flex justify-end gap-2 pt-2">
          <Button type="button" :label="t('header.settings.cancel')" class="p-button-text" @click="showSettings = false" />
          <Button type="submit" :label="t('header.settings.save')" :loading="auth.loading" :disabled="!canSave" />
        </div>
      </form>
    </Dialog>
  </header>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useI18n } from '~/composables/useI18n'
import Field from '~/components/Auth/Field.vue'

const props = defineProps({
  subtitle: { type: String, default: '' },
})

const { t, setLocale } = useI18n()
const subtitleText = computed(() => props.subtitle || t('header.subtitle.projects'))

const auth = useAuthStore()

const userMenu = ref(null)
const langMenu = ref(null)

const showSettings = ref(false)
const formEmail = ref('')
const formPassword = ref('')

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const isEmailValid = computed(() => emailPattern.test(formEmail.value))
const showEmailError = computed(() => formEmail.value !== '' && !isEmailValid.value)
const canSave = computed(() => isEmailValid.value && !auth.loading)

function toggleUserMenu(event) {
  userMenu.value?.toggle(event)
}

function toggleLangMenu(event) {
  langMenu.value?.toggle(event)
}

function setLanguage(lang) {
  setLocale(lang)
  langMenu.value?.hide()
}

function openSettings() {
  showSettings.value = true
  userMenu.value?.hide()
  formEmail.value = auth.user?.email || ''
  formPassword.value = ''
}

async function logout() {
  auth.logout()
  await navigateTo('/auth')
}

async function submitSettings() {
  if (!canSave.value) return

  const payload = { email: formEmail.value }
  if (formPassword.value) payload.password = formPassword.value

  try {
    await auth.updateUser(payload)
    showSettings.value = false
  } catch {}
}
</script>