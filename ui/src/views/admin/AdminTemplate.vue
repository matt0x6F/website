<template>
  <div class="min-h-screen">
    <header class="bg-white border-b px-6 py-4 shadow-sm dark:bg-neutral-900 dark:border-neutral-700 rounded-sm">
      <div class="flex items-center justify-between max-w-7xl mx-auto">
        <div class="flex items-center space-x-4">
          <h2 class="text-xl font-bold text-gray-800 dark:text-white">Admin Dashboard</h2>
          <nav class="hidden sm:flex space-x-4">
            <router-link 
              v-for="link in navLinks" 
              :key="link.to"
              :to="link.to"
              class="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-100 text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white"
            >
              {{ link.text }}
            </router-link>
          </nav>
        </div>
      </div>
    </header>
    <main class="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
const navLinks = [
  { to: '/admin/posts', text: 'Posts' },
  { to: '/admin/users', text: 'Users' },
  { to: '/admin/comments', text: 'Comments' },
]
</script> 