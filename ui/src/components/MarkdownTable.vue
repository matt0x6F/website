<template>
  <DataTable :value="rows" class="markdown-table rounded-lg" :rows="rows.length">
    <Column v-for="col in columns" :key="col.field" :field="col.field" :header="col.header" />
  </DataTable>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

const props = defineProps<{
  columns: { field: string, header: string }[],
  rows: Record<string, any>[]
}>()
</script>

<style scoped>
.markdown-table {
  width: 100%;
  margin: 1em 0;
}
:deep(.p-datatable-table) {
  border-radius: 0.75rem; /* rounded-lg */
  overflow: hidden;
}
:deep(.p-datatable-thead) {
  border-top-left-radius: 0.75rem;
  border-top-right-radius: 0.75rem;
}
:deep(.p-datatable-tfoot) {
  border-bottom-left-radius: 0.75rem;
  border-bottom-right-radius: 0.75rem;
}
</style> 