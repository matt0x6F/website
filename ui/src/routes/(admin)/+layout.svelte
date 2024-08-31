<script lang="ts">
	import { onMount } from 'svelte';
	import '../../app.css';
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

		Toast

	} from 'flowbite-svelte';
	import { authenticatedStore, getUserData, getUsername, isAuthenticated, removeAccessToken, removeRefreshToken, removeUserData, removeUsername, setUserData, userDataStore, usernameStore } from '../../stores/auth';
	import { addToast, notifications } from '../../stores/notifications';
	import { CheckCircleSolid, ChevronDownOutline } from 'flowbite-svelte-icons';
	import { goto } from '$app/navigation';

    let authenticated: boolean = $authenticatedStore;

    authenticatedStore.subscribe((value) => {
        authenticated = value;
    });

    onMount(async () => {
        authenticated = await isAuthenticated();

        if (!authenticated) {
            console.log("User is not authenticated. Redirecting to login page.");
            goto("/login");
        }

        await setUserData();

        let user = getUserData()

        if ((user) && !user.isStaff) {
            goto("/");
        }
    });

    let toasts: Record<number, boolean> = {}

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

        addToast({
                message: "You're logged out!"
        })

        goto("/");
    }
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
        <div class="flex items-center md:order-2">
            <Avatar id="avatar-menu" src="/images/profile-picture-3.webp"></Avatar>
            <NavHamburger class1="w-full md:flex md:w-auto md:order-1"></NavHamburger>
        </div>
        <Dropdown placement="bottom" triggeredby="#avatar-menu">
            {#if authenticated}
            <DropdownHeader>
                <span class="block text-sm">{$userDataStore.username}</span>
                <span class="block truncate text-sm font-medium">{$userDataStore.email}</span>
            </DropdownHeader>
            {#if $userDataStore.isStaff == true}
                <DropdownItem href="/admin">Admin</DropdownItem>
            {/if}
            <DropdownDivider></DropdownDivider>
            <DropdownItem on:click={() => signOut()}>Sign out</DropdownItem>
            {:else}
            <DropdownItem href="/login">Sign in</DropdownItem>
            {/if}
        </Dropdown>
        <NavUl>
            <NavLi href="/" active={true}>Home</NavLi>
            <NavLi href="/about">About</NavLi>
            <NavLi href="/blog">Blog</NavLi>
            <NavLi class="cursor-pointer">
                Admin<ChevronDownOutline class="w-6 h-6 ms-2 text-primary-800 dark:text-white inline" />
            </NavLi>
            <Dropdown class="w-44 z-20">
                <DropdownItem href="/admin">Dashboard</DropdownItem>
                <DropdownItem href="/admin/write">Write</DropdownItem>
            </Dropdown>
        </NavUl>
    </Navbar>

    <slot></slot>
</div>