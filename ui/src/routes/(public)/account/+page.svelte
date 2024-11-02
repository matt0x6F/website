<script lang="ts">
	import { goto } from '$app/navigation';
	import { PUBLIC_BASE_URL } from '$env/static/public';
	import { AccountsApi, Configuration, TokenApi, type UpdateAccount } from '$lib/api';

	import { Button, ButtonGroup, Input, InputAddon, Label } from 'flowbite-svelte';
	import { LockSolid, UserCircleSolid, TrashBinSolid, EnvelopeSolid } from 'flowbite-svelte-icons';
	import { retrieveAccessToken, getRefreshToken } from '../../../stores/auth';
	import { addToast } from '../../../stores/notifications';
	import type { PageData } from './$types';
	import { removeCookie } from 'typescript-cookie';

	export let data: PageData;

	let username = data.account.username;
	let email = data.account.email;
	let oldPassword = '';
	let newPassword = '';
	let newPassword2 = '';
	let firstName = data.account.firstName;
	let lastName = data.account.lastName;

	const saveUserData = async () => {
		if (oldPassword !== '' && newPassword !== newPassword2) {
			addToast({
				message: 'Passwords do not match'
			});
			return;
		}

		let token = undefined;
		try {
			token = await retrieveAccessToken();
		} catch {
			goto('/login');
		}

		const config = new Configuration({
			basePath: PUBLIC_BASE_URL,
			headers: {
				Authorization: `Bearer ${token}`
			}
		});

		const accountsAPI = new AccountsApi(config);

		try {
			let payload: UpdateAccount = {
				username: username,
				email: email,
				firstName: firstName,
				lastName: lastName
			};

			if (oldPassword !== '') {
				payload.oldPassword = oldPassword;
			}

			if (newPassword !== '') {
				payload.newPassword = newPassword;
			}

			let user = await accountsAPI.accountsApiUpdateSelf({
				updateAccount: payload
			});

			addToast({
				message: 'Account updated!'
			});
		} catch (error) {
			console.log('Error while updating account: ' + error);
		}
	};

	const deleteAccount = async () => {
		let token = undefined;
		try {
			token = await retrieveAccessToken();
		} catch {
			goto('/login');
		}

		const config = new Configuration({
			basePath: PUBLIC_BASE_URL,
			headers: {
				Authorization: `Bearer ${token}`
			}
		});

		const accountsAPI = new AccountsApi(config);

		try {
			await accountsAPI.accountsApiDeleteSelf();

			removeCookie('refresh_token');
			removeCookie('access_token');

			addToast({
				message: 'Account deleted!'
			});

			goto('/login');

			return;
		} catch (error) {
			console.log('Error while deleting account: ' + error);
		}
	};
</script>

<form on:submit|preventDefault={() => saveUserData()}>
	<div class="mx-auto max-w-sm">
		<div class="mb-6">
			<Label for="username" class="mb-2 block">Username</Label>
			<ButtonGroup class="w-full">
				<InputAddon>
					<UserCircleSolid class="h-4 w-4 text-gray-500 dark:text-gray-400" />
				</InputAddon>
				<Input id="username" bind:value={username} placeholder="mandretti" />
			</ButtonGroup>
		</div>

		<div class="mb-6">
			<Label for="email" class="mb-2 block">Email</Label>
			<ButtonGroup class="w-full">
				<InputAddon>
					<EnvelopeSolid class="h-4 w-4 text-gray-500 dark:text-gray-400" />
				</InputAddon>
				<Input type="email" id="email" bind:value={email} placeholder="mario@andretti.com" />
			</ButtonGroup>
		</div>

		<div class="mb-6">
			<Label for="old-password" class="mb-2 block">Old Password</Label>
			<ButtonGroup class="w-full">
				<InputAddon>
					<LockSolid class="h-4 w-4 text-gray-500 dark:text-gray-400" />
				</InputAddon>
				<Input
					id="old-password"
					bind:value={oldPassword}
					placeholder="old password"
					type="password"
				/>
			</ButtonGroup>
		</div>

		<div class="mb-6">
			<Label for="new-password" class="mb-2 block">New Password</Label>
			<ButtonGroup class="w-full">
				<InputAddon>
					<LockSolid class="h-4 w-4 text-gray-500 dark:text-gray-400" />
				</InputAddon>
				<Input
					id="new-password"
					disabled={oldPassword === ''}
					bind:value={newPassword}
					placeholder="new password"
					type="password"
				/>
			</ButtonGroup>
		</div>

		<div class="mb-6">
			<Label for="new-password-verification" class="mb-2 block">New Password verification</Label>
			<ButtonGroup class="w-full">
				<InputAddon>
					<LockSolid class="h-4 w-4 text-gray-500 dark:text-gray-400" />
				</InputAddon>
				<Input
					id="new-password-verification"
					disabled={newPassword === ''}
					bind:value={newPassword2}
					placeholder="new password"
					type="password"
				/>
			</ButtonGroup>
		</div>

		<div class="mb-6">
			<Label for="first-name" class="mb-2 block">First name</Label>
			<ButtonGroup class="w-full">
				<InputAddon>
					<UserCircleSolid class="h-4 w-4 text-gray-500 dark:text-gray-400" />
				</InputAddon>
				<Input id="first-name" bind:value={firstName} placeholder="Mario" />
			</ButtonGroup>
		</div>

		<div class="mb-6">
			<Label for="last-name" class="mb-2 block">Last name</Label>
			<ButtonGroup class="w-full">
				<InputAddon>
					<UserCircleSolid class="h-4 w-4 text-gray-500 dark:text-gray-400" />
				</InputAddon>
				<Input id="last-name" bind:value={lastName} placeholder="Andretti" />
			</ButtonGroup>
		</div>

		<div class="text-center">
			<Button type="submit">Save details</Button>
		</div>

		<div class="mt-10 text-center">
			<p class="text-sm">Account deletions are permanent and cannot be undone.</p>
			<Button color="red" class="mt-4" type="button" on:click={() => deleteAccount()}>
				<TrashBinSolid class="h-4 w-4" />
				Delete account
			</Button>
		</div>
	</div>
</form>
