<template>
  <DashboardView />
</template>
<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'auth' })
import DashboardView from '~/views/admin/DashboardView.vue'
</script> 