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

test.describe('Admin Database Konfigurasi', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/database', { waitUntil: 'networkidle' })
  })

  test('halaman render kartu export, import, dan bersihkan database', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Database Konfigurasi' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Export Data SQL' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Import Data SQL' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Bersihkan Database' })).toBeVisible()
  })

  test('export SQL memerlukan konfirmasi dan mengunduh file .sql', async ({ page }) => {
    const downloadPromise = page.waitForEvent('download', { timeout: 15000 })
    await page.getByRole('button', { name: 'Export SQL' }).click()
    await expect(
      page.getByRole('dialog').getByText('Export data SQL?'),
    ).toBeVisible()
    await page.getByRole('dialog').getByRole('button', { name: 'Ya, Export SQL' }).click()
    const download = await downloadPromise
    expect(download.suggestedFilename()).toMatch(/\.sql$/)
    await expect(page.getByText('File SQL berhasil diunduh.')).toBeVisible()
  })

  test('tombol Import tetap disabled sampai file dipilih dan konfirmasi diketik', async ({ page }) => {
    const importButton = page.getByRole('button', { name: 'Import SQL' })
    await expect(importButton).toBeDisabled()
    await page.locator('input[type="file"]').setInputFiles({
      name: 'test.sql',
      mimeType: 'application/sql',
      buffer: Buffer.from('SELECT 1;'),
    })
    await expect(importButton).toBeDisabled()
    await page.getByPlaceholder('Ketik IMPORT SQL').fill('IMPORT SQL')
    await expect(importButton).toBeEnabled()
  })

  test('import SQL jalan setelah konfirmasi modal', async ({ page }) => {
    await page.locator('input[type="file"]').setInputFiles({
      name: 'test.sql',
      mimeType: 'application/sql',
      buffer: Buffer.from('SELECT 1;'),
    })
    await page.getByPlaceholder('Ketik IMPORT SQL').fill('IMPORT SQL')
    await page.getByRole('button', { name: 'Import SQL' }).click()
    await expect(
      page.getByRole('dialog').getByText('Import data SQL?'),
    ).toBeVisible()
    await page.getByRole('dialog').getByRole('button', { name: 'Ya, Import SQL' }).click()
    await expect(page.getByText('Import selesai', { exact: true })).toBeVisible()
  })

  test('tombol bersihkan database hanya aktif setelah konfirmasi diketik', async ({ page }) => {
    const clearButton = page.getByRole('button', { name: 'Bersihkan Database' })
    await expect(clearButton).toBeDisabled()
    await page.getByPlaceholder('Ketik BERSIHKAN DATABASE').fill('BERSIHKAN DATABASE')
    await expect(clearButton).toBeEnabled()
  })
})