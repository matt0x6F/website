<script lang="ts">
	import '@cartamd/plugin-code/default.css';
	import '@cartamd/plugin-emoji/default.css';
	import '@cartamd/plugin-slash/default.css';
	import '@cartamd/plugin-anchor/default.css';
	import 'carta-md/default.css'; /* Default theme */

	import { Carta, Markdown } from 'carta-md';
	import DOMPurify from 'isomorphic-dompurify';
	import { code } from '@cartamd/plugin-code';
	import { emoji } from '@cartamd/plugin-emoji';
	import { slash } from '@cartamd/plugin-slash';
	import { anchor } from '@cartamd/plugin-anchor';
	import { Badge } from 'flowbite-svelte';
	import { MetaTags } from 'svelte-meta-tags';
	import Comment from '$lib/components/Comment.svelte';

	import { Button } from 'flowbite-svelte';
	import type { PageData } from './$types';
	import { getUserDetails } from '../../../../../../stores/auth';
	import type { CommentList, UserSelf } from '$lib/api';
	import { onMount } from 'svelte';
	import { formatDate, iso8601String, parseDateAsYear } from '$lib/utils';
	import { writable } from 'svelte/store';

	export let data: PageData;

	let post = data.post;
	let commentStore = writable(data.comments);

	let userDetails: UserSelf | undefined = undefined;
	let comments: CommentList[] = [];

	commentStore.subscribe((value) => {
		comments = value;
	});

	const carta = new Carta({
		sanitizer: DOMPurify.sanitize,
		extensions: [code(), emoji(), slash(), anchor()]
	});

	function removeCommentFromTree(event: CustomEvent) {
		const id = event.detail.id;

		const removeComment = (comments: CommentList[]) => {
			for (let i = 0; i < comments.length; i++) {
				if (comments[i].id === id) {
					comments.splice(i, 1);
					return true;
				}

				if (comments[i].children) {
					if (removeComment(comments[i].children)) {
						return true;
					}
				}
			}

			return false;
		};

		removeComment(comments);

		commentStore.set(comments);
	}

	const metadata = {
		'@context': 'https://schema.org/',
		'@type': 'BlogPosting',
		'@id': 'https://ooo-yay.com/blog/posts/' + parseDateAsYear(post.published) + '/' + post.slug,
		mainEntityOfPage:
			'https://ooo-yay.com/blog/posts/' + parseDateAsYear(post.published) + '/' + post.slug,
		headline: post.title,
		name: post.title,
		description:
			'When Schema.org arrived on the scene I thought we might have arrived at the point where library metadata  could finally blossom; adding value outside of library systems to help library curated resources become first class citizens, and hence results, in the global web we all inhabit.  But as yet it has not happened.',
		datePublished: post.published,
		dateModified: post.updatedAt,
		author: {
			'@type': 'Person',
			'@id': 'https://ooo-yay.com/about',
			name: 'Matt Ouille',
			url: 'https://ooo-yay.com/about'
		},
		publisher: {
			'@type': 'Organization',
			'@id': 'https://ooo-yay.com',
			name: 'ooo-yay'
		},
		url: 'https://ooo-yay.com/blog/posts/' + parseDateAsYear(post.published) + '/' + post.slug,
		isPartOf: {
			'@type': 'Blog',
			'@id': 'https://ooo-yay.com/blog/',
			name: 'ooo-yay Blog',
			publisher: {
				'@type': 'Organization',
				'@id': 'https://ooo-yay.com',
				name: 'ooo-yay'
			}
		},
		wordCount: post.content.split(' ').length,
		keywords: []
	};

	onMount(async () => {
		userDetails = await getUserDetails();
	});
</script>

<MetaTags
	title={post.title}
	titleTemplate="%s | Matt Ouille | ooo-yay.com"
	description={post.content
		.replaceAll(/(<([^>]+)>)/gi, '')
		.replace(/&ndash;/g, '')
		.slice(0, 200)}
	canonical="https://ooo-yay.com/"
	openGraph={{
		title: post.title,
		type: 'website',
		article: {
			publishedTime: iso8601String(post.published),
			modifiedTime: iso8601String(post.updatedAt),
			authors: ['Matt Ouille'],
			section: 'Blog'
		},
		images: [
			{
				url: 'https://ooo-yay.com/img/opengraph.png',
				width: 1200,
				height: 630,
				alt: 'ooo-yay.com opengraph image'
			}
		],
		url: 'https://ooo-yay.com/blog/posts/' + parseDateAsYear(post.published) + '/' + post.slug,
		description: post.content
			.replaceAll(/(<([^>]+)>)/gi, '')
			.replace(/&ndash;/g, '')
			.slice(0, 200),
		siteName: 'ooo-yay.com'
	}}
/>

<article class="markdown-body">
	<p><a href="/blog">Back to posts</a></p>

	{@html `<script type="application/ld+json">
        ${JSON.stringify(metadata)}
    </script>`}

	<h1 itemprop="headline" class="py-2 text-4xl font-semibold">{post.title}</h1>

	{#if post.published}
		<p class="text-sm text-gray-500">{formatDate(post.published)}</p>
	{:else}
		<Badge color="indigo">Draft</Badge>
	{/if}

	<div>
		<Markdown {carta} value={post.content} />
	</div>
</article>

<div>
	<!-- Do threaded comments with tailwind CSS -->
	<h2 class="mt-6 text-2xl font-semibold">Comments</h2>
	<div class="space-y-4">
		{#each $commentStore as comment (comment.id)}
			<Comment on:commentDeleted={removeCommentFromTree} {comment} user={userDetails} />
		{:else}
			<p>No comments yet</p>
		{/each}
		{#if userDetails !== undefined}
			<Button href="/comment/new/{post.id}">Reply</Button>
		{/if}
	</div>
</div>

<hr class="my-8" />
