<script lang="ts">
	import type { PageData } from './$types';
	import PostEditor from '$lib/components/PostEditor.svelte';

    let id = -1; // -1 means new post
    let title = "";
    let slug = "";
    let published_at = '';
    let content = '';
</script>

<PostEditor id={id} title={title} slug={slug} published_at={published_at} content={content} />