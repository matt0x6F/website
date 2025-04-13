<template>
  <div>
    <div class="p-6">
      <div class="space-y-4">
        <div v-if="loading" class="text-gray-600">Loading users...</div>
        
        <div v-else-if="error" class="text-red-600">
          Error loading users: {{ error }}
        </div>

        <div v-else-if="!users.length" class="text-gray-600">
          No users found
        </div>

        <div v-else class="-mx-12">
          <DataView
            :value="users"
            dataKey="id"
            :paginator="true"
            :rows="rows"
            :rows-per-page-options="[5, 10, 20, 50]"
            :sortField="sortField"
            :sortOrder="sortOrder"
            class="border-none !bg-transparent"
          >
            <template #header>
              <div class="flex justify-between items-center p-2">
                <h1 class="text-2xl font-bold">Users</h1>
                <div class="flex items-center gap-2">
                  <span class="text-gray-600 dark:text-gray-400">Sort by:</span>
                  <Dropdown
                    v-model="sortField"
                    :options="sortOptions"
                    optionLabel="label"
                    optionValue="value"
                    class="w-48"
                  >
                    <template #value="slotProps">
                      <div class="flex items-center gap-2">
                        <i class="pi pi-sort-alt"></i>
                        <span>{{ slotProps.value ? sortOptions.find(opt => opt.value === slotProps.value)?.label : 'Sort By' }}</span>
                      </div>
                    </template>
                    <template #option="slotProps">
                      <div class="flex items-center gap-2">
                        <i class="pi pi-sort-alt"></i>
                        <span>{{ slotProps.option.label }}</span>
                      </div>
                    </template>
                  </Dropdown>
                </div>
              </div>
            </template>

            <template #list="slotProps">
              <div class="flex flex-col px-12 py-2">
                <div v-for="(item, index) in slotProps.items" :key="item.id">
                  <div class="mb-4">
                    <Card class="shadow-sm">
                      <template #header>
                        <div class="flex items-center justify-between">
                          <div class="flex items-center gap-2">
                            <h2 class="text-xl font-semibold">{{ item.email }}</h2>
                            <div class="flex gap-1">
                              <Badge v-if="item.isStaff" value="Staff" severity="info" />
                              <Badge v-if="item.isSuperuser" value="Admin" severity="warning" />
                              <Badge v-if="!item.isActive" value="Inactive" severity="danger" />
                            </div>
                          </div>
                          <Button
                            icon="pi pi-user-edit"
                            label="Edit"
                            severity="secondary"
                            size="small"
                            @click="router.push({ name: 'admin-users-edit', params: { id: item.id }})"
                          />
                        </div>
                      </template>
                      <template #content>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div class="space-y-2">
                            <p><span class="font-medium">Name:</span> {{ item.firstName }} {{ item.lastName }}</p>
                            <p><span class="font-medium">Username:</span> {{ item.username }}</p>
                            <p><span class="font-medium">Joined:</span> {{ new Date(item.dateJoined).toLocaleDateString() }}</p>
                            <p v-if="item.lastLogin">
                              <span class="font-medium">Last login:</span> {{ new Date(item.lastLogin).toLocaleDateString() }}
                            </p>
                          </div>
                          <div v-if="item.notes" class="text-sm">
                            <p class="font-medium mb-1">Notes:</p>
                            <p class="italic">{{ item.notes }}</p>
                          </div>
                        </div>
                      </template>
                    </Card>
                  </div>
                </div>
              </div>
            </template>
          </DataView>
        </div>
      </div>
    </div>

    <router-view></router-view>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApiClient } from '@/composables/useApiClient'
import { AccountsApi } from '@/lib/api/apis/AccountsApi'
import type { AdminUserDetails } from '@/lib/api/models'
import Badge from 'primevue/badge'
import Card from 'primevue/card'
import Button from 'primevue/button'
import DataView from 'primevue/dataview'
import Dropdown from 'primevue/dropdown'

const router = useRouter()
const users = ref<AdminUserDetails[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

// Pagination and sorting state
const rows = ref(10)
const sortField = ref('email')
const sortOrder = ref(1)

const sortOptions = [
  { label: 'Email', value: 'email' },
  { label: 'Name', value: 'firstName' },
  { label: 'Username', value: 'username' },
  { label: 'Join Date', value: 'dateJoined' }
]

const loadUsers = async () => {
  const client = useApiClient(AccountsApi)
  try {
    loading.value = true
    const response = await client.apiListUsers()
    users.value = response.items
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'An error occurred'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style>
.p-dataview {
  background: transparent !important;
}

.p-dataview .p-dataview-content {
  background: transparent !important;
}

.p-dataview .p-paginator {
  background: transparent !important;
}

.p-dataview .p-dataview-header {
  background: transparent !important;
  border: none !important;
}

.p-card {
  background: transparent !important;
}

.p-card .p-card-content,
.p-card .p-card-header {
  background: transparent !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
}
</style> 