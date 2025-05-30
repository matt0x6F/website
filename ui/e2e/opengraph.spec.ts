import { test, expect, Page, Route } from '@playwright/test'

const postYear = 2025
const postSlug = 'test-post-og'
const postTitle = 'OpenGraph Test Post'
const postContent = 'This is a test post for OpenGraph.'

// Mock API response for the blog post
const mockPostApi = async (page: Page) => {
  await page.route(`**/api/posts/slug/${postYear}/${postSlug}`, async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 101,
        title: postTitle,
        content: postContent,
        created_at: '2025-05-18T02:53:01.410Z',
        updated_at: '2025-05-28T03:55:08.889Z',
        published_at: '2025-05-28T03:55:08.889Z',
        authorId: 1,
        slug: postSlug,
        series: null,
      })
    })
  })
  await page.route('**/api/comments/**', async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ items: [], count: 0 })
    })
  })
}

test('Blog post page injects correct OpenGraph and Twitter meta tags', async ({ page }) => {
  await mockPostApi(page)
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
  expect(ogUrl).toContain(`/blog/${postYear}/${postSlug}`)
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
}) 