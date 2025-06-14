<template>
  <div id="content" class="p-6">
    <Tabs v-model:value="activeTab">
      <TabList>
        <Tab value="0">Post Editor</Tab>
        <Tab value="1">Series Management</Tab>
        <Tab v-if="isEditing" value="2">Share Codes</Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="0">
          <h1 class="text-2xl font-bold mb-6">{{ isEditing ? 'Edit Post' : 'Create New Post' }}</h1>
          
          <!-- Created/Updated At Box -->
          <div v-if="isEditing && post.createdAt" class="mb-4 p-3 rounded bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 flex w-full items-center text-xs text-gray-600 dark:text-gray-300">
            <div class="flex gap-6">
              <span class="flex items-center gap-1">
                <i class="pi pi-calendar"></i>
                <span>Created:</span>
                <span>{{ post.createdAt ? new Date(post.createdAt).toLocaleString() : '' }}</span>
              </span>
              <span class="flex items-center gap-1">
                <i class="pi pi-clock"></i>
                <span>Updated:</span>
                <span>{{ post.updatedAt ? new Date(post.updatedAt).toLocaleString() : '' }}</span>
              </span>
            </div>
            <div v-if="!post.publishedAt" class="ml-auto">
              <Button
                icon="pi pi-trash"
                severity="danger"
                size="small"
                label="Delete Post"
                @click="confirmDeletePost()"
              />
            </div>
          </div>

          <form @submit.prevent class="h-full">
            <div class="editor-container-wrapper">
              <div class="grid grid-cols-3 gap-4 mb-4" :class="{ 'hidden': isExpanded }">
                <div class="col-span-2">
                  <label for="title" class="block mb-2 font-medium">Title</label>
                  <InputText
                    id="title"
                    v-model="post.title"
                    type="text"
                    class="w-full h-11"
                    required
                    size="small"
                  />
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
                    class="h-11 w-full"
                  />
                </div>

                <div class="col-span-2">
                  <label for="slug" class="block mb-2 font-medium">Slug</label>
                  <InputText
                    id="slug"
                    v-model="post.slug"
                    type="text"
                    class="w-full h-11"
                    required
                    @input="handleSlugInput"
                    size="small"
                  />
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

              <div class="button-container bg-white dark:bg-neutral-900 p-4 flex gap-4 border-t border-gray-200 dark:border-neutral-700 mt-4 shadow-sm" :class="{ 'hidden': isExpanded }">
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
                optionLabel="title"
                placeholder="Select a series"
                :disabled="!postId"
                class="w-64"
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
                  class="w-40"
                />
                <!-- Create new series -->
                <Button
                  v-if="postId"
                  label="Create New Series"
                  icon="pi pi-plus"
                  size="small"
                  @click="showCreateSeries = true"
                  class="w-48 whitespace-nowrap"
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
        <TabPanel v-if="isEditing" value="2">
          <!-- Share Codes Management (only for drafts) -->
          <div v-if="!post.publishedAt" class="mb-4 p-3 rounded bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700">
            <div class="flex items-center mb-2">
              <span class="font-semibold text-blue-700 dark:text-blue-300">Share Codes</span>
              <Button size="small" icon="pi pi-plus" label="New Share Code" class="ml-auto" @click="showCreateShareCode = true" />
            </div>
            <div v-if="loadingShareCodes" class="text-xs text-blue-500">Loading share codes...</div>
            <div v-else-if="shareCodes.length === 0" class="text-xs text-blue-500">No share codes created yet.</div>
            <ul v-else class="divide-y divide-blue-100 dark:divide-blue-800">
              <li v-for="sc in shareCodes" :key="sc.id" class="flex items-center py-2 gap-2">
                <span class="font-mono bg-blue-100 dark:bg-blue-800 px-2 py-1 rounded text-xs select-all">{{ sc.code }}</span>
                <Button icon="pi pi-copy" size="small" text class="ml-1" :aria-label="'Copy share link for code ' + sc.code" @click="copyShareCode(sc.code)" />
                <span v-if="copiedCode === sc.code" class="text-green-600 text-xs ml-1">Copied!</span>
                <span v-if="sc.note" class="ml-2 text-xs text-blue-700 dark:text-blue-300 italic">{{ sc.note }}</span>
                <span v-if="sc.expiresAt" class="ml-2 text-xs text-blue-400">(expires {{ new Date(sc.expiresAt).toLocaleString() }})</span>
                <Button icon="pi pi-trash" size="small" text severity="danger" class="ml-auto" @click="deleteShareCode(sc)" />
              </li>
            </ul>
            <!-- Create Share Code Dialog -->
            <Dialog v-model:visible="showCreateShareCode" header="Create Share Code" :modal="true" :closable="true" :style="{ width: '400px' }">
              <div class="flex flex-col gap-4">
                <InputText v-model="newShareCodeNote" placeholder="Note (optional)" />
                <label class="text-xs">Expiry (optional)</label>
                <DatePicker v-model="newShareCodeExpiry" showTime hourFormat="24" showIcon size="small" fluid class="w-full" />
                <div class="flex gap-2 justify-end">
                  <Button label="Cancel" severity="secondary" @click="showCreateShareCode = false" />
                  <Button label="Create" @click="createShareCode" :disabled="creatingShareCode" />
                </div>
              </div>
            </Dialog>
          </div>
          <div v-else class="text-xs text-blue-500">Share codes are only available for draft posts.</div>
        </TabPanel>
      </TabPanels>
    </Tabs>
    <ConfirmDialog></ConfirmDialog>
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
import { DatePicker } from 'primevue'
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
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'
import type { ShareCodeSchema } from '@/lib/api/models/ShareCodeSchema'
import type { ShareCodeCreate } from '@/lib/api/models/ShareCodeCreate'

const router = useRouter()
const route = useRoute()
const toast = useToast()
const confirm = useConfirm()

const isExpanded = ref(false)
const isEditing = computed(() => route.params.id !== undefined)
const postId = ref<number | undefined>(undefined)
const post = ref<PostUpdate & { createdAt?: string | Date | null, updatedAt?: string | Date | null }>({
  title: '',
  slug: '',
  content: '',
  publishedAt: null,
  seriesId: undefined,
  createdAt: null,
  updatedAt: null
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

const shareCodes = ref<ShareCodeSchema[]>([])
const loadingShareCodes = ref(false)
const showCreateShareCode = ref(false)
const newShareCodeNote = ref('')
const newShareCodeExpiry = ref<Date | null>(null)
const creatingShareCode = ref(false)
const copiedCode = ref<string | null>(null)

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
    const response = await seriesApi.listSeries({ includePostsCount: true })
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
      const response = await postsApi.getPostById({
        postId: parseInt(route.params.id as string)
      })
      console.log('Post loaded:', response)
      postId.value = response.id
      post.value = {
        title: response.title,
        slug: response.slug,
        content: response.content ?? '',
        publishedAt: response.publishedAt,
        seriesId: response.series?.id,
        createdAt: response.createdAt ?? null,
        updatedAt: response.updatedAt ?? null
      }
      // Set document title for editing
      document.title = `Edit Post: ${post.value.title} – Admin – ooo-yay.com`
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
  } else {
    // Set document title for new post
    document.title = 'Create Post – Admin – ooo-yay.com'
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
        await postsApi.updatePost({
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
      await postsApi.updatePost({
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
      const response = await postsApi.createPost({
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
          name: 'admin-posts-edit-id',
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
    await postsApi.updatePost({
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
  // TODO: Call SeriesApi.createSeries, then associate post and refresh list
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
    await seriesApi.deleteSeries({ seriesId: series.id });
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

const deletePost = async () => {
  if (!postId.value) return;
  try {
    const postsApi = useApiClient(PostsApi);
    await postsApi.deletePost({ postId: postId.value });
    toast.add({ severity: 'success', summary: 'Deleted', detail: 'Post deleted successfully', life: 3000 });
    router.push({ name: 'admin-posts' });
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete post', life: 3000 });
  }
};

const confirmDeletePost = () => {
  confirm.require({
    message: `Are you sure you want to delete this draft post? This action cannot be undone.`,
    header: 'Confirm Deletion',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: () => deletePost(),
    reject: () => {
      toast.add({ severity: 'info', summary: 'Cancelled', detail: 'Deletion cancelled', life: 2000 });
    }
  });
};

const loadShareCodes = async () => {
  if (!postId.value) return
  loadingShareCodes.value = true
  try {
    const postsApi = useApiClient(PostsApi)
    shareCodes.value = await postsApi.listSharecodes({ postId: postId.value })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load share codes', life: 3000 })
  } finally {
    loadingShareCodes.value = false
  }
}

const createShareCode = async () => {
  if (!postId.value) return
  creatingShareCode.value = true
  try {
    const postsApi = useApiClient(PostsApi)
    const payload: ShareCodeCreate = {
      note: newShareCodeNote.value || undefined,
      expiresAt: newShareCodeExpiry.value || undefined
    }
    await postsApi.createSharecode({ postId: postId.value, shareCodeCreate: payload })
    showCreateShareCode.value = false
    newShareCodeNote.value = ''
    newShareCodeExpiry.value = null
    await loadShareCodes()
    toast.add({ severity: 'success', summary: 'Created', detail: 'Share code created', life: 2000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to create share code', life: 3000 })
  } finally {
    creatingShareCode.value = false
  }
}

const deleteShareCode = async (sc: ShareCodeSchema) => {
  if (!postId.value) return
  try {
    const postsApi = useApiClient(PostsApi)
    await postsApi.deleteSharecode({ postId: postId.value, code: sc.code })
    await loadShareCodes()
    toast.add({ severity: 'success', summary: 'Deleted', detail: 'Share code deleted', life: 2000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete share code', life: 3000 })
  }
}

const copyShareCode = async (code: string) => {
  try {
    // Compose the full share URL
    const origin = window.location.origin
    const year = post.value.publishedAt
      ? new Date(post.value.publishedAt).getFullYear()
      : new Date().getFullYear()
    const slug = post.value.slug
    const url = `${origin}/blog/${year}/${slug}?sharecode=${code}`
    await navigator.clipboard.writeText(url)
    copiedCode.value = code
    setTimeout(() => {
      if (copiedCode.value === code) copiedCode.value = null
    }, 1500)
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to copy link', life: 2000 })
  }
}

// Load share codes after post is loaded (if editing and not published)
watch([postId, () => post.value.publishedAt], ([id, published]) => {
  if (id && !published) loadShareCodes()
})
</script>

<style scoped>
.fixed-editor-height {
  height: 32rem;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
</style>