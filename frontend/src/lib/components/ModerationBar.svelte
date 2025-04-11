<script lang="ts">
	import { PUBLIC_BASE_URL } from '$env/static/public';
	import { CommentsApi, Configuration, type AdminCommentList } from '$lib/api';
	import { Button, ButtonGroup, Input, Badge } from 'flowbite-svelte';
	import { retrieveAccessToken } from '../../stores/auth';
	import { goto } from '$app/navigation';
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	export let comment: AdminCommentList;

	let visible = comment.visible;
	let note = comment.note;
	let reviewed = comment.reviewed;

	async function updateComment(setVisible: boolean) {
		visible = setVisible;

		let token = undefined;
		try {
			token = await retrieveAccessToken();
		} catch (error) {
			goto('/login');
		}

		const config = new Configuration({
			basePath: PUBLIC_BASE_URL,
			headers: { Authorization: 'Bearer ' + token }
		});

		const api = new CommentsApi(config);

		try {
			await api.blogApiModUpdateComment({
				id: comment.id,
				adminCommentUpdate: { visible: visible, note: note, reviewed: true }
			});

			reviewed = true;
			dispatch('commentReviewed', { id: comment.id, reviewed: true, visible: visible, note: note });
		} catch (error) {
			console.error(error);
		}
	}
</script>

<div class="mt-6 flex flex-row">
	<ButtonGroup>
		<Button size="sm" on:click={() => updateComment(true)}>Approve</Button>
		<Button
			on:click={() => updateComment(false)}
			class="border-red-700 bg-red-100 text-red-700 hover:bg-red-300 hover:text-red-800"
			size="sm">Reject</Button
		>
	</ButtonGroup>
	<Input bind:value={note} class="ml-4" type="text" placeholder="Reason for rejection" />
	{#if reviewed}
		<Badge class="ml-4" color="green">Reviewed</Badge>
	{:else}
		<Badge class="ml-4" color="purple">Unreviewed</Badge>
	{/if}
</div>
