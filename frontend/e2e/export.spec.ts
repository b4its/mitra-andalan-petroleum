import { test, expect, type Page } from '@playwright/test'

const AUTH = JSON.stringify({
  id: 'test', name: 'Rina', email: 'accounting@email.com', password: 'x',
  role: 'accounting', token: 'x', loggedInAt: new Date().toISOString()
})

async function loginAndGoto(page: Page, path: string) {
  await page.addInitScript((v) => localStorage.setItem('auth', v), AUTH)
  await page.goto(path, { waitUntil: 'networkidle' })
  await page.waitForLoadState('networkidle')
}

// Buka dropdown export; retry jika klik pertama terjadi sebelum Vue hydration
// (handler belum terpasang sehingga menu tidak terbuka).
async function openExportMenu(page: Page) {
  const excel = page.getByText('Export to Excel')
  for (let attempt = 0; attempt < 3; attempt++) {
    await page.getByRole('button', { name: 'Export' }).click()
    try {
      await expect(excel).toBeVisible({ timeout: 5000 })
      return
    } catch {
      await page.keyboard.press('Escape').catch(() => {})
    }
  }
  throw new Error('Menu export tidak terbuka')
}

test('export dropdown muncul di halaman jurnal-umum', async ({ page }) => {
  await loginAndGoto(page, '/accounting/jurnal-umum')
  await expect(page.getByRole('button', { name: 'Export' })).toBeVisible()
})

for (const [path, menu] of [
  ['/accounting/jurnal-umum', 'Jurnal Umum'],
  ['/accounting/pemasukan', 'Pemasukan'],
  ['/accounting/pengeluaran', 'Pengeluaran'],
  ['/accounting/akun', 'Chart of Accounts']
]) {
  test(`dropdown export 3 opsi di ${menu}`, async ({ page }) => {
    await loginAndGoto(page, path)
    await openExportMenu(page)
    await expect(page.getByText('Export to PDF')).toBeVisible()
    await expect(page.getByText('Export to CSV')).toBeVisible()
  })
}

test('dropdown export 3 opsi di Buku Besar (setelah pilih akun)', async ({ page }) => {
  await loginAndGoto(page, '/accounting/buku-besar')
  await page.locator('button').filter({ hasText: 'Pilih akun' }).first().click()
  await page.getByRole('option', { name: /Kas/ }).first().click()
  await page.getByRole('button', { name: 'Tampilkan' }).click()
  await openExportMenu(page)
  await expect(page.getByText('Export to PDF')).toBeVisible()
  await expect(page.getByText('Export to CSV')).toBeVisible()
})

for (const fmt of ['Excel', 'PDF', 'CSV'] as const) {
  test(`download .${fmt.toLowerCase()} dari jurnal-umum`, async ({ page }) => {
    await loginAndGoto(page, '/accounting/jurnal-umum')
    const downloadPromise = page.waitForEvent('download', { timeout: 15000 })
    await openExportMenu(page)
    await page.getByText(`Export to ${fmt}`).click()
    const download = await downloadPromise
    expect(download.suggestedFilename()).toContain('.')
    const ext = fmt === 'Excel' ? 'xlsx' : fmt === 'PDF' ? 'pdf' : 'csv'
    expect(download.suggestedFilename()).toContain(ext)
  })
}