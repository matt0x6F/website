<script lang="ts">
	import { formatBytes } from "$lib/utils";
	import type { PageData } from "./$types";

    export let data: PageData

    let file = data.file
</script>

<h1>{file.name}</h1>

<p>Size: {file.size}</p>

<p>Uploaded at: {file.createdAt}</p>

<p>Visibility: {file.visibility}</p>

<p>Content type: {file.contentType}</p>

<p>Charset: {file.charset}</p>

<p>Size: {formatBytes(file.size)}</p>

<p>Visibility: {file.visibility}</p>

<p>Download link: <a href = {file.location}>{file.location}</a></p>