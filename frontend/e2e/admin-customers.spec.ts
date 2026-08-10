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

test.describe('Admin Customers — NPWP', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
  })

  test('halaman customer menampilkan kolom NPWP', async ({ page }) => {
    await page.goto('/admin/customers', { waitUntil: 'networkidle' })
    await expect(page.getByText('Manajemen Customer')).toBeVisible()
    await expect(page.getByRole('columnheader', { name: 'NPWP' })).toBeVisible()
  })

  test('error menambah customer dengan format NPWP salah', async ({ page }) => {
    await page.goto('/admin/customers', { waitUntil: 'networkidle' })
    await page.getByRole('button', { name: 'Tambah Customer' }).click()
    await expect(page.getByText('Tambah Customer Baru')).toBeVisible()
    await page.getByPlaceholder('Nama customer').fill('Test NPWP Invalid')
    await page.getByPlaceholder('00.000.000.0-000.000').fill('12345')
    await page.getByRole('button', { name: 'Tambah Customer', exact: true }).click()
    await expect(page.getByText('Format NPWP salah', { exact: true })).toBeVisible()
  })

  test('tambah customer dengan NPWP valid berhasil', async ({ page }) => {
    const name = `Test NPWP ${Date.now()}`
    await page.goto('/admin/customers', { waitUntil: 'networkidle' })
    await page.getByRole('button', { name: 'Tambah Customer' }).click()
    await expect(page.getByText('Tambah Customer Baru')).toBeVisible()
    await page.getByPlaceholder('Nama customer').fill(name)
    await page.getByPlaceholder('00.000.000.0-000.000').fill('12.345.678.0-123.456')
    await page.getByPlaceholder('email@contoh.com').fill('test-npwp@example.com')
    await page.getByRole('button', { name: 'Tambah Customer', exact: true }).click()
    await expect(page.getByText('Customer baru berhasil ditambahkan.', { exact: true })).toBeVisible()
    await expect(page.getByText(name)).toBeVisible()
  })
})
