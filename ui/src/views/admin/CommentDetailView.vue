<template>
  <div>
    <div class="mb-4">
      <Button 
        icon="pi pi-arrow-left" 
        label="Back to Comments" 
        class="p-button-text" 
        @click="$router.push({ name: 'admin-comments' })" 
      />
    </div>

    <div v-if="loading" class="flex justify-center py-8">
      <i class="pi pi-spin pi-spinner text-4xl"></i>
    </div>
    
    <div v-else-if="error" class="p-4 bg-red-100 text-red-700 rounded">
      {{ error }}
    </div>
    
    <div v-else-if="comment" class="space-y-6">
      <h1 class="text-2xl font-bold">Comment #{{ comment.id }}</h1>
      
      <!-- Parent comment (if exists) -->
      <div v-if="comment.parent" class="border-l-4 border-gray-300 pl-4 py-2">
        <h2 class="text-lg font-semibold mb-2">Parent Comment</h2>
        <div class="bg-gray-50 dark:bg-gray-800 p-4 rounded">
          <div class="flex justify-between">
            <div>
              <span class="font-medium">{{ comment.parent.author?.username }}</span>
              <span class="text-sm text-gray-500 ml-2">{{ formatDate(comment.parent.createdAt) }}</span>
            </div>
            <div>
              <Badge v-if="comment.parent.reviewed" :value="comment.parent.visible ? 'Approved' : 'Rejected'" :severity="comment.parent.visible ? 'success' : 'danger'" />
              <Badge v-else value="Pending Review" severity="warning" />
            </div>
          </div>
          <div class="mt-2 whitespace-pre-wrap">{{ comment.parent.content }}</div>
          
          <!-- Link to view parent comment -->
          <div class="mt-2">
            <Button 
              label="View Parent Comment" 
              icon="pi pi-arrow-up" 
              class="p-button-text p-button-sm" 
              @click="$router.push({ name: 'admin-comment-detail', params: { id: comment.parent.id.toString() } })" 
            />
          </div>
        </div>
      </div>
      
      <!-- Current comment -->
      <div class="border-l-4 border-primary pl-4 py-2">
        <h2 class="text-lg font-semibold mb-2">Current Comment</h2>
        <div class="bg-primary-50 dark:bg-primary-900 p-4 rounded">
          <div class="flex justify-between">
            <div>
              <span class="font-medium">{{ comment.author?.username }}</span>
              <span class="text-sm text-gray-500 ml-2">{{ formatDate(comment.createdAt) }}</span>
            </div>
            <div>
              <Badge v-if="comment.reviewed" :value="comment.visible ? 'Approved' : 'Rejected'" :severity="comment.visible ? 'success' : 'danger'" />
              <Badge v-else value="Pending Review" severity="warning" />
            </div>
          </div>
          <div class="mt-2 whitespace-pre-wrap">{{ comment.content }}</div>
          
          <!-- Post reference -->
          <div class="mt-4 text-sm">
            <span class="text-gray-500">On post: </span>
            <a :href="`/blog/${comment.post.slug}`" class="text-primary hover:underline" target="_blank">
              {{ comment.post.title }}
            </a>
          </div>
          
          <!-- Moderation actions -->
          <div class="mt-4 flex gap-2 items-center">
            <template v-if="!comment.reviewed">
              <Button 
                label="Approve" 
                icon="pi pi-check" 
                class="p-button-success" 
                @click="approveComment(comment.id)" 
              />
              <Button 
                label="Reject" 
                icon="pi pi-times" 
                class="p-button-danger" 
                @click="rejectComment(comment.id)" 
              />
            </template>
            <template v-else-if="comment.visible">
              <Button 
                label="Reject" 
                icon="pi pi-times" 
                class="p-button-danger" 
                @click="rejectComment(comment.id)" 
              />
            </template>
            <template v-else>
              <Button 
                label="Approve" 
                icon="pi pi-check" 
                class="p-button-success" 
                @click="approveComment(comment.id)" 
              />
            </template>
          </div>
          <div v-if="comment.reviewed && comment.note" class="mt-2 italic text-gray-600">
            Note: {{ comment.note }}
          </div>
        </div>
      </div>
      
      <!-- Child comments (if any) -->
      <div v-if="comment.children && comment.children.length > 0" class="border-l-4 border-gray-300 pl-4 py-2">
        <h2 class="text-lg font-semibold mb-2">Replies ({{ comment.children.length }})</h2>
        <div v-for="child in comment.children" :key="child.id" class="bg-gray-50 dark:bg-gray-800 p-4 rounded mb-2">
          <div class="flex justify-between">
            <div>
              <span class="font-medium">{{ child.author?.username }}</span>
              <span class="text-sm text-gray-500 ml-2">{{ formatDate(child.createdAt) }}</span>
            </div>
            <div>
              <Badge v-if="child.reviewed" :value="child.visible ? 'Approved' : 'Rejected'" :severity="child.visible ? 'success' : 'danger'" />
              <Badge v-else value="Pending Review" severity="warning" />
            </div>
          </div>
          <div class="mt-2 whitespace-pre-wrap">{{ child.content }}</div>
        </div>
      </div>
      
      <!-- Delete button -->
      <div class="mt-6">
        <Button 
          label="Delete Comment" 
          icon="pi pi-trash" 
          class="p-button-danger" 
          @click="confirmDelete(comment)" 
        />
      </div>
    </div>
    
    <ConfirmDialog></ConfirmDialog>
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useApiClient } from '@/composables/useApiClient';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import { CommentsApi, ModerationApi } from '@/lib/api';
import type { AdminCommentUpdate } from '@/lib/api/models';
import ConfirmDialog from 'primevue/confirmdialog';
import Toast from 'primevue/toast';
import Badge from 'primevue/badge';

const route = useRoute();
const router = useRouter();
const moderationApi = useApiClient(ModerationApi);
const commentsApi = useApiClient(CommentsApi);
const confirm = useConfirm();
const toast = useToast();

const comment = ref<any>(null);
const loading = ref(true);
const error = ref<string | null>(null);

// Helper function to format dates safely
const formatDate = (dateString: string | null | undefined) => {
  if (!dateString) return 'N/A';
  
  try {
    return new Date(dateString).toLocaleString();
  } catch (error) {
    console.error('Error formatting date:', dateString, error);
    return 'Invalid Date';
  }
};

const loadComment = async () => {
  loading.value = true;
  error.value = null;

  try {
    const commentId = parseInt(route.params.id as string);
    // Use the moderation API to get the comment with admin fields
    const response = await moderationApi.modGetComment({ id: commentId });
    comment.value = response;
    console.log('Loaded admin comment:', comment.value);
  } catch (err) {
    console.error('Error loading comment:', err);
    error.value = 'Failed to load comment details';
  } finally {
    loading.value = false;
  }
};

const approveComment = async (id: number) => {
  try {
    const update: AdminCommentUpdate = {
      reviewed: true,
      visible: true,
      note: 'Approved by moderator'
    };
    
    await moderationApi.modUpdateComment({
      id,
      adminCommentUpdate: update
    });
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Comment approved',
      life: 3000
    });
    
    // Reload the comment to show updated status
    loadComment();
  } catch (error) {
    console.error('Error approving comment:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to approve comment',
      life: 3000
    });
  }
};

const rejectComment = async (id: number) => {
  try {
    const update: AdminCommentUpdate = {
      reviewed: true,
      visible: false,
      note: 'Rejected by moderator'
    };
    
    await moderationApi.modUpdateComment({
      id,
      adminCommentUpdate: update
    });
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Comment rejected',
      life: 3000
    });
    
    // Reload the comment to show updated status
    loadComment();
  } catch (error) {
    console.error('Error rejecting comment:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to reject comment',
      life: 3000
    });
  }
};

const confirmDelete = (comment: { id: number }) => {
  confirm.require({
    message: 'Are you sure you want to delete this comment?',
    header: 'Confirm Deletion',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: () => deleteComment(comment.id)
  });
};

const deleteComment = async (id: number) => {
  try {
    await commentsApi.deleteComment({ id });
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Comment deleted',
      life: 3000
    });
    
    // Navigate back to the comments list
    router.push({ name: 'admin-comments' });
  } catch (error) {
    console.error('Error deleting comment:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to delete comment',
      life: 3000
    });
  }
};

onMounted(() => {
  loadComment();
});
</script> 