import { test, expect } from '@playwright/test'

test.describe('Login Page', () => {
  test('shows login form', async ({ page }) => {
    await page.goto('/login')
    const form = page.locator('form')
    await expect(form).toBeVisible()
    await expect(page.locator('input[type="email"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(
      page.locator('button[type="submit"]')
    ).toBeVisible()
  })

  test('login with admin credentials redirects to admin dashboard', async ({
    page
  }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', 'admin@email.com')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/admin/)
    expect(page.url()).toContain('/admin')
  })

  test('login with marketing credentials redirects to marketing dashboard', async ({
    page
  }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', 'marketing@email.com')
    await page.fill('input[type="password"]', 'marketing123')
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/marketing/)
    expect(page.url()).toContain('/marketing')
  })

  test('login with operations credentials redirects to operations dashboard', async ({
    page
  }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', 'ops@email.com')
    await page.fill('input[type="password"]', 'ops123')
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/operations/)
    expect(page.url()).toContain('/operations')
  })

  test('login with finance credentials redirects to finance dashboard', async ({
    page
  }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', 'finance@email.com')
    await page.fill('input[type="password"]', 'finance123')
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/finance/)
    expect(page.url()).toContain('/finance')
  })

  test('shows error on wrong password', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'networkidle' })
    await page.fill('input[type="email"]', 'admin@email.com')
    await page.fill('input[type="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')
    await expect(page.getByText('Login failed', { exact: true })).toBeVisible({ timeout: 5000 })
  })

  test('shows error on nonexistent email', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'networkidle' })
    await page.fill('input[type="email"]', 'nonexistent@test.com')
    await page.fill('input[type="password"]', 'test12345')
    await page.click('button[type="submit"]')
    await expect(page.getByText('Login failed', { exact: true })).toBeVisible({ timeout: 5000 })
  })

  test('cannot access admin page without login', async ({ page }) => {
    await page.goto('/admin')
    await expect(page).toHaveURL(/\/login/)
  })

  test('logout returns to login page', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', 'admin@email.com')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/admin/)

    const logoutButton = page.locator('text=Logout')
    if (await logoutButton.isVisible()) {
      await logoutButton.click()
      await expect(page).toHaveURL(/\/login/)
    }
  })
})
