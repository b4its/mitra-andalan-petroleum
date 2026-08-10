export interface AdminDrilldownMetric {
  key: string
  title: string
  value: number
  unit: string
  description: string
}

export interface AdminMetric extends AdminDrilldownMetric {
  icon: string
}

export interface AdminTrend {
  key: string
  label: string
  offering_letters: number
  purchase_orders: number
  delivery_orders: number
  invoices: number
  sales_amount: number
}

export interface AdminBreakdown {
  key: string
  label: string
  value: number
}

export interface AdminActivity {
  domain: string
  title: string
  subtitle: string
  created_at: string | null
  to: string | null
}

export interface AdminStats {
  date_from: string
  date_to: string
  metrics: AdminMetric[]
  trends: AdminTrend[]
  distributions: Record<string, AdminBreakdown[]>
  notifications: AdminActivity[]
  activities: AdminActivity[]
}

export interface AdminDrilldownItem {
  id: string
  title: string
  subtitle: string
  status: string | null
  value: number | null
  created_at: string | null
  to: string | null
}

export interface AdminDrilldown {
  metric: string
  title: string
  description: string
  total: number
  total_value: number
  page: number
  page_size: number
  items: AdminDrilldownItem[]
}

export interface AdminInvoiceRow {
  id: string
  invoice_number: string
  customer_id: string
  customer_name: string
  terms_day: number
  grand_total: number
  invoice_status: string
  deadline_status: string
  created_at: string | null
  updated_at: string | null
}

export interface AdminDeliveryOrderRow {
  id: string
  do_number: string
  customer_id: string
  customer_name: string
  po_number: string | null
  transport_name: string | null
  fuel_total: number
  status: string
  rilis_dana_at: string | null
  status_rilis_dana: boolean
  ready_order_at: string | null
  status_ready_order: boolean
  selesai_dikirim_at: string | null
  status_selesai_dikirim: boolean
  lunas_ongkir_at: string | null
  status_lunas_ongkir: boolean
  created_at: string | null
  updated_at: string | null
}

export interface Paginated<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
