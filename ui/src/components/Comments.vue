<template>
  <div class="mt-8 space-y-8">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Comments</h2>
      <button 
        v-if="isLoggedIn"
        @click="showNewCommentForm = !showNewCommentForm"
        class="px-4 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600"
      >
        {{ showNewCommentForm ? 'Cancel' : 'Add Comment' }}
      </button>
      <button 
        v-else
        @click="$emit('login-required')"
        class="px-4 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600"
      >
        Sign in to Comment
      </button>
    </div>
    
    <!-- New top-level comment form -->
    <div v-if="showNewCommentForm" class="bg-gray-50 dark:bg-gray-800 p-4 rounded">
      <textarea 
        v-model="newCommentContent" 
        class="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
        placeholder="Write your comment..."
        rows="4"
      ></textarea>
      <div class="mt-2 flex justify-end">
        <button 
          @click="submitNewComment" 
          class="px-4 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 disabled:opacity-50"
          :disabled="!newCommentContent.trim()"
        >
          Submit
        </button>
      </div>
    </div>
    
    <div v-if="comments.length === 0 && isLoggedIn" class="text-center py-6 text-gray-500">
      No comments yet. Be the first to share your thoughts!
    </div>
    
    <div v-else class="space-y-4">
      <template v-for="comment in comments" :key="comment.id">
        <CommentThread 
          :comment="comment" 
          :postId="postId"
          @reply-added="$emit('refresh-comments')" 
          @login-required="$emit('login-required')"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { CommentList } from '@/lib/api'
import { CommentsApi } from '@/lib/api'
import { useApiClient } from '@/composables/useApiClient'
import { useAuthStore } from '@/stores/auth'
import CommentThread from './CommentThread.vue'

const props = defineProps<{
  comments: CommentList[]
  postId: number
}>()

const emit = defineEmits<{
  (e: 'refresh-comments'): void
  (e: 'login-required'): void
}>()

const authStore = useAuthStore()
const isLoggedIn = computed(() => authStore.isLoggedIn)

const showNewCommentForm = ref(false)
const newCommentContent = ref('')
const api = useApiClient(CommentsApi)

async function submitNewComment() {
  if (!newCommentContent.value.trim()) return
  
  try {
    await api.blogApiCreateComment({
      commentCreate: {
        content: newCommentContent.value,
        postId: props.postId
      }
    })
    
    // Reset form and hide it
    newCommentContent.value = ''
    showNewCommentForm.value = false
    
    // Emit event to parent to refresh comments
    emit('refresh-comments')
  } catch (error) {
    console.error('Failed to submit comment:', error)
  }
}
</script> 