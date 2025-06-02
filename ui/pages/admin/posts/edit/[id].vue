<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'auth' })
import PostEditorView from '@/views/admin/PostEditorView.vue'
</script>

<template>
  <PostEditorView />
</template> 