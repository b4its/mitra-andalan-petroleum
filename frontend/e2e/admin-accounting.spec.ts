import { test, expect, type Page } from '@playwright/test'

const AUTH = JSON.stringify({
  id: 'test', name: 'Admin', email: 'admin@email.com', password: 'x',
  role: 'admin', token: 'x', loggedInAt: new Date().toISOString()
})

async function loginAndGoto(page: Page, path: string) {
  await page.addInitScript((v) => localStorage.setItem('auth', v), AUTH)
  await page.goto(path)
  await page.waitForLoadState('networkidle')
}

test.describe('Admin Accounting page', () => {
  test('rekap page renders stat cards and charts', async ({ page }) => {
    await loginAndGoto(page, '/admin/accounting')
    await expect(page.getByText('Accounting — Rekap')).toBeVisible()
    await expect(page.getByText('Total Pemasukan')).toBeVisible()
    await expect(page.getByText('Total Pengeluaran')).toBeVisible()
    await expect(page.getByText('Laba Bersih')).toBeVisible()
    await expect(page.getByText('Saldo Kas & Bank')).toBeVisible()
    await expect(page.getByText('Pemasukan vs Pengeluaran')).toBeVisible()
    await expect(page.getByText('Distribusi Akun per Tipe')).toBeVisible()
  })

  test('journal and trial balance tables render with data', async ({ page }) => {
    await loginAndGoto(page, '/admin/accounting')
    await expect(page.getByText('Data Jurnal Umum')).toBeVisible()
    await expect(page.getByText('Neraca Saldo')).toBeVisible()
    await expect(page.getByText('Total Debit')).toBeVisible()
    await expect(page.getByText('Total Kredit')).toBeVisible()
  })

  test('journal search filters table', async ({ page }) => {
    await loginAndGoto(page, '/admin/accounting')
    const search = page.getByPlaceholder('Cari nomor, deskripsi, akun...')
    await search.fill('tidak ada jurnal seperti ini xyz')
    await page.waitForTimeout(300)
    await expect(page.getByText('Tidak ada jurnal')).toBeVisible()
  })

  test('export dropdown available on both tables', async ({ page }) => {
    await loginAndGoto(page, '/admin/accounting')
    const exports = page.getByRole('button', { name: 'Export' })
    await expect(exports).toHaveCount(2)
    await exports.first().click()
    await expect(page.getByText('Export to Excel')).toBeVisible()
    await expect(page.getByText('Export to PDF')).toBeVisible()
    await expect(page.getByText('Export to CSV')).toBeVisible()
  })

  test('download .xlsx dari rekap jurnal', async ({ page }) => {
    await loginAndGoto(page, '/admin/accounting')
    const downloadPromise = page.waitForEvent('download', { timeout: 15000 })
    await page.getByRole('button', { name: 'Export' }).first().click()
    await page.getByText('Export to Excel').click()
    const download = await downloadPromise
    expect(download.suggestedFilename()).toContain('.xlsx')
  })
})
