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
	import { getUserDetails } from '../../stores/auth';
	import { type UserSelf } from '$lib/api';
	import { addToast, notifications } from '../../stores/notifications';
	import { CheckCircleSolid, ChevronDownOutline } from 'flowbite-svelte-icons';
	import { goto } from '$app/navigation';
	import { removeCookie } from 'typescript-cookie';

	export let staffOnly = false;

	let userDetails: UserSelf | undefined = undefined;
	let toasts: Record<number, boolean> = {};

	notifications.subscribe((notifs) => {
		for (var notification of notifs) {
			toasts[notification.id] = notification.toastStatus;
		}
	});

	const signOut = () => {
		console.log('Sign out');

		removeCookie('access_token');
		removeCookie('refresh_token');

		userDetails = undefined;

		addToast({
			message: "You're logged out!"
		});

		goto('/');
	};

	onMount(async () => {
		try {
			userDetails = await getUserDetails();
		} catch {
			if (staffOnly) {
				goto('/login');
			}
		}

		if (!userDetails?.isStaff && staffOnly) {
			goto('/');
		}
	});
</script>

{#if $notifications}
	{#each $notifications as notification (notification.id)}
		<Toast
			dismissable={notification.dismissable}
			transition={notification.transition}
			position={notification.position}
			toastStatus={toasts[notification.id]}
		>
			<CheckCircleSolid slot="icon" class="h-5 w-5" />
			{notification.message}
		</Toast>
	{/each}
{/if}

<div class="mx-auto max-w-screen-2xl">
	<Navbar>
		<NavBrand href="/">
			<span class="self-center whitespace-nowrap text-xl font-semibold dark:text-white"
				>ooo-yay.com</span
			>
		</NavBrand>
		{#if userDetails !== undefined}
			<div class="flex items-center md:order-2">
				<Avatar id="avatar-menu" src="/img/neon_fellow_mushroom_forest.png" rounded />
				<NavHamburger class1="w-full md:flex md:w-auto md:order-1"></NavHamburger>
			</div>
			<Dropdown placement="bottom" triggeredby="#avatar-menu">
				<DropdownHeader>
					<span class="block text-sm">{userDetails.username}</span>
					<span class="block truncate text-sm font-medium">{userDetails.email}</span>
				</DropdownHeader>
				{#if userDetails.isStaff == true}
					<DropdownItem href="/admin">Admin</DropdownItem>
				{/if}
				<DropdownItem href="/account">Account</DropdownItem>
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
			{#if userDetails !== undefined && userDetails.isStaff == true}
				<NavLi class="cursor-pointer">
					Admin<ChevronDownOutline class="text-primary-800 ms-2 inline h-6 w-6 dark:text-white" />
				</NavLi>
				<Dropdown class="z-20 w-44">
					<DropdownItem href="/admin">Dashboard</DropdownItem>
					<DropdownItem href="/admin/write">Write</DropdownItem>
					<DropdownItem href="/admin/files">Files</DropdownItem>
					<DropdownItem href="/admin/comments/queue">Comment Queue</DropdownItem>
				</Dropdown>
			{/if}
		</NavUl>
	</Navbar>

	<slot></slot>
</div>
