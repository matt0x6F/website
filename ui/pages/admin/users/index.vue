<template>
  <UsersView />
</template>
<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'auth' })
import UsersView from '~/views/admin/UsersView.vue'
</script> 