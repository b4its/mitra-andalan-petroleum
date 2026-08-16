export interface DeliveryOrdersDetails {
  id: string
  do_number: string
  customer_id: string
  customer_name: string
  id_purchase_order: string
  po_number: string
  transport_name: string
  fuel_total: number
  status: string
  details: Details
  created_at: Date
  updated_at: Date
}

export interface Details {
  companyInformation: CompanyInformation
  doInformation: DoInformation
  customerName: string
  customerId: string
  customerAddress: string
  receiverInformation: Information
  receiverDateReceived: Date
  transportName: string
  transportId: string
  transportAddress: string
  driverInformation: DriverInformation
  helperName: string
  transportDateReceived: Date
  dueDate: Date
  total: number
  productInformation: ProductInformation
  transportInformation: TransportInformation
  notes: Note[]
  t2Depot: number
  t2Unloading: number
  indexSensitivity: number
  fuelReceived: number
  companyCoordinator: string
  distributionAdmin: string
  receiver: string
  driver: string
}

export interface CompanyInformation {
  name: string
  nameSub: string
  address: string
  phoneNumber: string
}

export interface DoInformation {
  doNumber: string
  doDateCreated: Date
  poCustomerNumber: PoCustomerNumber
  soNumber: string
}

export interface PoCustomerNumber {
  id: string
  purchaseOrderNumber: string
  customerName: string
  customerId: string
  dateCreated: Date
  dateChanged: Date
  fuelTotalQty: number
}

export interface PoCustomerNumber {
  id: string
  purchaseOrderNumber: string
  customerName: string
  customerId: string
  dateCreated: Date
  dateChanged: Date
  fuelTotalQty: number
}

export interface DriverInformation {
  name: string
  phoneNumber: string
}

export interface Note {
  note: string
}

export interface ProductInformation {
  name: string
  qty: number
  temperature: number
  topSeal: string
  bottomSeal: string
}

export interface Information {
  name: string
  phoneNumber: string
}

export interface TimeInformation {
  departureTime: string
  arrivalTime: string
  unloadingTime: string
  depotArrivalTime: string
}

export interface TransportInformation {
  timeInformation: TimeInformation
  transportNumber: string
  transportType: string
  startKm: number
  endKm: number
  sgMeter: number
}

export interface DeliveryOrderPost {
  do_number: string
  customer_id: string
  id_purchase_order: string
  po_number: string
  transport_name: string | null
  date: string | null
  fuel_total: number
  status: string
  details: Record<string, unknown>
  created_by?: string | null
}

export interface DeliveryOrders {
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
  = | 'PT. Surya Tambang Energi'
    | 'CV. Kaltim Jaya Abadi'
    | 'PT. Borneo Energi Utama'

export type PoNumber = 'PO/2025/VI/101' | 'PO/2025/VI/100' | 'PO/2025/VI/102'

export type Status = 'created' | 'document_returned'

export type TransportName
  = | 'CV. Tiga Putra Transport'
    | 'PT. Armada Kaltim Sejahtera'
    | 'PT. Borneo Distribusi Logistik'

export interface PoTransportirs {
  id: string
  po_number: string
  date: string | null
  pic_person: string | null
  receiver: string | null
  total: number
  status: Status
  created_at: Date
  updated_at: Date
}

export interface PoTransportirsDetails extends PoTransportirs {
  details: PoTransportirDetails
}

export interface PoTransportirDetails {
  date: string
  poTransportNumber: string
  regarding: string
  receiver: string
  picPerson: string
  products: {
    name: string
    loadingDate: string
    unloadingDate: string
    qty: number
    ratePrice: number
    totalPrice: number
  }[]
  percentageNum: {
    ppn: number
  }
  priceSummary: {
    subTotal: number
    ppn: number
    grandTotal: number
  }
  loadingInformation: string
  discharge: string
  termsOfPayment: string
  shrinkageTolerance: string
  contactPerson: {
    companyName: string
    customerName: string
    companyContactPerson?: {
      name: string
      phoneNumber: string
    }[]
    customerContactPerson?: {
      name: string
      phoneNumber: string
    }[]
  }
  offeror: {
    name: string
    signature?: unknown
  }
}

export interface PoTransportirsPost {
  po_number: string
  date: string
  pic_person: string
  receiver: string
  total: number
  status: string
  details: PoTransportirDetails
  created_by: string | null
}
