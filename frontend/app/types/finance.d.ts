export interface InvoiceDetails {
  id: string
  invoice_number: string
  customer_id: string
  customer_name: string
  terms_day: number
  grand_total: number
  invoice_status: string
  deadline_status: string
  details: InvoiceDetailsData
  created_at: Date
  updated_at: Date
}

export interface InvoiceDetailsData {
  billToInformation: string
  deliveryPointInformation: string
  companyInformation: InvoiceCompanyInformation
  invoiceInformation: InvoiceInformation
  customerPurchaseInformation: CustomerPurchaseInformation
  products: InvoiceProduct[]
  priceSummary: PriceSummary
  termsAndCondition: TermsAndCondition[]
  paymentInformation: PaymentInformation
  signature: Signature
}

export interface InvoiceCompanyInformation {
  name: string
  address: string
  phoneNumber: string
  email: string
}

export interface CustomerPurchaseInformation {
  deliveryOrderNumberData: string[]
  customerPurchaseOrderNumber: CustomerPurchaseOrderNumber
  taxInvoiceNumber: string
  salesOrderNumber?: string
}

export interface CustomerPurchaseOrderNumber {
  id: string
  purchaseOrderNumber: string
  customerName: string
  customerId: string
  dateCreated: Date
  dateChanged: Date
  fuelTotalQty: number
}

export interface InvoiceInformation {
  invoiceNumber: string
  invoiceDate: Date
  invoiceDueDate: Date
  terms: number
}

export interface PaymentInformation {
  bankName: string
  accountNumber: string
  accountName: string
}

export interface PriceSummary {
  grandTotal: number
  subTotal: number
  ppn: number
  spellNumber: string
  discount: number
  prePaid: number
}

export interface InvoiceProduct {
  name: string
  qty: number
  unit: string
  price: number
  totalPrice: number
}

export interface Signature {
  companyName: string
  createdBy: string
}

export interface TermsAndCondition {
  term: string
}

export interface InvoicePost {
  invoice_number: string
  customer_id: string
  terms_day: number
  grand_total: number
  invoice_status: 'unpaid' | 'paid' | 'overdue'
  deadline_status: 'on_time' | 'due_soon' | 'overdue'
  details: Record<string, unknown>
}

export interface FinanceDeliveryOrders {
  id: string
  do_number: string
  customer_id: string
  customer_name: CustomerName
  po_number: PoNumber
  transport_name: TransportName
  fuel_total: number
  status: Status
  created_at: Date
  updated_at: Date
}

export type CustomerName
  = | 'PT. Bina Karya Sentosa'
    | 'CV. Maju Jaya Abadi'
    | 'PT. Sumber Rejeki Mandiri'

export type PoNumber = 'PO/2025/VI/101' | 'PO/2025/VI/100' | 'PO/2025/VI/102'

export type Status = 'created' | 'document_returned'

export type TransportName
  = | 'CV. Angkutan Cepat'
    | 'PT. Transport Logistik'
    | 'PT. Distribusi Mandiri'

export interface Invoices {
  id: string
  invoice_number: string
  customer_id: string
  customer_name: CustomerName
  terms_day: number
  grand_total: number
  invoice_status: InvoiceStatus
  deadline_status: DeadlineStatus
  created_at: Date
  updated_at: Date
}

export type CustomerName
  = | 'PT. Bina Karya Sentosa'
    | 'CV. Maju Jaya Abadi'
    | 'PT. Sumber Rejeki Mandiri'

export type DeadlineStatus = 'overdue' | 'on_time' | 'due_soon'

export type InvoiceStatus = 'paid' | 'unpaid' | 'overdue'
