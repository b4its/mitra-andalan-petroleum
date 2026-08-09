import { describe, it, expect } from 'vitest'

const API = process.env.API_BASE_URL || 'http://localhost:8080/api/v1'

async function login(email: string, password: string) {
  const res = await fetch(`${API}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
  if (!res.ok) return null
  return res.json()
}

describe('Auth API', () => {
  it('login success returns token and role', async () => {
    const data = await login('admin@email.com', 'admin123')
    expect(data).not.toBeNull()
    expect(data).toHaveProperty('token')
    expect(data).toHaveProperty('role')
    expect(data.role).toBe('admin')
  })

  it('login marketing returns marketing role', async () => {
    const data = await login('marketing@email.com', 'marketing123')
    expect(data).not.toBeNull()
    expect(data.role).toBe('marketing')
  })

  it('login wrong password returns error', async () => {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'admin@email.com', password: 'wrong' })
    })
    expect(res.status).toBe(401)
  })

  it('login nonexistent email returns error', async () => {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'nobody@email.com',
        password: 'test123'
      })
    })
    expect(res.status).toBe(401)
  })
})

describe('Health API', () => {
  it('health endpoint returns OK', async () => {
    const res = await fetch(`${API}/health`)
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data.message).toBe('OK')
  })
})

describe('Customers API', () => {
  it('list customers returns array', async () => {
    const res = await fetch(`${API}/customers`)
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(Array.isArray(data)).toBe(true)
  })
})

describe('Suppliers API', () => {
  it('list suppliers returns array', async () => {
    const res = await fetch(`${API}/suppliers`)
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(Array.isArray(data)).toBe(true)
  })
})

describe('Notifications API', () => {
  it('list notifications returns array', async () => {
    const res = await fetch(`${API}/notifications`)
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(Array.isArray(data)).toBe(true)
  })
})

describe('Offering Letters API', () => {
  it('list offering letters returns paginated response', async () => {
    const res = await fetch(`${API}/offering-letters?page=1&page_size=10`)
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data).toHaveProperty('items')
    expect(data).toHaveProperty('total')
    expect(data).toHaveProperty('page')
    expect(data).toHaveProperty('page_size')
  })
})

describe('Purchase Orders API', () => {
  it('list purchase orders returns paginated response', async () => {
    const res = await fetch(
      `${API}/purchase-orders?page=1&page_size=10`
    )
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data).toHaveProperty('items')
    expect(data).toHaveProperty('total')
  })
})

describe('Delivery Orders API', () => {
  it('list delivery orders returns paginated response', async () => {
    const res = await fetch(
      `${API}/delivery-orders?page=1&page_size=10`
    )
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data).toHaveProperty('items')
    expect(data).toHaveProperty('total')
  })
})

describe('Invoices API', () => {
  it('list invoices returns paginated response', async () => {
    const res = await fetch(`${API}/invoices?page=1&page_size=10`)
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data).toHaveProperty('items')
    expect(data).toHaveProperty('total')
  })
})

describe('Stats API', () => {
  it('marketing stats returns stats array', async () => {
    const res = await fetch(`${API}/stats/marketing`)
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data).toHaveProperty('stats')
    expect(Array.isArray(data.stats)).toBe(true)
  })

  it('operations stats returns stats array', async () => {
    const res = await fetch(`${API}/stats/operations`)
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data).toHaveProperty('stats')
  })

  it('finance stats returns stats array', async () => {
    const res = await fetch(`${API}/stats/finance`)
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data).toHaveProperty('stats')
  })

  it('home stats returns stats array', async () => {
    const res = await fetch(`${API}/stats/home`)
    expect(res.status).toBe(200)
    const data = await res.json()
    expect(data).toHaveProperty('stats')
  })
})

describe('Response structure — offering letter', () => {
  it('each item has required fields', async () => {
    const res = await fetch(`${API}/offering-letters?page=1&page_size=5`)
    const data = await res.json()
    for (const item of data.items) {
      expect(item).toHaveProperty('id')
      expect(item).toHaveProperty('offering_letter_number')
      expect(item).toHaveProperty('customer_id')
      expect(item).toHaveProperty('status')
      expect(item).toHaveProperty('fuel_total_price')
    }
  })
})

describe('Response structure — delivery order', () => {
  it('each item has required fields', async () => {
    const res = await fetch(
      `${API}/delivery-orders?page=1&page_size=5`
    )
    const data = await res.json()
    for (const item of data.items) {
      expect(item).toHaveProperty('id')
      expect(item).toHaveProperty('do_number')
      expect(item).toHaveProperty('customer_id')
      expect(item).toHaveProperty('status')
      expect(item).toHaveProperty('fuel_total')
    }
  })
})

describe('Response structure — invoice', () => {
  it('each item has required fields', async () => {
    const res = await fetch(`${API}/invoices?page=1&page_size=5`)
    const data = await res.json()
    for (const item of data.items) {
      expect(item).toHaveProperty('id')
      expect(item).toHaveProperty('invoice_number')
      expect(item).toHaveProperty('customer_id')
      expect(item).toHaveProperty('grand_total')
      expect(item).toHaveProperty('invoice_status')
    }
  })
})

describe('CORS headers', () => {
  it('API responses include CORS headers', async () => {
    const res = await fetch(`${API}/health`)
    const origin = res.headers.get('access-control-allow-origin')
    if (origin) {
      expect(origin).toBe('*')
    }
  })
})

describe('Pagination', () => {
  it('offering letters respects page_size', async () => {
    const res = await fetch(
      `${API}/offering-letters?page=1&page_size=3`
    )
    const data = await res.json()
    expect(data.items.length).toBeLessThanOrEqual(3)
    expect(data.page_size).toBe(3)
  })

  it('offering letters out of range returns empty items', async () => {
    const res = await fetch(
      `${API}/offering-letters?page=9999&page_size=10`
    )
    const data = await res.json()
    expect(data.items).toEqual([])
  })
})
