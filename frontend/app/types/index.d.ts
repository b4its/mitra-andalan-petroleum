import type { AvatarProps } from "@nuxt/ui";

export type UserStatus = "subscribed" | "unsubscribed" | "bounced";
export type SaleStatus = "paid" | "failed" | "refunded";
export type Role =
  | "admin"
  | "operations"
  | "marketing"
  | "finance"
  | "accounting";

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  password: string;
  role: Role;
  token: string;
  loggedInAt: string;
}

export interface DummyAccount {
  email: string;
  password: string;
  role: Role;
  name: string;
}

export interface Mail {
  id: number;
  unread?: boolean;
  from: User;
  subject: string;
  body: string;
  date: string;
}

export interface Member {
  name: string;
  username: string;
  role: "member" | "owner";
  avatar: AvatarProps;
}

export interface Stat {
  title: string;
  icon: string;
  value: number | string;
  variation: number;
  to: string;
  formatter?: (value: number) => string;
}

export interface Sale {
  id: string;
  date: string;
  status: SaleStatus;
  email: string;
  amount: number;
}

export interface MarketingOfferingLetterOverview {
  id: string;
  customerName: string;
  offeringLetterNumber: string;
  fuelTotalPrice: number;
  transportPrice: number;
  dateCreated: string;
  dateChanged: string;
  status: "created" | "under_revision" | "po_received";
}

export interface OperationsDeliveryOrderOverview {
  id: string;
  customerName: string;
  deliveryOrderNumber: string;
  purchaseOrderNumber: string;
  transportName: string;
  dateCreated: string;
  dateChanged: string;
  status: "created" | "document_returned";
}

export interface FinanceInvoiceOverview {
  id: string;
  customerName: string;
  invoiceNumber: string;
  termsDay: number;
  dateCreated: string;
  grandTotal: number;
  invoiceStatus: "unpaid" | "paid" | "overdue";
  deadlineStatus: "on_time" | "overdue" | "due_soon";
}

export interface Notification {
  id: number;
  unread?: boolean;
  sender: User;
  body: string;
  date: string;
}

export type Period = "daily" | "weekly" | "monthly";

export interface Range {
  start: Date;
  end: Date;
}

export interface Uploads {
  files: File[];
  folder: string;
  document_type?: string;
  document_id?: string;
}

export interface UpdateFileUploads {
  folder: string;
  document_type: string;
  document_id: string;
}

export interface ResUploads {
  id: string;
  original_filename: string;
  stored_filename: string;
  folder: string;
  mime_type: string;
  size: number;
  url: string;
  document_type: string;
  document_id: string;
  created_at: string;
  updated_at: string;
}
