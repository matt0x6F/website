<script lang="ts">
	import '@cartamd/plugin-code/default.css';
    import '@cartamd/plugin-emoji/default.css';
    import '@cartamd/plugin-slash/default.css';
    import '@cartamd/plugin-anchor/default.css';
    
    import { PUBLIC_BASE_URL } from '$env/static/public';
	import { Configuration, PostsApi, ResponseError, ValidationErrorResponseFromJSONTyped } from '$lib/api';
	import { Carta, MarkdownEditor } from 'carta-md';
    import { code } from '@cartamd/plugin-code';
    import { emoji } from '@cartamd/plugin-emoji';
    import { slash } from '@cartamd/plugin-slash';
    import { anchor } from '@cartamd/plugin-anchor';
	import 'carta-md/default.css'; /* Default theme */
	import { Input, Label, Tabs, TabItem, Button, ButtonGroup } from 'flowbite-svelte';
    import DOMPurify from 'isomorphic-dompurify';
	import { addToast } from '../../stores/notifications';
	import { getAccessToken } from '../../stores/auth';
	import { ArrowsRepeatOutline } from 'flowbite-svelte-icons';
	

	const carta = new Carta({
        sanitizer: DOMPurify.sanitize,
        extensions: [
            code(),
            emoji(),
            slash(),
            anchor()
        ]
	});

    export let id = -1; // -1 means new post
    export let title = "";
    export let slug = "";
    export let published_at = '';
    export let content = '';

    // function for converting datetime-local ("2024-08-21T12:00") to a Date object
    const parseDate = (dateString: string) => {
        if (!dateString) {
            return null
        }

        const [date, time] = dateString.split('T');
        const [year, month, day] = date.split('-');
        const [hours, minutes] = time.split(':');

        return new Date(parseInt(year), parseInt(month) - 1, parseInt(day), parseInt(hours), parseInt(minutes));
    }

    const slugify = (title: string): string => {
        return title.toLowerCase().replace(/ /g, '-').replace(/[^a-z0-9-]/g, '');
    }

    const generateSlugFromTitle = () => {
        slug = slugify(title)
    }

    const savePost = async () => {
        let token = await getAccessToken()

        const config = new Configuration({ basePath: PUBLIC_BASE_URL, headers: { Authorization: `Bearer ${token}` } });
        const api = new PostsApi(config);

        if (id === -1) {
            try {
                const post = await api.blogApiCreatePost({
                    postMutate: {
                        title: title,
                        slug: slug,
                        published: parseDate(published_at),
                        content: content
                    }
                })

                id = post.id;

                addToast({
                    message: "Created post!"
                })
            } catch (error) {
                if (error instanceof ResponseError) {
                    console.error('Error saving post: ', error.cause, error.message);

                    const json = await error.response.json();
                    const body = ValidationErrorResponseFromJSONTyped(json, false)
                
                    addToast({
                        message: "Error saving post: " + body.detail
                    })
                }
            }
        } else {
            try {
                await api.blogApiUpdatePost({
                    id: id,
                    postMutate: {
                        title: title,
                        slug: slug,
                        published: parseDate(published_at),
                        content: content
                    }
                })

                addToast({
                    message: "Saved post!"
                })
            } catch (error) {
                if (error instanceof ResponseError) {
                    console.error('Error saving post: ', error.cause, error.message);

                    const json = await error.response.json();
                    const body = ValidationErrorResponseFromJSONTyped(json, false)
                
                    addToast({
                        message: "Error saving post: " + body.detail
                    })
                }
            }
        }
    }
</script>

<p class="py-4"><a href="/admin">Back to admin dashboard</a></p>

<h1 class="text-2xl font-semibold">New post</h1>

<Tabs class="mt-4">
    <TabItem open title="Content">
        <div class="mb-6">
            <Label for="title" class="block mb-2">Title</Label>
            <Input id="title" size="lg" placeholder="Title" bind:value={title} />
        </div>

        <MarkdownEditor {carta} bind:value={content} />
    </TabItem>
    <TabItem title="Metadata">
        <div class="flex flex-row space-x-4">
            <div class="mb-6 flex-grow max-w-screen-sm">
                <Label for="slug" class="block mb-2">Slug</Label>
                <ButtonGroup class="w-full">
                    <Input id="slug" size="lg" placeholder="Slug" bind:value={slug} />
                    <Button on:click={() => generateSlugFromTitle()}><ArrowsRepeatOutline /> Generate</Button>
                </ButtonGroup>
            </div>
            <div class="mb-6">
                <Label for="published_at" class="block mb-2">Publish</Label>
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