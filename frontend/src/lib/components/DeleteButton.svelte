<script lang="ts">
	import { PUBLIC_BASE_URL } from '$env/static/public';
	import { Configuration, PostsApi } from '$lib/api';
	import { Button } from 'flowbite-svelte';
	import { TrashBinSolid } from 'flowbite-svelte-icons';
	import { retrieveAccessToken } from '../../stores/auth';
	import { createEventDispatcher } from 'svelte';
	import { goto } from '$app/navigation';

	const dispatch = createEventDispatcher();

	export let postID: number;

	const deletePost = async () => {
		let token = undefined;
		try {
			token = await retrieveAccessToken();
		} catch (error) {
			goto('/login');
		}

		const config = new Configuration({
			basePath: PUBLIC_BASE_URL,
			headers: {
				Authorization: 'Bearer ' + token
			}
		});

		const api = new PostsApi(config);

		try {
			await api.blogApiDeletePost({ id: postID });

			// echo the update up to the parent component
			dispatch('postDeleted', {
				postID: postID
			});
		} catch (error) {
			console.error(error);
		}
	};
</script>

<Button size="xs" on:click={() => deletePost()}>
	<TrashBinSolid class="inline-block" ariaLabel="Delete this post" />
	Delete
</Button>
