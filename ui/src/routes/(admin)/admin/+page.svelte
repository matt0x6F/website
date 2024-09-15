<script lang="ts">

	import { Button, ButtonGroup, Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from "flowbite-svelte";
	import type { PageData } from "./$types";
	import { EyeSolid, TrashBinSolid } from "flowbite-svelte-icons";
	import { PUBLIC_BASE_URL } from "$env/static/public";
	import { Configuration, PostsApi } from "$lib/api";
	import { getAccessToken } from "../../../stores/auth";
	import DeleteButton from "$lib/components/DeleteButton.svelte";
	import { addToast } from "../../../stores/notifications";

    export let data: PageData

    let draftPosts = data.draftPosts
    let publishedPosts = data.publishedPosts

    function formatDate(date: Date | null | undefined): string {
        if (!date) {
            return "";
        }
        
        const daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
        const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

        const dayOfWeek = daysOfWeek[date.getDay()];
        const month = months[date.getMonth()];
        const day = date.getDate();
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');

        // Function to get the correct ordinal suffix
        function getOrdinalSuffix(day: number): string {
            if (day > 3 && day < 21) return 'th'; // Handles 11th, 12th, 13th
            switch (day % 10) {
                case 1: return 'st';
                case 2: return 'nd';
                case 3: return 'rd';
                default: return 'th';
            }
        }

        const dayWithSuffix = day + getOrdinalSuffix(day);

        return `${dayOfWeek}, ${month} the ${dayWithSuffix}, ${year} @ ${hours}:${minutes}`;
    }

    function formatPostYear(date: Date | null | undefined): string {
        if (!date) {
            return new Date().getFullYear().toString();
        }

        return date.getFullYear().toString();
    }

    async function removeDraft(event: CustomEvent<{postID: number}>) {
        // search through draftPosts and delete the post with the matching ID
        draftPosts = draftPosts.filter(post => post.id !== event.detail.postID);

        addToast({
                message: "Deleted draft post"
            })
    }
</script>

<p class="py-4">Welcome to the admin interface.</p>

<p class="py-4"><a href="/admin/write">Write something new</a></p>

<div class="flex flex-row space-x-4 w-full">
    <div class="flex-grow">
        <h2 class="text-lg font-bold">Posts</h2>
        <Table hoverable>
            <TableHead>
            <TableHeadCell>Title</TableHeadCell>
            <TableHeadCell>Author</TableHeadCell>
            <TableHeadCell>Published</TableHeadCell>
            <TableHeadCell></TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#each publishedPosts as post }
                <TableBodyRow>
                    <TableBodyCell><a href="/admin/write/{post.id}">{post.title}</a></TableBodyCell>
                    <TableBodyCell>{post.authorId}</TableBodyCell>
                    <TableBodyCell>{formatDate(post.published)}</TableBodyCell>
                    <TableBodyCell class="text-right">
                        <ButtonGroup class="*:!ring-primary-700">
                            <Button size="xs" href="/blog/posts/{formatPostYear(post.published)}/{post.slug}">
                                <EyeSolid class="inline-block" ariaLabel="Preview this post" />
                                Preview
                            </Button>
                          </ButtonGroup>    
                    </TableBodyCell>
                </TableBodyRow>
                {:else}
                <TableBodyRow>
                    <TableBodyCell>No published posts</TableBodyCell>
                    <TableBodyCell></TableBodyCell>
                    <TableBodyCell></TableBodyCell>
                    <TableBodyCell></TableBodyCell>
                </TableBodyRow>
                {/each}
            </TableBody>
        </Table>
    </div>
    <div class="flex-grow">
        <h2 class="text-lg font-bold">Drafts</h2>
        <Table hoverable>
            <TableHead>
            <TableHeadCell>Title</TableHeadCell>
            <TableHeadCell>Author</TableHeadCell>
            <TableHeadCell></TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#each draftPosts as post }
                <TableBodyRow>
                    <TableBodyCell><a href="/admin/write/{post.id}">{post.title}</a></TableBodyCell>
                    <TableBodyCell>{post.authorId}</TableBodyCell>
                    <TableBodyCell class="text-right">
                        <ButtonGroup class="*:!ring-primary-700">
                            <Button size="xs" href="/blog/drafts/{formatPostYear(post.published)}/{post.id}">
                                <EyeSolid class="inline-block" ariaLabel="Preview this post" />
                                Preview
                            </Button>
                            <DeleteButton postID={post.id} on:postDeleted={removeDraft} />
                          </ButtonGroup>
                    </TableBodyCell>
                </TableBodyRow>
                {:else}
                <TableBodyRow>
                    <TableBodyCell>No drafts</TableBodyCell>
                    <TableBodyCell></TableBodyCell>
                    <TableBodyCell></TableBodyCell>
                </TableBodyRow>
                {/each}
            </TableBody>
        </Table>
    </div>
</div>