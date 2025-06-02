<template>
  <div id="content" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div v-if="props.loading" class="flex justify-center items-center min-h-[200px]">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
    </div>
    
    <div v-else-if="props.error" class="text-red-600">
      {{ props.error }}
    </div>
    
    <template v-else-if="props.post">
      <article class="mb-8">
        <header class="mb-8">
          <h1 class="text-4xl font-bold mb-2">{{ props.post.title }}</h1>
          <div v-if="props.post.published" class="text-sm text-gray-500 italic">
            Published {{ new Date(props.post.published).toLocaleDateString() }}
          </div>
        </header>
        <!-- Series box below the title -->
        <div
          v-if="props.post.series && seriesPosts.length > 1"
          class="mb-6 p-4 border-l-4 border-emerald-500 bg-emerald-50 dark:bg-emerald-900/30 rounded"
        >
          <div class="font-semibold text-emerald-700 dark:text-emerald-300 mb-2">
            Part of the series: <span class="underline">{{ props.post.series.title }}</span>
          </div>
          <ol class="list-decimal list-inside space-y-1">
            <li
              v-for="sp in seriesPosts"
              :key="sp.id"
              :class="{
                'font-bold text-emerald-800 dark:text-emerald-200': sp.id === props.post.id,
                'text-gray-700 dark:text-gray-300': sp.id !== props.post.id
              }"
            >
              <NuxtLink
                v-if="sp.id !== props.post.id"
                :to="{
                  name: 'blog-post',
                  params: { slug: sp.slug, year: sp.year || (sp.publishedAt ? new Date(sp.publishedAt).getFullYear() : undefined) }
                }"
                class="hover:underline"
              >
                {{ sp.title }}
              </NuxtLink>
              <span v-else>
                {{ sp.title }} <span class="text-xs text-emerald-600">(current)</span>
              </span>
            </li>
          </ol>
        </div>
        <!-- End Series box -->
        <MarkdownPreview
          class="no-prose-padding"
          :content="props.post?.content || ''"
          :meta="props.post"
        />
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
          :postId="props.post.id" 
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
import { ref, computed, watch } from 'vue'
import { useApiClient } from '@/composables/useApiClient'
import { CommentsApi, SeriesApi } from '@/lib/api'
import type { PostDetails, CommentList, PostSummaryForSeries } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'
import Comments from '@/components/Comments.vue'
import LoginDialog from '@/components/LoginDialog.vue'
import SignupDialog from '@/components/SignupDialog.vue'
import MarkdownPreview from '@/components/MarkdownPreview.vue'

const props = defineProps<{
  post: PostDetails | null
  loading: boolean
  error: any
}>()

const commentsApi = useApiClient(CommentsApi)
const seriesApi = useApiClient(SeriesApi)
const authStore = useAuthStore()

const comments = ref<CommentList[]>([])
const showLoginDialog = ref(false)
const showSignupDialog = ref(false)
const isLoggedIn = computed(() => authStore.isLoggedIn)
const isAuthInitialized = computed(() => authStore.isInitialized)
const seriesPosts = ref<PostSummaryForSeries[]>([])

watch(
  () => props.post,
  async (newPost) => {
    if (newPost) {
      if (newPost.series?.id || newPost.series?.title) {
        await loadSeriesPosts(newPost.series.id || newPost.series.title)
      } else {
        seriesPosts.value = []
      }
      await loadComments()
    }
  },
  { immediate: true }
)

async function loadComments() {
  if (props.post && props.post.id) {
    const commentsResult = await commentsApi.listComments({
      postId: props.post.id,
      topLevel: true
    })
    comments.value = commentsResult.items || []
  }
}

async function loadSeriesPosts(seriesIdOrSlug: number | string) {
  try {
    const result = await seriesApi.listPostsInSeries({ seriesIdOrSlug })
    let items = result.items || []
    if (props.post && !items.some(p => p.id === props.post!.id)) {
      items = [...items, {
        id: props.post.id,
        title: props.post.title,
        slug: props.post.slug,
        year: props.post.published ? new Date(props.post.published).getFullYear() : undefined,
        publishedAt: props.post.published ? new Date(props.post.published) : undefined
      }]
      items.sort((a, b) => {
        if (!a.publishedAt || !b.publishedAt) return 0
        return a.publishedAt.getTime() - b.publishedAt.getTime()
      })
    }
    seriesPosts.value = items
  } catch (e: any) {
    const status = e?.status || e?.response?.status
    if (status === 404) {
      seriesPosts.value = []
      return
    }
    // Log other errors
    console.warn('Failed to load series posts:', e)
    seriesPosts.value = []
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