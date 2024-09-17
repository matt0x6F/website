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
	import DeleteButton from '$lib/components/DeleteButton.svelte';


    export let data

    let post = data.post

    const carta = new Carta({
        sanitizer: DOMPurify.sanitize,
        extensions: [
            code(),
            emoji(),
            slash(),
            anchor()
        ]
	});

    function iso8601String(date: Date | null | undefined): string {
        if (!date) {
            return "";
        }
        
        return date.toISOString();
    }

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

    function parseDateAsYear(date: Date | null | undefined): string {
        if (!date) {
            return "";
        }
        
        return date.getFullYear().toString();
    }

    const metadata = {
        "@context": "https://schema.org/",
        "@type": "BlogPosting",
        "@id": "https://ooo-yay.com/blog/posts/" + parseDateAsYear(post.published) + "/" + post.slug,
        "mainEntityOfPage": "https://ooo-yay.com/blog/posts/" + parseDateAsYear(post.published) + "/" + post.slug,
        "headline": post.title,
        "name": post.title,
        "description": "When Schema.org arrived on the scene I thought we might have arrived at the point where library metadata  could finally blossom; adding value outside of library systems to help library curated resources become first class citizens, and hence results, in the global web we all inhabit.  But as yet it has not happened.",
        "datePublished": post.published,
        "dateModified": post.updatedAt,
        "author": {
            "@type": "Person",
            "@id": "https://ooo-yay.com/about",
            "name": "Matt Ouille",
            "url": "https://ooo-yay.com/about",
        },
        "publisher": {
            "@type": "Organization",
            "@id": "https://ooo-yay.com",
            "name": "ooo-yay",
        },
        "url": "https://ooo-yay.com/blog/posts/" + parseDateAsYear(post.published) + "/" + post.slug,
        "isPartOf": {
            "@type" : "Blog",
            "@id": "https://ooo-yay.com/blog/",
            "name": "ooo-yay Blog",
            "publisher": {
                "@type": "Organization",
                "@id": "https://ooo-yay.com",
                "name": "ooo-yay"
            }
        },
        "wordCount": post.content.split(" ").length,
        "keywords": [],
    }
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
        type: "website",
        article: {
            publishedTime: iso8601String(post.published),
            modifiedTime: iso8601String(post.updatedAt),
            authors: ["Matt Ouille"],
            section: "Blog",
        },
        images: [
            {
                url: "https://ooo-yay.com/img/opengraph.png",
                width: 1200,
                height: 630,
                alt: "ooo-yay.com opengraph image"
            }
        ],
        url: "https://ooo-yay.com/blog/posts/{parseDateAsYear(post.published)}/{post.slug}",
        description: post.content
            .replaceAll(/(<([^>]+)>)/gi, '')
            .replace(/&ndash;/g, '')
            .slice(0, 200),
        siteName:"ooo-yay.com"
    }}
/>

<article class="markdown-body">
    <p><a href="/blog">Back to posts</a></p>

    {@html `<script type="application/ld+json">
        ${JSON.stringify(metadata)}
    </script>`}

    <h1 itemprop="headline" class="text-4xl font-semibold py-2">{post.title}</h1>
    
    {#if post.published}
    <p class="text-gray-500 text-sm">{formatDate(post.published)}</p>
    {:else}
    <Badge color="indigo">Draft</Badge>
    {/if}
    
    <div>
        <Markdown {carta} value={post.content} />
    </div>
</article>

<hr class="my-8" />