import { test, expect } from '@playwright/test'
import { mockServer } from './mockServer.js'
import { URL } from 'url'

const postYear = 2025
const postSlug = 'test-post-og'
const postTitle = 'OpenGraph Test Post'
const postContent = 'This is a test post for OpenGraph.'

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
          id: 101,
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

test('Blog post page injects correct OpenGraph and Twitter meta tags', async ({ page }) => {
  await page.goto(`/blog/${postYear}/${postSlug}`)
  // Wait for the headline to appear
  await expect(page.locator('h1')).toHaveText(postTitle)
  // Evaluate OpenGraph meta tags
  const ogTitle = await page.locator('meta[property="og:title"]').getAttribute('content')
  expect(ogTitle).toBe(postTitle)
  const ogType = await page.locator('meta[property="og:type"]').getAttribute('content')
  expect(ogType).toBe('article')
  const ogDescription = await page.locator('meta[property="og:description"]').getAttribute('content')
  expect(ogDescription).toContain('This is a test post for OpenGraph')
  const ogUrl = await page.locator('meta[property="og:url"]').getAttribute('content')
  const currentUrl = page.url()
  expect(ogUrl).toBe(currentUrl)
  const ogImage = await page.locator('meta[property="og:image"]').getAttribute('content')
  expect(ogImage).toContain('ooo-yay.com/og-default.png')
  const published = await page.locator('meta[property="article:published_time"]').getAttribute('content')
  expect(published).toContain('2025-05-28T03:55:08.889Z')
  // Twitter tags
  const twitterTitle = await page.locator('meta[name="twitter:title"]').getAttribute('content')
  expect(twitterTitle).toBe(postTitle)
  const twitterDescription = await page.locator('meta[name="twitter:description"]').getAttribute('content')
  expect(twitterDescription).toContain('This is a test post for OpenGraph')
  const twitterImage = await page.locator('meta[name="twitter:image"]').getAttribute('content')
  expect(twitterImage).toContain('ooo-yay.com/og-default.png')

  // Debug: print all meta tags
  const metaHtml = await page.evaluate(() => {
    // @ts-expect-error: document is available in browser context
    return Array.from(document.head.querySelectorAll('meta')).map(m => (m as Element).outerHTML);
  });
  console.log('Meta tags:', metaHtml);

  // Debug: print Nuxt post data if available
  const postData = await page.evaluate(() => {
    // @ts-expect-error
    return window.__NUXT__ ? window.__NUXT__.data : null;
  });
  console.log('Nuxt postData:', postData);
}) 