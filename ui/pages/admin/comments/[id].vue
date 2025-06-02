<template>
  <CommentDetailView />
</template>
<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'auth' })
import CommentDetailView from '~/views/admin/CommentDetailView.vue'
</script> 