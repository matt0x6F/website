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
	import { authenticatedStore, getUsername, isAuthenticated, removeAccessToken, removeRefreshToken, removeUserData, removeUsername, usernameStore } from '../../stores/auth';
	import { addToast, notifications } from '../../stores/notifications';
	import { CheckCircleSolid } from 'flowbite-svelte-icons';
	import { goto } from '$app/navigation';

    let authenticated: boolean = $authenticatedStore;

    authenticatedStore.subscribe((value) => {
        authenticated = value;
    });

    onMount(async () => {
        authenticated = await isAuthenticated();
    })

    notifications.subscribe((notifs) => {
        for (var notification of notifs) {
            toasts[notification.id] = notification.toastStatus;
        }
    })

    let toasts: Record<number, boolean> = {}

    const signOut = () => {
        console.log("Signing out")

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
                <span class="block text-sm">{$usernameStore}</span>
                <span class="block truncate text-sm font-medium">name@flowbite.com</span>
            </DropdownHeader>
            <DropdownItem>Dashboard</DropdownItem>
            <DropdownItem>Settings</DropdownItem>
            <DropdownItem>Earnings</DropdownItem>
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
        </NavUl>
    </Navbar>

    <slot></slot>
</div>