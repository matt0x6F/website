<template>
  <BlogPostView :post="mappedPost" :loading="pending" :error="error" />
  <div v-if="error" style="color: red; font-weight: bold;">
    SSR error: {{ error }}
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useAsyncData } from '#app'
import { useHead } from '@vueuse/head'
import { computed } from 'vue'
import BlogPostView from '~/views/BlogPostView.vue'
import { useApiClient } from '@/composables/useApiClient'
import { PostsApi } from '@/lib/api'

const route = useRoute()
const postsApi = useApiClient(PostsApi)
console.log('API basePath:', import.meta.env.VITE_API_URL)

const { data: post, pending, error } = await useAsyncData('post', async () => {
  try {
    return await postsApi.getPostBySlugAndYear({
      slug: route.params.slug as string,
      year: Number(route.params.year)
    })
  } catch (e: any) {
    // Log everything we can
    console.error('SSR API error:', e)
    if (e && typeof e === 'object') {
      for (const key in e) {
        console.error(`SSR API error property [${key}]:`, e[key])
      }
    }
    if (e?.response) {
      console.error('SSR API error response:', e.response)
    }
    if (e?.message) {
      console.error('SSR API error message:', e.message)
    }
    try {
      console.error('SSR API error (JSON):', JSON.stringify(e, null, 2))
    } catch {}
    if (e.status === 404) {
      return null
    }
    throw e
  }
})

const mappedPost = computed(() => {
  if (!post.value) return null
  return {
    ...post.value,
    authorId: post.value.author?.id ?? 0,
    // add any other required PostDetails fields here if needed
  }
})

if (post.value) {
  const description = post.value.content
    ? post.value.content.replace(/[#_*>\-\n]/g, '').slice(0, 160)
    : ''
  const publishedIso = post.value.publishedAt
    ? new Date(post.value.publishedAt).toISOString()
    : undefined
  const image = 'https://ooo-yay.com/og-default.png'
  useHead({
    title: `${post.value.title} – Blog – ooo-yay.com`,
    meta: [
      { property: 'og:title', content: post.value.title },
      { property: 'og:description', content: description },
      { property: 'og:type', content: 'article' },
      { property: 'og:url', content: typeof window !== 'undefined' ? window.location.href : '' },
      { property: 'og:site_name', content: 'ooo-yay.com' },
      { property: 'og:image', content: image },
      ...(publishedIso ? [{ property: 'article:published_time', content: publishedIso }] : []),
      { name: 'twitter:card', content: 'summary_large_image' },
      { name: 'twitter:title', content: post.value.title },
      { name: 'twitter:description', content: description },
      { name: 'twitter:image', content: image }
    ],
    script: [
      {
        type: 'application/ld+json',
        children: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "BlogPosting",
          "headline": post.value.title,
          "datePublished": post.value.publishedAt,
          "dateModified": post.value.updatedAt,
          "author": {
            "@type": "Person",
            "name": "Matt Ouille",
            "url": "https://ooo-yay.com",
            "image": "https://ooo-yay.com/avatar_resized.png",
            "description": "Distributed Systems Software and Systems Engineer in the PNW"
          },
          "articleBody": post.value.content,
          "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": typeof window !== 'undefined' ? window.location.href : ''
          },
          "publisher": {
            "@type": "Organization",
            "name": "ooo-yay.com",
            "logo": {
              "@type": "ImageObject",
              "url": "https://ooo-yay.com/logo.svg"
            }
          }
        })
      }
    ]
  })
}
</script> 