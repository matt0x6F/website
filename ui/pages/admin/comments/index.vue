<template>
  <CommentsView />
</template>
<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'auth' })
import CommentsView from '~/views/admin/CommentsView.vue'
</script> 