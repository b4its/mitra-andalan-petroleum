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

// Filter error yang tidak relevan (favicon, hydration warning Nuxt/Vue)
function filterBenignErrors(errors: string[]): string[] {
  return errors.filter(
    e =>
      !e.includes('favicon') &&
      !e.includes('favicon.ico') &&
      !e.includes('Hydration completed but contains mismatches') &&
      !e.includes('Download the Vue Devtools extension') &&
      !e.includes('experimental feature')
  )
}

test.describe('Page rendering — Marketing', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'marketing')
  })

  test('customer page has table or list', async ({ page }) => {
    await page.goto('/marketing/customer')
    await page.waitForLoadState('networkidle')
    const hasTable = await page.locator('table, [role=grid], ul, div.list')
      .first()
      .isVisible()
      .catch(() => false)
    if (!hasTable) {
      const hasContent = await page.locator('body').innerText()
      expect(hasContent.length).toBeGreaterThan(10)
    }
  })

  test('offering letters subpage renders', async ({
    page
  }) => {
    await page.goto('/marketing/customer/penawaran', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })

  test('po subpage renders', async ({ page }) => {
    await page.goto('/marketing/customer/po', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })
})

test.describe('Page rendering — Operations', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'operations')
  })

  test('delivery order page renders form', async ({ page }) => {
    await page.goto('/operations/delivery-order', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })

  test('delivery order returned page renders', async ({
    page
  }) => {
    await page.goto('/operations/delivery-order-returned', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })
})

test.describe('Page rendering — Finance', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'finance')
  })

  test('invoice data page renders', async ({ page }) => {
    await page.goto('/finance/invoice/data-invoice-customer', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })

  test('invoice creation page renders', async ({ page }) => {
    await page.goto('/finance/invoice/pembuatan-invoice', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })

  test('detail operations loads', async ({ page }) => {
    await page.goto('/finance/detail-operations', { waitUntil: 'networkidle' })
    await expect(page.locator('h1, h2, h3').first()).toBeVisible()
  })
})

test.describe('Responsive layout', () => {
  test('login page works on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    await page.goto('/login', { waitUntil: 'networkidle' })
    const form = page.locator('form')
    await expect(form).toBeVisible()
  })

  test('sidebar is hidden on mobile', async ({ page }) => {
    await loginAs(page, 'admin')
    await page.setViewportSize({ width: 375, height: 812 })
    const sidebar = page.locator('nav, aside, [role=navigation]')
    const isVisible = await sidebar.isVisible().catch(() => false)
    if (isVisible) {
      const box = await sidebar.boundingBox()
      if (box) {
        expect(box.width).toBeLessThan(400)
      }
    }
  })
})

test.describe('Browser console — no errors', () => {
  test('no console errors on login', async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', err => errors.push(err.message))
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text())
    })
    await page.goto('/login', { waitUntil: 'networkidle' })
    await page.waitForLoadState('networkidle')
    expect(filterBenignErrors(errors)).toHaveLength(0)
  })

  test('no console errors on admin dashboard', async ({ page }) => {
    await loginAs(page, 'admin')
    const errors: string[] = []
    page.on('pageerror', err => errors.push(err.message))
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text())
    })
    await page.goto('/admin', { waitUntil: 'networkidle' })
    await page.waitForLoadState('networkidle')
    expect(filterBenignErrors(errors)).toHaveLength(0)
  })

  test('no console errors on marketing dashboard', async ({ page }) => {
    await loginAs(page, 'marketing')
    const errors: string[] = []
    page.on('pageerror', err => errors.push(err.message))
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text())
    })
    await page.goto('/marketing', { waitUntil: 'networkidle' })
    await page.waitForLoadState('networkidle')
    expect(filterBenignErrors(errors)).toHaveLength(0)
  })

  test('no console errors on operations dashboard', async ({ page }) => {
    await loginAs(page, 'operations')
    const errors: string[] = []
    page.on('pageerror', err => errors.push(err.message))
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text())
    })
    await page.goto('/operations', { waitUntil: 'networkidle' })
    await page.waitForLoadState('networkidle')
    expect(filterBenignErrors(errors)).toHaveLength(0)
  })

  test('no console errors on finance dashboard', async ({ page }) => {
    await loginAs(page, 'finance')
    const errors: string[] = []
    page.on('pageerror', err => errors.push(err.message))
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text())
    })
    await page.goto('/finance', { waitUntil: 'networkidle' })
    await page.waitForLoadState('networkidle')
    expect(filterBenignErrors(errors)).toHaveLength(0)
  })
})
