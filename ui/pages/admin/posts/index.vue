<template>
  <PostsView />
</template>
<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'auth' })
import PostsView from '~/views/admin/PostsView.vue'
</script> 