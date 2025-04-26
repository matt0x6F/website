<template>
  <div class="space-y-8 p-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Files</h1>
      <Button
        @click="openFileUpload"
        size="small"
        icon="pi pi-upload"
        label="Upload File"
      />
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <ProgressSpinner class="h-12 w-12" strokeWidth="4" />
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading files...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 p-4 rounded-md">
      <p class="text-red-600 dark:text-red-400">{{ error }}</p>
    </div>

    <!-- Files List -->
    <div v-else-if="files.length" class="bg-white dark:bg-neutral-800 shadow rounded-lg overflow-hidden">
      <ul class="divide-y divide-gray-200 dark:divide-neutral-700">
        <li v-for="file in files" :key="file.id" class="p-4 hover:bg-gray-50 dark:hover:bg-neutral-700">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-6">
              <span class="text-gray-600 dark:text-gray-300">{{ file.name }}</span>
              <span class="text-sm text-gray-500 dark:text-gray-400">{{ formatFileSize(file.size) }}</span>
            </div>
            <div class="flex items-center space-x-4">
              <div class="flex gap-2">
                <Button
                  @click="() => openInNewTab(getSpacesUrl(file.name))"
                  size="small"
                  icon="pi pi-cloud"
                  label="View in DO Spaces"
                />
                <Button
                  @click="downloadFile(file)"
                  size="small"
                  icon="pi pi-download"
                  label="Download"
                />
                <Button
                  @click="deleteFile(file)"
                  variant="danger"
                  size="small"
                  icon="pi pi-trash"
                  label="Delete"
                />
              </div>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12 bg-white dark:bg-neutral-800 rounded-lg">
      <p class="text-gray-600 dark:text-gray-400">No files uploaded yet.</p>
    </div>

    <!-- Orphaned Files Section -->
    <div class="mt-12 space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Orphaned Files</h2>
        <Button
          @click="checkOrphanedFiles"
          size="small"
          :loading="checkingOrphaned"
          icon="pi pi-refresh"
          label="Check for Orphaned Files"
      />
      </div>

      <div class="text-gray-600 dark:text-gray-400 text-xs">
        <p>Orphaned files are files that exist in storage but lack corresponding database entries. This inconsistency typically occurs in three scenarios: when file uploads fail to complete properly, when database records are deleted without removing the actual files, or when files are not properly synchronized between public and private storage locations. These files need to be manually deleted from storage to maintain system consistency.</p>
      </div>

      <!-- Orphaned Files Loading State -->
      <div v-if="checkingOrphaned" class="text-center py-6">
        <ProgressSpinner class="h-8 w-8" strokeWidth="4" />
        <p class="mt-2 text-gray-600 dark:text-gray-400">Checking for orphaned files...</p>
      </div>

      <div v-else-if="orphanedError" class="bg-red-50 dark:bg-red-900/20 p-4 rounded-md">
        <p class="text-red-600 dark:text-red-400">{{ orphanedError }}</p>
      </div>

      <div v-else-if="orphanedFiles._public.length || orphanedFiles._private.length" class="bg-white dark:bg-neutral-800 shadow rounded-lg overflow-hidden">
        <div class="p-4">
          <div v-if="orphanedFiles._public.length" class="mb-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Public Storage</h3>
            <ul class="space-y-2">
              <li v-for="file in orphanedFiles._public" :key="file.name" class="flex items-center justify-between p-2 hover:bg-gray-50 dark:hover:bg-neutral-700 rounded-md">
                <div class="flex items-center gap-6">
                  <span class="text-gray-600 dark:text-gray-300">{{ file.name }}</span>
                  <span class="text-sm text-gray-500 dark:text-gray-400">{{ formatFileSize(file.size) }}</span>
                  <span class="text-sm text-gray-500 dark:text-gray-400">{{ file.contentType }}</span>
                </div>
                <div class="flex items-center gap-4">
                  <Button
                    @click="() => openInNewTab(getSpacesUrl(file.name))"
                    size="small"
                    icon="pi pi-cloud"
                    label="View in DO Spaces"
                  />
                  <Button
                    @click="() => openInNewTab(file.location)"
                    size="small"
                    icon="pi pi-eye"
                    label="View File"
                  />
                </div>
              </li>
            </ul>
          </div>
          <div v-if="orphanedFiles._private.length">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Private Storage</h3>
            <ul class="space-y-2">
              <li v-for="file in orphanedFiles._private" :key="file.name" class="flex items-center justify-between p-2 hover:bg-gray-50 dark:hover:bg-neutral-700 rounded-md">
                <div class="flex items-center gap-6">
                  <span class="text-gray-600 dark:text-gray-300">{{ file.name }}</span>
                  <span class="text-sm text-gray-500 dark:text-gray-400">{{ formatFileSize(file.size) }}</span>
                  <span class="text-sm text-gray-500 dark:text-gray-400">{{ file.contentType }}</span>
                </div>
                <div class="flex items-center gap-4">
                  <Button
                    @click="() => openInNewTab(getSpacesUrl(file.name))"
                    size="small"
                    icon="pi pi-cloud"
                    label="View in DO Spaces"
                  />
                  <Button
                    @click="() => openInNewTab(file.location)"
                    size="small"
                    icon="pi pi-eye"
                    label="View File"
                  />
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div v-else-if="hasCheckedOrphaned" class="text-center py-6 bg-white dark:bg-neutral-800 rounded-lg">
        <p class="text-gray-600 dark:text-gray-400">No orphaned files found.</p>
      </div>
    </div>

    <!-- File Upload Input (hidden) -->
    <input
      type="file"
      ref="fileInput"
      @change="handleFileUpload"
      class="hidden"
      multiple
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useApiClient } from '@/composables/useApiClient'
import { FilesApi } from '@/lib/api'
import type { FileDetails, OrphanedFiles } from '@/lib/api'
import Button from 'primevue/button'
import ProgressSpinner from 'primevue/progressspinner'

const filesApi = useApiClient(FilesApi)
const files = ref<FileDetails[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

// Environment detection
const isDev = computed(() => import.meta.env.MODE === 'development')

// DO Spaces configuration
const DO_SPACES_BASE_URL = 'https://cloud.digitalocean.com/spaces/ooo-files'
const DO_SPACES_PARAMS = 'i=64818b&manageMetadata=&type=&managePermissions='

function getSpacesUrl(filename: string): string {
  const pathPrefix = isDev.value ? 'dev/' : ''
  const encodedPath = encodeURIComponent(`${pathPrefix}${filename}`)
  return `${DO_SPACES_BASE_URL}?${DO_SPACES_PARAMS}&path=${encodedPath}`
}

// Add method to handle opening URLs
function openInNewTab(url: string): void {
  window.open(url, '_blank')
}

// Orphaned files state
const orphanedFiles = ref<OrphanedFiles>({ _public: [], _private: [] })
const checkingOrphaned = ref(false)
const orphanedError = ref<string | null>(null)
const hasCheckedOrphaned = ref(false)

// Fetch files on component mount
onMounted(async () => {
  await fetchFiles()
  await checkOrphanedFiles()
})

async function fetchFiles() {
  loading.value = true
  error.value = null
  try {
    const response = await filesApi.apiListFiles()
    files.value = response.items
  } catch (err) {
    error.value = 'Failed to load files. Please try again.'
    console.error('Error fetching files:', err)
  } finally {
    loading.value = false
  }
}

function openFileUpload() {
  fileInput.value?.click()
}

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (!target.files?.length) return

  try {
    loading.value = true
    for (const file of Array.from(target.files)) {
      await filesApi.apiCreateFile({
        upload: file,
        metadata: {
          visibility: 'public'
        }
      })
    }
    await fetchFiles()
  } catch (err) {
    error.value = 'Failed to upload file(s). Please try again.'
    console.error('Error uploading files:', err)
  } finally {
    loading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

async function deleteFile(file: FileDetails) {
  if (!confirm(`Are you sure you want to delete ${file.name}?`)) return

  try {
    loading.value = true
    await filesApi.apiDeleteFile({ id: file.id })
    await fetchFiles()
  } catch (err) {
    error.value = 'Failed to delete file. Please try again.'
    console.error('Error deleting file:', err)
  } finally {
    loading.value = false
  }
}

async function downloadFile(file: FileDetails) {
  try {
    const response = await fetch(file.location)
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', file.name)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    error.value = 'Failed to download file. Please try again.'
    console.error('Error downloading file:', err)
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

async function checkOrphanedFiles() {
  checkingOrphaned.value = true
  orphanedError.value = null
  try {
    const response = await filesApi.apiListOrphanedFiles()
    orphanedFiles.value = response
    hasCheckedOrphaned.value = true
  } catch (err) {
    orphanedError.value = 'Failed to check for orphaned files. Please try again.'
    console.error('Error checking orphaned files:', err)
  } finally {
    checkingOrphaned.value = false
  }
}
</script> 