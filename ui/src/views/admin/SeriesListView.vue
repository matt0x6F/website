<template>
  <div>
    <div id="content" class="">
      <h1 class="text-2xl font-bold">Manage Series</h1>
      <Toolbar class="mb-6">
        <template #start>
          <router-link :to="{ name: 'admin-series-new' }">
            <Button v.tooltip.bottom="{ value: 'Create New Series', showDelay: 1000 }" icon="pi pi-plus" aria-label="Create New Series" class="mr-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600" text />
          </router-link>
        </template>
      </Toolbar>

      <div class="space-y-4">
        <div v-if="loading" class="text-gray-600">Loading series...</div>
        <div v-else-if="error" class="text-red-600">
          Error loading series: {{ error }}
        </div>
        <div v-else-if="!seriesList.length" class="text-gray-600">
          No series found. Create one!
        </div>
        <div v-else class="divide-y">
          <div v-for="series in seriesList" :key="series.id" class="py-4">
            <div class="flex justify-between items-start">
              <div>
                <h2 class="text-xl font-semibold">{{ series.title }}</h2>
                <p class="text-gray-600 mt-1 text-sm">Slug: {{ series.slug }}</p>
                <p v-if="series.description" class="text-gray-500 mt-1 text-sm">{{ series.description }}</p>
                <p class="text-gray-500 mt-1 text-sm">Posts: {{ series.postCount || 0 }}</p>
              </div>
              <div class="flex gap-2">
                <router-link
                  :to="{ name: 'admin-series-edit', params: { id: series.id }}"
                  class="px-3 py-1 bg-emerald-100 text-emerald-700 rounded hover:bg-emerald-200 dark:bg-emerald-900 dark:text-emerald-100 dark:hover:bg-emerald-800"
                >
                  Edit
                </router-link>
                <Button
                  v.tooltip.bottom="{ value: 'Delete Series', showDelay: 1000 }"
                  icon="pi pi-trash"
                  aria-label="Delete Series"
                  class="bg-red-500 hover:bg-red-600 text-white rounded-lg dark:bg-red-600 dark:hover:bg-red-700"
                  text
                  @click="confirmDeleteSeries(series)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <ConfirmDialog></ConfirmDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApiClient } from '@/composables/useApiClient'
import { SeriesApi } from '@/lib/api/apis/SeriesApi'
import type { SeriesDetailPublic } from '@/lib/api/models/SeriesDetailPublic'
import Toolbar from 'primevue/toolbar'
import Button from 'primevue/button'
import ConfirmDialog from 'primevue/confirmdialog';
import { useConfirm } from "primevue/useconfirm";
import { useToast } from 'primevue/usetoast';
import { ResponseError } from '@/lib/api/runtime';

const seriesApi = useApiClient(SeriesApi)

const seriesList = ref<SeriesDetailPublic[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const confirm = useConfirm();
const toast = useToast();

const loadSeries = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await seriesApi.listSeries({ includePostsCount: true })
    seriesList.value = response.items
  } catch (e) {
    console.error('Error loading series:', e)
    error.value = e instanceof Error ? e.message : 'An unknown error occurred'
  } finally {
    loading.value = false
  }
}

const deleteSeries = async (seriesId: number) => {
  try {
    await seriesApi.deleteSeries({ seriesId })
    seriesList.value = seriesList.value.filter(s => s.id !== seriesId)
    toast.add({ severity: 'success', summary: 'Deleted', detail: 'Series deleted successfully', life: 3000 })
    // Optionally reload the list: await loadSeries()
  } catch (err: unknown) {
    let detail = 'Failed to delete series';
    if (err instanceof ResponseError) {
      const data = await err.response.json();
      if (data && typeof data === 'object' && 'detail' in data) {
        detail = data.detail;
      }
    }
    toast.add({ severity: 'error', summary: 'Error', detail, life: 3000 });
  }
};

const confirmDeleteSeries = (series: SeriesDetailPublic) => {
  confirm.require({
    message: `Are you sure you want to delete the series "${series.title}"? This action cannot be undone.`,
    header: 'Confirm Deletion',
    icon: 'pi pi-exclamation-triangle',
    rejectClass: 'p-button-secondary p-button-outlined',
    acceptClass: 'p-button-danger',
    accept: () => {
      deleteSeries(series.id);
    },
    reject: () => {
      toast.add({ severity: 'info', summary: 'Cancelled', detail: 'Deletion cancelled', life: 3000 });
    }
  });
};

onMounted(() => {
  loadSeries()
})
</script>

<style scoped>
/* Scoped styles if needed */
</style> 