<template>
  <p v-html="content"></p>
</template>

<script setup lang="ts">
defineProps<{ content: string }>()
</script> 