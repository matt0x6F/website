<template>
  <SeriesListView />
</template>
<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'auth' })
import SeriesListView from '~/views/admin/SeriesListView.vue'
</script> 