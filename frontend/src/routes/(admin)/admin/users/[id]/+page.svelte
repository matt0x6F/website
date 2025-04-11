<script lang="ts">
	import type { PageData } from './$types';
	import { formatDate } from '$lib/utils';
	import { Badge, Button, ButtonGroup } from 'flowbite-svelte';
	import { retrieveAccessToken } from '../../../../../stores/auth';
	import { AccountsApi, Configuration } from '$lib/api';
	import { PUBLIC_BASE_URL } from '$env/static/public';
	import { goto } from '$app/navigation';
	import { addToast } from '../../../../../stores/notifications';

	export let data: PageData;

	let user = data.user;

	async function deleteUser() {
		let token = undefined;
		try {
			token = await retrieveAccessToken();
		} catch {
			goto('/login');
		}

		const config = new Configuration({
			basePath: PUBLIC_BASE_URL,
			headers: {
				Authorization: 'Bearer ' + token
			}
		});

		const api = new AccountsApi(config);

		try {
			await api.accountsApiDeleteUser({ userId: user.id });

			addToast({
				message: 'User deleted successfully!'
			});

			goto('/admin');
		} catch (error) {
			addToast({
				message: 'Error deleting user: ' + error
			});

			console.error(error);
		}
	}
</script>

<p><a href="/admin">Back to the admin dashboard</a></p>

<ButtonGroup size="xs" class="my-4">
	<Button size="xs" href="/admin/users/{data.user.id}/edit">Edit</Button>
	<Button size="xs" on:click={() => deleteUser()} color="red">Delete</Button>
</ButtonGroup>

<h1 class="text-lg font-semibold">{user.username}</h1>

{#if user.isActive}
	<Badge border color="green">Active</Badge>
{:else}
	<Badge border color="red">Inactive</Badge>
{/if}

<p>Email: {user.email}</p>

<p>First name: {user.firstName}</p>

<p>Last name: {user.lastName}</p>

<p>Joined: {formatDate(user.dateJoined)}</p>

<p>Last login: {formatDate(user.lastLogin)}</p>

<h2 class="text-xl font-semibold">Groups and permissions</h2>

{#if user.isSuperuser}
	<Badge border color="purple">Superuser</Badge>
{/if}

{#if user.isStaff}
	<Badge border color="blue">Staff</Badge>
{/if}

{#if user.groups.length > 0}
	<h3 class="text-lg font-semibold">Groups</h3>

	{#each user.groups as group}
		<Badge border color="green">{group}</Badge>
	{/each}
{/if}

{#if user.userPermissions.length > 0}
	<h3 class="text-lg font-semibold">Permissions</h3>
	{#each user.userPermissions as permission}
		<Badge border color="yellow">{permission}</Badge>
	{/each}
{/if}
