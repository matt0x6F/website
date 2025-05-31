<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import type { NewAccount } from '../lib/api/models';

const authStore = useAuthStore();
const visible = defineModel<boolean>('visible');
const loading = ref(false);
const errorMessage = ref('');

const formData = ref<NewAccount>({
    username: '',
    email: '',
    password: '',
    firstName: '',
    lastName: ''
});

const handleSubmit = async () => {
    try {
        loading.value = true;
        errorMessage.value = '';
        await authStore.signup(formData.value);
        visible.value = false;
        // Reset form
        formData.value = {
            username: '',
            email: '',
            password: '',
            firstName: '',
            lastName: ''
        };
    } catch (error) {
        errorMessage.value = 'Failed to create account. Please try again.';
    } finally {
        loading.value = false;
    }
};
</script>

<template>
    <Dialog 
        v-model:visible="visible" 
        modal 
        header="Create Account" 
        :style="{ width: '400px' }"
        :closable="!loading"
    >
        <div class="flex flex-col gap-4">
            <div v-if="errorMessage" class="text-red-500 text-sm">
                {{ errorMessage }}
            </div>
            
            <div class="flex flex-col gap-2">
                <label for="username">Username*</label>
                <InputText 
                    id="username"
                    v-model="formData.username" 
                    :disabled="loading"
                    class="w-full"
                />
            </div>

            <div class="flex flex-col gap-2">
                <label for="email">Email*</label>
                <InputText 
                    id="email"
                    v-model="formData.email" 
                    type="email" 
                    :disabled="loading"
                    class="w-full"
                />
            </div>

            <div class="flex flex-col gap-2">
                <label for="password">Password*</label>
                <Password 
                    id="password"
                    v-model="formData.password" 
                    :feedback="false"
                    :disabled="loading"
                    class="w-full"
                    inputClass="w-full"
                />
            </div>

            <div class="flex gap-4">
                <div class="flex flex-col gap-2 flex-1">
                    <label for="firstName">First Name</label>
                    <InputText 
                        id="firstName"
                        v-model="formData.firstName" 
                        :disabled="loading"
                        class="w-full"
                    />
                </div>

                <div class="flex flex-col gap-2 flex-1">
                    <label for="lastName">Last Name</label>
                    <InputText 
                        id="lastName"
                        v-model="formData.lastName" 
                        :disabled="loading"
                        class="w-full"
                    />
                </div>
            </div>
        </div>

        <template #footer>
            <div class="flex justify-between items-center w-full">
                <Button 
                    label="Create Account" 
                    @click="handleSubmit" 
                    :loading="loading"
                />
            </div>
        </template>
    </Dialog>
</template> 