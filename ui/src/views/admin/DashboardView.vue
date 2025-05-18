<template>
  <div class="p-6">
    <h1 class="text-3xl font-bold mb-6">Dashboard</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Stats Card -->
      <div class="rounded-lg p-6 border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-md transition-all">
        <h2 class="text-xl font-semibold mb-4">Quick Stats</h2>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span>Total Users</span>
            <span class="font-medium">{{ userCount }}</span>
          </div>
          <div class="flex justify-between">
            <span>Published Posts</span>
            <span class="font-medium">{{ publishedPostCount }}</span>
          </div>
          <div class="flex justify-between">
            <span>Draft Posts</span>
            <span class="font-medium">{{ draftPostCount }}</span>
          </div>
        </div>
      </div>

      <!-- Recent Activity Card -->
      <div class="rounded-lg p-6 border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-md transition-all">
        <h2 class="text-xl font-semibold mb-4">Recent Activity</h2>
        <div class="space-y-3">
          <p class="text-sm">No recent activity</p>
        </div>
      </div>

      <!-- Quick Actions Card -->
      <div class="rounded-lg p-6 border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-md transition-all">
        <h2 class="text-xl font-semibold mb-4">Quick Actions</h2>
        <div class="space-y-3">
          <button 
            @click="router.push('/admin/posts/new')" 
            class="w-full px-4 py-2 text-sm rounded bg-green-100 dark:bg-green-950/50 text-green-700 dark:text-green-200 hover:bg-green-200 dark:hover:bg-green-900/50 shadow-sm hover:shadow-md transition-all cursor-pointer"
          >
            Create New Post
          </button>
          <button 
            @click="router.push('/admin/users')"
            class="w-full px-4 py-2 text-sm rounded bg-green-100 dark:bg-green-950/50 text-green-700 dark:text-green-200 hover:bg-green-200 dark:hover:bg-green-900/50 shadow-sm hover:shadow-md transition-all cursor-pointer"
          >
            Manage Users
          </button>
          <button class="w-full px-4 py-2 text-sm rounded bg-green-100 dark:bg-green-950/50 text-green-700 dark:text-green-200 hover:bg-green-200 dark:hover:bg-green-900/50 shadow-sm hover:shadow-md transition-all cursor-pointer">
            View Reports
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { PostsApi } from '@/lib/api/apis/PostsApi'
import { AccountsApi } from '@/lib/api/apis/AccountsApi'
import { Configuration } from '@/lib/api'

const authStore = useAuthStore()
const publishedPostCount = ref(0)
const totalPostCount = ref(0)
const userCount = ref(0)

const draftPostCount = computed(() => {
  return totalPostCount.value - publishedPostCount.value
})

const router = useRouter()

const fetchPublishedPostCount = async () => {
  try {
    const config = new Configuration({
      basePath: import.meta.env.VITE_API_URL,
      headers: {
        Authorization: `Bearer ${authStore.storedAccessToken}`
      }
    })
    const postsApi = new PostsApi(config)
    const response = await postsApi.apiListPosts({ allPosts: false })
    publishedPostCount.value = response.count || 0
  } catch (error) {
    console.error('Failed to fetch published post count:', error)
    publishedPostCount.value = 0
  }
}

const fetchTotalPostCount = async () => {
  try {
    const config = new Configuration({
      basePath: import.meta.env.VITE_API_URL,
      headers: {
        Authorization: `Bearer ${authStore.storedAccessToken}`
      }
    })
    const postsApi = new PostsApi(config)
    const response = await postsApi.apiListPosts({ allPosts: true })
    totalPostCount.value = response.count || 0
  } catch (error) {
    console.error('Failed to fetch total post count:', error)
    totalPostCount.value = 0
  }
}

const fetchUserCount = async () => {
  try {
    const config = new Configuration({
      basePath: import.meta.env.VITE_API_URL,
      headers: {
        Authorization: `Bearer ${authStore.storedAccessToken}`
      }
    })
    const accountsApi = new AccountsApi(config)
    const response = await accountsApi.apiListUsers()
    userCount.value = response.count || 0
  } catch (error) {
    console.error('Failed to fetch user count:', error)
    userCount.value = 0
  }
}

onMounted(() => {
  // Verify user is staff, though the router guard should prevent non-staff access
  if (!authStore.userData.isStaff) {
    console.warn('Non-staff user accessed admin dashboard')
    return
  }
  
  fetchPublishedPostCount()
  fetchTotalPostCount()
  fetchUserCount()
})
</script> 