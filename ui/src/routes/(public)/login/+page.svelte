<script lang="ts">
	import { PUBLIC_BASE_URL } from '$env/static/public';
	import { Configuration, ResponseError, TokenApi } from '$lib/api';

	import { Button, ButtonGroup, Input, InputAddon, Label } from 'flowbite-svelte';
	import { LockSolid, UserCircleSolid } from 'flowbite-svelte-icons';
	import { addToast } from '../../../stores/notifications';
	import { setCookie } from 'typescript-cookie';
	import { goto } from '$app/navigation';
	import { getUserDetails } from '../../../stores/auth';

	let username = '';
	let password = '';

	const signIn = async () => {
		const config = new Configuration({
			basePath: PUBLIC_BASE_URL
		});

		const client = new TokenApi(config);

		try {
			let tokens = await client.tokenObtainPair({
				tokenObtainPairInputSchema: {
					username: username,
					password: password
				}
			});

			// expires in 5 minutes
			setCookie('access_token', tokens.access, { expires: new Date().getTime() + 300000 });
			// expires in 24 hours
			setCookie('refresh_token', tokens.refresh, { expires: new Date().getTime() + 86400000 });

			addToast({
				message: "You're logged in!"
			});

			try {
				await getUserDetails();
			} catch (error) {
				console.log('Error while getting user details ' + error);
			}

			goto('/');
		} catch (error) {
			if (error instanceof ResponseError) {
				const body = await error.response.json();

				addToast({
					message: body.detail
				});
			} else {
				addToast({
					message: 'An error occurred while signing in'
				});

				console.log('Error while signing in ' + error);
			}
		}
	};
</script>

<form on:submit|preventDefault={() => signIn()}>
	<div class="mx-auto max-w-sm">
		<div class="mb-6">
			<Label for="username" class="mb-2 block">Username</Label>
			<ButtonGroup class="w-full">
				<InputAddon>
					<UserCircleSolid class="h-4 w-4 text-gray-500 dark:text-gray-400" />
				</InputAddon>
				<Input id="username" bind:value={username} placeholder="username" />
			</ButtonGroup>
		</div>

		<div class="mb-6">
			<Label for="password" class="mb-2 block">Password</Label>
			<ButtonGroup class="w-full">
				<InputAddon>
					<LockSolid class="h-4 w-4 text-gray-500 dark:text-gray-400" />
				</InputAddon>
				<Input id="password" bind:value={password} placeholder="password" type="password" />
			</ButtonGroup>
		</div>

		<div>
			<p>Not a user? <a href="/sign-up">Sign up!</a></p>
		</div>

		<div class="text-center">
			<Button type="submit">Login</Button>
		</div>
	</div>
</form>
