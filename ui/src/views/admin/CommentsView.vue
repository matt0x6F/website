<template>
  <div class="max-w-5xl mx-auto mt-4 px-1 sm:mt-6 sm:px-4">
    <div id="content" class="">
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 gap-4">
        <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">Comment Moderation</h1>
        <div class="flex gap-2 flex-wrap">
          <Button 
            :class="['min-w-[110px] sm:min-w-[120px]', { 'p-button-outlined': reviewFilter !== null }]"
            label="All Comments" 
            @click="setReviewFilter(null)" 
          />
          <Button 
            :class="['min-w-[110px] sm:min-w-[120px]', { 'p-button-outlined': reviewFilter !== false }]"
            label="Pending Review" 
            @click="setReviewFilter(false)" 
          />
          <Button 
            :class="['min-w-[110px] sm:min-w-[120px]', { 'p-button-outlined': reviewFilter !== true }]"
            label="Reviewed" 
            @click="setReviewFilter(true)" 
          />
        </div>
      </div>

      <div class="overflow-x-auto rounded-md">
        <DataTable 
          :value="comments" 
          :loading="loading" 
          paginator 
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20, 50]"
          v-model:filters="filters"
          filterDisplay="menu"
          :globalFilterFields="['content', 'author.username', 'post.title']"
          responsiveLayout="scroll"
          class="p-datatable-sm min-w-[600px] dark:bg-gray-800 dark:text-gray-100"
          selectionMode="single"
          @row-click="onRowClick"
          v-model:selection="selectedComment"
        >
          <template #header>
            <div class="flex justify-end">
              <InputGroup>
                <InputGroupAddon>
                  <i class="pi pi-search text-gray-700 dark:text-gray-300" />
                </InputGroupAddon>
                <InputText v-model="filters['global'].value" placeholder="Search..." class="dark:bg-gray-900 dark:text-gray-100" />
              </InputGroup>
            </div>
          </template>

          <Column field="id" header="ID" sortable style="width: 5%"></Column>
          <Column field="content" header="Content" sortable style="width: 35%">
            <template #body="{ data }">
              <div class="whitespace-pre-wrap">{{ data.content }}</div>
            </template>
          </Column>
          <Column field="author.username" header="Author" sortable style="width: 15%"></Column>
          <Column field="post.title" header="Post" sortable style="width: 20%"></Column>
          <Column field="createdAt" header="Date" sortable style="width: 15%">
            <template #body="{ data }">
              {{ formatDate(data.createdAt) }}
            </template>
          </Column>
          <Column header="Actions" style="width: 10%">
            <template #body="{ data }">
              <div class="flex gap-2 flex-wrap">
                <Button 
                  v-if="!data.reviewed" 
                  icon="pi pi-check" 
                  class="p-button-success p-button-sm min-w-[36px]" 
                  @click="approveComment(data.id)" 
                  tooltip="Approve" 
                />
                <Button 
                  v-if="!data.reviewed" 
                  icon="pi pi-times" 
                  class="p-button-danger p-button-sm min-w-[36px]" 
                  @click="rejectComment(data.id)" 
                  tooltip="Reject" 
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-danger p-button-sm min-w-[36px]" 
                  @click="confirmDelete(data)" 
                  tooltip="Delete" 
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>

      <ConfirmDialog></ConfirmDialog>
      <Toast />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useApiClient } from '@/composables/useApiClient';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import { CommentsApi, ModerationApi } from '@/lib/api';
import type { AdminCommentUpdate } from '@/lib/api/models';
import ConfirmDialog from 'primevue/confirmdialog';
import Toast from 'primevue/toast';
import { useRouter } from 'vue-router';
import InputGroup from 'primevue/inputgroup';
import InputGroupAddon from 'primevue/inputgroupaddon';
import InputText from 'primevue/inputtext';

const router = useRouter();
const moderationApi = useApiClient(ModerationApi);
const commentsApi = useApiClient(CommentsApi);
const confirm = useConfirm();
const toast = useToast();

const comments = ref<any[]>([]);
const loading = ref(true);
const reviewFilter = ref<boolean | null>(false); // Default to showing pending comments
const selectedComment = ref(null);

// Define our own filter match mode since we don't have the PrimeVue import
const filters = ref({
  global: { value: null, matchMode: 'contains' }
});

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

const loadComments = async () => {
  loading.value = true;
  try {
    let allComments: any[] = [];
    
    // If we want all comments, fetch both reviewed and unreviewed comments
    if (reviewFilter.value === null) {
      // First fetch reviewed comments
      const reviewedResponse = await moderationApi.modQueueList({
        reviewed: true
      });
      
      // Then fetch unreviewed comments
      const unreviewedResponse = await moderationApi.modQueueList({
        reviewed: false
      });
      
      // Combine the results
      allComments = [
        ...(reviewedResponse.items || []),
        ...(unreviewedResponse.items || [])
      ];
      
      comments.value = allComments;
    } else {
      // Just fetch the filtered comments
      const response = await moderationApi.modQueueList({
        reviewed: reviewFilter.value
      });
      comments.value = response.items || [];
    }
    
    // Log the first comment to see its structure
    if (comments.value.length > 0) {
      console.log('Sample comment:', comments.value[0]);
    }
  } catch (error) {
    console.error('Error loading comments:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load comments',
      life: 3000
    });
  } finally {
    loading.value = false;
  }
};

const setReviewFilter = (value: boolean | null) => {
  reviewFilter.value = value;
  loadComments();
};

const approveComment = async (id: number) => {
  try {
    // Using only the fields that exist in AdminCommentUpdate
    const update: AdminCommentUpdate = {
      reviewed: true,
      visible: true,  // Make the comment visible to approve it
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
    loadComments();
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
    // Using only the fields that exist in AdminCommentUpdate
    const update: AdminCommentUpdate = {
      reviewed: true,
      visible: false,  // Hide the comment to reject it
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
    loadComments();
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
    loadComments();
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

// Handle row click to navigate to comment detail view
const onRowClick = (event: { data: { id: number } }) => {
  const commentId = event.data.id;
  router.push({ name: 'admin-comment-detail', params: { id: commentId.toString() } });
};

onMounted(() => {
  loadComments();
  document.title = 'Admin: Comments – ooo-yay.com';
});
</script>

<style scoped>
:deep(.p-datatable-table),
:deep(.p-datatable-thead),
:deep(.p-datatable-tbody),
:deep(.p-datatable-tfoot),
:deep(.p-datatable-header),
:deep(.p-datatable-thead > tr > th),
:deep(.p-datatable-tbody > tr > td) {
  border: none !important;
  background-color: transparent;
}

:deep(.p-datatable-paginator-bottom) {
  border: none !important;
}

:deep(.p-datatable) {
  background-color: transparent !important;
}

:deep(.p-datatable) {
  color: #111827;
}

:deep(.dark .p-datatable),
:deep(.dark .p-datatable-table),
:deep(.dark .p-datatable-thead),
:deep(.dark .p-datatable-tbody),
:deep(.dark .p-datatable-tfoot),
:deep(.dark .p-datatable-header),
:deep(.dark .p-datatable-thead > tr > th),
:deep(.dark .p-datatable-tbody > tr > td) {
  background-color: #1f2937 !important; /* gray-800 */
  color: #f3f4f6 !important; /* gray-100 */
}

:deep(.dark .p-datatable .p-datatable-header) {
  background-color: #111827 !important; /* gray-900 */
}

:deep(.dark .p-inputtext) {
  background-color: #111827 !important;
  color: #f3f4f6 !important;
}
</style> 