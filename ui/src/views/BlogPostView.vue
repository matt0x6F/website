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
        
        <MarkdownPreview :content="post?.content || ''" />
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
import MarkdownPreview from '@/components/MarkdownPreview.vue'

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

<style>
/* Add some basic prose styles */
.prose {
  font-size: 1.125rem;
  line-height: 1.75;
}

.prose h1 {
  font-size: 2.25rem;
  margin-top: 2rem;
  margin-bottom: 1rem;
  font-weight: 700;
}

.prose h2 {
  font-size: 1.875rem;
  margin-top: 1.75rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
}

.prose h3 {
  font-size: 1.5rem;
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.prose p {
  margin-top: 1.25rem;
  margin-bottom: 1.25rem;
}

.prose a {
  color: #2563eb;
  text-decoration: underline;
}

.prose ul {
  margin-top: 1.25rem;
  margin-bottom: 1.25rem;
  list-style-type: disc;
  padding-left: 1.625rem;
}

.prose ol {
  margin-top: 1.25rem;
  margin-bottom: 1.25rem;
  list-style-type: decimal;
  padding-left: 1.625rem;
}

.prose blockquote {
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
  padding-left: 1rem;
  border-left: 4px solid #e5e7eb;
  font-style: italic;
}

.dark .prose a {
  color: #60a5fa;
}

.dark .prose blockquote {
  border-left-color: #374151;
}

.prose pre {
  padding: 1em;
  border-radius: 0.5em;
  margin: 1em 0;
  background-color: #1e1e1e;
  overflow-x: auto;
}

.prose code {
  color: #e06c75;
  background-color: rgba(0, 0, 0, 0.1);
  padding: 0.2em 0.4em;
  border-radius: 0.25em;
  font-size: 0.9em;
}

.prose pre code {
  color: inherit;
  background-color: transparent;
  padding: 0;
  border-radius: 0;
  font-size: inherit;
}

/* Add styles for collapsible code blocks */
.hljs {
  position: relative;
}

.hljs::before {
  content: attr(class);
  position: absolute;
  top: 0;
  right: 1em;
  color: #999;
  font-size: 0.8em;
  font-family: monospace;
  text-transform: uppercase;
  /* Remove 'language-' prefix */
  content: attr(class);
  content: attr(class) !important;
  content: attr(class) !important;
  content: attr(class) !important;
}

/* Code block styles */
.code-block-wrapper {
  position: relative;
  margin: 1em 0;
  background: var(--p-surface-50);
  border-radius: 0.5em;
  border: 1px solid var(--p-content-border-color);
}

.code-block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5em 1em;
  background: var(--p-surface-100);
  border-top-left-radius: 0.5em;
  border-top-right-radius: 0.5em;
  border-bottom: 1px solid var(--p-content-border-color);
  font-family: monospace;
  font-size: 0.8em;
  color: var(--p-text-muted-color);
}

.code-block-lang {
  text-transform: uppercase;
  color: var(--p-text-muted-color);
}

.code-block-actions {
  display: flex;
  gap: 0.5em;
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2em;
  height: 2em;
  padding: 0.25em;
  background: transparent;
  border: 1px solid var(--p-content-border-color);
  border-radius: 0.25em;
  color: var(--p-text-muted-color);
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-button:hover {
  background: var(--p-surface-200);
  border-color: var(--p-text-muted-color);
  color: var(--p-text-color);
}

.action-button.success {
  background: var(--p-primary-600);
  border-color: var(--p-primary-500);
  color: white;
}

.action-button.error {
  background: #dc2626;
  border-color: #ef4444;
  color: white;
}

.copy-icon, .collapse-icon {
  width: 1.2em;
  height: 1.2em;
}

.prose pre {
  margin: 0;
  padding: 1em;
  background: var(--p-surface-50);
  border-bottom-left-radius: 0.5em;
  border-bottom-right-radius: 0.5em;
  overflow: hidden;
  transition: height 0.3s ease-in-out;
  height: auto;
  color: var(--p-text-color);
}

.prose code {
  color: var(--p-primary-600);
  background-color: var(--p-surface-100);
  padding: 0.2em 0.4em;
  border-radius: 0.25em;
  font-size: 0.9em;
}

.prose pre code {
  color: var(--p-text-color);
  background-color: transparent;
  padding: 0;
  border-radius: 0;
  font-size: inherit;
}

/* Dark mode styles */
@media (prefers-color-scheme: dark) {
  .code-block-wrapper {
    background: var(--p-surface-800);
  }

  .code-block-header {
    background: var(--p-surface-900);
  }

  .action-button:hover {
    background: var(--p-surface-700);
  }

  .prose pre {
    background: var(--p-surface-800);
  }

  .prose code {
    color: var(--p-primary-300);
    background-color: var(--p-surface-700);
  }
}

/* Collapsed state */
.code-block-wrapper.collapsed .collapse-icon {
  transform: rotate(180deg);
}

.code-block-wrapper.collapsed pre {
  height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

/* Remove the language indicator since we now have it in the header */
.hljs::before {
  display: none;
}

/* Highlight.js theme overrides for better visibility */
.hljs-section {
  color: var(--p-primary-700);
  font-weight: bold;
}

.hljs-bullet {
  color: var(--p-primary-600);
}

.hljs-link {
  color: var(--p-primary-700);
  text-decoration: underline;
}

.hljs-quote {
  color: var(--p-surface-700);
  font-style: italic;
}

.hljs-strong {
  color: var(--p-primary-700);
  font-weight: bold;
}

.hljs-emphasis {
  color: var(--p-primary-700);
  font-style: italic;
}

.hljs-code {
  color: var(--p-primary-800);
}

@media (prefers-color-scheme: dark) {
  .hljs-section {
    color: var(--p-primary-400);
  }

  .hljs-bullet {
    color: var(--p-primary-300);
  }

  .hljs-link {
    color: var(--p-primary-300);
  }

  .hljs-quote {
    color: var(--p-surface-400);
  }

  .hljs-strong {
    color: var(--p-primary-300);
  }

  .hljs-emphasis {
    color: var(--p-primary-300);
  }

  .hljs-code {
    color: var(--p-primary-400);
  }
}
</style> 