import type {
  FinanceInvoiceOverview,
  MarketingOfferingLetterOverview,
  OperationsDeliveryOrderOverview,
} from "~/types";

const API_BASE = "http://localhost:8000/api/v1";
const API_BASE_POST = "/api/v1";

export function useApi() {
  async function get<T>(
    path: string,
    params?: Record<string, any>,
  ): Promise<T> {
    const url = new URL(`${API_BASE}${path}`);
    if (params) {
      Object.entries(params).forEach(([k, v]) =>
        url.searchParams.set(k, String(v)),
      );
    }
    const res = await fetch(url.toString());
    if (!res.ok) {
      throw new Error(`API error: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  async function post<T, U>(path: string, body: U): Promise<T> {
    const res = await fetch(`${API_BASE_POST}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `API error: ${res.status}`);
    }
    return res.json();
  }

  return { get, post };
}

export interface ApiOfferingLetter {
  id: string;
  offering_letter_number: string;
  customer_id: string;
  customer_name: string;
  fuel_total_price: number;
  transport_price: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ApiDeliveryOrder {
  id: string;
  do_number: string;
  customer_id: string;
  customer_name: string;
  po_number: string;
  transport_name: string;
  fuel_total: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ApiInvoice {
  id: string;
  invoice_number: string;
  customer_id: string;
  customer_name: string;
  terms_day: number;
  grand_total: number;
  invoice_status: string;
  deadline_status: string;
  created_at: string;
  updated_at: string;
}

export interface ApiSale {
  id: string;
  date: string;
  status: string;
  email: string;
  amount: number;
  created_at: string;
}

export interface ApiPurchaseOrder {
  id: string;
  po_number: string;
  type: string;
  customer_id: string | null;
  supplier_id: string | null;
  customer_name: string;
  supplier_name: string;
  date: string | null;
  total: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ApiPaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface ApiStats {
  stats: {
    title: string;
    icon: string;
    value: number | string;
    variation: number;
    to: string;
  }[];
}

export function mapOfferingLetter(
  ol: ApiOfferingLetter,
): MarketingOfferingLetterOverview {
  return {
    id: ol.id,
    offeringLetterNumber: ol.offering_letter_number,
    customerName: ol.customer_name,
    fuelTotalPrice: ol.fuel_total_price,
    transportPrice: ol.transport_price,
    dateCreated: ol.created_at,
    dateChanged: ol.updated_at,
    status: ol.status as MarketingOfferingLetterOverview["status"],
  };
}

export function mapDeliveryOrder(
  do_: ApiDeliveryOrder,
): OperationsDeliveryOrderOverview {
  return {
    id: do_.id,
    deliveryOrderNumber: do_.do_number,
    customerName: do_.customer_name,
    purchaseOrderNumber: do_.po_number,
    transportName: do_.transport_name,
    dateCreated: do_.created_at,
    dateChanged: do_.updated_at,
    status: do_.status as OperationsDeliveryOrderOverview["status"],
  };
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
      inv.invoice_status as FinanceInvoiceOverview["invoiceStatus"],
    deadlineStatus:
      inv.deadline_status as FinanceInvoiceOverview["deadlineStatus"],
  };
}
