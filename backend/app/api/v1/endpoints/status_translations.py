"""
Backend API for translating status codes to Indonesian labels.
Returns translations for all database status values.
"""
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(prefix="/status-translations", tags=["Status Translations"])

# Comprehensive status translation map (mirrors frontend)
STATUS_TRANSLATIONS = {
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
    
    # Filter options
    "all": "Semua",
    
    # Color mappings (for UI badges)
    "_colors": {
        "unpaid": "warning",
        "paid": "success",
        "overdue": "error",
        "due_soon": "warning",
        "on_time": "info",
        "created": "info",
        "approved": "success",
        "rejected": "error",
        "cancelled": "neutral",
        "completed": "success",
        "default": "neutral"
    }
}

@router.get("/")
async def get_all_statuses():
    """Get all status translations with colors"""
    return {
        "translations": STATUS_TRANSLATIONS,
        "count": len([k for k in STATUS_TRANSLATIONS.keys() if not k.startswith('_')])
    }

@router.get("/status/{status_code}")
async def translate_status(status_code: str):
    """Translate single status code to Indonesian label and color"""
    label = STATUS_TRANSLATIONS.get(status_code.lower(), status_code)
    color = STATUS_TRANSLATIONS.get("_colors", {}).get(status_code.lower(), "neutral")
    return {
        "value": status_code,
        "label": label,
        "color": color,
        "translated": label != status_code
    }

@router.get("/translate-multiple")
async def translate_multiple_status(
    statuses: str = Query(..., description="Comma-separated status codes"),
    include_colors: bool = True
):
    """Translate multiple status codes at once"""
    status_list = [s.strip().lower() for s in statuses.split(",")]
    
    results = []
    for status in status_list:
        label = STATUS_TRANSLATIONS.get(status, status)
        color = STATUS_TRANSLATIONS.get("_colors", {}).get(status, "neutral") if include_colors else None
        
        results.append({
            "value": status,
            "label": label,
            "color": color,
            "translated": label != status
        })
    
    return {"results": results, "count": len(results)}
