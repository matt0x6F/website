<template>
  <UserEditorView />
</template>
<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'auth' })
import UserEditorView from '~/views/admin/UserEditorView.vue'
</script> 