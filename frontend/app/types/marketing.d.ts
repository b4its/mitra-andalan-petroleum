export interface Customer {
  id: string
  name: string
  npwp: string | null
  address: string
  province: string | null
  city: string | null
  phone: string
  email: string
}

export interface PurchaseOrderDetails {
  id: string
  po_number: string
  type: 'customer' | 'supplier'
  customer_id: null
  supplier_id: string
  customer_name: string
  supplier_name: string
  date: Date
  total: number
  status: string
  details: Details
  created_at: Date
  updated_at: Date
}

export interface Details {
  companyInformation: CompanyInformation
  receiver: CompanyInformation
  po: Po
  vat: number
  paymentAddress: PaymentAddress
  selectedOfferingLetter: SelectedOfferingLetter
  products: Product[]
  totalProductsPrice: number
  termAndCondition: string
  delivery: Delivery
  forwarder: Forwarder
  signed: Signed
}

export interface CompanyInformation {
  name: string
  address: string
  npwp: string
  contactPerson: string
  email: string
}

export interface Delivery {
  loadingTerminal: string
  loadingDate: Date
  picOperationMap: string
  distance?: string
}

export interface Forwarder {
  trucking: string
}

export interface PaymentAddress {
  bankName: string
  accountNumber: string
  accountName: string
}

export interface Po {
  date: Date
  number: string
}

export interface Product {
  name: string
  qty: number
  unit: string
  price: number
  totalPrice: number
  ppkb?: number
  pph?: number
  ppn?: number
}

export interface SelectedOfferingLetter {
  id: string
  offeringLetterNumber: string
  customerName: string
  customerId: string
  fuelTotalPrice: number
  transportPrice: number
  dateCreated: Date
  dateChanged: Date
  status: string
}

export interface Signed {
  createdBy: string
  approvedBy: string
}

export interface OfferingLetterDetails {
  location: string
  date: Date | string
  offeringLetterNumber: string
  regarding: string
  receiver: string
  supplyPoint: string
  qualityAssurance: string
  custodyTransfer: string
  unloadingProcedure: string
  volumeUnit: string
  volumeTolerance: number
  paymentMethod?: string
  cashMethod?: string
  paymentTerm: string
  latePenalty: number
  servicePattern: string
  personInCharge: PersonInCharge
  paymentAddress: PaymentAddress
  fuelPrices: FuelPrices
  purchaseOrderDeadline: string
  offeror: Offeror
  companyInformation: OfferingLetterCompanyInformation
  informasiTambahan?: string[]
}

export interface OfferingLetterCompanyInformation {
  address: string
  phoneNumber: string
  email: string
}

export interface FuelPrices {
  logisticInformation: string
  productName: string
  hppPrice: number
  basePrice: number
  totalPrice: number
  sellingPrice: {
    ppkb: number
    oat: number | null
    ppn: number
    pph?: number | null
  }
  percentageNum: {
    ppkb: number
    oat: number
    ppn: number
    pph?: number
  }
}

export interface Offeror {
  name: string
  signature: File | undefined
}

export interface PaymentAddress {
  bankName: string
  accountNumber: string
  accountName: string
}

export interface PersonInCharge {
  name: string
  phoneNumber: string
}

export interface OfferingLetterPost {
  offering_letter_number: string
  customer_id: string
  location: string | null
  date: string | null
  regarding: string | null
  receiver: string
  fuel_total_price: number
  transport_price: number
  status: string
  details: OfferingLetterDetails
  created_by?: string | null
}

export interface OfferingLetters {
  id: string
  offering_letter_number: string
  customer_id: string | null
  customer_name: CustomerName | null
  location: Location
  date: Date | string
  regarding: Regarding
  receiver: CustomerName
  fuel_total_price: number
  transport_price: number
  status: Status
  created_at: Date | string
  updated_at: Date | string
  details: OfferingLetterDetails
}

export interface PurchaseOrdersSupplier {
  id: string
  po_number: string
  type: string
  customer_id: string | null
  supplier_id: string
  customer_name: string
  supplier_name: string
  date: Date
  total: number
  status: 'created' | 'under_revision' | 'po_received'
  created_at: Date
  updated_at: Date
  details: Details
}

export interface PurchaseOrdersCustomerPost {
  po_number: string
  type: 'customer' | 'supplier'
  customer_id: string | null
  supplier_id: string | null
  date: string
  total: number
  status: string
  details?: Record<string, unknown>
  created_by?: string | null
  id_offering_letters?: string | null
}

export interface PurchaseOrdersDetails {
  id: string
  po_number: string
  type: 'customer' | 'supplier'
  customer_id: string | null
  supplier_id: string
  customer_name: string
  supplier_name: string
  date: Date
  total: number
  status: string
  created_at: Date
  updated_at: Date
}

// ── Purchase order & delivery order terkait offering letter ──
export interface RelatedDeliveryOrder {
  id: string
  do_number: string
  customer_id: string | null
  customer_name: string
  id_purchase_order: string | null
  po_number: string | null
  transport_name: string | null
  fuel_total: number
  status: string
  details: Record<string, unknown> | null
}

export interface RelatedPurchaseOrder {
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
  details: Record<string, unknown> | null
  created_by: string | null
  id_offering_letters: string | null
  created_at: string | null
  updated_at: string | null
  delivery_orders: RelatedDeliveryOrder[]
}

export interface OfferingLetterPurchaseOrdersResponse {
  items: RelatedPurchaseOrder[]
}

export type CustomerName
  = | 'CV. Kaltim Jaya Abadi'
    | 'PT. Surya Tambang Energi'
    | 'PT. Borneo Energi Utama'

export type Location = 'Jakarta'

export type Regarding = 'Penawaran BBM Solar Industri'

export type Status = 'created' | 'under_revision' | 'po_received'
