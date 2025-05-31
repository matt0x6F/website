<script setup lang="ts">
import { useAuthStore } from '../stores/auth';
import { ref, computed, onMounted } from 'vue';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { useToast } from 'primevue/usetoast';

const authStore = useAuthStore();
const toast = useToast();
const editMode = ref(false);

const formData = ref({
    username: authStore.userData.username,
    email: authStore.userData.email,
    firstName: authStore.userData.firstName,
    lastName: authStore.userData.lastName,
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
});

// Password validation rules
const passwordRules = {
    minLength: 8,
    requireUppercase: true,
    requireLowercase: true,
    requireNumber: true,
    requireSpecial: true
};

// Validation states
const validationErrors = ref({
    newPassword: '',
    confirmPassword: ''
});

// Validation functions
const validatePasswordComplexity = (password: string): string => {
    if (password.length < passwordRules.minLength) {
        return `Password must be at least ${passwordRules.minLength} characters long`;
    }
    if (passwordRules.requireUppercase && !/[A-Z]/.test(password)) {
        return 'Password must contain at least one uppercase letter';
    }
    if (passwordRules.requireLowercase && !/[a-z]/.test(password)) {
        return 'Password must contain at least one lowercase letter';
    }
    if (passwordRules.requireNumber && !/\d/.test(password)) {
        return 'Password must contain at least one number';
    }
    if (passwordRules.requireSpecial && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        return 'Password must contain at least one special character';
    }
    return '';
};

const validatePasswords = () => {
    validationErrors.value.newPassword = '';
    validationErrors.value.confirmPassword = '';

    if (formData.value.newPassword) {
        // Check password complexity
        const complexityError = validatePasswordComplexity(formData.value.newPassword);
        if (complexityError) {
            validationErrors.value.newPassword = complexityError;
            return false;
        }

        // Check if new password is same as old password
        if (formData.value.newPassword === formData.value.oldPassword) {
            validationErrors.value.newPassword = 'New password must be different from current password';
            return false;
        }

        // Check if passwords match
        if (formData.value.newPassword !== formData.value.confirmPassword) {
            validationErrors.value.confirmPassword = 'Passwords do not match';
            return false;
        }
    }

    return true;
};

// Reset form data when entering edit mode
const handleEdit = () => {
    formData.value = {
        username: authStore.userData.username,
        email: authStore.userData.email,
        firstName: authStore.userData.firstName,
        lastName: authStore.userData.lastName,
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
    };
    validationErrors.value = {
        newPassword: '',
        confirmPassword: ''
    };
    editMode.value = true;
};

const handleSave = async () => {
    try {
        // Validate passwords if either password field is filled
        if (formData.value.oldPassword || formData.value.newPassword) {
            if (!formData.value.oldPassword) {
                validationErrors.value.newPassword = 'Current password is required to change password';
                return;
            }
            if (!formData.value.newPassword) {
                validationErrors.value.newPassword = 'New password is required';
                return;
            }
            if (!validatePasswords()) {
                return;
            }
        }

        const updateData = {
            username: formData.value.username,
            email: formData.value.email,
            firstName: formData.value.firstName,
            lastName: formData.value.lastName,
            ...(formData.value.oldPassword && formData.value.newPassword ? {
                oldPassword: formData.value.oldPassword,
                newPassword: formData.value.newPassword
            } : {})
        };
        
        await authStore.updateProfile(updateData);
        editMode.value = false;
        toast.add({
            severity: 'success',
            summary: 'Profile Updated',
            detail: 'Your profile has been successfully updated',
            life: 3000
        });
    } catch (error) {
        console.error(error);
        toast.add({
            severity: 'error',
            summary: 'Update Failed',
            detail: 'Failed to update profile. Please try again.',
            life: 5000
        });
    }
};

const handleLogout = async () => {
    await authStore.logout();
};

onMounted(() => {
  document.title = 'Profile – ooo-yay.com';
});
</script>

<template>
    <div class="p-4">
        <h1 class="text-2xl font-bold mb-6">Profile</h1>
        
        <div class="max-w-md space-y-4">
            <div v-if="!editMode">
                <div class="mb-4">
                    <p class="text-sm text-gray-600">Username</p>
                    <p class="font-medium">{{ authStore.userData.username }}</p>
                </div>
                <div class="mb-4">
                    <p class="text-sm text-gray-600">Email</p>
                    <p class="font-medium">{{ authStore.userData.email }}</p>
                </div>
                <div class="mb-4">
                    <p class="text-sm text-gray-600">First Name</p>
                    <p class="font-medium">{{ authStore.userData.firstName }}</p>
                </div>
                <div class="mb-4">
                    <p class="text-sm text-gray-600">Last Name</p>
                    <p class="font-medium">{{ authStore.userData.lastName }}</p>
                </div>
                <div class="mb-4">
                    <p class="text-sm text-gray-600">Member Since</p>
                    <p class="font-medium">{{ new Date(authStore.userData.dateJoined).toLocaleDateString() }}</p>
                </div>
                <div class="flex gap-2">
                    <Button label="Edit Profile" @click="handleEdit" />
                    <Button label="Logout" severity="danger" @click="handleLogout" />
                </div>
            </div>

            <div v-else class="space-y-4">
                <div class="field">
                    <label for="username" class="block text-sm text-gray-600">Username</label>
                    <InputText id="username" v-model="formData.username" class="w-full" />
                </div>
                <div class="field">
                    <label for="email" class="block text-sm text-gray-600">Email</label>
                    <InputText id="email" v-model="formData.email" class="w-full" type="email" />
                </div>
                <div class="field">
                    <label for="firstName" class="block text-sm text-gray-600">First Name</label>
                    <InputText id="firstName" v-model="formData.firstName" class="w-full" />
                </div>
                <div class="field">
                    <label for="lastName" class="block text-sm text-gray-600">Last Name</label>
                    <InputText id="lastName" v-model="formData.lastName" class="w-full" />
                </div>
                
                <!-- Password section -->
                <div class="mt-6 pt-6 border-t border-gray-200">
                    <h3 class="text-lg font-medium mb-4">Change Password</h3>
                    <div class="field">
                        <label for="oldPassword" class="block text-sm text-gray-600">Current Password</label>
                        <InputText id="oldPassword" v-model="formData.oldPassword" type="password" class="w-full" />
                    </div>
                    <div class="field">
                        <label for="newPassword" class="block text-sm text-gray-600">New Password</label>
                        <InputText id="newPassword" v-model="formData.newPassword" type="password" class="w-full" />
                        <small class="text-red-500" v-if="validationErrors.newPassword">{{ validationErrors.newPassword }}</small>
                    </div>
                    <div class="field">
                        <label for="confirmPassword" class="block text-sm text-gray-600">Confirm New Password</label>
                        <InputText id="confirmPassword" v-model="formData.confirmPassword" type="password" class="w-full" />
                        <small class="text-red-500" v-if="validationErrors.confirmPassword">{{ validationErrors.confirmPassword }}</small>
                    </div>
                </div>

                <div class="flex gap-2">
                    <Button label="Save" @click="handleSave" />
                    <Button label="Cancel" severity="secondary" @click="editMode = false" />
                </div>
            </div>
        </div>
    </div>
</template> 