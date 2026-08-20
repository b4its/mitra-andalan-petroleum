import type {
  FinanceInvoiceOverview,
  MarketingOfferingLetterOverview,
  OperationsDeliveryOrderOverview,
  Uploads
} from '~/types'

const API_BASE = '/api/v1'

function apiUrl(path: string, params?: Record<string, unknown>) {
  const search = params
    ? '?' + new URLSearchParams(
      Object.entries(params)
        .filter(([, v]) => v !== undefined && v !== null)
        .flatMap(([k, v]) =>
          Array.isArray(v)
            ? v.map(item => [k, String(item)] as [string, string])
            : [[k, String(v)] as [string, string]]
        )
    ).toString()
    : ''
  const url = `${API_BASE}${path}${search}`

  if (import.meta.server) {
    const serverApiBase = process.env.NUXT_API_PROXY_TARGET || 'http://127.0.0.1:8012/api/v1'
    return `${serverApiBase}${path}${search}`
  }

  return url
}

async function parseError(res: Response) {
  const err = await res.json().catch(() => ({ detail: res.statusText }))
  throw new Error(err.detail || `API error: ${res.status}`)
}

interface SortableItem {
  created_at?: string | null
  dateCreated?: string | null
  createdAt?: string | null
}

function newestFirst<T>(data: T, path: string): T {
  if (path.startsWith('/accounting/accounts') || path.startsWith('/accounting/ledger') || path.startsWith('/accounting/trial-balance')) {
    return data
  }

  const sort = (items: unknown[]): unknown[] => {
    const toTime = (item: unknown): number => {
      const sortable = item as Partial<SortableItem>
      return Date.parse(sortable.created_at ?? sortable.dateCreated ?? sortable.createdAt ?? '')
    }
    return [...items].sort((a, b) => {
      const aTime = toTime(a)
      const bTime = toTime(b)
      if (Number.isNaN(aTime) || Number.isNaN(bTime)) return 0
      return bTime - aTime
    })
  }

  if (Array.isArray(data)) {
    return sort(data) as T
  }
  if (data && typeof data === 'object' && Array.isArray((data as unknown as { items?: unknown[] }).items)) {
    return { ...(data as Record<string, unknown>), items: sort((data as unknown as { items: unknown[] }).items) } as T
  }
  return data
}

async function request(input: string, init?: RequestInit) {
  const headers = new Headers(init?.headers)
  if (import.meta.client) {
    const raw = localStorage.getItem('auth')
    if (raw) {
      try {
        const { id, name, role } = JSON.parse(raw)
        if (id) headers.set('x-user-id', id)
        if (name) headers.set('x-user-name', name)
        if (role) headers.set('x-user-role', role)
      } catch {
        /* abaikan payload auth yang korup */
      }
    }
  }
  try {
    return await fetch(input, { ...init, headers })
  } catch {
    const target = import.meta.server
      ? process.env.NUXT_API_PROXY_TARGET || 'http://127.0.0.1:8012/api/v1'
      : API_BASE
    throw new Error(`Backend tidak terhubung. Pastikan API lokal berjalan di ${target}.`)
  }
}

export function useApi() {
  async function get<T>(
    path: string,
    params?: Record<string, unknown>
  ): Promise<T> {
    const res = await request(apiUrl(path, params))
    if (!res.ok) {
      await parseError(res)
    }
    return newestFirst(await res.json(), path)
  }

  async function put<T, U>(path: string, body: U): Promise<T> {
    const res = await request(apiUrl(path), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    if (!res.ok) {
      await parseError(res)
    }
    return res.json()
  }

  async function post<T, U>(path: string, body: U): Promise<T> {
    const res = await request(apiUrl(path), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    if (!res.ok) {
      await parseError(res)
    }
    return res.json()
  }

  async function postFile<T>(path: string, payload: Uploads): Promise<T> {
    if (!payload.files.length) {
      throw new Error('Tidak ada file yang dipilih')
    }
    if (Boolean(payload.document_type) !== Boolean(payload.document_id)) {
      throw new Error('document_type dan document_id harus diisi bersamaan')
    }

    const formData = new FormData()

    payload.files.forEach((file) => {
      formData.append('files', file)
    })

    if (payload.folder !== undefined) {
      formData.append('folder', payload.folder)
    }

    if (payload.document_type) {
      formData.append('document_type', payload.document_type)
    }

    if (payload.document_id) {
      formData.append('document_id', payload.document_id)
    }

    const res = await request(apiUrl(path), {
      method: 'POST',
      body: formData
    })
    if (!res.ok) {
      await parseError(res)
    }
    return res.json()
  }

  async function putFile<T>(path: string, payload: Uploads): Promise<T> {
    if (!payload.files.length) {
      throw new Error('Tidak ada file yang dipilih')
    }
    if (Boolean(payload.document_type) !== Boolean(payload.document_id)) {
      throw new Error('document_type dan document_id harus diisi bersamaan')
    }

    const formData = new FormData()

    payload.files.forEach((file) => {
      formData.append('files', file)
    })

    if (payload.folder !== undefined) {
      formData.append('folder', payload.folder)
    }

    if (payload.document_type) {
      formData.append('document_type', payload.document_type)
    }

    if (payload.document_id) {
      formData.append('document_id', payload.document_id)
    }

    const res = await request(apiUrl(path), {
      method: 'PUT',
      body: formData
    })
    if (!res.ok) {
      await parseError(res)
    }
    return res.json()
  }

  async function del<T>(path: string): Promise<T> {
    const res = await request(apiUrl(path), {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    })
    if (!res.ok) {
      await parseError(res)
    }
    return res.json()
  }

  return { get, post, put, del, putFile, postFile }
}

export interface ApiOfferingLetter {
  id: string
  offering_letter_number: string
  customer_id: string
  customer_name: string
  fuel_total_price: number
  transport_price: number
  status: string
  created_at: string
  updated_at: string
}

export interface ApiDeliveryOrder {
  id: string
  do_number: string
  customer_id: string
  customer_name: string
  po_number: string
  transport_name: string
  fuel_total: number
  status: string
  created_at: string
  updated_at: string
}

export interface ApiInvoice {
  id: string
  invoice_number: string
  customer_id: string
  customer_name: string
  terms_day: number
  grand_total: number
  invoice_status: string
  deadline_status: string
  created_at: string
  updated_at: string
}

export interface ApiPurchaseOrder {
  id: string
  po_number: string
  type: string
  customer_id: string | null
  supplier_id: string | null
  customer_name: string
  supplier_name: string
  date: string | null
  total: number
  status: string
  created_at: string
  updated_at: string
}

export interface ApiPaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface ApiStats {
  stats: {
    title: string
    icon: string
    value: number | string
    variation: number
    to: string
  }[]
}

export function mapOfferingLetter(
  ol: ApiOfferingLetter
): MarketingOfferingLetterOverview {
  return {
    id: ol.id,
    offeringLetterNumber: ol.offering_letter_number,
    customerName: ol.customer_name,
    fuelTotalPrice: ol.fuel_total_price,
    transportPrice: ol.transport_price,
    dateCreated: ol.created_at,
    dateChanged: ol.updated_at,
    status: ol.status as MarketingOfferingLetterOverview['status']
  }
}

export function mapDeliveryOrder(
  do_: ApiDeliveryOrder
): OperationsDeliveryOrderOverview {
  return {
    id: do_.id,
    deliveryOrderNumber: do_.do_number,
    customerName: do_.customer_name,
    purchaseOrderNumber: do_.po_number,
    transportName: do_.transport_name,
    dateCreated: do_.created_at,
    dateChanged: do_.updated_at,
    status: do_.status as OperationsDeliveryOrderOverview['status']
  }
}

export function mapInvoice(inv: ApiInvoice): FinanceInvoiceOverview {
  return {
    id: inv.id,
    invoiceNumber: inv.invoice_number,
    customerName: inv.customer_name,
    termsDay: inv.terms_day,
    dateCreated: inv.created_at,
    grandTotal: inv.grand_total,
    invoiceStatus:
      inv.invoice_status as FinanceInvoiceOverview['invoiceStatus'],
    deadlineStatus:
      inv.deadline_status as FinanceInvoiceOverview['deadlineStatus']
  }
}
