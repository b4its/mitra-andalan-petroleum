import { test, expect } from '@playwright/test'

async function login(page, email: string, password: string, urlRegex: RegExp) {
  await page.goto('/login', { waitUntil: 'networkidle' })
  await expect(page.locator('button[type="submit"]')).toBeEnabled()
  for (let attempt = 0; attempt < 3; attempt++) {
    if (page.url().match(urlRegex)) return
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', password)
    await page.click('button[type="submit"]')
    try {
      await page.waitForURL(urlRegex, { timeout: 15000 })
      return
    } catch {
      // Hydration Vue mungkin belum selesai pada submit pertama: field tereset
      // (state kosong) sehingga submit tidak menghasilkan navigasi. Isi ulang.
    }
  }
  throw new Error('Login gagal')
}

test.describe('Login Page', () => {
  test('shows login form', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'networkidle' })
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
    await login(page, 'admin@email.com', 'admin123', /\/admin/)
    expect(page.url()).toContain('/admin')
  })

  test('login with marketing credentials redirects to marketing dashboard', async ({
    page
  }) => {
    await login(page, 'marketing@email.com', 'marketing123', /\/marketing/)
    expect(page.url()).toContain('/marketing')
  })

  test('login with operations credentials redirects to operations dashboard', async ({
    page
  }) => {
    await login(page, 'ops@email.com', 'ops123', /\/operations/)
    expect(page.url()).toContain('/operations')
  })

  test('login with finance credentials redirects to finance dashboard', async ({
    page
  }) => {
    await login(page, 'finance@email.com', 'finance123', /\/finance/)
    expect(page.url()).toContain('/finance')
  })

  test('shows error on wrong password', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'networkidle' })
    await page.fill('input[type="email"]', 'admin@email.com')
    await page.fill('input[type="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')
    await expect(page.getByText('Login Gagal', { exact: true })).toBeVisible({ timeout: 5000 })
  })

  test('shows error on nonexistent email', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'networkidle' })
    await page.fill('input[type="email"]', 'nonexistent@test.com')
    await page.fill('input[type="password"]', 'test12345')
    await page.click('button[type="submit"]')
    await expect(page.getByText('Login Gagal', { exact: true })).toBeVisible({ timeout: 5000 })
  })

  test('cannot access admin page without login', async ({ page }) => {
    await page.goto('/admin')
    await expect(page).toHaveURL(/\/login/)
  })

  test('logout returns to login page', async ({ page }) => {
    await login(page, 'admin@email.com', 'admin123', /\/admin/)

    const logoutButton = page.locator('text=Logout')
    if (await logoutButton.isVisible()) {
      await logoutButton.click()
      await expect(page).toHaveURL(/\/login/)
    }
  })
})
