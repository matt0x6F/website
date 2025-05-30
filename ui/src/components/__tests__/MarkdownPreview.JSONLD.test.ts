import { describe, it, expect, afterEach } from 'vitest';
import { render, waitFor } from '@testing-library/vue'
import MarkdownPreview from '../MarkdownPreview.vue'
import { nextTick } from 'vue'
import { createHead } from '@vueuse/head'

afterEach(() => {
  document.head.querySelectorAll('script[type="application/ld+json"]').forEach(el => el.remove())
})

describe('MarkdownPreview.vue JSON-LD', () => {
  it('injects JSON-LD script when jsonLd prop is provided', async () => {
    const jsonLd = {
      '@context': 'https://schema.org',
      '@type': 'BlogPosting',
      headline: 'Test Post',
      articleBody: '<p>Hello <strong>world</strong></p>'
    }
    const head = createHead()
    render(MarkdownPreview, {
      props: {
        content: '# Hello **world**',
        jsonLd
      },
      global: { plugins: [head] }
    })
    await waitFor(() => {
      const scripts = Array.from(document.head.querySelectorAll('script[type="application/ld+json"]'))
      const found = scripts.some(script => {
        try {
          const data = JSON.parse(script.textContent || '')
          return data.headline === jsonLd.headline && data['@type'] === jsonLd['@type']
        } catch {
          return false
        }
      })
      expect(found).toBe(true)
    })
  })

  it('does not inject JSON-LD script when jsonLd prop is not provided', async () => {
    const head = createHead()
    render(MarkdownPreview, {
      props: {
        content: '# Hello **world**'
      },
      global: { plugins: [head] }
    })
    await nextTick()
    const scripts = Array.from(document.head.querySelectorAll('script[type="application/ld+json"]'))
    // Should not find a script with our test headline
    const found = scripts.some(script => {
      try {
        const data = JSON.parse(script.textContent || '')
        return data.headline === 'Test Post'
      } catch {
        return false
      }
    })
    expect(found).toBe(false)
  })
}) 