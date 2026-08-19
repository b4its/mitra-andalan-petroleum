// Comprehensive Status Translation Layer
// Meng-handle mapping dari database status → Indonesian label

export const STATUS_LABELS: Record<string, string> = {
  // Invoice statuses
  "unpaid": "Belum Lunas",
  "paid": "Lunas",
  "partial": "Sebagian Lunas",
  "overdue": "Jatuh Tempo",
  
  // Deadline statuses
  "on_time": "Tepat Waktu",
  "due_soon": "Segera",
  
  // General statuses
  "created": "Dibuat",
  "approved": "Disetujui",
  "rejected": "Ditolak",
  "cancelled": "Dibatalkan",
  "completed": "Selesai",
  "sent": "Dikirim",
  "received": "Diterima",
  "returned": "Dikembalikan",
  "delivered": "Terkirim",
  "ready": "Siap",
  "do_completed": "DO Selesai",
  "document_returned": "Dokumen Dikembalikan",
  "under_revision": "Dalam Revisi",
  "po_received": "PO Diterima",
  "failed": "Gagal",
  "refunded": "Dikembalikan",
  "posted": "Dibukukan",
  "draft": "Draf",
  "void": "Dibatalkan",
  "read": "Dibaca",
  "unread": "Belum Dibaca",
  
  // Filter options
  "all": "Semua"
}

/**
 * Translate any status code to Indonesian label
 * @param status - Raw status from database (e.g., "unpaid", "overdue")
 * @returns Translated Indonesian label (e.g., "Belum Lunas", "Jatuh Tempo")
 */
export function translateStatus(status?: string | null): string {
  if (!status) return "-"
  return STATUS_LABELS[status.toLowerCase()] ?? status
}

/**
 * Translate multiple statuses at once
 * @param statuses - Array of status codes
 * @returns Array of translated labels
 */
export function translateMultipleStatuses(statuses: string[]): string[] {
  return statuses.map(s => translateStatus(s))
}

/**
 * Get color mapping for status
 */
export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    unpaid: 'warning',
    paid: 'success',
    overdue: 'error',
    draft: 'neutral',
    posted: 'info',
    created: 'info',
    approved: 'success',
    rejected: 'error',
    cancelled: 'neutral',
    completed: 'success',
    default: 'neutral'
  }
  return colors[status.toLowerCase()] || 'neutral'
}
