import { test, expect, type Page } from '@playwright/test'

async function loginAs(page: Page, role: string) {
  const credentials: Record<string, { email: string, password: string }> = {
    admin: { email: 'admin@email.com', password: 'admin123' },
    marketing: { email: 'marketing@email.com', password: 'marketing123' },
    operations: { email: 'ops@email.com', password: 'ops123' },
    finance: { email: 'finance@email.com', password: 'finance123' },
    accounting: { email: 'accounting@email.com', password: 'accounting123' }
  }
  const cred = credentials[role]
  await page.goto('/login', { waitUntil: 'networkidle' })
  await expect(page.locator('button[type="submit"]')).toBeEnabled()
  const expected = new RegExp(`/${role}`)
  for (let attempt = 0; attempt < 3; attempt++) {
    if (page.url().match(expected)) return
    await page.fill('input[type="email"]', cred.email)
    await page.fill('input[type="password"]', cred.password)
    await page.click('button[type="submit"]')
    try {
      await page.waitForURL(expected, { timeout: 15000 })
      return
    } catch {
      // Hydration Vue mungkin belum selesai pada submit pertama: field tereset
      // (state kosong) sehingga submit tidak menghasilkan navigasi. Isi ulang.
    }
  }
  throw new Error(`Login gagal untuk role ${role}`)
}

test.describe('Accounting pages', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'accounting')
  })

  test('dashboard renders summary cards and quick menu', async ({ page }) => {
    await page.goto('/accounting', { waitUntil: 'networkidle' })
    await expect(page.locator('h1').filter({ hasText: 'Akuntansi' })).toBeVisible()
    await expect(page.locator('text=Total Pemasukan').first()).toBeVisible()
    await expect(page.locator('text=Menu Cepat').first()).toBeVisible()
  })

  test('chart of accounts renders table with seeded accounts', async ({ page }) => {
    await page.goto('/accounting/akun', { waitUntil: 'networkidle' })
    await expect(page.locator('h1').filter({ hasText: 'Chart of Accounts' })).toBeVisible()
    await expect(page.locator('table').first()).toBeVisible()
    await expect(page.locator('text=Kas Besar').first()).toBeVisible()
  })

  test('create a new account via modal', async ({ page }) => {
    await page.goto('/accounting/akun', { waitUntil: 'networkidle' })
    await page.click('text=Tambah Akun')
    const code = `9-${Date.now().toString().slice(-6)}`
    await page.fill('input[placeholder*="Contoh: 1100"]', code)
    await page.fill('input[placeholder*="Contoh: Kas"]', 'Akun E2E Test')
    await page.locator('[role=dialog] [role=combobox]').click()
    await page.locator('[role=option]').filter({ hasText: 'Aset' }).click()
    await page.click('button:has-text("Simpan")')
    await expect(page.locator('text=Akun berhasil dibuat').first()).toBeVisible()
    await expect(page.locator(`text=${code}`).first()).toBeVisible()
  })

  test('journal page renders and creates balanced journal', async ({ page }) => {
    await page.goto('/accounting/jurnal-umum', { waitUntil: 'networkidle' })
    await expect(page.locator('h1').filter({ hasText: 'Jurnal Umum' })).toBeVisible()

    await page.click('text=Buat Jurnal')
    await page.fill('input[placeholder="Deskripsi jurnal..."]', 'Jurnal E2E Test')
    await expect(page.locator('text=Tidak Balance').first()).toBeVisible()

    const dialog = page.locator('[role=dialog]')
    const comboboxes = dialog.locator('[role=combobox]')

    // line 1: pick an account, fill debit
    await comboboxes.nth(0).click()
    await page.locator('[role=option]').nth(1).click()
    await dialog.locator('input[placeholder="Debit"]').nth(0).fill('100000')

    // line 2: pick another account, fill credit
    await comboboxes.nth(1).click()
    await page.locator('[role=option]').nth(2).click()
    await dialog.locator('input[placeholder="Kredit"]').nth(1).fill('100000')

    await expect(page.locator('text=Balance').first()).toBeVisible()
    await page.click('button:has-text("Simpan Jurnal")')
    await expect(page.locator('text=Jurnal berhasil dibuat').first()).toBeVisible()
  })

  test('ledger page loads after selecting account', async ({ page }) => {
    await page.goto('/accounting/buku-besar', { waitUntil: 'networkidle' })
    await expect(page.locator('h1').filter({ hasText: 'Buku Besar' })).toBeVisible()
    await expect(page.locator('text=Pilih Akun').first()).toBeVisible()
  })

  test('income & expenses pages render', async ({ page }) => {
    await page.goto('/accounting/pemasukan', { waitUntil: 'networkidle' })
    await expect(page.locator('h1').filter({ hasText: 'Pemasukan' })).toBeVisible()

    await page.goto('/accounting/pengeluaran', { waitUntil: 'networkidle' })
    await expect(page.locator('h1').filter({ hasText: 'Pengeluaran' })).toBeVisible()
  })

  test('daily cash, balance sheet, and cost recap pages render', async ({ page }) => {
    for (const [path, title] of [
      ['/accounting/kas-harian', 'Kas Harian'],
      ['/accounting/neraca', 'Neraca'],
      ['/accounting/rekap-cashflow', 'Rekap Arus Kas'],
      ['/accounting/rekap-biaya', 'Rekap Biaya'],
      ['/accounting/rekap-bunga-bank', 'Rekap Bunga Bank'],
      ['/accounting/rekap-monitoring', 'Rekap Monitoring']
    ]) {
      await page.goto(path, { waitUntil: 'networkidle' })
      await expect(
        page.locator('p').filter({ hasText: title }).first(),
      ).toBeVisible()
    }
  })

  test('notification page renders and marks all as read', async ({ page }) => {
    await page.goto('/accounting/notifikasi', { waitUntil: 'networkidle' })
    await expect(page.locator('p').filter({ hasText: 'Notifikasi' }).first()).toBeVisible()
    const markAll = page.getByRole('button', { name: /Tandai semua|tandai semua/i }).first()
    // Tombol hanya aktif bila ada notifikasi belum dibaca — skip bila tidak
    if (await markAll.count() && await markAll.isEnabled()) {
      await markAll.click()
      await expect(page.getByText('Semua notifikasi ditandai dibaca').first()).toBeVisible()
    }
  })

  test('no console errors on accounting pages', async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', err => errors.push(err.message))
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text())
    })
    for (const path of [
      '/accounting',
      '/accounting/jurnal-umum',
      '/accounting/buku-besar',
      '/accounting/pemasukan',
      '/accounting/pengeluaran',
      '/accounting/akun',
      '/accounting/kas-harian',
      '/accounting/neraca',
      '/accounting/rekap-cashflow',
      '/accounting/rekap-biaya',
      '/accounting/rekap-bunga-bank',
      '/accounting/rekap-monitoring',
      '/accounting/notifikasi'
    ]) {
      // Beberapa halaman rekap bisa menahan networkidle (request berulang),
      // jadi tunggu 'load' saja lalu beri waktu hydration berjalan.
      await page.goto(path, { waitUntil: 'load' })
      await page.waitForTimeout(500)
    }
    const filtered = errors.filter(
      e =>
        !e.includes('favicon') &&
        !e.includes('favicon.ico') &&
        !e.includes('Hydration completed but contains mismatches')
    )
    expect(filtered).toHaveLength(0)
  })
})
