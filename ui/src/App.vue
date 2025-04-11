<script setup lang="ts">
import { RouterView } from 'vue-router'
import { ref } from "vue";
import { useAuthStore } from './stores/auth';
import LoginDialog from './components/LoginDialog.vue';

const userStore = useAuthStore();
const showLoginDialog = ref(false);

const items = ref([
    {
        label: 'Home',
        icon: 'pi pi-home',
        route: '/'
    },
    {
        label: 'About',
        icon: 'pi pi-info-circle',
        route: '/about'
    },
    {
        label: 'Blog',
        icon: 'pi pi-fw pi-pencil',
        route: '/blog'
    },
    {
        label: 'Admin',
        icon: 'pi pi-lock',
        visible: () => userStore.isLoggedIn,
        items: [
            {
                label: 'Dashboard',
                icon: 'pi pi-chart-line',
                route: '/admin/'
            },
            {
                label: 'Posts',
                icon: 'pi pi-file',
                route: '/admin/posts'
            },
            {
                label: 'Users',
                icon: 'pi pi-users',
                route: '/admin/users'
            },
            {
                label: 'Comments',
                icon: 'pi pi-comments',
                route: '/admin/comments'
            }
        ]
    }
]);

const handleLoginClick = () => {
    showLoginDialog.value = true;
};
</script>

<template>
  <Toast />
  <div class="max-w-screen-lg mx-auto space-y-4">
    <MenuBar :model="items">
      <template #item="{ item, props, hasSubmenu }">
        <router-link v-if="item.route" v-slot="{ href, navigate }" :to="item.route" custom>
            <a v-ripple :href="href" v-bind="props.action" @click="navigate">
                <span :class="item.icon" />
                <span>{{ item.label }}</span>
                <span v-if="hasSubmenu" class="pi pi-fw pi-angle-down ml-2" />
            </a>
        </router-link>
        <a v-else v-ripple v-bind="props.action">
            <span :class="item.icon" />
            <span>{{ item.label }}</span>
            <span v-if="hasSubmenu" class="pi pi-fw pi-angle-down ml-2" />
        </a>
      </template>
      <template #end>
        <div class="flex items-center gap-2">
            <template v-if="userStore.isLoggedIn">
                <span>Welcome, <RouterLink :to="'/profile'" class="text-primary hover:underline">
                    {{ userStore.userData.username }}
                </RouterLink></span>
            </template>
            <template v-else>
                <Button label="Login" size="small" @click="handleLoginClick" />
            </template>
        </div>
      </template>
    </MenuBar>

    <div class="min-h-64">
      <RouterView />
    </div>
    <div>
        <p class="m-0 text-xs text-center">
            Copyright &copy; 2022-2025 Matt Ouille. All rights reserved.
        </p>
    </div>
  </div>

  <LoginDialog v-model:visible="showLoginDialog" />
</template>

<style scoped>

</style>