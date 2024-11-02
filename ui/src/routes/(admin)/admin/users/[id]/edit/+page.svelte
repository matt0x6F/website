<script lang="ts">
	import { Label, Input, Checkbox, Button } from 'flowbite-svelte';
	import type { PageData } from './$types';
	import { AccountsApi, Configuration, type AdminUserModify } from '$lib/api';
	import { retrieveAccessToken } from '../../../../../../stores/auth';
	import { PUBLIC_BASE_URL } from '$env/static/public';
	import { addToast } from '../../../../../../stores/notifications';
	import { goto } from '$app/navigation';

	export let data: PageData;

	let account = data.user;
	let password = '';
	let password2 = '';

	async function saveUser() {
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

		const modifications: AdminUserModify = {
			username: account.username,
			email: account.email,
			firstName: account.firstName,
			lastName: account.lastName,
			isActive: account.isActive,
			isSuperuser: account.isSuperuser,
			isStaff: account.isStaff
		};

		if (password !== '' && password2 !== '') {
			if (password === password2) {
				modifications.password = password;
			} else {
				addToast({
					message: 'Passwords must match'
				});

				return;
			}
		}

		try {
			await api.accountsApiUpdateUser({ userId: account.id, adminUserModify: modifications });

			addToast({
				message: 'User details changed successfully!'
			});
		} catch (error) {
			addToast({
				message: 'Error changing user details: ' + error
			});

			console.error(error);
		}
	}
</script>

<p><a href="/admin">Back to the admin dashboard</a></p>

<h1 class="text-lg font-semibold">Editing {account.username}</h1>

<form on:submit|preventDefault={() => saveUser()}>
	<div class="grid grid-cols-2 gap-4">
		<div>
			<div class="mb-6">
				<Label for="username" class="mb-2 block">Username</Label>
				<Input id="username" bind:value={account.username} placeholder="Username" />
			</div>

			<div class="mb-6">
				<Label for="email" class="mb-2 block">Email</Label>
				<Input id="email" bind:value={account.email} type="email" placeholder="Email" />
			</div>

			<div class="mb-6">
				<Label for="firstName" class="mb-2 block">First name</Label>
				<Input id="firstName" bind:value={account.firstName} placeholder="First name" />
			</div>

			<div class="mb-6">
				<Label for="lastName" class="mb-2 block">Last name</Label>
				<Input id="lastName" bind:value={account.lastName} placeholder="Last name" />
			</div>

			<div class="mb-6">
				<Label for="isActive" class="mb-2 block">Active</Label>
				<Checkbox id="isActive" bind:checked={account.isActive} />
			</div>

			<div class="mb-6">
				<Label for="isSuperuser" class="mb-2 block">Superuser</Label>
				<Checkbox id="isSuperuser" bind:checked={account.isSuperuser} />
			</div>

			<div class="mb-6">
				<Label for="isStaff" class="mb-2 block">Staff</Label>
				<Checkbox id="isStaff" bind:checked={account.isStaff} />
			</div>

			<Button type="submit">Save</Button>
		</div>
		<div>
			<div class="mb-6">
				<Label for="password" class="mb-2 block">Password</Label>
				<Input id="password" bind:value={password} type="password" placeholder="Password" />
			</div>
			<div class="mb-6">
				<Label for="confirmPassword" class="mb-2 block">Confirm password</Label>
				<Input
					id="confirmPassword"
					bind:value={password2}
					type="password"
					placeholder="Confirm password"
				/>
			</div>
			<div class="mb-6 text-center">
				<p class="text-xs text-gray-500">
					Leave the password fields empty to keep the current password.
				</p>
			</div>
		</div>
	</div>
</form>
