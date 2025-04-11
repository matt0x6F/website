<script lang="ts">
	import type { AdminCommentList } from '$lib/api';
	import { Accordion, AccordionItem, ButtonGroup, Button, Input } from 'flowbite-svelte';
	import ModerationCommentOP from './ModerationCommentOP.svelte';
	import ModerationCommentParent from './ModerationCommentParent.svelte';
	import ModerationCommentChildren from './ModerationCommentChildren.svelte';
	import ModerationBar from './ModerationBar.svelte';
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	export let comment: AdminCommentList;

	function handleReviewed(event: CustomEvent) {
		comment.reviewed = event.detail.reviewed;
		comment.note = event.detail.note;
		comment.visible = event.detail.visible;

		// relay the event to the parent component
		dispatch('commentReviewed', {
			id: comment.id,
			reviewed: comment.reviewed,
			visible: comment.visible,
			note: comment.note
		});
	}
</script>

<div>
	<h3 class="text-xl font-semibold text-orange-600">Comment #{comment.id}</h3>
	<Accordion flush>
		{#if comment.parent}
			<AccordionItem open>
				<span slot="header">Parent</span>
				<ModerationCommentParent comment={comment.parent} />
			</AccordionItem>
		{/if}
		<AccordionItem open>
			<span slot="header">Original poster</span>
			<ModerationCommentOP {comment} />
		</AccordionItem>
		{#if comment.children !== undefined && comment.children !== null && comment.children?.length !== 0}
			<AccordionItem>
				<span slot="header">Replies</span>
				{#each comment.children as child (child.id)}
					<ModerationCommentChildren comment={child} />
				{/each}
			</AccordionItem>
		{/if}
	</Accordion>
	<ModerationBar {comment} on:commentReviewed={handleReviewed} />
</div>
