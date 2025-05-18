<template>
  <div id="content" class="p-6">
    <Tabs v-model:value="activeTab">
      <TabList>
        <Tab value="0">Post Editor</Tab>
        <Tab value="1">Series Management</Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="0">
          <h1 class="text-2xl font-bold mb-6">{{ isEditing ? 'Edit Post' : 'Create New Post' }}</h1>
          
          <form @submit.prevent class="h-full">
            <div class="editor-container-wrapper">
              <div class="grid grid-cols-3 gap-4 mb-4" :class="{ 'hidden': isExpanded }">
                <div class="col-span-2">
                  <label for="title" class="block mb-2 font-medium">Title</label>
                  <input
                    id="title"
                    v-model="post.title"
                    type="text"
                    class="w-full p-2 border rounded-lg"
                    required
                  >
                </div>

                <div>
                  <label for="publishedAt" class="block mb-2 font-medium">Published Date</label>
                  <DatePicker
                    v-model="post.publishedAt"
                    showTime
                    hourFormat="24"
                    showIcon
                    size="small"
                    fluid
                  />
                </div>

                <div class="col-span-2">
                  <label for="slug" class="block mb-2 font-medium">Slug</label>
                  <input
                    id="slug"
                    v-model="post.slug"
                    type="text"
                    class="w-full p-2 border rounded-lg"
                    required
                    @input="handleSlugInput"
                  >
                </div>
              </div>

              <div class="mb-4 editor-wrapper fixed-editor-height" :class="{ 'expanded': isExpanded }">
                <MarkdownEditor
                  v-model="postContent"
                  label="Content"
                  :post-id="postId"
                  @file-upload="handleImageUpload"
                />
              </div>

              <div class="button-container" :class="{ 'hidden': isExpanded }">
                <div class="flex gap-4">
                  <Button
                    type="button"
                    size="small"
                    label="Save"
                    @click="handleSave(false)"
                  />
                  <Button
                    type="button"
                    size="small"
                    label="Save & Back"
                    @click="handleSave(true)"
                  />
                  <Button
                    type="button"
                    severity="secondary"
                    size="small"
                    label="Cancel"
                    @click="$router.push({ name: 'admin-posts' })"
                  />
                </div>
              </div>
            </div>
          </form>
        </TabPanel>
        <TabPanel value="1">
          <!-- Series Management Section -->
          <div class="mt-4">
            <h2 class="text-xl font-semibold mb-4">Series Management</h2>
            <div class="flex flex-col gap-4">
              <!-- Associate with existing series -->
              <Dropdown
                v-model="selectedSeries"
                :options="availableSeries"
                optionLabel="name"
                placeholder="Select a series"
                :disabled="!postId"
                class="w-full md:w-40"
                @change="handleSeriesChange"
              />
              <div class="flex gap-2">
                <!-- Disassociate -->
                <Button
                  v-if="selectedSeries && postId"
                  label="Remove from Series"
                  severity="secondary"
                  size="small"
                  @click="handleDisassociateSeries"
                />
                <!-- Create new series -->
                <Button
                  v-if="postId"
                  label="Create New Series"
                  icon="pi pi-plus"
                  size="small"
                  @click="showCreateSeries = true"
                />
              </div>
              <!-- List all series with delete option -->
              <div>
                <h3 class="font-medium mb-2">All Series</h3>
                <ul>
                  <li v-for="series in availableSeries" :key="series.id" class="flex items-center gap-2 mb-1">
                    <span>{{ series.title }}</span>
                    <Button
                      icon="pi pi-trash"
                      severity="danger"
                      size="small"
                      text
                      :disabled="!!series.post_count"
                      @click="handleDeleteSeries(series)"
                    />
                    <span v-if="series.post_count && series.post_count > 0" class="text-xs text-gray-400">({{ series.post_count }} posts)</span>
                  </li>
                </ul>
              </div>
            </div>
            <!-- Create Series Dialog -->
            <Dialog v-model:visible="showCreateSeries" header="Create New Series" :modal="true" :closable="true" :style="{ width: '400px' }">
              <div class="flex flex-col gap-4">
                <InputText v-model="newSeriesTitle" placeholder="Series Title" />
                <InputText v-model="newSeriesSlug" placeholder="Slug (optional)" />
                <div class="flex gap-2 justify-end">
                  <Button label="Cancel" severity="secondary" @click="showCreateSeries = false" />
                  <Button label="Create" @click="handleCreateSeries" :disabled="!newSeriesTitle.trim()" />
                </div>
              </div>
            </Dialog>
          </div>
        </TabPanel>
      </TabPanels>
    </Tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { PostsApi } from '@/lib/api/apis/PostsApi'
import type { PostUpdate } from '@/lib/api/models/PostUpdate'
import type { SeriesSummary } from '@/lib/api/models/SeriesSummary'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import DatePicker from 'primevue/datepicker'
import { useApiClient } from '@/composables/useApiClient'
import { useAuthStore } from '@/stores/auth'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import { SeriesApi } from '@/lib/api/apis/SeriesApi'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import { ResponseError } from '@/lib/api/runtime'

const router = useRouter()
const route = useRoute()
const toast = useToast()

const isExpanded = ref(false)
const isEditing = computed(() => route.params.id !== undefined)
const postId = ref<number | undefined>(undefined)
const post = ref<PostUpdate>({
  title: '',
  slug: '',
  content: '',
  publishedAt: null,
  seriesId: undefined
})

// Add this to track if slug was manually edited
const slugManuallyEdited = ref(false)

// Add refs for series selection
const availableSeries = ref<SeriesSummaryWithCount[]>([])
const selectedSeries = ref<SeriesSummaryWithCount | undefined>(undefined)
const loadingSeries = ref(false)

// Series management state
const showCreateSeries = ref(false)
const newSeriesTitle = ref('')
const newSeriesSlug = ref('')

const activeTab = ref('0')

// Add function to generate slug from title
const generateSlug = (title: string): string => {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-') // Replace non-alphanumeric chars with hyphen
    .replace(/^-+|-+$/g, '') // Remove leading/trailing hyphens
    .replace(/-+/g, '-') // Replace multiple consecutive hyphens with single hyphen
}

// Watch title changes and update slug if not manually edited
watch(() => post.value.title, (newTitle) => {
  if (!slugManuallyEdited.value) {
    post.value.slug = generateSlug(newTitle ?? '')
  }
})

// Watch selectedSeries and update post.seriesId
watch(selectedSeries, (newSeries) => {
  post.value.seriesId = newSeries ? newSeries.id : undefined;
});

// Add handler for manual slug edits
const handleSlugInput = () => {
  slugManuallyEdited.value = true
}

const loadAvailableSeries = async () => {
  loadingSeries.value = true;
  try {
    const seriesApi = useApiClient(SeriesApi)
    const response = await seriesApi.apiListSeries({ includePostsCount: true })
    availableSeries.value = response.items.map((s: any) => ({
      id: s.id,
      title: s.title,
      post_count: s.post_count ?? 0
    }))
    // If editing a post that has a seriesId, pre-select it
    if (post.value.seriesId) {
      selectedSeries.value = availableSeries.value.find((s: SeriesSummaryWithCount) => s.id === post.value.seriesId);
    }
  } catch (error) {
    console.error("Error loading series:", error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Could not load series list',
      life: 3000
    });
  } finally {
    loadingSeries.value = false;
  }
};

const handleImageUpload = async (files: File[]) => {
  const uploadedUrls: string[] = []
  const auth = useAuthStore()

  try {
    for (const file of files) {
      const formData = new FormData()
      formData.append('upload', file)

      const metadata = {
        visibility: 'public',
        posts: postId.value ? [postId.value] : []
      }

      formData.append('metadata', JSON.stringify(metadata))

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/files/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${auth.storedAccessToken}`
        },
        body: formData
      })

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`)
      }

      const fileMetadata = await response.json()
      uploadedUrls.push(fileMetadata.location)

      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: `Uploaded ${fileMetadata.name} successfully`,
        life: 3000
      })
    }

    // Insert the URLs into the editor at cursor position
    const urlsMarkdown = uploadedUrls.map(url => `![](${url})`).join('\n')
    post.value.content += '\n' + urlsMarkdown
  } catch (error) {
    console.error('Error uploading images:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to upload images',
      life: 3000
    })
  }
}

onMounted(async () => {
  loadAvailableSeries(); // Load series when component mounts
  if (isEditing.value) {
    try {
      const postsApi = useApiClient(PostsApi)
      const response = await postsApi.apiGetPostById({
        postId: parseInt(route.params.id as string)
      })
      console.log('Post loaded:', response)
      postId.value = response.id
      post.value = {
        title: response.title,
        slug: response.slug,
        content: response.content ?? '',
        publishedAt: response.publishedAt,
        seriesId: response.series?.id
      }
      // After post is loaded, if it has a seriesId, make sure selectedSeries is updated
      if (post.value.seriesId && availableSeries.value.length) {
         selectedSeries.value = availableSeries.value.find((s: SeriesSummaryWithCount) => s.id === post.value.seriesId);
      } else if (post.value.seriesId) {
        // If series aren't loaded yet but post has seriesId, selectedSeries will be set by loadAvailableSeries
      }
      console.log('Post content set:', post.value.content)
    } catch (error) {
      console.error('Error fetching post:', error)
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load post',
        life: 3000
      })
      router.push({ name: 'admin-posts' })
    }
  }
})

// Add auto-save functionality for unpublished posts
let autoSaveInterval: number | null = null

const startAutoSave = () => {
  if (autoSaveInterval) return // Don't start if already running
  
  autoSaveInterval = window.setInterval(async () => {
    // Only auto-save if we have an ID (existing post) and it's not published
    if (postId.value && !post.value.publishedAt) {
      try {
        const postsApi = useApiClient(PostsApi)
        await postsApi.apiUpdatePost({
          postId: postId.value,
          postUpdate: post.value
        })
        toast.add({
          severity: 'info',
          summary: 'Auto-saved',
          detail: 'Draft saved automatically',
          life: 2000
        })
      } catch (error) {
        console.error('Auto-save failed:', error)
        // Don't show error toast for auto-save failures to avoid spam
      }
    }
  }, 60000) // Run every minute
}

const stopAutoSave = () => {
  if (autoSaveInterval) {
    window.clearInterval(autoSaveInterval)
    autoSaveInterval = null
  }
}

// Start auto-save when conditions are met
watch(() => [postId.value, post.value.publishedAt], ([newId, isPublished]) => {
  if (newId && !isPublished) {
    startAutoSave()
  } else {
    stopAutoSave()
  }
}, { immediate: true })

// Clean up on component unmount
onUnmounted(() => {
  stopAutoSave()
})

const handleSave = async (shouldRedirect: boolean) => {
  // Ensure seriesId from selectedSeries is on post object before saving
  post.value.seriesId = selectedSeries.value ? selectedSeries.value.id : undefined;

  // Frontend validation for required fields
  if (!post.value.title || post.value.title.trim() === '' || !post.value.content || post.value.content.trim() === '') {
    toast.add({
      severity: 'error',
      summary: 'Validation Error',
      detail: 'Title and content are required.',
      life: 3000
    })
    return
  }

  try {
    if (isEditing.value) {
      const postsApi = useApiClient(PostsApi)
      await postsApi.apiUpdatePost({
        postId: parseInt(route.params.id as string),
        postUpdate: post.value
      })
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Post updated successfully',
        life: 3000
      })
      if (shouldRedirect) {
        router.push({ name: 'admin-posts' })
      }
    } else {
      const postsApi = useApiClient(PostsApi)
      const response = await postsApi.apiCreatePost({
        postCreate: {
          title: post.value.title ?? '',
          slug: post.value.slug ?? '',
          content: post.value.content ?? '',
          publishedAt: post.value.publishedAt ?? null,
          seriesId: post.value.seriesId ?? undefined
        }
      })
      postId.value = response.id // Set the post ID after creation
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Post created successfully',
        life: 3000
      })
      if (shouldRedirect) {
        router.push({ name: 'admin-posts' })
      } else {
        router.replace({ 
          name: 'admin-posts-edit',
          params: { id: response.id.toString() }
        })
      }
    }
  } catch (error) {
    console.error('Error saving post:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `Failed to ${isEditing.value ? 'update' : 'create'} post`,
      life: 3000
    })
  }
}

const postContent = computed({
  get: () => post.value.content ?? '',
  set: (val: string) => { post.value.content = val }
})

// Add post_count to SeriesSummary for UI
interface SeriesSummaryWithCount extends SeriesSummary {
  post_count?: number
}

// Handler stubs for series management
const handleSeriesChange = async () => {
  // TODO: Save post with new seriesId
}
const handleDisassociateSeries = async () => {
  if (!postId.value) return;
  try {
    post.value.seriesId = undefined;
    selectedSeries.value = undefined;
    const postsApi = useApiClient(PostsApi);
    await postsApi.apiUpdatePost({
      postId: postId.value,
      postUpdate: post.value
    });
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Post disassociated from series',
      life: 3000
    });
    // Optionally, reload series list if you want to update post counts
    await loadAvailableSeries();
  } catch (error) {
    console.error('Error disassociating series:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to remove post from series',
      life: 3000
    });
  }
};
const handleCreateSeries = async () => {
  // TODO: Call SeriesApi.apiCreateSeries, then associate post and refresh list
}
const handleDeleteSeries = async (series: SeriesSummaryWithCount) => {
  if (series.post_count && series.post_count > 0) {
    toast.add({
      severity: 'error',
      summary: 'Cannot Delete',
      detail: 'You can only delete a series with no posts.',
      life: 3000
    });
    return;
  }
  try {
    const seriesApi = useApiClient(SeriesApi);
    await seriesApi.apiDeleteSeries({ seriesId: series.id });
    toast.add({
      severity: 'success',
      summary: 'Deleted',
      detail: 'Series deleted successfully.',
      life: 3000
    });
    await loadAvailableSeries();
  } catch (error: unknown) {
    let detail = 'Failed to delete series.';
    if (error instanceof ResponseError) {
      const data = await error.response.json();
      if (data.detail) {
        detail = data.detail;
      }
    }
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail,
      life: 3000
    });
  }
};
</script>

<style>
.button-container {
  margin-top: 1rem;
  position: relative;
  z-index: 1;
}
.fixed-editor-height {
  height: 32rem;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
</style>