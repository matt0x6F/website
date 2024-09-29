<script lang="ts">
	import { FileImageOutline, LockOutline, FileDocOutline, FileCirclePlusOutline, TrashBinOutline } from "flowbite-svelte-icons";
    import type { PageData } from "./$types";
	import { Accordion, AccordionItem, Listgroup, ListgroupItem, Table, PaginationItem } from "flowbite-svelte";
	import TableBody from "flowbite-svelte/TableBody.svelte";
	import TableBodyCell from "flowbite-svelte/TableBodyCell.svelte";
	import TableBodyRow from "flowbite-svelte/TableBodyRow.svelte";
	import TableHead from "flowbite-svelte/TableHead.svelte";
	import TableHeadCell from "flowbite-svelte/TableHeadCell.svelte";
	import { PUBLIC_BASE_URL } from "$env/static/public";
	import { Configuration, FilesApi } from "$lib/api";
	import { getAccessToken } from "../../../../stores/auth";
	import { addToast } from "../../../../stores/notifications";
	import { goto } from "$app/navigation";

    export let data: PageData

    let files = data.files;
    let count = data.count;
    let checked: string[] = [];
    let limit = data.limit;
    let offset = data.offset;

    // function that converts to bytes to KB, MB, GB, TB
    function formatBytes(bytes: number, decimals = 2) {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    function formatCharset(charset: string | null) {
        if (charset === null) return 'N/A';
        return charset;
    }

    async function getNextPage() {
        offset += limit;

        const token = await getAccessToken();
        const config = new Configuration({
            basePath: PUBLIC_BASE_URL,
            headers: {
                "Authorization": "Bearer " + token
            }
        });
    
        const api = new FilesApi(config);

        try {
            const response = await api.blogApiListFiles({ visibility: "all", limit, offset });
            files = response.items;
        } catch (error) {
            console.error(error);
        }
    }

    async function getPreviousPage() {
        offset -= limit;

        const token = await getAccessToken();
        const config = new Configuration({
            basePath: PUBLIC_BASE_URL,
            headers: {
                "Authorization": "Bearer " + token
            }
        });
    
        const api = new FilesApi(config);

        try {
            const response = await api.blogApiListFiles({ visibility: "all", limit, offset });
            files = response.items;
        } catch (error) {
            console.error(error);
        }
    }

    async function deleteFiles() {
        const token = await getAccessToken();
        const config = new Configuration({
            basePath: PUBLIC_BASE_URL,
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        let deleted = 0;

        const api = new FilesApi(config);

        for (const id of checked) {
            try {
                await api.blogApiDeleteFile({ id: +id });
                deleted++;
            } catch (error) {
                console.error(error);

                addToast({
                    message: "Error deleting file: " + error
                })
            }
        }

        checked = [];

        // refresh based on the current offset
        try {
            const response = (await api.blogApiListFiles({ visibility: "all", limit, offset }));
            files = response.items;
            count = response.count;
        } catch (e) {
            console.error(e);
        }

        addToast({
            message: "Deleted " + deleted + " files"
        })
    }
</script>

<div class="flex space-x-2">
    <!-- side toolbar -->
    <div>
        <Listgroup active let:item class="w-48" on:click={(e) => alert(Object.entries(e.detail))}>
            <ListgroupItem active current on:click={() => goto("/admin/files/upload")}>
                <FileCirclePlusOutline class="w-4 h-4 me-2" size="xl"/>
                Upload
            </ListgroupItem>
            <ListgroupItem on:click={() => deleteFiles()}>
                <TrashBinOutline class="w-4 h-4 me-2" size="xl"/>
                Delete 
                {#if checked.length > 0}
                    ({checked.length})
                {/if}
            </ListgroupItem>
        </Listgroup>
    </div>
    <!-- main accordion -->
    <Accordion class="flex-grow">
        {#each files as file}
            <AccordionItem>
                <!-- header -->
                <span slot="header" class="text-base flex gap-2">
                    <label class="text-sm rtl:text-right font-medium text-gray-900 dark:text-gray-300 flex items-center">
                        <input class="w-4 h-4 bg-gray-100 border-gray-300 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-600 dark:border-gray-500 rounded text-primary-600 focus:ring-primary-500 dark:focus:ring-primary-600" type="checkbox" value={file.id} bind:group={checked} />
                    </label>
                    {#if !file.contentType.startsWith('image')}
                        <FileImageOutline class="mt-0.5" />
                    {:else}
                        <FileDocOutline class="mt-0.5" />
                    {/if}
                    
                    <span>{file.name}</span>
                    
                    {#if file.visibility == "private"}
                        <LockOutline class="inline-block" size="lg"/>
                    {/if}
                </span>
                <!-- content -->
                <div class="mb-2 text-gray-500 dark:text-gray-400">
                    <div class="flex">
                        <div class="flex-grow max-h-96">
                            {#if file.contentType.startsWith('image')}
                                <img class="max-h-96 mx-auto" src={file.location} alt={file.name}/>
                            {:else}
                                <img class="max-h-96 mx-auto" src="/img/document.png" alt={file.name} />
                            {/if}
                        </div>

                        <Table noborder>
                            <TableHead>
                              <TableHeadCell>Property</TableHeadCell>
                              <TableHeadCell>Value</TableHeadCell>
                            </TableHead>
                            <TableBody tableBodyClass="divide-y">
                                <TableBodyRow>
                                    <TableBodyCell>ID</TableBodyCell>
                                    <TableBodyCell>{file.id}</TableBodyCell>
                                </TableBodyRow>
                                <TableBodyRow>
                                    <TableBodyCell>Created</TableBodyCell>
                                    <TableBodyCell>{file.createdAt}</TableBodyCell>
                                </TableBodyRow>
                                <TableBodyRow>
                                    <TableBodyCell>Name</TableBodyCell>
                                    <TableBodyCell><a href={file.location}>{file.name}</a></TableBodyCell>
                                </TableBodyRow>
                                <TableBodyRow>
                                    <TableBodyCell>Content Type</TableBodyCell>
                                    <TableBodyCell>{file.contentType}</TableBodyCell>
                                </TableBodyRow>
                                <TableBodyRow>
                                    <TableBodyCell>Size</TableBodyCell>
                                    <TableBodyCell>{formatBytes(file.size)}</TableBodyCell>
                                </TableBodyRow>
                                {#if file.charset}
                                    <TableBodyRow>
                                        <TableBodyCell>Charset</TableBodyCell>
                                        <TableBodyCell>{formatCharset(file.charset)}</TableBodyCell>
                                    </TableBodyRow>
                                {/if}
                            </TableBody>
                          </Table>
                    </div>
                </div>
            </AccordionItem>
        {:else}
            <div class="text-center">
                No files found
            </div>
        {/each}
        <div class="flex space-x-3 rtl:space-x-reverse w-fit max-w-fit mx-auto mt-4">
            {#if offset - limit >= 0}
                <PaginationItem large on:click={() => getPreviousPage()}>Previous</PaginationItem>
            {/if}
            {#if offset + limit < count}
                <PaginationItem large on:click={() => getNextPage()}>Next</PaginationItem>
            {/if}
        </div>
    </Accordion>
</div>
