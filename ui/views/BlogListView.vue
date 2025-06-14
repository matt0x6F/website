<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <h1 class="text-3xl font-bold mb-8">Blog Posts</h1>
    
    <div v-if="loading" class="text-center py-10">
      Loading posts...
    </div>
    
    <div v-else-if="error" class="text-center py-10 text-red-600">
      {{ error }}
    </div>
    
    <div v-else>
      <div class="divide-y divide-emerald-500/10">
        <div v-for="post in posts" :key="post.id" 
             class="py-4 transition">
          <div class="flex items-center justify-between gap-4">
            <h2 class="text-xl font-semibold">{{ post.title }}</h2>
            <div class="flex items-center gap-4">
              <p class="text-sm text-gray-600 whitespace-nowrap">
                {{ new Date(post.publishedAt || '').toLocaleDateString() }}
              </p>
              <NuxtLink 
                :to="`/blog/${new Date(post.publishedAt || '').getFullYear()}/${post.slug}`" 
                class="read-more underline hover:opacity-80 whitespace-nowrap"
              >
                Read more
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="total > limit" class="flex justify-center items-center gap-4 mt-8">
        <button 
          :disabled="offset === 0" 
          @click="loadPosts(offset - limit)"
          class="px-4 py-2 border-emerald-300 border rounded-md text-emerald-700 bg-emerald-50 hover:bg-emerald-100 transition disabled:opacity-50 disabled:cursor-not-allowed dark:bg-emerald-900 dark:text-emerald-200 dark:border-emerald-700 dark:hover:bg-emerald-800"
        >
          Previous
        </button>
        <span>Page {{ currentPage }} of {{ totalPages }}</span>
        <button 
          :disabled="offset + limit >= total" 
          @click="loadPosts(offset + limit)"
          class="px-4 py-2 border-emerald-300 border rounded-md text-emerald-700 bg-emerald-50 hover:bg-emerald-100 transition disabled:opacity-50 disabled:cursor-not-allowed dark:bg-emerald-900 dark:text-emerald-200 dark:border-emerald-700 dark:hover:bg-emerald-800"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { PostsApi } from '@/lib/api/apis/PostsApi'
import type { PostListPublic } from '@/lib/api/models'
import { Configuration, type ConfigurationParameters } from '@/lib/api'

const params: ConfigurationParameters = {
  basePath: import.meta.env.VITE_API_URL,
}
const config = new Configuration(params)
const postsApi = new PostsApi(config)

const posts = ref<PostListPublic[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const total = ref(0)
const offset = ref(0)
const limit = ref(10)

const currentPage = computed(() => Math.floor(offset.value / limit.value) + 1)
const totalPages = computed(() => Math.ceil(total.value / limit.value))

const loadPosts = async (newOffset: number) => {
  loading.value = true
  error.value = null
  offset.value = newOffset

  try {
    const response = await postsApi.listPosts({
      offset: offset.value,
      limit: limit.value
    })
    
    posts.value = response.items
    total.value = response.count
  } catch (e) {
    error.value = 'Failed to load posts. Please try again later.'
    console.error('Error loading posts:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPosts(0)
  document.title = 'Blog – ooo-yay.com'
})
</script>

<style scoped>
.blog-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.post-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  transition: transform 0.2s;
}

.post-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.post-meta {
  color: #666;
  font-size: 0.9em;
}

.post-excerpt {
  margin: 10px 0;
}

.read-more {
  color: #10b981;
  text-decoration: underline;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.pagination button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
}

.pagination button:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.loading, .error {
  text-align: center;
  margin: 40px 0;
}

.error {
  color: #dc3545;
}
</style>
