<script lang="ts">
	import type { PageData } from './$types';
	import PostEditor from '$lib/components/PostEditor.svelte';

    export let data: PageData;

    let id = data.post.id; // -1 means new post
    let title = data.post.title;
    let slug = data.post.slug;
    let published_at = data.post.published ? data.post.published.toISOString().slice(0, 16) : '';
    let content = data.post.content;
</script>

<PostEditor id={id} title={title} slug={slug} published_at={published_at} content={content} />