<template>
    <MainNav />
    <div class="min-h-screen">
        <header class="bg-white border-b px-6 py-4 shadow-sm dark:bg-neutral-900 dark:border-neutral-700 rounded-sm">
            <div class="flex items-center justify-between max-w-7xl mx-auto">
            <div class="flex items-center space-x-4">
                <h2 class="text-xl font-bold text-gray-800 dark:text-white">Admin Dashboard</h2>
                <nav class="hidden sm:flex space-x-4">
                <NuxtLink 
                    v-for="link in navLinks" 
                    :key="link.to"
                    :to="link.to"
                    class="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-100 text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white"
                >
                    <span :class="link.icon" class="mr-2" />
                    {{ link.text }}
                </NuxtLink>
                </nav>
            </div>
            </div>
        </header>
        <div class="max-w-7xl mx-auto px-4 sm:px-6 py-8 min-h-64">
            <NuxtPage />
        </div>
        <MainFooter />
    </div>
</template>
  
<script setup lang="ts">
import MainNav from '~/components/MainNav.vue';
import MainFooter from '~/components/MainFooter.vue';
const navLinks = [
    { to: '/admin/', text: 'Dashboard', icon: 'pi pi-chart-line' },
    { to: '/admin/posts', text: 'Posts', icon: 'pi pi-file' },
    { to: '/admin/series', text: 'Series', icon: 'pi pi-list' },
    { to: '/admin/users', text: 'Users', icon: 'pi pi-users' },
    { to: '/admin/comments', text: 'Comments', icon: 'pi pi-comments' },
    { to: '/admin/files', text: 'Files', icon: 'pi pi-folder' },
];
</script> 