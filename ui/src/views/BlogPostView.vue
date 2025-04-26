<template>
  <div id="content" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div v-if="loading" class="flex justify-center items-center min-h-[200px]">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
    </div>
    
    <div v-else-if="error" class="text-red-600">
      {{ error }}
    </div>
    
    <template v-else-if="post">
      <article class="mb-8">
        <header class="mb-8">
          <h1 class="text-4xl font-bold mb-2">{{ post.title }}</h1>
          <div v-if="post.published" class="text-sm text-gray-500 italic">
            Published {{ new Date(post.published).toLocaleDateString() }}
          </div>
        </header>
        
        <!-- Use MdPreview to render markdown content -->
        <MdPreview :id="id" :modelValue="post.content" preview-theme="vuepress" />
      </article>
      
      <!-- Comments section -->
      <div class="mt-8">
        <div v-if="!isLoggedIn && comments.length === 0" class="text-center py-6 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p class="text-gray-600 dark:text-gray-300 mb-4">
            Sign in to be the first to share your thoughts on this post!
          </p>
          <div class="flex justify-center space-x-4">
            <button 
              @click="showLoginDialog = true" 
              class="px-4 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700"
            >
              Sign In
            </button>
            <button 
              @click="showSignupDialog = true" 
              class="px-4 py-2 border border-gray-300 rounded hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700"
            >
              Sign Up
            </button>
          </div>
        </div>
        
        <Comments 
          :comments="comments" 
          :postId="post.id" 
          @refresh-comments="loadComments" 
        />
      </div>
    </template>
    
    <!-- Login/Signup dialogs -->
    <LoginDialog v-model:visible="showLoginDialog" />
    <SignupDialog v-model:visible="showSignupDialog" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useApiClient } from '@/composables/useApiClient'
import { PostsApi, CommentsApi } from '@/lib/api'
import type { PostDetails, CommentList } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import Comments from '@/components/Comments.vue'
import LoginDialog from '@/components/LoginDialog.vue'
import SignupDialog from '@/components/SignupDialog.vue'
import { MdPreview, MdCatalog } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'

const route = useRoute()
const posts = useApiClient(PostsApi)
const commentsApi = useApiClient(CommentsApi)
const authStore = useAuthStore()

const post = ref<PostDetails | null>(null)
const comments = ref<CommentList[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const showLoginDialog = ref(false)
const showSignupDialog = ref(false)

const isLoggedIn = computed(() => authStore.isLoggedIn)

const id = 'preview-only'
const scrollElement = document.documentElement

onMounted(async () => {
  try {
    const slug = route.params.slug as string
    const year = route.params.year as string
    
    // First load the post
    const postResult = await posts.apiGetPostBySlug({ slug: slug, year: +year })
    post.value = postResult
    
    // Then load comments using the post's ID
    await loadComments()
  } catch (e) {
    error.value = 'Failed to load blog post'
    console.error(e)
  } finally {
    loading.value = false
  }
})

// Function to reload comments
async function loadComments() {
  if (post.value && post.value.id) {
    const commentsResult = await commentsApi.apiListComments({ 
      postId: post.value.id,
      topLevel: true 
    })
    comments.value = commentsResult.items || []
  }
}
</script> 