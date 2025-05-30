<template>
  <div>
    <div id="content" class="">
      <h1 class="text-2xl font-bold">Blog Posts</h1>
      <Toolbar class="mb-6">
        <template #start>
          <router-link :to="{ name: 'admin-posts-new' }">
            <Button v-tooltip.bottom="{ value: 'Create New Post', showDelay: 1000 }" icon="pi pi-plus" aria-label="Create New Post" class="mr-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600" text />
          </router-link>
        </template>
        <template #center>
          <div class="flex items-center gap-4">
            <SelectButton v-model="filterStatus" optionLabel="label" :options="filterOptions" aria-label="Post Status" />
          </div>
        </template>
        <template #end>
          
        </template>
      </Toolbar>

      <div class="space-y-4">
        <div v-if="loading" class="text-gray-600">Loading posts...</div>
        
        <div v-else-if="error" class="text-red-600">
          Error loading posts: {{ error }}
        </div>

        <div v-else-if="!posts.length" class="text-gray-600">
          No posts found
        </div>

        <div v-else class="divide-y">
          <div v-for="post in posts" :key="post.id" class="py-4">
            <div class="flex justify-between items-start">
              <div>
                <div class="flex items-center gap-2">
                  <h2 class="text-xl font-semibold">{{ post.title }}</h2>
                  <Badge v-if="!post.publishedAt" value="Draft" severity="warning" />
                </div>
                <div class="flex flex-row flex-wrap items-center gap-4 mt-1 text-gray-500 text-xs">
                  <span class="flex items-center gap-1" v-tooltip.bottom="{ value: new Date(post.createdAt).toLocaleString(), showDelay: 500 }">
                    <i class="pi pi-calendar"></i>
                    <span>Created</span>
                    <span>
                      {{ getRelativeDate(new Date(post.createdAt)) }}
                    </span>
                  </span>
                  <span class="flex items-center gap-1" v-tooltip.bottom="{ value: new Date(post.updatedAt).toLocaleString(), showDelay: 500 }">
                    <i class="pi pi-clock"></i>
                    <span>Updated</span>
                    <span>
                      {{ getRelativeDate(new Date(post.updatedAt)) }}
                    </span>
                  </span>
                  <span
                    v-if="post.publishedAt"
                    class="flex items-center gap-1"
                    v-tooltip.bottom="{ value: new Date(post.publishedAt).toLocaleString(), showDelay: 500 }"
                  >
                    <i class="pi pi-calendar"></i>
                    <span>Published</span>
                    <span>{{ getRelativeDate(new Date(post.publishedAt)) }}</span>
                  </span>
                </div>
                <p class="mt-2">{{ post.content.substring(0, 150) }}...</p>
              </div>
              <div class="flex flex-col gap-2 items-end">
                <router-link 
                  :to="{ name: 'admin-posts-edit', params: { id: post.id }}"
                  class="px-3 py-1 bg-emerald-100 text-emerald-700 rounded hover:bg-emerald-200 dark:bg-emerald-900 dark:text-emerald-100 dark:hover:bg-emerald-800"
                >
                  Edit
                </router-link>
                <Button
                  v-if="!post.publishedAt"
                  icon="pi pi-trash"
                  severity="danger"
                  size="small"
                  text
                  label="Delete"
                  @click="confirmDeletePost(post)"
                  class="mt-2"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <ConfirmDialog></ConfirmDialog>
    <!-- Router view for nested routes (like new post form) -->
    <router-view></router-view>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useApiClient } from '@/composables/useApiClient'
import { PostsApi, type ListPostsRequest } from '@/lib/api/apis/PostsApi'
import type { PostListPublic } from '@/lib/api/models'
import Badge from 'primevue/badge'
import Toolbar from 'primevue/toolbar'
import SelectButton from 'primevue/selectbutton'
import Button from 'primevue/button'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'

const posts = ref<PostListPublic[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const filterOptions = [
  { label: 'Published', value: 'published' },
  { label: 'Drafts', value: 'drafts' },
  { label: 'All Posts', value: 'all' }
]

const filterStatus = ref({ label: 'Published', value: 'published' })

const confirm = useConfirm()
const toast = useToast()

function getRelativeDate(date: Date): string {
  const now = new Date()
  const diff = (now.getTime() - date.getTime()) / 1000 // seconds
  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)} min ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)} hour${Math.floor(diff / 3600) === 1 ? '' : 's'} ago`
  if (diff < 604800) return `${Math.floor(diff / 86400)} day${Math.floor(diff / 86400) === 1 ? '' : 's'} ago`
  return date.toLocaleDateString()
}

const loadPosts = async () => {
  const client = useApiClient(PostsApi)
  try {
    loading.value = true
    error.value = null

    console.log("Filter status: ", filterStatus.value)
    
    const queryParams: ListPostsRequest = {}
    if (filterStatus.value.value === 'all') {
      queryParams.allPosts = true
      queryParams.drafts = true
    } else {
      queryParams.drafts = filterStatus.value.value !== 'published'
    }
    
    const response = await client.listPosts(queryParams)
    posts.value = response.items
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'An error occurred'
  } finally {
    loading.value = false
  }
}

// Watch for filter changes and reload posts
watch(filterStatus, () => {
  loadPosts()
})

const deletePost = async (postId: number) => {
  try {
    const client = useApiClient(PostsApi)
    await client.deletePost({ postId })
    toast.add({ severity: 'success', summary: 'Deleted', detail: 'Post deleted successfully', life: 3000 })
    await loadPosts()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete post', life: 3000 })
  }
}

const confirmDeletePost = (post: PostListPublic) => {
  confirm.require({
    message: `Are you sure you want to delete the post "${post.title}"? This action cannot be undone.`,
    header: 'Confirm Deletion',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: () => deletePost(post.id),
    reject: () => {
      toast.add({ severity: 'info', summary: 'Cancelled', detail: 'Deletion cancelled', life: 2000 })
    }
  })
}

onMounted(() => {
  loadPosts()
  document.title = 'Admin: Posts – ooo-yay.com'
})
</script> 