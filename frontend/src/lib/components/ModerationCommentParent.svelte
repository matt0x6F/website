<script lang="ts">
	import '@cartamd/plugin-code/default.css';
	import '@cartamd/plugin-emoji/default.css';
	import 'carta-md/default.css'; /* Default theme */

	import { Carta, Markdown } from 'carta-md';
	import DOMPurify from 'isomorphic-dompurify';
	import { code } from '@cartamd/plugin-code';
	import { emoji } from '@cartamd/plugin-emoji';
	import { CommentsApi, Configuration, type AdminParentCommentList } from '$lib/api';
	import { formatDate } from '$lib/utils';
	import { retrieveAccessToken } from '../../stores/auth';
	import { PUBLIC_BASE_URL } from '$env/static/public';
	import { addToast } from '../../stores/notifications';
	import { createEventDispatcher } from 'svelte';
	import { goto } from '$app/navigation';

	export let comment: AdminParentCommentList;

	const carta = new Carta({
		sanitizer: DOMPurify.sanitize,
		extensions: [code(), emoji()]
	});

	const dispatch = createEventDispatcher();

	async function hideComment() {
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

		const commentsAPI = new CommentsApi(config);

		try {
			await commentsAPI.blogApiModUpdateComment({
				id: comment.id,
				adminCommentUpdate: { visible: false, reviewed: true }
			});

			addToast({
				message: 'Comment deleted successfully'
			});

			dispatch('commentDeleted', { id: comment.id });
		} catch (error) {
			addToast({
				message: 'Error deleting comment: ' + error
			});

			console.error(error);
		}
	}
</script>

<div class="flex flex-col">
	<div>
		<p class="font-semibold">{comment.author.username}</p>
		<p class="text-sm text-gray-500">{formatDate(comment.createdAt)}</p>
		<p><Markdown {carta} value={comment.content} /></p>
	</div>
</div>
