<template>
  <Toast />
  <div class="max-w-screen-lg mx-auto mb-4">
    <nav>
      <MenuBar :model="items" class="no-print">
        <template #start>
          <span class="font-bold text-lg">m</span>
          <span class="font-semibold text-lg text-emerald-500">@</span>
          <span class="font-bold text-lg">ooo-yay</span>
        </template>
        <template #item="{ item, props, hasSubmenu }">
          <NuxtLink v-if="item.route" v-slot="{ href, navigate }" :to="item.route" custom>
            <a v-ripple :href="href" v-bind="props.action" @click="navigate">
              <span :class="item.icon" />
              <span>{{ item.label }}</span>
              <span v-if="hasSubmenu" class="pi pi-fw pi-angle-down ml-2" />
            </a>
          </NuxtLink>
          <a v-else v-ripple v-bind="props.action">
            <span :class="item.icon" />
            <span>{{ item.label }}</span>
            <span v-if="hasSubmenu" class="pi pi-fw pi-angle-down ml-2" />
          </a>
        </template>
        <template #end>
          <div class="flex items-center gap-2">
            <template v-if="userStore.isLoggedIn">
              <span>Welcome, <NuxtLink :to="'/profile'" class="text-emerald-500 hover:underline">
                {{ userStore.userData.username }}
              </NuxtLink></span>
            </template>
            <template v-else>
              <Button label="Login" size="small" @click="$emit('login')" />
            </template>
          </div>
        </template>
      </MenuBar>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '~/stores/auth';

defineEmits(['login'])

const userStore = useAuthStore();
const items = ref([
  { label: 'Home', icon: 'pi pi-home', route: '/' },
  { label: 'About', icon: 'pi pi-info-circle', route: '/about' },
  { label: 'Blog', icon: 'pi pi-fw pi-pencil', route: '/blog' },
  { label: 'Resume', icon: 'pi pi-id-card', route: '/resume' },
  { label: 'Admin', icon: 'pi pi-lock', route: '/admin/', visible: () => userStore.isLoggedIn }
]);
</script>

<style scoped>
</style> 