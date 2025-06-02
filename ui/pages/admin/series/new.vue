<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'auth' })
import SeriesFormView from '@/views/admin/SeriesFormView.vue'
</script>

<template>
  <SeriesFormView />
</template> 