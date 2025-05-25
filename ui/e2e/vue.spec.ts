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
