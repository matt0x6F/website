<script lang="ts">
	import { Dropzone, MultiSelect, Label, Button, Checkbox } from "flowbite-svelte";
    import type { PageData } from "./$types";
    import type { SelectOptionType } from "flowbite-svelte";
	import { onMount } from "svelte";
	import { getAccessToken } from "../../../../../stores/auth";
	import { PUBLIC_BASE_URL } from "$env/static/public";
	import { goto } from "$app/navigation";
	import { addToast } from "../../../../../stores/notifications";


    export let data: PageData

    // populate the posts variable where each item is an object with the keys value and name where value is the id and name is the title
    let posts: SelectOptionType<any>[] = [];

    onMount(async () => {
        for (const post of data.posts) {
            posts.push({
                value: post.id,
                name: post.title
            })
        }

        posts = posts;
    });

    let visbility: string = "public";
    let selected: string[] = [];
    let value: string[] = [];
    let files: File[] = [];
    const dropHandle = (event: DragEvent) => {
        value = [];
        event.preventDefault();

        if (event.dataTransfer === null) return;

        if (event.dataTransfer.items) {
            [...event.dataTransfer.items].forEach((item, i) => {
                if (item.kind === 'file') {
                    const file = item.getAsFile();

                    if (file === null) return;

                    files.push(file);
                    files = files;

                    value.push(file.name);
                    value = value;
                }
            });
        } else {
            [...event.dataTransfer.files].forEach((file, i) => {
                value.push(file.name);
                value = value;

                files.push(file);
                files = files;
            });
        }
    };

    const handleChange = (event: Event) => {
        const target = event.target as HTMLInputElement;

        if (target.files === null) return;

        

        if (target.files.length > 0) {
            value.push(target.files[0].name);
            value = value;

            files.push(target.files[0]);
            files = files;
        }
    };

    const showFiles = (values: string[]) => {
        if (values.length === 1) return values[0];

        let i = 0;

        let concat = '';
        values.map((file) => {
            if (i === values.length - 1) {
                concat += file;
                return;
            }

            concat += file;
            concat += ',';
            concat += ' ';
            i++;
        });

        if (concat.length > 256) concat = concat.slice(0, 256) + "...";

        return concat;
    };

    const uploadFiles = async () => {
        const token = await getAccessToken();

        let succeeded = 0;
        let failed = 0;

        for (const file of files) {
            const formData = new FormData();
            formData.append("upload", files[0]);

            const metadata = {
                posts: selected.map((id) => {
                    return +id;
                }),
                visibility: visbility
            };

            formData.append("metadata", JSON.stringify(metadata));
            try {
                const response = await fetch(PUBLIC_BASE_URL + "/api/files/", {
                    method: "POST",
                    headers: {
                        "Authorization": "Bearer " + token
                    },
                    body: formData
                });

                if (response.ok) {
                    succeeded++;
                } else {
                    failed++;

                    addToast({
                        message: "Failed to upload file: " + response.statusText
                    })
                }
            } catch (error) {
                console.error(error);

                addToast({
                    message: "Failed to upload file: " + error
                })
            }
        }

        addToast({
            message: "Uploaded " + succeeded + " files successfully"
        });

        goto("/admin/files");
    };
</script>

<form class="space-y-2" on:submit|preventDefault={() => {uploadFiles()}}>
    <Label for="postSelect" class="mb-2 text-sm text-gray-500 dark:text-gray-400">Select post(s)</Label>
    <MultiSelect id="postSelect" items={posts} bind:value={selected} placeholder="Select a post or posts" />

    <Label for="visibility" class="mb-2 text-sm text-gray-500 dark:text-gray-400">Visibility</Label>
    <Checkbox id="visibility" checked={visbility==="public"} on:change={() => { visbility === "public" ? visbility = "private" : visbility = "public"}}>Public</Checkbox>

    <Label for="dropzone" class="mb-2 text-sm text-gray-500 dark:text-gray-400">Upload file</Label>
    <Dropzone
    id="dropzone"
    on:drop={dropHandle}
    on:dragover={(event) => {
        event.preventDefault();
    }}
    on:change={handleChange}>
    <svg aria-hidden="true" class="mb-3 w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
    {#if value.length === 0}
        <p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> or drag and drop</p>
        <p class="text-xs text-gray-500 dark:text-gray-400">Any image or file type</p>
    {:else}
        <p>{showFiles(value)}</p>
    {/if}
    </Dropzone>
    <Button type="submit" class="mt-4">Upload</Button>
</form>