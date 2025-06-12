<template>
  <ResumeEditorView />
</template>
<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'auth' })
import ResumeEditorView from '~/views/admin/ResumeEditorView.vue'
</script> 