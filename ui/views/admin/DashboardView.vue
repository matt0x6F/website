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

    <!-- Calendar Heatmap -->
    <div class="mt-10">
      <h2 class="text-xl font-semibold mb-4">Posts Calendar Heatmap</h2>
      <CalendarHeatmap :data="calendarHeatmapData" :today="today" @select="onHeatmapSelect" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { PostsApi } from '@/lib/api/apis/PostsApi'
import { AccountsApi } from '@/lib/api/apis/AccountsApi'
import { Configuration } from '@/lib/api'
import CalendarHeatmap from '@/components/CalendarHeatmap.vue'

const authStore = useAuthStore()
const publishedPostCount = ref(0)
const totalPostCount = ref(0)
const userCount = ref(0)
const calendarHeatmapData = ref<{ date: string, count: number }[]>([])
const today = new Date().toISOString().slice(0, 10)

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
    const response = await postsApi.listPosts({ allPosts: false })
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
    const response = await postsApi.listPosts({ allPosts: true })
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
    const response = await accountsApi.listUsers()
    userCount.value = response.count || 0
  } catch (error) {
    console.error('Failed to fetch user count:', error)
    userCount.value = 0
  }
}

const fetchPublishedPostsForHeatmap = async () => {
  try {
    const config = new Configuration({
      basePath: import.meta.env.VITE_API_URL,
      headers: {
        Authorization: `Bearer ${authStore.storedAccessToken}`
      }
    })
    const postsApi = new PostsApi(config)
    const limit = 100
    let offset = 0
    let allPosts: any[] = []
    let total = 0
    do {
      const response = await postsApi.listPosts({ allPosts: false, order: 'published_at', limit, offset })
      const posts = response.items || []
      if (offset === 0) total = response.count || 0
      allPosts = allPosts.concat(posts)
      offset += limit
    } while (allPosts.length < total)
    // Group by publishedAt date
    const counts: Record<string, number> = {}
    for (const post of allPosts) {
      let dateObj: Date | null = null;
      if (post.publishedAt) {
        if (typeof post.publishedAt === 'string') {
          dateObj = new Date(post.publishedAt);
        } else if (post.publishedAt instanceof Date) {
          dateObj = post.publishedAt;
        }
      }
      if (dateObj && !isNaN(dateObj.getTime())) {
        const dateStr = dateObj.toISOString().slice(0, 10);
        counts[dateStr] = (counts[dateStr] || 0) + 1;
      }
    }
    calendarHeatmapData.value = Object.entries(counts).map(([date, count]) => ({ date, count }))
    console.log('calendarHeatmapData', calendarHeatmapData.value)
  } catch (error) {
    console.error('Failed to fetch posts for heatmap:', error)
    calendarHeatmapData.value = []
  }
}

function onHeatmapSelect(day: { date: string, count: number }) {
  // You can handle cell selection here (e.g., show a modal or filter posts)
  if (day.count > 0) {
    alert(`Posts published on ${day.date}: ${day.count}`)
  }
}

onMounted(() => {
  if (typeof window === 'undefined') return; // Only run on client
  watch(
    () => authStore.userData.isStaff,
    (isStaff) => {
      if (isStaff) {
        document.title = 'Admin Dashboard – ooo-yay.com'
        fetchPublishedPostCount()
        fetchTotalPostCount()
        fetchUserCount()
        fetchPublishedPostsForHeatmap()
      } else {
        console.warn('Non-staff user accessed admin dashboard')
      }
    },
    { immediate: true }
  )
})
</script> 