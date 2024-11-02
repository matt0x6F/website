<script lang="ts">
	import 'carta-md/default.css'; /* Default theme */
	import '@cartamd/plugin-code/default.css';
	import '@cartamd/plugin-emoji/default.css';

	import DOMPurify from 'isomorphic-dompurify';
	import { Carta, MarkdownEditor } from 'carta-md';
	import { code } from '@cartamd/plugin-code';
	import { emoji } from '@cartamd/plugin-emoji';
	import Comment from '$lib/components/Comment.svelte';

	import type { PageData } from './$types';
	import { onMount } from 'svelte';
	import { retrieveAccessToken } from '../../../../../stores/auth';
	import { goto } from '$app/navigation';
	import { Button } from 'flowbite-svelte';
	import { CommentsApi, Configuration } from '$lib/api';
	import { PUBLIC_BASE_URL } from '$env/static/public';
	import { addToast } from '../../../../../stores/notifications';

	export let data: PageData;

	let parent = data.parent;
	let postID = data.postID;
	let content = '';

	const carta = new Carta({
		sanitizer: DOMPurify.sanitize,
		extensions: [code(), emoji()]
	});

	onMount(async () => {
		// require users to be logged in to view this page
		let token = undefined;
		try {
			token = await retrieveAccessToken();
		} catch {
			goto('/login');
		}
	});

	async function submitComment() {
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

		const commentsAPI = new CommentsApi(config);

		try {
			await commentsAPI.blogApiCreateComment({
				commentCreate: {
					content: content,
					parentId: parent?.id,
					postId: +postID
				}
			});

			addToast({
				message: 'Comment submitted successfully!'
			});

			// back to the post page
			window.history.back();
		} catch (error) {
			console.error(error);
		}
	}
</script>

<p class="mb-4">
	<button
		type="button"
		class="text-primary-800 hover:underline"
		on:click={() => window.history.back()}>Back to post</button
	>
</p>

{#if parent}
	<h2 class="text-lg font-semibold">Replying to</h2>
	<div class="border-primary-700 border-l-4 pl-4">
		<Comment showReplyButtons={false} showChildren={false} comment={parent} user={parent.author} />
	</div>
{/if}

<form on:submit|preventDefault={() => submitComment()} class="mt-6">
	<MarkdownEditor {carta} bind:value={content} />

	<Button type="submit" class="mt-6" color="primary">Submit</Button>
</form>

<style>
	/* Set your monospace font (Required to have the editor working correctly!) */
	:global(.carta-font-code) {
		font-family: 'Source Code Pro', monospace;
		font-size: 1.1rem;
		line-height: 1.5rem;
	}
</style>
