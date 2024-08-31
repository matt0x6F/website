<script lang="ts">

	import { Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from "flowbite-svelte";
	import type { PageData } from "./$types";

    export let data: PageData

</script>
<p class="py-4">Welcome to the admin interface.</p>

<p class="py-4"><a href="/admin/write">Write something new</a></p>

<Table>
    <TableHead>
      <TableHeadCell>Title</TableHeadCell>
      <TableHeadCell>Author</TableHeadCell>
    </TableHead>
    <TableBody tableBodyClass="divide-y">
        {#each data.posts as post }
        <TableBodyRow>
            <TableBodyCell><a href="/admin/write/{post.id}">{post.title}</a></TableBodyCell>
            <TableBodyCell>{post.authorId}</TableBodyCell>
        </TableBodyRow>
        {/each}
    </TableBody>
  </Table>