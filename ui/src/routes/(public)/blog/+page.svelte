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
</script>

<h1 class="text-4xl font-semibold py-6">Blog</h1>

{#each posts as post}
    <article class="markdown-body">
        <h1 class="text-4xl font-semibold py-2">{post.title}</h1>
        <!-- Format published date as "Friday, July 10th @ 23:00 2024" -->
        <p class="text-gray-500 text-sm">{formatDate(post.published)}</p>
        <Markdown {carta} value={post.content} />
    </article>
{/each}