<template>
  <div>
    <div class="p-6">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold">Blog Posts</h1>
        <router-link 
          :to="{ name: 'admin-posts-new' }"
          class="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600"
        >
          Create New Post
        </router-link>
      </div>

      <div class="space-y-4">
        <div v-if="loading" class="text-gray-600">Loading posts...</div>
        
        <div v-else-if="error" class="text-red-600">
          Error loading posts: {{ error }}
        </div>

        <div v-else-if="!posts.length" class="text-gray-600">
          No posts yet
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
import { ref, onMounted } from 'vue'
import { useApiClient } from '@/composables/useApiClient'
import { PostsApi } from '@/lib/api/apis/PostsApi'
import type { PostDetails } from '@/lib/api/models'
import Badge from 'primevue/badge'

const posts = ref<PostDetails[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const loadPosts = async () => {
  const client = useApiClient(PostsApi)
  try {
    loading.value = true
    const response = await client.apiListPosts({ all: true })
    posts.value = response.items
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'An error occurred'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPosts()
})
</script> 