import { test, expect, type Page } from '@playwright/test'

async function loginAs(page: Page, role: string) {
  const credentials: Record<string, { email: string, password: string }> = {
    admin: { email: 'admin@email.com', password: 'admin123' },
    marketing: { email: 'marketing@email.com', password: 'marketing123' },
    operations: { email: 'ops@email.com', password: 'ops123' },
    finance: { email: 'finance@email.com', password: 'finance123' }
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

test.describe('Admin Dashboard', () => {
  test.setTimeout(60000)

  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'admin')
  })

  test('dashboard renders stat cards', async ({ page }) => {
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })

  test('sidebar navigation is visible', async ({ page }) => {
    const sidebar = page.locator('aside, [data-reka-navigation-menu]').first()
    await expect(sidebar).toBeVisible()
  })

  test('can navigate to finance subpage', async ({ page }) => {
    await page.goto('/admin/finance')
    await expect(page).toHaveURL(/\/admin\/finance/)
  })

  test('can navigate to operations subpage', async ({ page }) => {
    await page.goto('/admin/operations')
    await expect(page).toHaveURL(/\/admin\/operations/)
  })

  test('can navigate to marketing subpage', async ({ page }) => {
    await page.goto('/admin/marketing')
    await expect(page).toHaveURL(/\/admin\/marketing/)
  })

  test('overview shows system metrics and opens the details modal', async ({ page }) => {
    await expect(page.getByText('Monitoring Keseluruhan Sistem')).toBeVisible()
    await expect(page.getByText('Surat Penawaran').first()).toBeVisible()
    await page.getByText('Surat Penawaran').first().click()
    // Modal detail metrik terbuka
    await expect(page.getByRole('dialog')).toBeVisible()
    await expect(page.getByRole('dialog').getByText('Surat Penawaran').first()).toBeVisible()
  })

  test('overview applies a one-week date preset', async ({ page }) => {
    await expect(page.getByText('Monitoring Keseluruhan Sistem')).toBeVisible()
    // Buka popover date range dan pilih preset 7 hari terakhir
    await page.getByRole('button', { name: /\d{1,2} \w{3} \d{4} - \d{1,2} \w{3} \d{4}/ }).click()
    await page.getByRole('button', { name: '7 hari terakhir' }).click()
    await expect(page.getByText('Monitoring Keseluruhan Sistem')).toBeVisible()
  })
})

test.describe('Marketing Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'marketing')
  })

  test('dashboard loads without errors', async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', err => errors.push(err.message))
    await page.goto('/marketing', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
    expect(errors).toHaveLength(0)
  })

  test('customer page loads', async ({ page }) => {
    await page.goto('/marketing/customer', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })

  test('supplier page loads', async ({ page }) => {
    await page.goto('/marketing/supplier', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })

  test('harga page loads', async ({ page }) => {
    await page.goto('/marketing/harga', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })

  test('profile page loads', async ({ page }) => {
    await page.goto('/marketing/profile', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })
})

test.describe('Operations Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'operations')
  })

  test('dashboard loads without errors', async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', err => errors.push(err.message))
    await page.goto('/operations', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
    expect(errors).toHaveLength(0)
  })

  test('delivery order page loads', async ({ page }) => {
    await page.goto('/operations/delivery-order', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })

  test('rekap page loads', async ({ page }) => {
    await page.goto('/operations/rekap', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })
})

test.describe('Finance Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'finance')
  })

  test('dashboard loads without errors', async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', err => errors.push(err.message))
    await page.goto('/finance', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
    expect(errors).toHaveLength(0)
  })

  test('invoice page loads', async ({ page }) => {
    await page.goto('/finance/invoice', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })

  test('do page loads', async ({ page }) => {
    await page.goto('/finance/do', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })
})
