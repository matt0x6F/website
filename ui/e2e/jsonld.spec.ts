import { test, expect, Page, Route } from '@playwright/test'

const postYear = 2025
const postSlug = 'test-post-jsonld'
const postTitle = 'JSON-LD Test Post'
const postContent = 'This is a test post for JSON-LD.'

// Mock API response for the blog post
const mockPostApi = async (page: Page) => {
  await page.route(`**/api/posts/slug/${postYear}/${postSlug}`, async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 100,
        title: postTitle,
        content: postContent,
        createdAt: '2025-05-18T02:53:01.410Z',
        updatedAt: '2025-05-28T03:55:08.889Z',
        publishedAt: '2025-05-28T03:55:08.889Z',
        author: { id: 1, username: 'matt', email: 'm@ooo-yay.com', is_staff: true },
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

test('Blog post page injects correct JSON-LD', async ({ page }) => {
  await mockPostApi(page)
  await page.goto(`/blog/${postYear}/${postSlug}`)
  // Wait for the headline to appear
  await expect(page.locator('h1')).toHaveText(postTitle)
  // Evaluate the JSON-LD in the head
  const jsonld = await page.evaluate(() => {
    const script = document.head.querySelector('script[type="application/ld+json"]')
    if (!script || !script.textContent) return null
    return JSON.parse(script.textContent)
  })
  expect(jsonld).not.toBeNull()
  expect(jsonld.headline).toBe(postTitle)
  expect(jsonld['@type']).toBe('BlogPosting')
  expect(jsonld.articleBody).toContain('This is a test post for JSON-LD')
}) 