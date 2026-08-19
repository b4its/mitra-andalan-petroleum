// Pemetaan label Indonesia untuk nilai status dari database.
// Nilai status disimpan sebagai konstanta Inggris (mis. "created", "paid"),
// tetapi ditampilkan sebagai bahasa Indonesia di seluruh UI.

export const STATUS_LABELS: Record<string, string> = {
  created: 'Dibuat',
  approved: 'Disetujui',
  rejected: 'Ditolak',
  cancelled: 'Dibatalkan',
  completed: 'Selesai',
  sent: 'Dikirim',
  received: 'Diterima',
  returned: 'Dikembalikan',
  delivered: 'Terkirim',
  ready: 'Siap',
  do_completed: 'DO Selesai',
  document_returned: 'Dokumen Dikembalikan',
  under_revision: 'Dalam Revisi',
  po_received: 'PO Diterima',
  unpaid: 'Belum Lunas',
  paid: 'Lunas',
  partial: 'Sebagian Lunas',
  overdue: 'Jatuh Tempo',
  due_soon: 'Segera',
  on_time: 'Tepat Waktu',
  failed: 'Gagal',
  refunded: 'Dikembalikan',
  posted: 'Dibukukan',
  draft: 'Draf',
  read: 'Dibaca',
  unread: 'Belum Dibaca'
}

export function statusLabel(status?: string | null): string {
  if (!status) return ''
  return STATUS_LABELS[status] ?? status
}
