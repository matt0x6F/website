<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6">Edit User</h1>
    
    <form @submit.prevent="handleSubmit">
      <div class="space-y-4">
        <div>
          <label for="email" class="block mb-2 font-medium">Email</label>
          <input
            id="email"
            v-model="user.email"
            type="email"
            class="w-full p-2 border rounded-lg"
            required
          >
        </div>

        <div>
          <label for="firstName" class="block mb-2 font-medium">First Name</label>
          <input
            id="firstName"
            v-model="user.firstName"
            type="text"
            class="w-full p-2 border rounded-lg"
          >
        </div>

        <div>
          <label for="lastName" class="block mb-2 font-medium">Last Name</label>
          <input
            id="lastName"
            v-model="user.lastName"
            type="text"
            class="w-full p-2 border rounded-lg"
          >
        </div>

        <div>
          <label for="username" class="block mb-2 font-medium">Username</label>
          <input
            id="username"
            v-model="user.username"
            type="text"
            class="w-full p-2 border rounded-lg"
          >
        </div>

        <div>
          <label for="groups" class="block mb-2 font-medium">Groups</label>
          <MultiSelect
            id="groups"
            v-model="user.groups"
            :options="availableGroups"
            optionLabel="name"
            placeholder="Select Groups"
            class="w-full"
            display="chip"
          />
        </div>

        <div>
          <label for="permissions" class="block mb-2 font-medium">Permissions</label>
          <MultiSelect
            id="permissions"
            v-model="user.userPermissions"
            :options="availablePermissions"
            optionLabel="name"
            placeholder="Select Permissions"
            class="w-full"
            display="chip"
          />
        </div>

        <div class="space-y-2">
          <div>
            <label class="flex items-center">
              <input
                v-model="user.isActive"
                type="checkbox"
                class="w-4 h-4 mr-2"
              >
              <span class="font-medium">Account Active</span>
            </label>
          </div>

          <div>
            <label class="flex items-center">
              <input
                v-model="user.isStaff"
                type="checkbox"
                class="w-4 h-4 mr-2"
              >
              <span class="font-medium">Staff Member</span>
            </label>
          </div>

          <div>
            <label class="flex items-center">
              <input
                v-model="user.isSuperuser"
                type="checkbox"
                class="w-4 h-4 mr-2"
              >
              <span class="font-medium">Superuser</span>
            </label>
          </div>
        </div>

        <div>
          <label for="notes" class="block mb-2 font-medium">Notes</label>
          <textarea
            id="notes"
            v-model="user.notes"
            rows="3"
            class="w-full p-2 border rounded-lg"
          ></textarea>
        </div>

        <div class="border-t pt-4">
          <label for="password" class="block mb-2 font-medium">New Password (leave blank to keep current)</label>
          <input
            id="password"
            v-model="user.password"
            type="password"
            class="w-full p-2 border rounded-lg"
          >
        </div>
      </div>

      <div class="flex gap-4 mt-6">
        <Button
          type="submit"
          severity="success"
          size="small"
          label="Update User"
        />
        <Button
          type="button"
          severity="secondary"
          size="small"
          label="Cancel"
          @click="$router.push({ name: 'admin-users' })"
        />
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { AccountsApi } from '@/lib/api/apis/AccountsApi'
import type { AdminUserDetails, AdminUserModify, Group, Permission } from '@/lib/api/models'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import { useApiClient } from '@/composables/useApiClient'
import MultiSelect from 'primevue/multiselect'

const router = useRouter()
const route = useRoute()
const toast = useToast()
const accountsApi = useApiClient(AccountsApi)

const user = ref<AdminUserModify>({
  email: '',
  firstName: '',
  lastName: '',
  password: '',
  username: '',
  isActive: true,
  isStaff: false,
  isSuperuser: false,
  notes: '',
  groups: [],
  userPermissions: []
})

const availableGroups = ref<Group[]>([])
const availablePermissions = ref<Permission[]>([])

onMounted(async () => {
  try {
    const response = await accountsApi.getUser({
      userId: parseInt(route.params.id as string)
    })
    
    availableGroups.value = response.groups
    availablePermissions.value = response.userPermissions

    user.value = {
      email: response.email,
      firstName: response.firstName,
      lastName: response.lastName,
      username: response.username,
      password: '',
      isActive: response.isActive,
      isStaff: response.isStaff,
      isSuperuser: response.isSuperuser,
      notes: response.notes ?? '',
      groups: response.groups,
      userPermissions: response.userPermissions
    }
    // Set document title for editing user
    document.title = `Edit User: ${response.email} – Admin – ooo-yay.com`
  } catch (error) {
    console.error('Error fetching user:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load user',
      life: 3000
    })
    router.push({ name: 'admin-users' })
  }
})

const handleSubmit = async () => {
  try {
    await accountsApi.updateUser({
      userId: parseInt(route.params.id as string),
      adminUserModify: user.value
    })
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'User updated successfully',
      life: 3000
    })
    router.push({ name: 'admin-users' })
  } catch (error) {
    console.error('Error updating user:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to update user',
      life: 3000
    })
  }
}
</script> 