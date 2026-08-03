import { test, expect } from '@playwright/test'

const AUTH = JSON.stringify({
  id: 'test', name: 'Rina', email: 'accounting@email.com', password: 'x',
  role: 'accounting', token: 'x', loggedInAt: new Date().toISOString()
})

async function loginAndGoto(page, path) {
  await page.addInitScript((v) => localStorage.setItem('auth', v), AUTH)
  await page.goto(path)
  await page.waitForLoadState('networkidle')
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
    await page.getByRole('button', { name: 'Export' }).click()
    await expect(page.getByText('Export to Excel')).toBeVisible()
    await expect(page.getByText('Export to PDF')).toBeVisible()
    await expect(page.getByText('Export to CSV')).toBeVisible()
  })
}

test('dropdown export 3 opsi di Buku Besar (setelah pilih akun)', async ({ page }) => {
  await loginAndGoto(page, '/accounting/buku-besar')
  await page.locator('button').filter({ hasText: 'Pilih akun' }).first().click()
  await page.getByRole('option', { name: /Kas/ }).first().click()
  await page.getByRole('button', { name: 'Tampilkan' }).click()
  await page.getByRole('button', { name: 'Export' }).click()
  await expect(page.getByText('Export to Excel')).toBeVisible()
  await expect(page.getByText('Export to PDF')).toBeVisible()
  await expect(page.getByText('Export to CSV')).toBeVisible()
})

for (const fmt of ['Excel', 'PDF', 'CSV'] as const) {
  test(`download .${fmt.toLowerCase()} dari jurnal-umum`, async ({ page }) => {
    await loginAndGoto(page, '/accounting/jurnal-umum')
    const downloadPromise = page.waitForEvent('download', { timeout: 15000 })
    await page.getByRole('button', { name: 'Export' }).click()
    await page.getByText(`Export to ${fmt}`).click()
    const download = await downloadPromise
    expect(download.suggestedFilename()).toContain('.')
    const ext = fmt === 'Excel' ? 'xlsx' : fmt === 'PDF' ? 'pdf' : 'csv'
    expect(download.suggestedFilename()).toContain(ext)
  })
}