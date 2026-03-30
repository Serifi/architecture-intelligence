<template>
  <NuxtPage />
  <Toast />
</template>

<script setup>
const route = useRoute()

if (route.path === '/' || route.path === '') {
  await navigateTo('/auth')
}
</script>