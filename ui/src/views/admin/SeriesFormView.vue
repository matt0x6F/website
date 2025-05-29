<template>
  <div id="content" class="p-6">
    <h1 class="text-2xl font-bold mb-6">{{ isEditing ? 'Edit Series' : 'Create New Series' }}</h1>
    
    <form @submit.prevent="handleSave" class="space-y-6">
      <div>
        <label for="title" class="block mb-2 font-medium">Title</label>
        <InputText
          id="title"
          v-model="series.title"
          type="text"
          class="w-full"
          required
          :invalid="!!validationErrors.title"
        />
        <small v-if="validationErrors.title" class="text-red-600">{{ validationErrors.title }}</small>
      </div>

      <div>
        <label for="slug" class="block mb-2 font-medium">Slug</label>
        <InputText
          id="slug"
          v-model="series.slug"
          type="text"
          class="w-full"
          required
          @input="handleSlugInput"
          :invalid="!!validationErrors.slug"
        />
        <small class="text-gray-500">URL-friendly version of the title. Auto-generated but can be customized.</small>
        <small v-if="validationErrors.slug" class="text-red-600 block">{{ validationErrors.slug }}</small>
      </div>

      <div>
        <label for="description" class="block mb-2 font-medium">Description (Optional)</label>
        <Textarea
          id="description"
          v-model="series.description"
          rows="5"
          class="w-full"
          autoResize
        />
      </div>

      <div class="flex gap-4">
        <Button
          type="submit"
          size="small"
          :label="isEditing ? 'Save Changes' : 'Create Series'"
          :loading="saving"
        />
        <Button
          type="button"
          severity="secondary"
          size="small"
          label="Cancel"
          @click="cancel"
          :disabled="saving"
        />
      </div>
    </form>

    <template v-if="isEditing && loadedSeries && loadedSeries.posts && loadedSeries.posts.length">
      <div class="mt-10">
        <h2 class="text-xl font-semibold mb-4">Posts in this Series</h2>
        <ul class="space-y-2">
          <li v-for="post in loadedSeries.posts" :key="post.id" class="flex items-center gap-2">
            <router-link :to="{ name: 'admin-posts-edit', params: { id: post.id } }" class="text-blue-700 hover:underline dark:text-blue-300">
              {{ post.title }}
            </router-link>
            <span class="text-xs text-gray-400">({{ post.slug }}<span v-if="post.year">, {{ post.year }}</span>)</span>
          </li>
        </ul>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useApiClient } from '@/composables/useApiClient'
import { SeriesApi } from '@/lib/api/apis/SeriesApi'
import type { SeriesCreate, SeriesUpdate, SeriesDetailPublic } from '@/lib/api/models'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'

const router = useRouter()
const route = useRoute()
const toast = useToast()

const isEditing = computed(() => route.params.id !== undefined)
const seriesId = ref<number | undefined>(isEditing.value ? parseInt(route.params.id as string) : undefined)
const saving = ref(false)
const validationErrors = ref<Record<string, string>>({})

const seriesApi = useApiClient(SeriesApi)

const series = ref<SeriesCreate>({
  title: '',
  slug: '',
  description: ''
})

const slugManuallyEdited = ref(false)
const loadedSeries = ref<SeriesDetailPublic | null>(null)

const generateSlug = (title: string): string => {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9_]+/g, '-') // Replace non-alphanumeric chars (allowing underscore) with hyphen
    .replace(/^-+|-+$/g, '')    // Remove leading/trailing hyphens
    .replace(/-+/g, '-')         // Replace multiple consecutive hyphens with single hyphen
    .substring(0, 75);            // Max length for slugs
}

watch(() => series.value.title, (newTitle) => {
  if (!slugManuallyEdited.value && !isEditing.value) { // Only auto-generate for new series or if not manually edited
    series.value.slug = generateSlug(newTitle)
  } else if (!slugManuallyEdited.value && isEditing.value && seriesId.value && series.value.slug === '') {
    // If editing and slug becomes empty (e.g. loaded data had empty slug), regenerate
     series.value.slug = generateSlug(newTitle);
  }
})

const handleSlugInput = () => {
  slugManuallyEdited.value = true
}

const validateForm = (): boolean => {
  validationErrors.value = {};
  let isValid = true;
  if (!series.value.title.trim()) {
    validationErrors.value.title = "Title is required.";
    isValid = false;
  }
  if (!series.value.slug.trim()) {
    validationErrors.value.slug = "Slug is required.";
    isValid = false;
  } else if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(series.value.slug)) {
    validationErrors.value.slug = "Slug must be lowercase alphanumeric with hyphens and no leading/trailing/multiple hyphens.";
    isValid = false;
  }
  return isValid;
}

onMounted(async () => {
  if (isEditing.value && seriesId.value) {
    try {
      const fetchedSeries = await seriesApi.getSeriesDetailById({ seriesId: seriesId.value })
      series.value.title = fetchedSeries.title
      series.value.slug = fetchedSeries.slug
      series.value.description = fetchedSeries.description || ''
      loadedSeries.value = fetchedSeries
      if (fetchedSeries.slug && fetchedSeries.slug !== generateSlug(fetchedSeries.title)) {
        slugManuallyEdited.value = true;
      }
    } catch (error) {
      console.error('Error fetching series details:', error)
      toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load series details', life: 3000 })
      router.push({ name: 'admin-series' })
    }
  } else {
    slugManuallyEdited.value = false;
  }
})

const handleSave = async () => {
  if (!validateForm()) {
    toast.add({ severity: 'warn', summary: 'Validation Error', detail: 'Please check the form for errors.', life: 3000 });
    return;
  }

  saving.value = true
  try {
    if (isEditing.value && seriesId.value) {
      await seriesApi.updateSeries({ seriesId: seriesId.value, seriesUpdate: series.value as SeriesUpdate })
      toast.add({ severity: 'success', summary: 'Success', detail: 'Series updated successfully', life: 3000 })
    } else {
      const newSeries = await seriesApi.createSeries({ seriesCreate: series.value })
      toast.add({ severity: 'success', summary: 'Success', detail: 'Series created successfully', life: 3000 })
      router.replace({ name: 'admin-series-edit', params: { id: newSeries.id.toString() }})
    }
  } catch (error) {
    console.error('Error saving series:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `Failed to ${isEditing.value ? 'update' : 'create'} series`,
      life: 3000
    })
  } finally {
    saving.value = false
  }
}

const cancel = () => {
  router.push({ name: 'admin-series' });
}
</script>

<style scoped>
/* Scoped styles if needed */
</style> 