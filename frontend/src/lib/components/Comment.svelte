<script lang="ts">
	import '@cartamd/plugin-code/default.css';
	import '@cartamd/plugin-emoji/default.css';
	import 'carta-md/default.css'; /* Default theme */

	import { Carta, Markdown } from 'carta-md';
	import DOMPurify from 'isomorphic-dompurify';
	import { code } from '@cartamd/plugin-code';
	import { emoji } from '@cartamd/plugin-emoji';
	import {
		CommentsApi,
		Configuration,
		type AuthorSummary,
		type CommentList,
		type UserSelf
	} from '$lib/api';
	import { formatDate } from '$lib/utils';
	import { retrieveAccessToken } from '../../stores/auth';
	import { PUBLIC_BASE_URL } from '$env/static/public';
	import { addToast } from '../../stores/notifications';
	import { createEventDispatcher } from 'svelte';
	import { goto } from '$app/navigation';

	export let comment: CommentList;
	// User viewing the comment
	export let user: UserSelf | AuthorSummary | undefined = undefined;
	// Show replies (aka children) or not
	export let showReplyButtons: boolean = true;
	export let showChildren: boolean = true;

	const carta = new Carta({
		sanitizer: DOMPurify.sanitize,
		extensions: [code(), emoji()]
	});

	const dispatch = createEventDispatcher();

	async function deleteComment() {
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
			await commentsAPI.blogApiDeleteComment({ id: comment.id });

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
		{#if showReplyButtons}
			<div class="space-x-2 text-xs font-semibold">
				<div class="inline-block">
					<a href="/comment/new/{comment.post.id}?parent={comment.id}">Reply</a>
				</div>
				{#if user !== undefined && comment.author.id === user.id}
					<div class="inline-block"><a href="/comment/edit/{comment.id}">Edit</a></div>
					<div class="inline-block">
						<button
							type="button"
							class="text-primary-800 hover:underline"
							on:click={() => deleteComment()}>Delete</button
						>
					</div>
				{/if}
			</div>
		{/if}
	</div>
	{#if showChildren}
		<div class="ml-4 mt-2">
			{#each comment.children as child (child.id)}
				<svelte:self on:commentDeleted comment={child} {user} />
			{/each}
		</div>
	{/if}
</div>
