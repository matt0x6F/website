<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6">{{ isEditing ? 'Edit Post' : 'Create New Post' }}</h1>
    
    <form @submit.prevent="handleSubmit">
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
            :theme="isDarkMode ? 'dark' : 'light'"
          />
        </div>
      </div>

      <div class="flex gap-4">
        <Button
          type="submit"
          severity="success"
          size="small"
          :label="isEditing ? 'Update Post' : 'Create Post'"
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
import { ref, onMounted, computed, watch } from 'vue'
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
      const response = await postsApi.blogApiGetPostById({
        id: parseInt(route.params.id as string)
      })
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

const handleSubmit = async () => {
  try {
    if (isEditing.value) {
      await postsApi.blogApiUpdatePost({
        id: parseInt(route.params.id as string),
        postMutate: post.value
      })
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Post updated successfully',
        life: 3000
      })
      router.push({ name: 'admin-posts' })
    } else {
      const response = await postsApi.blogApiCreatePost({
        postMutate: post.value
      })
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Post created successfully',
        life: 3000
      })
      router.push({ 
        name: 'admin-posts-edit',
        params: { id: response.id.toString() }
      })
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