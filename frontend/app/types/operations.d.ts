export interface DeliveryOrders {
  id: string;
  do_number: string;
  customer_id: string;
  customer_name: CustomerName;
  po_number: PoNumber;
  transport_name: TransportName;
  fuel_total: number;
  status: Status;
  created_at: Date;
  updated_at: Date;
}

export type CustomerName =
  | "PT. Bina Karya Sentosa"
  | "CV. Maju Jaya Abadi"
  | "PT. Sumber Rejeki Mandiri";

export type PoNumber = "PO/2025/VI/101" | "PO/2025/VI/100" | "PO/2025/VI/102";

export type Status = "created" | "document_returned";

export type TransportName =
  | "CV. Angkutan Cepat"
  | "PT. Transport Logistik"
  | "PT. Distribusi Mandiri";
