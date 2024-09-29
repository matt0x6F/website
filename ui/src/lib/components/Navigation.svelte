<script lang="ts">
	import { onMount } from 'svelte';
	import {
		Navbar,
		NavBrand,
		NavLi,
		NavUl,
		NavHamburger,
		Avatar,
		Dropdown,
		DropdownItem,
		DropdownHeader,
		DropdownDivider,
		Toast,
		Button
	} from 'flowbite-svelte';
	import { authenticatedStore, getUserData, isAuthenticated, removeAccessToken, removeRefreshToken, removeUserData, removeUsername, setUserData, userDataStore } from '../../stores/auth';
    import { type UserSelf } from "$lib/api";
	import { addToast, notifications } from '../../stores/notifications';
	import { CheckCircleSolid, ChevronDownOutline } from 'flowbite-svelte-icons';
	import { goto } from '$app/navigation';

    export let staffOnly = false;

    let authenticated: boolean = $authenticatedStore;

    authenticatedStore.subscribe((value) => {
        authenticated = value;
    });

    let userData: UserSelf | undefined = undefined
    let toasts: Record<number, boolean> = {}

    userDataStore.subscribe((value) => {
        userData = value;
    });

    notifications.subscribe((notifs) => {
        for (var notification of notifs) {
            toasts[notification.id] = notification.toastStatus;
        }
    })

    const signOut = () => {
        console.log("Sign out")

        removeAccessToken();
        removeRefreshToken();
        removeUsername();
        removeUserData();

        userData = undefined;

        addToast({
                message: "You're logged out!"
        })

        goto("/");
    }

    onMount(async () => {
        authenticated = await isAuthenticated();

        if (!authenticated && staffOnly) {
            console.log("User is not authenticated. Redirecting to login page.");
            goto("/login");
        }

        await setUserData();

        let user = getUserData()
        userData = user;

        if ((user) && (!user.isStaff && staffOnly)) {
            goto("/");
        }
    });
</script>

{#if $notifications}
    {#each $notifications as notification (notification.id)}
        <Toast dismissable={notification.dismissable} transition={notification.transition} position={notification.position} toastStatus={toasts[notification.id]}>
            <CheckCircleSolid slot="icon" class="w-5 h-5" />
            {notification.message}
        </Toast>
    {/each}
{/if}

<div class="max-w-screen-2xl mx-auto">
    <Navbar>
        <NavBrand href="/">
            <span class="self-center whitespace-nowrap text-xl font-semibold dark:text-white">ooo-yay.com</span>
        </NavBrand>
        {#if userData !== undefined}
        <div class="flex items-center md:order-2">
            <Avatar id="avatar-menu" src="/img/neon_fellow_mushroom_forest.png" rounded />
            <NavHamburger class1="w-full md:flex md:w-auto md:order-1"></NavHamburger>
        </div>
        <Dropdown placement="bottom" triggeredby="#avatar-menu">
            <DropdownHeader>
                <span class="block text-sm">{userData.username}</span>
                <span class="block truncate text-sm font-medium">{userData.email}</span>
            </DropdownHeader>
            {#if userData.isStaff == true}
                <DropdownItem href="/admin">Admin</DropdownItem>
            {/if}
            <DropdownDivider></DropdownDivider>
            <DropdownItem on:click={() => signOut()}>Sign out</DropdownItem>
        </Dropdown>
        {:else}
        <div class="flex items-center md:order-2">
            <Button href="/login">Sign in</Button>
            <NavHamburger class1="w-full md:flex md:w-auto md:order-1"></NavHamburger>
        </div>
        {/if}
        <NavUl>
            <NavLi href="/" active={true}>Home</NavLi>
            <NavLi href="/about">About</NavLi>
            <NavLi href="/blog">Blog</NavLi>
            {#if userData !== undefined && userData.isStaff == true}
            <NavLi class="cursor-pointer">
                Admin<ChevronDownOutline class="w-6 h-6 ms-2 text-primary-800 dark:text-white inline" />
            </NavLi>
            <Dropdown class="w-44 z-20">
                <DropdownItem href="/admin">Dashboard</DropdownItem>
                <DropdownItem href="/admin/write">Write</DropdownItem>
                <DropdownItem href="/admin/files">Files</DropdownItem>
            </Dropdown>
            {/if}
        </NavUl>
    </Navbar>

    <slot></slot>
</div>