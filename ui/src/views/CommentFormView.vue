<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div v-if="loading" class="flex justify-center items-center min-h-[200px]">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
    </div>
    
    <div v-else-if="error" class="text-red-600 dark:text-red-400 mb-4">
      {{ error }}
    </div>
    
    <template v-else-if="!isLoggedIn">
      <div class="bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-700 rounded-md p-4 mb-6">
        <p class="text-yellow-700 dark:text-yellow-300 mb-3">You need to be logged in to post a comment.</p>
        <div class="flex space-x-4">
          <button 
            @click="login" 
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary dark:focus:ring-offset-gray-900"
          >
            Log in
          </button>
          <button 
            @click="signup" 
            class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md shadow-sm text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary dark:focus:ring-offset-gray-900"
          >
            Sign up
          </button>
        </div>
      </div>
    </template>
    
    <template v-else>
      <h1 class="text-2xl font-bold mb-6 dark:text-white">Add a Comment to "{{ post?.title }}"</h1>
      
      <div v-if="submitted" class="bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-700 rounded-md p-4 mb-6">
        <p class="text-green-700 dark:text-green-300">Your comment has been submitted and is awaiting approval. Thank you!</p>
        <router-link 
          :to="`/post/${route.params.year}/${route.params.slug}`" 
          class="mt-2 inline-block text-primary hover:underline"
        >
          Return to post
        </router-link>
      </div>
      
      <form v-else @submit.prevent="submitComment" class="space-y-4">
        <div>
          <label for="content" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Comment</label>
          <textarea 
            id="content" 
            v-model="form.content" 
            rows="6" 
            required
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          ></textarea>
        </div>
        
        <div class="flex items-center justify-between">
          <button 
            type="submit" 
            class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary dark:focus:ring-offset-gray-900"
            :disabled="submitting"
          >
            <span v-if="submitting">Submitting...</span>
            <span v-else>Submit Comment</span>
          </button>
          
          <router-link 
            :to="`/post/${route.params.year}/${route.params.slug}`" 
            class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:underline"
          >
            Cancel
          </router-link>
        </div>
      </form>
    </template>
    
    <!-- Add the login dialog component -->
    <LoginDialog v-model:visible="showLoginDialog" />
    <SignupDialog v-model:visible="showSignupDialog" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useApiClient } from '@/composables/useApiClient'
import { PostsApi, CommentsApi } from '@/lib/api'
import type { PostDetails, CommentCreate } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import LoginDialog from '@/components/LoginDialog.vue'
import SignupDialog from '@/components/SignupDialog.vue'

const route = useRoute()
const posts = useApiClient(PostsApi)
const commentsApi = useApiClient(CommentsApi)
const authStore = useAuthStore()

// Create refs for dialog visibility
const showLoginDialog = ref(false)
const showSignupDialog = ref(false)

const isLoggedIn = computed(() => authStore.isLoggedIn)
const post = ref<PostDetails | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const submitting = ref(false)
const submitted = ref(false)

const form = ref<CommentCreate>({
  content: '',
  postId: 0,
  parentId: null
})

function login() {
  // Store the current URL to redirect back after login
  authStore.setRedirectUrl(route.fullPath)
  
  // Show the login dialog directly
  showLoginDialog.value = true
}

function signup() {
  // Store the current URL to redirect back after signup
  authStore.setRedirectUrl(route.fullPath)
  
  // Show the signup dialog directly
  showSignupDialog.value = true
}

onMounted(async () => {
  try {
    const slug = route.params.slug as string
    const year = route.params.year as string
    
    // Load the post to get its ID and title
    const postResult = await posts.getPostBySlugAndYear({ slug: slug, year: +year })
    post.value = {
      id: postResult.id,
      title: postResult.title,
      content: postResult.content,
      createdAt: postResult.createdAt,
      updatedAt: postResult.updatedAt,
      published: postResult.publishedAt,
      authorId: postResult.author?.id ?? 0,
      slug: postResult.slug,
      series: postResult.series ? { id: postResult.series.id, title: postResult.series.title } : undefined
    }
    
    if (post.value && post.value.id) {
      form.value.postId = post.value.id
    } else {
      throw new Error('Post not found')
    }
  } catch (e) {
    error.value = 'Failed to load blog post'
    console.error(e)
  } finally {
    loading.value = false
  }
})

async function submitComment() {
  if (!isLoggedIn.value) {
    login()
    return
  }
  
  if (!form.value.postId) {
    error.value = 'Invalid post'
    return
  }
  
  try {
    submitting.value = true
    await commentsApi.createComment({ 
      commentCreate: form.value
    })
    submitted.value = true
  } catch (e) {
    error.value = 'Failed to submit comment. Please try again.'
    console.error(e)
  } finally {
    submitting.value = false
  }
}
</script> 