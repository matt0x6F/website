<template>
  <div class="comment-thread">
    <div class="bg-gray-50 dark:bg-gray-800 p-4 rounded">
      <div class="flex justify-between">
        <div class="font-medium">{{ comment.author.username }}</div>
        <div class="text-sm text-gray-500">
          {{ new Date(comment.createdAt).toLocaleDateString() }}
        </div>
      </div>
      <div class="mt-2 prose-sm">{{ comment.content }}</div>
      
      <!-- Reply link - only show if depth is less than 5 -->
      <div v-if="depth < 5" class="mt-2 text-sm">
        <button 
          @click="isLoggedIn ? (showReplyForm = !showReplyForm) : $emit('login-required')" 
          class="text-emerald-600 hover:text-emerald-800 dark:text-emerald-400 dark:hover:text-emerald-300"
        >
          {{ isLoggedIn ? (showReplyForm ? 'Cancel' : 'Reply') : 'Sign in to Reply' }}
        </button>
      </div>
      
      <!-- Reply form -->
      <div v-if="showReplyForm" class="mt-3">
        <textarea 
          v-model="replyContent" 
          class="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
          placeholder="Write your reply..."
          rows="3"
        ></textarea>
        <div class="mt-2 flex justify-end space-x-2">
          <button 
            @click="showReplyForm = false" 
            class="px-3 py-1 text-sm border rounded hover:bg-gray-100 dark:hover:bg-gray-700 dark:border-gray-600"
          >
            Cancel
          </button>
          <button 
            @click="submitReply" 
            class="px-3 py-1 text-sm bg-emerald-600 text-white rounded hover:bg-emerald-700 disabled:opacity-50"
            :disabled="!replyContent.trim()"
          >
            Submit
          </button>
        </div>
      </div>
    </div>
    
    <!-- Nested replies -->
    <div v-if="comment.children?.length" class="ml-8 mt-4 space-y-4">
      <template v-for="reply in comment.children" :key="reply.id">
        <CommentThread 
          :comment="reply" 
          :depth="depth + 1"
          :postId="postId"
          @reply-added="$emit('reply-added')" 
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { CommentsApi, type CommentList } from '@/lib/api'
import { useApiClient } from '@/composables/useApiClient'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  comment: CommentList
  depth?: number
  postId: number
}>()

const emit = defineEmits<{
  (e: 'reply-added'): void
  (e: 'login-required'): void
}>()

const authStore = useAuthStore()
const isLoggedIn = computed(() => authStore.isLoggedIn)

// Default depth to 0 if not provided
const depth = props.depth ?? 0

const showReplyForm = ref(false)
const replyContent = ref('')
const api = useApiClient(CommentsApi)

async function submitReply() {
  if (!replyContent.value.trim()) return
  
  try {
    console.log('Submitting reply with postId:', props.postId);
    
    await api.blogApiCreateComment({
      commentCreate: {
        content: replyContent.value,
        parentId: props.comment.id,
        postId: props.postId
      }
    })
    
    // Reset form and hide it
    replyContent.value = ''
    showReplyForm.value = false
    
    // Emit event to parent to refresh comments
    emit('reply-added')
  } catch (error) {
    console.error('Failed to submit reply:', error)
    // You could add error handling UI here
  }
}
</script> 