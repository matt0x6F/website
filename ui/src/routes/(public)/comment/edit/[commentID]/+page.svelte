<script lang="ts">
	import 'carta-md/default.css'; /* Default theme */
	import '@cartamd/plugin-code/default.css';
	import '@cartamd/plugin-emoji/default.css';

	import DOMPurify from 'isomorphic-dompurify';
	import { Carta, MarkdownEditor } from 'carta-md';
	import { code } from '@cartamd/plugin-code';
	import { emoji } from '@cartamd/plugin-emoji';

	import type { PageData } from './$types';
	import { onMount } from 'svelte';
	import { retrieveAccessToken } from '../../../../../stores/auth';
	import { goto } from '$app/navigation';
	import { Button } from 'flowbite-svelte';
	import { CommentsApi, Configuration } from '$lib/api';
	import { PUBLIC_BASE_URL } from '$env/static/public';
	import { addToast } from '../../../../../stores/notifications';

	export let data: PageData;

	let comment = data.comment;
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

		if (comment === null) {
			goto('/404');
			return;
		}

		content = comment.content;
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
			if (comment == null) {
				return;
			}

			await commentsAPI.blogApiUpdateComment({
				id: +comment.id,
				commentMutate: {
					content: content
				}
			});

			addToast({
				message: 'Comment updated successfully!'
			});

			// back to the post page
			window.history.back();
		} catch (error) {
			console.error(error);
		}
	}
</script>

<form on:submit|preventDefault={() => submitComment()}>
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
