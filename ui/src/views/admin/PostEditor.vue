<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6">{{ isEditing ? 'Edit Post' : 'Create New Post' }}</h1>
    
    <form @submit.prevent>
      <div class="grid grid-cols-3 gap-4 mb-4">
        <div class="col-span-2">
          <label for="title" class="block mb-2 font-medium">Title</label>
          <input
            id="title"
            v-model="post.title"
            type="text"
            class="w-full p-2 border rounded-lg"
            required
          >
        </div>

        <div>
          <label for="publishedAt" class="block mb-2 font-medium">Published Date</label>
          <DatePicker
            v-model="post.published"
            showTime
            hourFormat="24"
            showIcon
            size="small"
            fluid
          />
        </div>

        <div class="col-span-2">
          <label for="slug" class="block mb-2 font-medium">Slug</label>
          <input
            id="slug"
            v-model="post.slug"
            type="text"
            class="w-full p-2 border rounded-lg"
            required
            @input="handleSlugInput"
          >
        </div>
      </div>

      <div class="mb-4">
        <label class="block mb-2 font-medium">Content</label>
        <div class="relative -mx-32">
          <MdEditor 
            v-model="post.content"
            class="w-full"
            language="en-US"
            height="800px"
            preview-theme="vuepress"
            :theme="isDarkMode ? 'dark' : 'light'"
          />
        </div>
      </div>

      <div class="flex gap-4">
        <Button
          type="button"
          severity="success"
          size="small"
          label="Save"
          @click="handleSave(false)"
        />
        <Button
          type="button"
          severity="success"
          size="small"
          label="Save & Back"
          @click="handleSave(true)"
        />
        <Button
          type="button"
          severity="secondary"
          size="small"
          label="Cancel"
          @click="$router.push({ name: 'admin-posts' })"
        />
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { MdEditor, config } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { PostsApi, type PostMutate } from '@/lib/api'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import DatePicker from 'primevue/datepicker'
import { useApiClient } from '@/composables/useApiClient'

const router = useRouter()
const route = useRoute()
const toast = useToast()
const postsApi = useApiClient(PostsApi)

const isEditing = computed(() => route.params.id !== undefined)
const postId = ref<number | null>(null)
const post = ref<PostMutate>({
  title: '',
  slug: '',
  content: '',
  published: null
})

// Add this to track if slug was manually edited
const slugManuallyEdited = ref(false)

// Add function to generate slug from title
const generateSlug = (title: string): string => {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-') // Replace non-alphanumeric chars with hyphen
    .replace(/^-+|-+$/g, '') // Remove leading/trailing hyphens
    .replace(/-+/g, '-') // Replace multiple consecutive hyphens with single hyphen
}

// Watch title changes and update slug if not manually edited
watch(() => post.value.title, (newTitle) => {
  if (!slugManuallyEdited.value) {
    post.value.slug = generateSlug(newTitle)
  }
})

// Add handler for manual slug edits
const handleSlugInput = () => {
  slugManuallyEdited.value = true
}

const isDarkMode = ref(window.matchMedia('(prefers-color-scheme: dark)').matches)

// Listen for system theme changes
onMounted(() => {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', (e) => {
    isDarkMode.value = e.matches
  })
})

let editorConfig = {
  editorExtensions: {
    highlight: {
      css: {
        atom: {
          light:
            'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.1/styles/atom-one-light.min.css',
          dark: 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.1/styles/atom-one-dark.min.css',
        },
        xxx: {
          light:
            'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.1/styles/xxx-light.css',
          dark: 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.1/styles/xxx-dark.css',
        },
      },
    },
  },
}

config(editorConfig)

onMounted(async () => {
  if (isEditing.value) {
    try {
      const response = await postsApi.apiGetPostById({
        id: parseInt(route.params.id as string)
      })
      postId.value = response.id
      post.value = {
        title: response.title,
        slug: response.slug,
        content: response.content,
        published: response.published
      }
    } catch (error) {
      console.error('Error fetching post:', error)
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load post',
        life: 3000
      })
      router.push({ name: 'admin-posts' })
    }
  }
})

// Add auto-save functionality for unpublished posts
let autoSaveInterval: number | null = null

const startAutoSave = () => {
  if (autoSaveInterval) return // Don't start if already running
  
  autoSaveInterval = window.setInterval(async () => {
    // Only auto-save if we have an ID (existing post) and it's not published
    if (postId.value && !post.value.published) {
      try {
        await postsApi.apiUpdatePost({
          id: postId.value,
          postMutate: post.value
        })
        toast.add({
          severity: 'info',
          summary: 'Auto-saved',
          detail: 'Draft saved automatically',
          life: 2000
        })
      } catch (error) {
        console.error('Auto-save failed:', error)
        // Don't show error toast for auto-save failures to avoid spam
      }
    }
  }, 60000) // Run every minute
}

const stopAutoSave = () => {
  if (autoSaveInterval) {
    window.clearInterval(autoSaveInterval)
    autoSaveInterval = null
  }
}

// Start auto-save when conditions are met
watch(() => [postId.value, post.value.published], ([newId, isPublished]) => {
  if (newId && !isPublished) {
    startAutoSave()
  } else {
    stopAutoSave()
  }
}, { immediate: true })

// Clean up on component unmount
onUnmounted(() => {
  stopAutoSave()
})

const handleSave = async (shouldRedirect: boolean) => {
  try {
    if (isEditing.value) {
      await postsApi.apiUpdatePost({
        id: parseInt(route.params.id as string),
        postMutate: post.value
      })
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Post updated successfully',
        life: 3000
      })
      if (shouldRedirect) {
        router.push({ name: 'admin-posts' })
      }
    } else {
      const response = await postsApi.apiCreatePost({
        postMutate: post.value
      })
      postId.value = response.id // Set the post ID after creation
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Post created successfully',
        life: 3000
      })
      if (shouldRedirect) {
        router.push({ name: 'admin-posts' })
      } else {
        router.replace({ 
          name: 'admin-posts-edit',
          params: { id: response.id.toString() }
        })
      }
    }
  } catch (error) {
    console.error('Error saving post:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `Failed to ${isEditing.value ? 'update' : 'create'} post`,
      life: 3000
    })
  }
}
</script>