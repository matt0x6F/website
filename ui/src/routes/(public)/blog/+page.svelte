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
	

    export let data

    let posts = data.posts

    const carta = new Carta({
        sanitizer: DOMPurify.sanitize,
        extensions: [
            code(),
            emoji(),
            slash(),
            anchor()
        ]
	});
</script>

<h1 class="text-4xl font-semibold py-6">Blog</h1>

{#each posts as post}
    <article class="markdown-body">
        <h1 class="text-4xl font-semibold py-2">{post.title}</h1>
        <Markdown {carta} value={post.content} />
    </article>
{/each}