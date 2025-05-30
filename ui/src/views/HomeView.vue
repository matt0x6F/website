<script setup lang="ts">
import TheWelcome from '../components/TheWelcome.vue'
import { onMounted } from 'vue'

onMounted(() => {
  document.title = 'ooo-yay.com – Home'
})
</script>

<template>
  <main>
    <TheWelcome />
  </main>
</template>
