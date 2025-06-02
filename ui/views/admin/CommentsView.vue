<template>
  <div>
    <div id="content">
      <h1 class="text-2xl font-bold">Comment Moderation</h1>
      <Toolbar class="mb-6">
        <template #start></template>
        <template #center>
          <div class="flex items-center gap-4">
            <SelectButton
              v-model="reviewFilterOption"
              :options="reviewFilterOptions"
              optionLabel="label"
              :allowEmpty="false"
              aria-label="Review Status"
            />
          </div>
        </template>
        <template #end></template>
      </Toolbar>

      <div class="space-y-4">
        <div v-if="loading" class="text-gray-600">Loading comments...</div>
        <div v-else-if="error" class="text-red-600">Error loading comments: {{ error }}</div>
        <div v-else-if="!comments.length" class="text-gray-600">No comments found</div>
        <div v-else class="overflow-x-auto rounded-md">
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
                {{ getRelativeDate(new Date(data.createdAt)) }}
              </template>
            </Column>
            <Column header="Actions" style="width: 10%">
              <template #body="{ data }">
                <div class="flex gap-2 flex-wrap">
                  <Button 
                    v-if="!data.reviewed" 
                    icon="pi pi-check" 
                    class="p-button-success p-button-sm min-w-[36px]" 
                    @click.stop="approveComment(data.id)" 
                    tooltip="Approve" 
                  />
                  <Button 
                    v-if="!data.reviewed" 
                    icon="pi pi-times" 
                    class="p-button-danger p-button-sm min-w-[36px]" 
                    @click.stop="rejectComment(data.id)" 
                    tooltip="Reject" 
                  />
                  <Button 
                    icon="pi pi-trash" 
                    class="p-button-danger p-button-sm min-w-[36px]" 
                    @click.stop="confirmDelete(data)" 
                    tooltip="Delete" 
                  />
                </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </div>

      <ConfirmDialog></ConfirmDialog>
      <Toast />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
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
import Toolbar from 'primevue/toolbar';
import Button from 'primevue/button';
import { useAuthStore } from '@/stores/auth'
import SelectButton from 'primevue/selectbutton';

const router = useRouter();
const confirm = useConfirm();
const toast = useToast();
const auth = useAuthStore();

const comments = ref<any[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);
const reviewFilterOptions = [
  { label: 'All Comments', value: null },
  { label: 'Pending Review', value: false },
  { label: 'Reviewed', value: true }
];
const reviewFilterOption = ref<{ label: string, value: boolean | null }>(reviewFilterOptions[1]); // Default to Pending Review
const selectedComment = ref(null);

const filters = ref({
  global: { value: null, matchMode: 'contains' }
});

function getRelativeDate(date: Date | string | null | undefined): string {
  if (!date) return 'N/A';
  try {
    const d = typeof date === 'string' ? new Date(date) : date;
    const now = new Date();
    const diff = (now.getTime() - d.getTime()) / 1000; // seconds
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hour${Math.floor(diff / 3600) === 1 ? '' : 's'} ago`;
    if (diff < 604800) return `${Math.floor(diff / 86400)} day${Math.floor(diff / 86400) === 1 ? '' : 's'} ago`;
    return d.toLocaleDateString();
  } catch (error) {
    return 'Invalid Date';
  }
}

const loadComments = async () => {
  loading.value = true;
  error.value = null;
  try {
    const moderationApi = useApiClient(ModerationApi);
    let allComments: any[] = [];
    if (reviewFilterOption.value.value === null) {
      const reviewedResponse = await moderationApi.modQueueList({ reviewed: true });
      const unreviewedResponse = await moderationApi.modQueueList({ reviewed: false });
      allComments = [
        ...(reviewedResponse.items || []),
        ...(unreviewedResponse.items || [])
      ];
      comments.value = allComments;
    } else {
      const response = await moderationApi.modQueueList({ reviewed: reviewFilterOption.value.value });
      comments.value = response.items || [];
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load comments';
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
  reviewFilterOption.value.value = value;
  loadComments();
};

const approveComment = async (id: number) => {
  try {
    const moderationApi = useApiClient(ModerationApi);
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
    loadComments();
  } catch (error) {
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
    const moderationApi = useApiClient(ModerationApi);
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
    loadComments();
  } catch (error) {
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
    accept: () => deleteComment(comment.id),
    reject: () => {
      toast.add({ severity: 'info', summary: 'Cancelled', detail: 'Deletion cancelled', life: 2000 })
    }
  });
};

const deleteComment = async (id: number) => {
  try {
    const commentsApi = useApiClient(CommentsApi);
    await commentsApi.deleteComment({ id });
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Comment deleted',
      life: 3000
    });
    loadComments();
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to delete comment',
      life: 3000
    });
  }
};

const onRowClick = (event: { data: { id: number } }) => {
  const commentId = event.data.id;
  router.push({ name: 'admin-comments-id', params: { id: commentId.toString() } });
};

watch(reviewFilterOption, (newVal) => {
  setReviewFilter(newVal.value);
});

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