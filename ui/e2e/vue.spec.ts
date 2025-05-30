import { test, expect } from '@playwright/test';

// See here how to get started:
// https://playwright.dev/docs/intro
test('visits the app root url', async ({ page }) => {
  // Mock POST /api/token/refresh
  await page.route('**/api/token/refresh', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        refresh: 'mock-refresh-token',
        access: 'mock-access-token'
      })
    });
  });

  // Mock GET /api/accounts/me
  await page.route('**/api/accounts/me', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 1,
        username: 'matt',
        email: 'm@ooo-yay.com',
        first_name: '',
        last_name: '',
        is_staff: true,
        is_active: true,
        date_joined: '2025-05-18T00:34:52.125Z',
        avatar_link: null
      })
    });
  });

  await page.goto('/');
  await expect(page.locator('h1')).toHaveText("Hello! I'm Matt");
})

test.describe('Blog post sharecode access', () => {
  const draftYear = 2025;
  const draftSlug = 'this-is-a-test-post';
  const validSharecode = 'MHMip6m7DZKn3fmF';
  const invalidSharecode = 'INVALIDCODE123';
  const publishedYear = 2025;
  const publishedSlug = 'published-post';

  test('Draft post with valid sharecode is accessible', async ({ page }) => {
    // Mock API for draft post with valid sharecode
    await page.route(
      `**/api/posts/slug/${draftYear}/${draftSlug}?sharecode=${validSharecode}`,
      async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 5,
            title: 'This is a test post',
            content: 'Test content',
            createdAt: '2025-05-18T02:53:01.410Z',
            updatedAt: '2025-05-28T03:55:08.889Z',
            publishedAt: null,
            author: { id: 1, username: 'matt', email: 'm@ooo-yay.com', is_staff: true },
            slug: draftSlug,
            series: null,
          })
        });
      }
    );
    await page.route('**/api/comments/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], count: 0 })
      });
    });
    await page.goto(`http://localhost:3000/blog/${draftYear}/${draftSlug}?sharecode=${validSharecode}`);
    await expect(page.locator('h1')).toHaveText('This is a test post');
    await expect(page.locator('article')).toContainText('Test content');
  });

  test('Draft post with invalid sharecode shows error/404', async ({ page }) => {
    // Mock API for draft post with invalid sharecode (404)
    await page.route(
      `**/api/posts/slug/${draftYear}/${draftSlug}?sharecode=${invalidSharecode}`,
      async route => {
        await route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Post not found' })
        });
      }
    );
    await page.goto(`http://localhost:3000/blog/${draftYear}/${draftSlug}?sharecode=${invalidSharecode}`);
    await expect(page.locator('body')).toContainText(/Failed to load blog post|not found|error|404/i);
  });

  test('Published post is accessible with sharecode', async ({ page }) => {
    // Mock API for published post (sharecode ignored)
    await page.route(
      `**/api/posts/slug/${publishedYear}/${publishedSlug}?sharecode=${validSharecode}`,
      async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 6,
            title: 'Published Post',
            content: 'Published content',
            createdAt: '2025-05-18T02:53:01.410Z',
            updatedAt: '2025-05-28T03:55:08.889Z',
            publishedAt: '2025-05-28T03:55:08.889Z',
            author: { id: 1, username: 'matt', email: 'm@ooo-yay.com', is_staff: true },
            slug: publishedSlug,
            series: null,
          })
        });
      }
    );
    await page.route('**/api/comments/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], count: 0 })
      });
    });
    await page.goto(`http://localhost:3000/blog/${publishedYear}/${publishedSlug}?sharecode=${validSharecode}`);
    await expect(page.locator('h1')).toHaveText('Published Post');
    await expect(page.locator('article')).toContainText('Published content');
  });

  test('Published post is accessible without sharecode', async ({ page }) => {
    // Mock API for published post (no sharecode)
    await page.route(
      `**/api/posts/slug/${publishedYear}/${publishedSlug}`,
      async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 6,
            title: 'Published Post',
            content: 'Published content',
            createdAt: '2025-05-18T02:53:01.410Z',
            updatedAt: '2025-05-28T03:55:08.889Z',
            publishedAt: '2025-05-28T03:55:08.889Z',
            author: { id: 1, username: 'matt', email: 'm@ooo-yay.com', is_staff: true },
            slug: publishedSlug,
            series: null,
          })
        });
      }
    );
    await page.route('**/api/comments/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], count: 0 })
      });
    });
    await page.goto(`http://localhost:3000/blog/${publishedYear}/${publishedSlug}`);
    await expect(page.locator('h1')).toHaveText('Published Post');
    await expect(page.locator('article')).toContainText('Published content');
  });
});

test('Home page sets correct document title', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle('ooo-yay.com – Home');
});

test('About page sets correct document title', async ({ page }) => {
  await page.goto('/about');
  await expect(page).toHaveTitle('About – ooo-yay.com');
});

test('Blog list page sets correct document title', async ({ page }) => {
  await page.goto('/blog');
  await expect(page).toHaveTitle('Blog – ooo-yay.com');
});

test('404 page sets correct document title', async ({ page }) => {
  await page.goto('/this-page-does-not-exist');
  await expect(page).toHaveTitle('404 – Page Not Found – ooo-yay.com');
});

test('Blog post page sets correct document title', async ({ page }) => {
  // Mock API for blog post
  await page.route('**/api/posts/slug/2025/test-post', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 42,
        title: 'Test Post',
        content: 'Test content',
        createdAt: '2025-05-18T02:53:01.410Z',
        updatedAt: '2025-05-28T03:55:08.889Z',
        publishedAt: '2025-05-28T03:55:08.889Z',
        author: { id: 1, username: 'matt', email: 'm@ooo-yay.com', is_staff: true },
        slug: 'test-post',
        series: null,
      })
    });
  });
  await page.route('**/api/comments/**', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ items: [], count: 0 })
    });
  });
  await page.goto('/blog/2025/test-post');
  await expect(page).toHaveTitle('Test Post – Blog – ooo-yay.com');
});
