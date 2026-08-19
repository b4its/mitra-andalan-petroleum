"""
Status Translation Utility for Backend
Maps English database status values to Indonesian display labels
"""

STATUS_LABELS = {
    # Invoice statuses
    "unpaid": "Belum Lunas",
    "paid": "Lunas", 
    "partial": "Sebagian Lunas",
    "overdue": "Jatuh Tempo",
    
    # Deadline statuses
    "on_time": "Tepat Waktu",
    "due_soon": "Segera",
    
    # General document statuses
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
    "unknown": "-",
}

def translate_status(status: str) -> str:
    """Translate single status value to Indonesian"""
    if not status:
        return ""
    return STATUS_LABELS.get(status.lower(), status)

def translate_multiple_statuses(statuses: list) -> list:
    """Translate multiple status values at once"""
    return [translate_status(s) for s in statuses]

def translate_breakdown_item(key: str, label: str, value: int) -> dict:
    """Translate a breakdown item (for charts) and return with translated label"""
    return {
        "key": key,
        "label": translate_status(label),  # Use translated Indonesian label
        "value": value
    }
