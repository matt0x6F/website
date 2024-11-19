<script lang="ts">
	import '@cartamd/plugin-code/default.css';
	import '@cartamd/plugin-emoji/default.css';
	import '@cartamd/plugin-slash/default.css';
	import '@cartamd/plugin-anchor/default.css';
	import 'carta-md/default.css'; /* Default theme */

	import { PUBLIC_BASE_URL } from '$env/static/public';
	import {
		Configuration,
		PostsApi,
		ResponseError,
		ValidationErrorResponseFromJSONTyped,
		type BlogApiUpdatePostRequest,
		type FileDetails,
		type PostMutate
	} from '$lib/api';
	import { Carta, MarkdownEditor } from 'carta-md';
	import { code } from '@cartamd/plugin-code';
	import { emoji } from '@cartamd/plugin-emoji';
	import { slash } from '@cartamd/plugin-slash';
	import { anchor } from '@cartamd/plugin-anchor';
	import { Input, Label, Tabs, TabItem, Button, ButtonGroup } from 'flowbite-svelte';
	import DOMPurify from 'isomorphic-dompurify';
	import { addToast } from '../../stores/notifications';
	import { retrieveAccessToken } from '../../stores/auth';
	import { ArrowsRepeatOutline } from 'flowbite-svelte-icons';
	import { attachment } from '@cartamd/plugin-attachment';
	import { goto } from '$app/navigation';
	import { parseUTCDateTimeToLocal } from '$lib/utils';

	export let id = -1; // -1 means new post
	export let title = '';
	export let slug = '';
	export let published_at = '';
	export let content = '';

	if (published_at !== '') {
		published_at = parseUTCDateTimeToLocal(published_at);
	}

	const slugify = (title: string): string => {
		return title
			.toLowerCase()
			.replace(/ /g, '-')
			.replace(/[^a-z0-9-]/g, '');
	};

	const generateSlugFromTitle = () => {
		slug = slugify(title);
	};

	const uploadFile = async (file: File): Promise<string | null> => {
		if (id === -1) {
			addToast({
				message: 'Please save the post before uploading files'
			});

			return null;
		}

		let token = undefined;
		try {
			token = await retrieveAccessToken();
		} catch (error) {
			goto('/login');
		}

		const formData = new FormData();
		formData.append('upload', file);

		const metadata = {
			posts: [id],
			visibility: 'public'
		};

		formData.append('metadata', JSON.stringify(metadata));
		try {
			const response = await fetch(PUBLIC_BASE_URL + '/api/files/', {
				method: 'POST',
				headers: {
					Authorization: 'Bearer ' + token
				},
				body: formData
			});

			const fileMetadata: FileDetails = await response.json();

			if (response.ok) {
				addToast({
					message: 'Uploaded ' + fileMetadata.name + ' successfully'
				});
			} else {
				addToast({
					message: 'Failed to upload file: ' + response.statusText
				});
			}

			return fileMetadata.location;
		} catch (error) {
			console.error(error);

			addToast({
				message: 'Failed to upload file: ' + error
			});

			return null;
		}
	};

	const savePost = async () => {
		let token = undefined;
		try {
			token = await retrieveAccessToken();
		} catch (error) {
			goto('/login');
		}

		const config = new Configuration({
			basePath: PUBLIC_BASE_URL,
			headers: { Authorization: `Bearer ${token}` }
		});
		const api = new PostsApi(config);

		if (id === -1) {
			// Create new post
			console.log('Creating new post');
			try {
				let details: PostMutate = {
					title: title,
					slug: slug,
					content: content
				};

				if (published_at !== '') {
					details.published = new Date(published_at);
				}

				const post = await api.blogApiCreatePost({
					postMutate: details
				});

				console.log('Created post with id: ' + post.id);

				id = post.id;

				addToast({
					message: 'Created post!'
				});
			} catch (error) {
				if (error instanceof ResponseError) {
					console.error('Error saving post: ', error.cause, error.message);

					const json = await error.response.json();
					const body = ValidationErrorResponseFromJSONTyped(json, false);

					addToast({
						message: 'Error saving post: ' + body.detail
					});
				} else {
					console.error('Error saving post: ', error);
				}
			}
		} else {
			console.log('Updating post with id: ' + id);
			try {
				let details: BlogApiUpdatePostRequest = {
					id: id,
					postMutate: {
						title: title,
						slug: slug,
						content: content
					}
				};

				if (published_at !== '') {
					details.postMutate.published = new Date(published_at);
				}

				await api.blogApiUpdatePost(details);

				console.log('Updated post with id: ' + id);

				addToast({
					message: 'Saved post!'
				});
			} catch (error) {
				if (error instanceof ResponseError) {
					console.error('Error saving post: ', error.cause, error.message);

					const json = await error.response.json();
					const body = ValidationErrorResponseFromJSONTyped(json, false);

					addToast({
						message: 'Error saving post: ' + body.detail
					});
				}
			}
		}
	};

	const carta = new Carta({
		sanitizer: DOMPurify.sanitize,
		extensions: [
			code(),
			emoji(),
			slash(),
			anchor(),
			attachment({
				upload: uploadFile
			})
		]
	});
</script>

<p class="py-4"><a href="/admin">Back to admin dashboard</a></p>

<h1 class="text-2xl font-semibold">New post</h1>

<Tabs class="mt-4">
	<TabItem open title="Content">
		<div class="mb-6">
			<Label for="title" class="mb-2 block">Title</Label>
			<Input id="title" size="lg" placeholder="Title" bind:value={title} />
		</div>

		<MarkdownEditor {carta} bind:value={content} />
	</TabItem>
	<TabItem title="Metadata">
		<div class="flex flex-row space-x-4">
			<div class="mb-6 max-w-screen-sm flex-grow">
				<Label for="slug" class="mb-2 block">Slug</Label>
				<ButtonGroup class="w-full">
					<Input id="slug" size="lg" placeholder="Slug" bind:value={slug} />
					<Button on:click={() => generateSlugFromTitle()}><ArrowsRepeatOutline /> Generate</Button>
				</ButtonGroup>
			</div>
			<div class="mb-6">
				<Label for="published_at" class="mb-2 block">Publish</Label>
				<Input id="published_at" size="lg" type="datetime-local" bind:value={published_at} />
			</div>
		</div>
	</TabItem>
</Tabs>

<Button pill class="mt-6" on:click={() => savePost()}>Save</Button>

<style>
	/* Set your monospace font (Required to have the editor working correctly!) */
	:global(.carta-font-code) {
		font-family: 'Source Code Pro', monospace;
		font-size: 1.1rem;
		line-height: 1.5rem;
	}
</style>
