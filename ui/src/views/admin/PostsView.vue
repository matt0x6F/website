<template>
  <div>
    <div class="">
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
                  <Badge v-if="!post.published" value="Draft" severity="warning" />
                </div>
                <p class="text-gray-600 mt-1">
                  {{ new Date(post.createdAt).toLocaleDateString() }}
                </p>
                <p class="mt-2">{{ post.content.substring(0, 150) }}...</p>
              </div>
              <router-link 
                :to="{ name: 'admin-posts-edit', params: { id: post.id }}"
                class="px-3 py-1 bg-emerald-100 text-emerald-700 rounded hover:bg-emerald-200 dark:bg-emerald-900 dark:text-emerald-100 dark:hover:bg-emerald-800"
              >
                Edit
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Router view for nested routes (like new post form) -->
    <router-view></router-view>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useApiClient } from '@/composables/useApiClient'
import { PostsApi, type ApiListPostsRequest } from '@/lib/api/apis/PostsApi'
import type { PostDetails } from '@/lib/api/models'
import Badge from 'primevue/badge'
import Toolbar from 'primevue/toolbar'
import SelectButton from 'primevue/selectbutton'
import Button from 'primevue/button'

const posts = ref<PostDetails[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const filterOptions = [
  { label: 'Published', value: 'published' },
  { label: 'Drafts', value: 'drafts' },
  { label: 'All Posts', value: 'all' }
]

const filterStatus = ref({ label: 'Published', value: 'published' })

const loadPosts = async () => {
  const client = useApiClient(PostsApi)
  try {
    loading.value = true
    error.value = null

    console.log("Filter status: ", filterStatus.value)
    
    const queryParams: ApiListPostsRequest = {}
    if (filterStatus.value.value === 'all') {
      queryParams.all = true
      queryParams.drafts = true
    } else {
      queryParams.drafts = filterStatus.value.value !== 'published'
    }
    
    const response = await client.apiListPosts(queryParams)
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

onMounted(() => {
  loadPosts()
})
</script> 