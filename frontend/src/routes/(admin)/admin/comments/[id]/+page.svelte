<script lang="ts">
	import 'carta-md/default.css'; /* Default theme */
	import '@cartamd/plugin-code/default.css';
	import '@cartamd/plugin-emoji/default.css';

	import DOMPurify from 'isomorphic-dompurify';
	import { Carta } from 'carta-md';
	import { code } from '@cartamd/plugin-code';
	import { emoji } from '@cartamd/plugin-emoji';
	import Comment from '$lib/components/Comment.svelte';

	import type { PageData } from './$types';
	import { getUserDetails, userDetailsStore } from '../../../../../stores/auth';
	import { onMount } from 'svelte';
	import type { UserSelf } from '$lib/api';
	import { goto } from '$app/navigation';

	export let data: PageData;

	let userDetails: UserSelf | undefined = undefined;
	let comment = data.comment;

	const carta = new Carta({
		sanitizer: DOMPurify.sanitize,
		extensions: [code(), emoji()]
	});

	onMount(async () => {
		if ($userDetailsStore === undefined) {
			try {
				userDetails = await getUserDetails();
			} catch {
				// Redirect to login if user is not logged in
				goto('/login');
			}
		} else {
			userDetails = $userDetails;
		}
	});
</script>

{#if comment !== null}
	<Comment {comment} user={userDetails} />
{/if}

<style>
	/* Set your monospace font (Required to have the editor working correctly!) */
	:global(.carta-font-code) {
		font-family: 'Source Code Pro', monospace;
		font-size: 1.1rem;
		line-height: 1.5rem;
	}
</style>
