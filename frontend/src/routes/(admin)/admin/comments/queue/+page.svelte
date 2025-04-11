<script lang="ts">
	import type { PageData } from './$types';
	import CommentModerationItem from '$lib/components/ModerationQueueItem.svelte';
	import { addToast } from '../../../../../stores/notifications';

	export let data: PageData;

	let comments = data.comments;

	function handleReviewed(event: CustomEvent) {
		// remove the comment from the list if it was reviewed
		if (event.detail.reviewed) {
			comments = comments.filter((c) => c.id !== event.detail.id);
			comments = comments;
		}

		addToast({
			message: 'Comment reviewed'
		});
	}
</script>

<h2 class="text-2xl font-semibold">Comment moderation queue</h2>

<div class="space-y-8">
	{#each comments as comment (comment.id)}
		<CommentModerationItem {comment} on:commentReviewed={handleReviewed} />
	{:else}
		<p>No comments to moderate.</p>
	{/each}
</div>
