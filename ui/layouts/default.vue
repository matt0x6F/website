<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useAuthStore } from '~/stores/auth';
import LoginDialog from '~/components/LoginDialog.vue';
import MainNav from '~/components/MainNav.vue';
import MainFooter from '~/components/MainFooter.vue';
// PrimeVue MenuBar, Button, Toast, etc. should be auto-imported or imported as needed

const userStore = useAuthStore();
const showLoginDialog = ref(false);
const isDarkMode = ref(false);

onMounted(() => {
  isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches;
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    isDarkMode.value = e.matches;
  });
});

const handleLoginClick = () => {
    showLoginDialog.value = true;
};
</script>

<template>
  <MainNav @login="handleLoginClick" />
  <div class="max-w-screen-lg mx-auto space-y-4">
    <div class="min-h-64">
      <NuxtPage />
    </div>
    <MainFooter />
  </div>
  <LoginDialog v-model:visible="showLoginDialog" />
</template>

<style scoped>
@media print {
  .no-print {
    display: none !important;
  }
}
</style> 