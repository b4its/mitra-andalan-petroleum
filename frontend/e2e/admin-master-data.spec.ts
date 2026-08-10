import { test, expect, type Page } from '@playwright/test'

async function loginAsAdmin(page: Page) {
  await page.goto('/login', { waitUntil: 'networkidle' })
  await expect(page.locator('button[type="submit"]')).toBeEnabled()
  const expected = /\/admin/
  for (let attempt = 0; attempt < 3; attempt++) {
    if (page.url().match(expected)) return
    await page.fill('input[type="email"]', 'admin@email.com')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    try {
      await page.waitForURL(expected, { timeout: 15000 })
      return
    } catch {
      // Hydration Vue mungkin belum selesai pada submit pertama: field tereset
      // (state kosong) sehingga submit tidak menghasilkan navigasi. Isi ulang.
    }
  }
  throw new Error('Login gagal sebagai admin')
}

test.describe('Admin Master Data', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
  })

  test('users page renders table of seeded users', async ({ page }) => {
    await page.goto('/admin/users', { waitUntil: 'networkidle' })
    await expect(page.getByText('Manajemen Pengguna')).toBeVisible()
    await expect(page.locator('table').first()).toBeVisible()
    await expect(page.getByText('admin@email.com').first()).toBeVisible()
    await expect(page.getByText('accounting@email.com').first()).toBeVisible()
  })

  test('suppliers page renders seeded suppliers', async ({ page }) => {
    await page.goto('/admin/suppliers', { waitUntil: 'networkidle' })
    await expect(page.getByText('Manajemen Supplier')).toBeVisible()
    await expect(page.locator('table').first()).toBeVisible()
  })

  test('data delivery order page renders', async ({ page }) => {
    await page.goto('/admin/data-do', { waitUntil: 'networkidle' })
    await expect(page.getByText('Data Delivery Order').first()).toBeVisible()
    await expect(page.locator('table').first()).toBeVisible()
  })
})
