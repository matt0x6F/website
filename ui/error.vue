<script setup lang="ts">
import PageNotFoundView from '~/views/PageNotFoundView.vue'
defineProps<{ error: { statusCode: number, message: string } }>()
</script>

<template>
  <PageNotFoundView v-if="error.statusCode === 404" />
  <div v-else class="flex flex-col items-center justify-center min-h-[80vh] text-center p-5">
    <h1 class="text-5xl font-bold mb-4">Error {{ error.statusCode }}</h1>
    <p class="mb-8">{{ error.message }}</p>
    <NuxtLink to="/" class="text-blue-500 underline">Go Home</NuxtLink>
  </div>
</template> 