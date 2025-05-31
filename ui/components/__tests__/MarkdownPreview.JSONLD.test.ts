import { describe, it, expect, afterEach } from 'vitest';
import { render, waitFor } from '@testing-library/vue'
import MarkdownPreview from '../MarkdownPreview.vue'
import { nextTick } from 'vue'
import { createHead } from '@vueuse/head'
import type { PostDetails } from '@/lib/api/models/PostDetails'

afterEach(() => {
  document.head.querySelectorAll('meta[property^="og:"],meta[property^="article:"],meta[name^="twitter:"]').forEach(el => el.remove())
  document.head.querySelectorAll('script[type="application/ld+json"]').forEach(el => el.remove())
})

describe('MarkdownPreview.vue OpenGraph & Twitter', () => {
  const baseMeta: PostDetails = {
    id: 1,
    title: 'Test OG Post',
    content: '# Hello **OpenGraph**',
    createdAt: new Date('2024-01-01T00:00:00Z'),
    updatedAt: new Date('2024-01-02T00:00:00Z'),
    published: new Date('2024-01-01T12:00:00Z'),
    authorId: 42,
    slug: 'test-og-post',
    series: null
  }

  it('injects OpenGraph and Twitter meta tags when meta prop is provided', async () => {
    const head = createHead()
    render(MarkdownPreview, {
      props: {
        content: baseMeta.content,
        meta: baseMeta
      },
      global: { plugins: [head] }
    })
    await waitFor(() => {
      // Check og:title
      expect(document.head.querySelector('meta[property="og:title"][content="Test OG Post"]')).toBeTruthy()
      // Check og:type
      expect(document.head.querySelector('meta[property="og:type"][content="article"]')).toBeTruthy()
      // Check og:description
      expect(document.head.querySelector('meta[property="og:description"]')).toBeTruthy()
      // Check og:url
      expect(document.head.querySelector('meta[property="og:url"]')).toBeTruthy()
      // Check og:image
      expect(document.head.querySelector('meta[property="og:image"]')).toBeTruthy()
      // Check article:published_time
      expect(document.head.querySelector('meta[property="article:published_time"]')).toBeTruthy()
      // Check twitter:title
      expect(document.head.querySelector('meta[name="twitter:title"][content="Test OG Post"]')).toBeTruthy()
      // Check twitter:description
      expect(document.head.querySelector('meta[name="twitter:description"]')).toBeTruthy()
      // Check twitter:image
      expect(document.head.querySelector('meta[name="twitter:image"]')).toBeTruthy()
    })
  })

  it('does not inject OpenGraph or Twitter meta tags when meta prop is not provided', async () => {
    const head = createHead()
    render(MarkdownPreview, {
      props: {
        content: '# No meta here'
      },
      global: { plugins: [head] }
    })
    await nextTick()
    expect(document.head.querySelector('meta[property^="og:"]')).toBeFalsy()
    expect(document.head.querySelector('meta[property^="article:"]')).toBeFalsy()
    expect(document.head.querySelector('meta[name^="twitter:"]')).toBeFalsy()
  })
}) 