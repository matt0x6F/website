<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import SignupDialog from './SignupDialog.vue';

const authStore = useAuthStore();

const visible = defineModel<boolean>('visible');
const email = ref('');
const password = ref('');
const loading = ref(false);
const errorMessage = ref('');
const showSignup = ref(false);
const emailInputRef = ref<HTMLElement | null>(null);

const handleSubmit = async () => {
    try {
        loading.value = true;
        errorMessage.value = '';
        await authStore.login(email.value, password.value);
        visible.value = false;
        // Reset form
        email.value = '';
        password.value = '';
    } catch (error) {
        errorMessage.value = 'Invalid email or password';
    } finally {
        loading.value = false;
    }
};

const handleSignupClick = () => {
    visible.value = false;
    showSignup.value = true;
};
</script>

<template>
    <Dialog 
        v-model:visible="visible" 
        modal 
        header="Login" 
        :style="{ width: '350px' }"
        :closable="!loading"
    >
        <div class="flex flex-col gap-4">
            <div v-if="errorMessage" class="text-red-500 text-sm">
                {{ errorMessage }}
            </div>
            
            <div class="flex flex-col gap-2">
                <label for="email">Email</label>
                <InputText 
                    id="email"
                    v-model="email" 
                    type="email" 
                    :disabled="loading"
                    @keyup.enter="handleSubmit"
                    class="w-full"
                    ref="emailInputRef"
                    autofocus
                />
            </div>

            <div class="flex flex-col gap-2">
                <label for="password">Password</label>
                <Password 
                    id="password"
                    v-model="password" 
                    :feedback="false"
                    :disabled="loading"
                    @keyup.enter="handleSubmit"
                    class="w-full"
                    inputClass="w-full"
                />
            </div>
        </div>

        <template #footer>
            <div class="flex justify-between items-center w-full">
                <Button 
                    label="Login" 
                    @click="handleSubmit" 
                    :loading="loading"
                />
                <button 
                    @click="handleSignupClick"
                    class="text-sm hover:underline"
                    :disabled="loading"
                >
                    Create Account
                </button>
            </div>
        </template>
    </Dialog>

    <SignupDialog v-model:visible="showSignup" />
</template> 