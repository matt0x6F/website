import { test, expect } from '@playwright/test'
import { mockServer } from './mockServer.js'
import { URL } from 'url'

const postYear = 2025
const postSlug = 'test-post-jsonld'
const postTitle = 'JSON-LD Test Post'
const postContent = 'This is a test post for JSON-LD.'

test.beforeAll(async () => {
  await mockServer.start(4100);
  // Register the post mock
  const path = `/api/posts/slug/${postYear}/${postSlug}`;
  await mockServer.forGet(path)
    .asPriority(1)
    .thenCallback(req => {
      return {
        status: 200,
        json: {
          id: 102,
          title: postTitle,
          content: postContent,
          created_at: '2025-05-18T02:53:01.410Z',
          updated_at: '2025-05-28T03:55:08.889Z',
          published_at: '2025-05-28T03:55:08.889Z',
          author: { id: 1, username: 'matt', email: 'm@ooo-yay.com', is_staff: true },
          slug: postSlug,
          series: null,
        }
      }
    });
  // Register comments mock
  await mockServer.forGet(/\/api\/comments\/.*/).thenJson(200, { items: [], count: 0 });
});

test.afterAll(async () => {
  await mockServer.stop()
})

test('Blog post page injects correct JSON-LD', async ({ page }) => {
  await page.goto(`/blog/${postYear}/${postSlug}`)
  await expect(page.locator('h1')).toHaveText(postTitle)
  const jsonld = await page.evaluate(() => {
    // @ts-expect-error: 'document' is available in browser context
    const script = document.head.querySelector('script[type="application/ld+json"]')
    if (!script || !script.textContent) return null
    return JSON.parse(script.textContent)
  })
  expect(jsonld).not.toBeNull()
  expect(jsonld.headline).toBe(postTitle)
  expect(jsonld['@type']).toBe('BlogPosting')
  expect(jsonld.articleBody).toContain('This is a test post for JSON-LD')
}) 