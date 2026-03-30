<template>
  <div class="flex min-h-screen bg-slate-100">
    <div class="relative hidden w-1/2 items-center justify-center overflow-hidden lg:flex">
      <img src="/auth.png" class="h-full max-h-screen w-full object-cover" alt="auth"/>
      <div class="absolute inset-0 bg-black/30" />
    </div>

    <div class="flex w-full items-center justify-center lg:w-1/2">
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-lg">
        <div class="mb-6 flex flex-col items-center gap-2">
          <img src="/favicon.ico" alt="Logo" class="h-12 w-12" />
          <h1 class="text-lg font-semibold text-slate-800">
            {{ t('header.appTitle') }}
          </h1>
        </div>

        <form class="space-y-4" @submit.prevent="handleSubmit">
          <div class="space-y-2">
            <label class="block text-xs font-medium text-slate-600">
              {{ t('header.settings.emailLabel') }}
            </label>

            <InputText v-model="email" type="email" class="w-full" autocomplete="email" />

            <p v-if="showEmailError" class="text-xs text-red-500">
              {{ t('auth.email.invalid') }}
            </p>
          </div>

          <Field v-model="password" :label="t('auth.password.label')" :feedback="isRegister" :autocomplete="passwordAutocomplete"/>

          <div class="flex justify-center py-2 text-[0.75rem] text-slate-500">
            <button type="button" class="cursor-pointer text-blue-600 hover:underline" @click="toggleMode">
              {{ modeSwitchText }}
            </button>
          </div>

          <Button type="submit" class="w-full" :label="submitLabel" :loading="auth.loading" icon="pi pi-user" :disabled="!canSubmit"/>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useI18n } from '~/composables/useI18n'
import Field from '~/components/Auth/Field.vue'

const { t } = useI18n()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const isRegister = ref(false)

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const isEmailValid = computed(() => emailPattern.test(email.value))
const showEmailError = computed(() => email.value !== '' && !isEmailValid.value)

const canSubmit = computed(() => isEmailValid.value && Boolean(password.value) && !auth.loading)

const submitLabel = computed(() => (isRegister.value ? t('auth.register.submit') : t('auth.login.submit')))
const modeSwitchText = computed(() => (isRegister.value ? t('auth.switch.toLogin') : t('auth.switch.toRegister')))
const passwordAutocomplete = computed(() => (isRegister.value ? 'new-password' : 'current-password'))

function toggleMode() {
  isRegister.value = !isRegister.value
}

async function handleSubmit() {
  if (!canSubmit.value) return

  const payload = { email: email.value, password: password.value }

  try {
    if (isRegister.value) await auth.register(payload)
    else await auth.login(payload)

    await navigateTo('/')
  } catch {}
}
</script>