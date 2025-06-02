<template>
  <FilesView />
</template>
<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'auth' })
import FilesView from '~/views/admin/FilesView.vue'
</script> 