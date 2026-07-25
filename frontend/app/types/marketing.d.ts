export interface OfferingLetters {
  id: string;
  offering_letter_number: string;
  customer_id: string;
  customer_name: CustomerName;
  location: Location;
  date: Date;
  regarding: Regarding;
  receiver: CustomerName;
  fuel_total_price: number;
  transport_price: number;
  status: Status;
  created_at: Date | string;
  updated_at: Date | string;
}

export interface PurchaseOrdersSupplier {
  id: string;
  po_number: string;
  type: string;
  customer_id: string | null;
  supplier_id: string;
  customer_name: string;
  supplier_name: string;
  date: Date;
  total: number;
  status: "created" | "under_revision" | "po_received";
  created_at: Date;
  updated_at: Date;
}

export interface PurchaseOrdersDetails {
  id: string;
  po_number: string;
  type: string;
  customer_id: string | null;
  supplier_id: string;
  customer_name: string;
  supplier_name: string;
  date: Date;
  total: number;
  status: string;
  created_at: Date;
  updated_at: Date;
}

export type CustomerName =
  | "CV. Maju Jaya Abadi"
  | "PT. Bina Karya Sentosa"
  | "PT. Sumber Rejeki Mandiri";

export type Location = "Jakarta";

export type Regarding = "Penawaran BBM Solar Industri";

export type Status = "created" | "under_revision" | "po_received";
