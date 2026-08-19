<script setup lang="ts">
type DocType = 'ol' | 'po' | 'do' | 'invoice'

interface RecordDetail {
  id: string
  offering_letter_number: string
  po_number: string
  do_number: string
  invoice_number: string
  status: string
  invoice_status: string
  deadline_status: string
  type: string
  customer_name: string
  supplier_name: string
  date: string
  location: string
  regarding: string
  receiver: string
  fuel_total_price: number
  transport_price: number
  total: number
  grand_total: number
  terms_day: number
  fuel_total: number
  transport_name: string
  status_rilis_dana: boolean
  rilis_dana_at: string | null
  status_ready_order: boolean
  ready_order_at: string | null
  status_selesai_dikirim: boolean
  selesai_dikirim_at: string | null
  status_lunas_ongkir: boolean
  lunas_ongkir_at: string | null
  created_at: string
  updated_at: string
  details?: Record<string, unknown> | null
}

interface RecordUpload {
  id: string
  url: string
  original_filename: string
  mime_type: string
  size: number
}

const props = defineProps<{
  open: boolean
  type: DocType
  id: string | null
}>()

const emit = defineEmits<{ 'update:open': [value: boolean] }>()

const { get } = useApi()

const endpointMap: Record<DocType, string> = {
  ol: '/offering-letters',
  po: '/purchase-orders',
  do: '/delivery-orders',
  invoice: '/invoices'
}

const titleMap: Record<DocType, string> = {
  ol: 'Detail Surat Penawaran',
  po: 'Detail Purchase Order',
  do: 'Detail Delivery Order',
  invoice: 'Detail Invoice'
}

// ── Fetch record ──────────────────────────────────────────────
const { data, pending, error } = await useAsyncData(
  () => `record-detail-${props.type}-${props.id}`,
  () => {
    if (!props.id) return Promise.resolve(null)
    return get<RecordDetail>(`${endpointMap[props.type]}/${props.id}`)
  },
  { watch: [() => props.id, () => props.type] }
)

// ── Fetch files terkait ───────────────────────────────────────
const { data: uploads, pending: uploadsPending } = await useAsyncData(
  () => `record-uploads-${props.type}-${props.id}`,
  () => {
    if (!props.id) return Promise.resolve([])
    return get<RecordUpload[]>('/uploads', {
      document_type: props.type,
      document_id: props.id
    })
  },
  { watch: [() => props.id, () => props.type], default: () => [] }
)

interface RelatedPO {
  id: string
  po_number: string
  type?: string
  customer_name?: string
  supplier_name?: string
  date?: string
  total?: number
  status?: string
  created_at?: string
  id_offering_letters?: string | null
}

interface RelatedDO {
  id: string
  do_number: string
  po_number?: string | null
  id_purchase_order?: string | null
}

interface RelatedDODetail {
  id: string
  do_number: string
  customer_id: string | null
  customer_name: string
  id_purchase_order: string | null
  po_number: string | null
  transport_name: string | null
  fuel_total: number
  status: string
  status_rilis_dana: boolean
  rilis_dana_at: string | null
  status_ready_order: boolean
  ready_order_at: string | null
  status_selesai_dikirim: boolean
  selesai_dikirim_at: string | null
  status_lunas_ongkir: boolean
  lunas_ongkir_at: string | null
  created_at: string
  updated_at: string
}

interface InvoiceDetails {
  customerPurchaseInformation?: {
    deliveryOrderNumberData?: string[]
  }
}

// ── Fetch PO customer terkait offering letter ─────────────────
const { data: relatedPos, pending: relatedPosPending } = await useAsyncData(
  () => `record-related-pos-${props.type}-${props.id}`,
  () => {
    if (!props.id || props.type !== 'ol') return Promise.resolve([])
    return get<{ items: RelatedPO[] }>('/purchase-orders', {
      type: 'customer',
      offering_letter_id: props.id,
      page: 1,
      page_size: 50
    }).then(r => r.items)
  },
  { watch: [() => props.id, () => props.type], default: () => [] }
)

// ── Fetch uploads lampiran PO customer ────────────────────────
const { data: poUploads, pending: poUploadsPending } = await useAsyncData(
  () => `record-po-uploads-${props.type}-${props.id}`,
  async () => {
    if (!props.id || props.type !== 'ol') return []
    const files: RecordUpload[] = []
    for (const po of relatedPos.value) {
      const ups = await get<RecordUpload[]>('/uploads', {
        document_type: 'po',
        document_id: po.id
      })
      files.push(...ups)
    }
    return files
  },
  {
    watch: [() => props.id, () => props.type, () => relatedPos.value],
    default: () => []
  }
)

// ── Fetch PO terkait delivery order ────────────────────────────
const { data: doRelatedPo, pending: doRelatedPoPending } = await useAsyncData(
  () => `record-do-po-${props.type}-${props.id}`,
  async () => {
    if (!props.id || props.type !== 'do' || !data.value) return null
    const doRecord = data.value as RecordDetail & {
      id_purchase_order?: string | null
    }
    if (doRecord.id_purchase_order) {
      try {
        return await get<RelatedPO>(`/purchase-orders/${doRecord.id_purchase_order}`)
      } catch {
        // fallback ke pencarian po_number
      }
    }
    const poNumber = (data.value as RecordDetail).po_number
    if (!poNumber) return null
    const res = await get<{ items: RelatedPO[] }>('/purchase-orders', {
      type: 'customer',
      search: poNumber,
      page: 1,
      page_size: 5
    })
    return (res.items || []).find(po => po.po_number === poNumber) || null
  },
  { watch: [() => props.id, () => props.type, () => data.value], default: () => null }
)

interface DODetailsShape {
  t2Depot?: number
  t2Unloading?: number
  indexSensitivity?: number
  fuelReceived?: number
  notes?: Array<{ note?: string }>
}

const doDetails = computed<DODetailsShape | null>(() => {
  const rec = data.value as (RecordDetail & { details?: DODetailsShape }) | null
  return rec?.details ?? null
})

// ── Fetch riwayat DO yang bereferensi ke PO (parent) ──────────
const { data: poRelatedDos, pending: poRelatedDosPending } = await useAsyncData(
  () => `record-po-dos-${props.type}-${props.id}`,
  async () => {
    if (!props.id || props.type !== 'po' || !data.value) return []
    const poId = (data.value as RecordDetail).id
    if (!poId) return []
    const res = await get<{ items: RelatedDODetail[] }>('/delivery-orders', {
      purchase_order_id: poId,
      page: 1,
      page_size: 100
    })
    return res.items || []
  },
  { watch: [() => props.id, () => props.type, () => data.value], default: () => [] }
)

// ── Fetch uploads PO + OL terkait delivery order ───────────────
const { data: doRelatedUploads, pending: doRelatedUploadsPending } = await useAsyncData(
  () => `record-do-related-uploads-${props.type}-${props.id}`,
  async () => {
    if (!props.id || props.type !== 'do' || !doRelatedPo.value) return []
    const files: RecordUpload[] = []
    const po = doRelatedPo.value

    // Uploads PO
    const poUps = await get<RecordUpload[]>('/uploads', {
      document_type: 'po',
      document_id: po.id
    })
    files.push(...poUps)

    // Uploads OL dari id_offering_letters
    if (po.id_offering_letters) {
      try {
        const olIds: string[] = JSON.parse(po.id_offering_letters)
        for (const olId of olIds) {
          const olUps = await get<RecordUpload[]>('/uploads', {
            document_type: 'offering_letter',
            document_id: olId
          })
          files.push(...olUps)
        }
      } catch {
        // ignore parse error
      }
    }

    return files
  },
  {
    watch: [() => props.id, () => props.type, () => doRelatedPo.value],
    default: () => []
  }
)

// ── Fetch delivery orders terkait invoice ─────────────────────
const { data: invoiceRelatedDos, pending: invoiceRelatedDosPending } = await useAsyncData(
  () => `record-invoice-dos-${props.type}-${props.id}`,
  async () => {
    if (!props.id || props.type !== 'invoice' || !data.value) return []
    const details = (data.value as RecordDetail & { details?: InvoiceDetails }).details
    const doNumbers = details?.customerPurchaseInformation?.deliveryOrderNumberData || []
    if (!doNumbers.length) return []

    const dos: RelatedDO[] = []
    for (const doNumber of doNumbers) {
      const res = await get<{ items: RelatedDO[] }>('/delivery-orders', {
        search: doNumber,
        page: 1,
        page_size: 5
      })
      const found = (res.items || []).find(d => d.do_number === doNumber)
      if (found) dos.push(found)
    }
    return dos
  },
  { watch: [() => props.id, () => props.type, () => data.value], default: () => [] }
)

// ── Fetch uploads (DO + PO + OL) terkait invoice ───────────────
const { data: invoiceRelatedUploads, pending: invoiceRelatedUploadsPending } = await useAsyncData(
  () => `record-invoice-related-uploads-${props.type}-${props.id}`,
  async () => {
    if (!props.id || props.type !== 'invoice' || !invoiceRelatedDos.value?.length) return []
    const files: RecordUpload[] = []
    const seen = new Set<string>()

    const push = (ups: RecordUpload[]) => {
      for (const up of ups) {
        if (seen.has(up.id)) continue
        seen.add(up.id)
        files.push(up)
      }
    }

    for (const doItem of invoiceRelatedDos.value) {
      // Uploads DO itu sendiri
      const doUps = await get<RecordUpload[]>('/uploads', {
        document_type: 'do',
        document_id: doItem.id
      })
      push(doUps)

      // Uploads PO terkait DO (prioritaskan id_purchase_order)
      let po: RelatedPO | null = null
      if (doItem.id_purchase_order) {
        try {
          po = await get<RelatedPO>(`/purchase-orders/${doItem.id_purchase_order}`)
        } catch {
          po = null
        }
      }
      if (!po && doItem.po_number) {
        const res = await get<{ items: RelatedPO[] }>('/purchase-orders', {
          type: 'customer',
          search: doItem.po_number,
          page: 1,
          page_size: 5
        })
        po = (res.items || []).find(p => p.po_number === doItem.po_number) || null
      }
      if (!po) continue

      const poUps = await get<RecordUpload[]>('/uploads', {
        document_type: 'po',
        document_id: po.id
      })
      push(poUps)

      // Uploads OL dari id_offering_letters
      if (po.id_offering_letters) {
        try {
          const olIds: string[] = JSON.parse(po.id_offering_letters)
          for (const olId of olIds) {
            const olUps = await get<RecordUpload[]>('/uploads', {
              document_type: 'offering_letter',
              document_id: olId
            })
            push(olUps)
          }
        } catch {
          // ignore parse error
        }
      }
    }

    return files
  },
  {
    watch: [() => props.id, () => props.type, () => invoiceRelatedDos.value],
    default: () => []
  }
)

// ── Format helpers ────────────────────────────────────────────
function fmt(v: unknown): string {
  if (v === null || v === undefined || v === '') return '-'
  return String(v)
}
function fmtCurrency(v: unknown): string {
  if (v === null || v === undefined) return '-'
  return formatCurrency(Number(v))
}
function fmtDateTime(v: unknown): string {
  if (!v) return '-'
  const d = new Date(v as string | number)
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const yyyy = d.getFullYear()
  const hh = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${dd}-${mm}-${yyyy}, ${hh}:${min}`
}
function fmtSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// ── Status colors ──────────────────────────────────────────────
const olStatusColor: Record<string, 'info' | 'warning' | 'success'> = {
  created: 'info',
  under_revision: 'warning',
  po_received: 'success'
}
const doStatusColor: Record<string, 'info' | 'success'> = {
  created: 'info',
  document_returned: 'success'
}
const invStatusColor: Record<string, 'warning' | 'success' | 'error'> = {
  unpaid: 'warning',
  paid: 'success',
  overdue: 'error'
}
const deadlineColor: Record<string, 'info' | 'warning' | 'error'> = {
  on_time: 'info',
  due_soon: 'warning',
  overdue: 'error'
}

// ── File helpers ──────────────────────────────────────────────
function fileIcon(mimeType: string): string {
  if (mimeType.startsWith('image/')) return 'i-lucide-image'
  if (mimeType === 'application/pdf') return 'i-lucide-file-text'
  if (mimeType.includes('spreadsheet') || mimeType.includes('excel'))
    return 'i-lucide-table'
  if (mimeType.includes('word')) return 'i-lucide-file-type'
  return 'i-lucide-paperclip'
}

function fileUrl(url: string): string {
  // backend mengembalikan url seperti /media/folder/filename
  // di dev mode Nuxt proxy /media → backend:8012/media
  if (url.startsWith('http')) return url
  return url // /media/... sudah cukup, proxied oleh nitro devProxy
}

async function downloadFile(upload: RecordUpload) {
  const url = fileUrl(upload.url)
  const a = document.createElement('a')
  a.href = url
  a.download = upload.original_filename
  a.target = '_blank'
  a.rel = 'noopener noreferrer'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}
</script>

<template>
  <UModal
    :open="open"
    :ui="{ content: 'max-w-2xl' }"
    @update:open="emit('update:open', $event)"
  >
    <template #title>
      <div class="flex items-center gap-2">
        <UIcon name="i-lucide-file-text" class="size-4 text-primary" />
        {{ titleMap[type] }}
      </div>
    </template>

    <template #body>
      <!-- Loading -->
      <div v-if="pending" class="space-y-3">
        <USkeleton v-for="i in 6" :key="i" class="h-10 rounded-lg" />
      </div>

      <!-- Error -->
      <UAlert
        v-else-if="error"
        color="error"
        title="Gagal memuat data"
        :description="error.message"
      />

      <template v-else>
        <!-- ── Offering Letter ── -->
        <div v-if="type === 'ol' && data" class="space-y-4 text-sm">
          <div class="grid grid-cols-2 gap-x-6 gap-y-3">
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Nomor Surat Penawaran
              </p>
              <p class="font-semibold">
                {{ fmt(data.offering_letter_number) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Status
              </p>
              <UBadge
                :color="olStatusColor[data.status] ?? 'neutral'"
                variant="subtle"
              >
                {{ statusLabel(data.status) }}
              </UBadge>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Customer
              </p>
              <p class="font-medium">
                {{ fmt(data.customer_name) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Tanggal
              </p>
              <p class="font-medium">
                {{ fmt(data.date) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Lokasi
              </p>
              <p class="font-medium">
                {{ fmt(data.location) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Perihal
              </p>
              <p class="font-medium">
                {{ fmt(data.regarding) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Penerima
              </p>
              <p class="font-medium">
                {{ fmt(data.receiver) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Harga BBM
              </p>
              <p class="font-bold text-success">
                {{ fmtCurrency(data.fuel_total_price) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Ongkos Transportir
              </p>
              <p class="font-bold text-success">
                {{ fmtCurrency(data.transport_price) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Dibuat
              </p>
              <p class="font-medium">
                {{ fmtDateTime(data.created_at) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Diperbarui
              </p>
              <p class="font-medium">
                {{ fmtDateTime(data.updated_at) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                ID
              </p>
              <p class="font-mono text-xs text-muted truncate">
                {{ data.id }}
              </p>
            </div>
          </div>
        </div>

        <!-- ── Purchase Order ── -->
        <div v-else-if="type === 'po' && data" class="space-y-4 text-sm">
          <div class="grid grid-cols-2 gap-x-6 gap-y-3">
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Nomor Purchase Order
              </p>
              <p class="font-semibold">
                {{ fmt(data.po_number) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Tipe
              </p>
              <UBadge
                :color="data.type === 'customer' ? 'info' : 'warning'"
                variant="subtle"
                class="capitalize"
              >
                {{ data.type }}
              </UBadge>
            </div>
            <div v-if="data.customer_name">
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Customer
              </p>
              <p class="font-medium">
                {{ fmt(data.customer_name) }}
              </p>
            </div>
            <div v-if="data.supplier_name">
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Supplier
              </p>
              <p class="font-medium">
                {{ fmt(data.supplier_name) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Tanggal
              </p>
              <p class="font-medium">
                {{ fmt(data.date) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Total
              </p>
              <p class="font-semibold text-primary">
                {{ fmtCurrency(data.total) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Status
              </p>
              <UBadge color="neutral" variant="subtle" class="capitalize">
                {{
                  fmt(data.status)
                }}
              </UBadge>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Dibuat
              </p>
              <p class="font-medium">
                {{ fmtDateTime(data.created_at) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Diperbarui
              </p>
              <p class="font-medium">
                {{ fmtDateTime(data.updated_at) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                ID
              </p>
              <p class="font-mono text-xs text-muted truncate">
                {{ data.id }}
              </p>
            </div>
          </div>

          <!-- ── Riwayat Delivery Order (parent PO) ── -->
          <div class="border-t border-default pt-3">
            <div class="flex items-center justify-between mb-3">
              <p
                class="text-xs font-semibold text-muted uppercase tracking-wide"
              >
                Riwayat Delivery Order dari Purchase Order ini
              </p>
              <UBadge variant="subtle" color="primary">
                {{ poRelatedDos?.length || 0 }} Delivery Order
              </UBadge>
            </div>

            <!-- Loading -->
            <div v-if="poRelatedDosPending" class="space-y-2">
              <USkeleton v-for="i in 2" :key="i" class="h-16 rounded-lg" />
            </div>

            <!-- Kosong -->
            <p v-else-if="!poRelatedDos?.length" class="text-sm text-dimmed">
              Belum ada Delivery Order yang dibuat dari Purchase Order ini.
            </p>

            <!-- Daftar DO -->
            <div v-else class="flex flex-col gap-3">
              <div
                v-for="doItem in poRelatedDos"
                :key="doItem.id"
                class="rounded-lg border border-default p-3 space-y-2"
              >
                <div class="flex flex-wrap items-center gap-2">
                  <UIcon name="i-lucide-truck" class="size-4 text-primary shrink-0" />
                  <p class="font-semibold">
                    {{ fmt(doItem.do_number) }}
                  </p>
                  <UBadge
                    :color="doStatusColor[doItem.status] ?? 'neutral'"
                    variant="subtle"
                    class="ml-auto"
                  >
                    {{ statusLabel(doItem.status) }}
                  </UBadge>
                </div>

                <div class="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
                  <div>
                    <p class="text-muted">
                      Customer
                    </p>
                    <p class="font-medium truncate">
                      {{ fmt(doItem.customer_name) }}
                    </p>
                  </div>
                  <div>
                    <p class="text-muted">
                      Volume BBM
                    </p>
                    <p class="font-medium">
                      {{ formatNumber(doItem.fuel_total ?? 0) }} L
                    </p>
                  </div>
                  <div>
                    <p class="text-muted">
                      Transportir
                    </p>
                    <p class="font-medium truncate">
                      {{ fmt(doItem.transport_name) }}
                    </p>
                  </div>
                  <div>
                    <p class="text-muted">
                      Dibuat
                    </p>
                    <p class="font-medium">
                      {{ fmtDateTime(doItem.created_at) }}
                    </p>
                  </div>
                </div>

                <!-- Alur pengiriman -->
                <div class="flex flex-wrap gap-x-4 gap-y-1.5 pt-1.5 border-t border-default text-xs">
                  <span class="flex items-center gap-1">
                    <UIcon
                      name="i-lucide-package"
                      class="size-3.5"
                      :class="doItem.status_ready_order ? 'text-info' : 'text-muted'"
                    />
                    Siap Kirim:
                    <span class="font-medium">
                      {{ doItem.status_ready_order ? 'Siap' : '-' }}
                    </span>
                  </span>
                  <span class="flex items-center gap-1">
                    <UIcon
                      name="i-lucide-check-circle"
                      class="size-3.5"
                      :class="doItem.status_selesai_dikirim ? 'text-success' : 'text-muted'"
                    />
                    Selesai Dikirim:
                    <span class="font-medium">
                      {{ doItem.status_selesai_dikirim ? 'Selesai' : '-' }}
                    </span>
                  </span>
                  <span class="flex items-center gap-1">
                    <UIcon
                      name="i-lucide-truck"
                      class="size-3.5"
                      :class="doItem.status_lunas_ongkir ? 'text-success' : 'text-muted'"
                    />
                    Lunas Ongkir:
                    <span class="font-medium">
                      {{ doItem.status_lunas_ongkir ? 'Lunas' : '-' }}
                    </span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Delivery Order ── -->
        <div v-else-if="type === 'do' && data" class="space-y-4 text-sm">
          <div class="grid grid-cols-2 gap-x-6 gap-y-3">
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Nomor Delivery Order
              </p>
              <p class="font-semibold">
                {{ fmt(data.do_number) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Status
              </p>
              <UBadge
                :color="doStatusColor[data.status] ?? 'neutral'"
                variant="subtle"
              >
                {{ statusLabel(data.status) }}
              </UBadge>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Customer
              </p>
              <p class="font-medium">
                {{ fmt(data.customer_name) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Nomor Purchase Order
              </p>
              <p class="font-medium">
                {{ fmt(data.po_number) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Transportir
              </p>
              <p class="font-medium">
                {{ fmt(data.transport_name) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Volume BBM
              </p>
              <p class="font-semibold text-primary">
                {{ formatNumber(data.fuel_total ?? 0) }} L
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Dibuat
              </p>
              <p class="font-medium">
                {{ fmtDateTime(data.created_at) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Diperbarui
              </p>
              <p class="font-medium">
                {{ fmtDateTime(data.updated_at) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                ID
              </p>
              <p class="font-mono text-xs text-muted truncate">
                {{ data.id }}
              </p>
            </div>
          </div>

          <!-- ── Informasi Purchase Order (parent) ── -->
          <div class="border-t border-default pt-3">
            <div class="flex items-center justify-between mb-3">
              <p
                class="text-xs font-semibold text-muted uppercase tracking-wide"
              >
                Purchase Order
              </p>
            </div>

            <!-- Loading -->
            <div v-if="doRelatedPoPending" class="space-y-2">
              <USkeleton v-for="i in 2" :key="i" class="h-12 rounded-lg" />
            </div>

            <!-- Tidak ada PO -->
            <p v-else-if="!doRelatedPo" class="text-sm text-dimmed">
              Tidak ada Purchase Order terkait Delivery Order ini.
            </p>

            <!-- Detail PO -->
            <div
              v-else
              class="rounded-lg border border-default p-3 space-y-3"
            >
              <div class="flex flex-wrap items-center gap-2">
                <UIcon name="i-lucide-shopping-cart" class="size-4 text-primary shrink-0" />
                <p class="font-semibold">
                  {{ fmt(doRelatedPo.po_number) }}
                </p>
                <UBadge
                  :color="doRelatedPo.type === 'customer' ? 'info' : 'warning'"
                  variant="subtle"
                  class="ml-auto capitalize"
                >
                  {{ doRelatedPo.type }}
                </UBadge>
              </div>

              <div class="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
                <div>
                  <p class="text-muted">
                    Customer
                  </p>
                  <p class="font-medium truncate">
                    {{ fmt(doRelatedPo.customer_name) }}
                  </p>
                </div>
                <div>
                  <p class="text-muted">
                    Supplier
                  </p>
                  <p
                    class="font-medium truncate"
                    :class="doRelatedPo.supplier_name ? '' : 'text-muted'"
                  >
                    {{
                      doRelatedPo.supplier_name
                        ? fmt(doRelatedPo.supplier_name)
                        : '- (Purchase Order Customer, tanpa supplier)'
                    }}
                  </p>
                </div>
                <div>
                  <p class="text-muted">
                    Tanggal Purchase Order
                  </p>
                  <p class="font-medium">
                    {{ fmt(doRelatedPo.date) }}
                  </p>
                </div>
                <div>
                  <p class="text-muted">
                    Total Purchase Order
                  </p>
                  <p class="font-medium text-primary">
                    {{ fmtCurrency(doRelatedPo.total) }}
                  </p>
                </div>
                <div>
                  <p class="text-muted">
                    Status
                  </p>
                  <p class="font-medium capitalize">
                    {{ fmt(doRelatedPo.status) }}
                  </p>
                </div>
                <div>
                  <p class="text-muted">
                    Dibuat
                  </p>
                  <p class="font-medium">
                    {{ fmtDateTime(doRelatedPo.created_at) }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Status alur pengiriman -->
          <div class="border-t border-default pt-3">
            <p
              class="text-xs font-semibold text-muted uppercase tracking-wide mb-3"
            >
              Status Alur Pengiriman
            </p>
            <div class="grid grid-cols-2 gap-3">
              <div class="rounded-lg border border-default p-3 space-y-1">
                <div class="flex items-center gap-2">
                  <UIcon
                    name="i-lucide-package"
                    class="size-4 shrink-0"
                    :class="
                      data.status_ready_order ? 'text-info' : 'text-muted'
                    "
                  />
                  <p class="text-xs font-medium">
                    Siap Kirim
                  </p>
                  <UBadge
                    :color="data.status_ready_order ? 'info' : 'neutral'"
                    variant="subtle"
                    class="ml-auto text-xs"
                  >
                    {{ data.status_ready_order ? "Siap" : "-" }}
                  </UBadge>
                </div>
                <p v-if="data.ready_order_at" class="text-xs text-muted pl-6">
                  {{ fmtDateTime(data.ready_order_at) }}
                </p>
              </div>
              <div class="rounded-lg border border-default p-3 space-y-1">
                <div class="flex items-center gap-2">
                  <UIcon
                    name="i-lucide-check-circle"
                    class="size-4 shrink-0"
                    :class="
                      data.status_selesai_dikirim
                        ? 'text-success'
                        : 'text-muted'
                    "
                  />
                  <p class="text-xs font-medium">
                    Selesai Dikirim
                  </p>
                  <UBadge
                    :color="data.status_selesai_dikirim ? 'success' : 'neutral'"
                    variant="subtle"
                    class="ml-auto text-xs"
                  >
                    {{ data.status_selesai_dikirim ? "Selesai" : "-" }}
                  </UBadge>
                </div>
                <p
                  v-if="data.selesai_dikirim_at"
                  class="text-xs text-muted pl-6"
                >
                  {{ fmtDateTime(data.selesai_dikirim_at) }}
                </p>
              </div>
              <div class="rounded-lg border border-default p-3 space-y-1">
                <div class="flex items-center gap-2">
                  <UIcon
                    name="i-lucide-truck"
                    class="size-4 shrink-0"
                    :class="
                      data.status_lunas_ongkir ? 'text-success' : 'text-muted'
                    "
                  />
                  <p class="text-xs font-medium">
                    Lunas Ongkir
                  </p>
                  <UBadge
                    :color="data.status_lunas_ongkir ? 'success' : 'neutral'"
                    variant="subtle"
                    class="ml-auto text-xs"
                  >
                    {{ data.status_lunas_ongkir ? "Lunas" : "-" }}
                  </UBadge>
                </div>
                <p v-if="data.lunas_ongkir_at" class="text-xs text-muted pl-6">
                  {{ fmtDateTime(data.lunas_ongkir_at) }}
                </p>
              </div>
            </div>
          </div>

          <!-- Catatan Pengiriman -->
          <div
            v-if="
              doDetails
                && (doDetails.t2Depot
                  || doDetails.t2Unloading
                  || doDetails.indexSensitivity
                  || doDetails.fuelReceived)
            "
            class="border-t border-default pt-3"
          >
            <p
              class="text-xs font-semibold text-muted uppercase tracking-wide mb-3"
            >
              Catatan Pengiriman
            </p>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <p class="text-xs text-muted">
                  T2 Depo
                </p>
                <p class="font-medium">
                  {{ doDetails.t2Depot ?? '-' }}
                </p>
              </div>
              <div>
                <p class="text-xs text-muted">
                  T2 Bongkar
                </p>
                <p class="font-medium">
                  {{ doDetails.t2Unloading ?? '-' }}
                </p>
              </div>
              <div>
                <p class="text-xs text-muted">
                  Kepekaan Index
                </p>
                <p class="font-medium">
                  {{ doDetails.indexSensitivity ?? '-' }}
                </p>
              </div>
              <div>
                <p class="text-xs text-muted">
                  BBM Diterima
                </p>
                <p class="font-medium">
                  {{ doDetails.fuelReceived ?? '-' }} L
                </p>
              </div>
            </div>
          </div>

          <!-- Catatan Tambahan -->
          <div
            v-if="doDetails?.notes?.length"
            class="border-t border-default pt-3"
          >
            <p
              class="text-xs font-semibold text-muted uppercase tracking-wide mb-2"
            >
              Catatan Tambahan
            </p>
            <ul class="space-y-1.5 list-disc pl-4 text-sm">
              <li v-for="(note, i) in doDetails.notes" :key="i">
                {{ note.note || '-' }}
              </li>
            </ul>
          </div>
        </div>

        <!-- ── Invoice ── -->
        <div v-else-if="type === 'invoice' && data" class="space-y-4 text-sm">
          <div class="grid grid-cols-2 gap-x-6 gap-y-3">
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Nomor Invoice
              </p>
              <p class="font-semibold">
                {{ fmt(data.invoice_number) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Status Bayar
              </p>
              <UBadge
                :color="invStatusColor[data.invoice_status] ?? 'neutral'"
                variant="subtle"
              >
                {{
                  statusLabel(data.invoice_status)
                }}
              </UBadge>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Customer
              </p>
              <p class="font-medium">
                {{ fmt(data.customer_name) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Status Tenggat
              </p>
              <UBadge
                :color="deadlineColor[data.deadline_status] ?? 'neutral'"
                variant="subtle"
              >
                {{
                  statusLabel(data.deadline_status)
                }}
              </UBadge>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Grand Total
              </p>
              <p class="font-semibold text-primary text-base">
                {{ fmtCurrency(data.grand_total) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Terms
              </p>
              <p class="font-medium">
                {{ fmt(data.terms_day) }} hari
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Dibuat
              </p>
              <p class="font-medium">
                {{ fmtDateTime(data.created_at) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                Diperbarui
              </p>
              <p class="font-medium">
                {{ fmtDateTime(data.updated_at) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted uppercase tracking-wide mb-0.5">
                ID
              </p>
              <p class="font-mono text-xs text-muted truncate">
                {{ data.id }}
              </p>
            </div>
          </div>
        </div>

        <UEmpty v-else icon="i-lucide-file-x" title="Data tidak ditemukan" />

        <!-- ── Lampiran / File Terkait ── -->
        <div class="mt-5 border-t border-default pt-4">
          <p
            class="text-xs font-semibold text-muted uppercase tracking-wide mb-3"
          >
            {{
              type === 'ol'
                ? 'Lampiran Surat Penawaran'
                : type === 'po'
                  ? 'Lampiran Purchase Order'
                  : type === 'do'
                    ? 'Lampiran Delivery Order'
                    : 'Lampiran Invoice'
            }}
          </p>

          <!-- Loading files -->
          <div v-if="uploadsPending" class="space-y-2">
            <USkeleton v-for="i in 2" :key="i" class="h-12 rounded-lg" />
          </div>

          <!-- No files -->
          <p v-else-if="!uploads?.length" class="text-sm text-dimmed">
            Tidak ada file lampiran untuk dokumen ini.
          </p>

          <!-- File list -->
          <div v-else class="space-y-2">
            <div
              v-for="file in uploads"
              :key="file.id"
              class="flex items-center justify-between gap-3 rounded-lg border border-default bg-muted/30 px-3 py-2.5"
            >
              <div class="flex items-center gap-2.5 min-w-0">
                <UIcon
                  :name="fileIcon(file.mime_type)"
                  class="size-5 shrink-0 text-primary"
                />
                <div class="min-w-0">
                  <p class="text-sm font-medium truncate">
                    {{ file.original_filename }}
                  </p>
                  <p class="text-xs text-muted">
                    {{ fmtSize(file.size) }} · {{ file.mime_type }}
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-1.5 shrink-0">
                <!-- Lihat (redirect ke halaman lampiran) -->
                <UButton
                  icon="i-lucide-eye"
                  size="xs"
                  color="neutral"
                  variant="ghost"
                  :to="`/lampiran/${file.id}`"
                  aria-label="Lihat file"
                />
                <!-- Download -->
                <UButton
                  icon="i-lucide-download"
                  size="xs"
                  color="primary"
                  variant="ghost"
                  aria-label="Unduh file"
                  @click="downloadFile(file)"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- ── Lampiran Purchase Order Customer ── -->
        <div
          v-if="type === 'ol'"
          class="mt-5 border-t border-default pt-4"
        >
          <p
            class="text-xs font-semibold text-muted uppercase tracking-wide mb-3"
          >
            Lampiran Purchase Order Customer
          </p>

          <!-- Loading PO -->
          <div v-if="relatedPosPending" class="space-y-2">
            <USkeleton v-for="i in 1" :key="i" class="h-12 rounded-lg" />
          </div>

          <!-- Loading files PO -->
          <div v-else-if="poUploadsPending" class="space-y-2">
            <USkeleton v-for="i in 2" :key="i" class="h-12 rounded-lg" />
          </div>

          <!-- No PO -->
          <p v-else-if="!relatedPos?.length" class="text-sm text-dimmed">
            Tidak ada Purchase Order Customer untuk surat penawaran ini.
          </p>

          <!-- No files PO -->
          <p v-else-if="!poUploads?.length" class="text-sm text-dimmed">
            Tidak ada file lampiran untuk Purchase Order Customer ini.
          </p>

          <!-- File list PO -->
          <div v-else class="space-y-2">
            <div
              v-for="file in poUploads"
              :key="file.id"
              class="flex items-center justify-between gap-3 rounded-lg border border-default bg-muted/30 px-3 py-2.5"
            >
              <div class="flex items-center gap-2.5 min-w-0">
                <UIcon
                  :name="fileIcon(file.mime_type)"
                  class="size-5 shrink-0 text-primary"
                />
                <div class="min-w-0">
                  <p class="text-sm font-medium truncate">
                    {{ file.original_filename }}
                  </p>
                  <p class="text-xs text-muted">
                    {{ fmtSize(file.size) }} · {{ file.mime_type }}
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-1.5 shrink-0">
                <!-- Lihat (redirect ke halaman lampiran) -->
                <UButton
                  icon="i-lucide-eye"
                  size="xs"
                  color="neutral"
                  variant="ghost"
                  :to="`/lampiran/${file.id}`"
                  aria-label="Lihat file"
                />
                <!-- Download -->
                <UButton
                  icon="i-lucide-download"
                  size="xs"
                  color="primary"
                  variant="ghost"
                  aria-label="Unduh file"
                  @click="downloadFile(file)"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- ── Lampiran Terkait (PO & Surat Penawaran) untuk DO ── -->
        <div
          v-if="type === 'do'"
          class="mt-5 border-t border-default pt-4"
        >
          <p
            class="text-xs font-semibold text-muted uppercase tracking-wide mb-3"
          >
            Lampiran Purchase Order & Surat Penawaran
          </p>

          <!-- Loading -->
          <div v-if="doRelatedPoPending || doRelatedUploadsPending" class="space-y-2">
            <USkeleton v-for="i in 2" :key="i" class="h-12 rounded-lg" />
          </div>

          <!-- PO tidak ditemukan -->
          <p v-else-if="!doRelatedPo" class="text-sm text-dimmed">
            Tidak ada Purchase Order terkait Delivery Order ini.
          </p>

          <!-- Tidak ada file -->
          <p v-else-if="!doRelatedUploads?.length" class="text-sm text-dimmed">
            Tidak ada file lampiran untuk Purchase Order atau Surat Penawaran terkait.
          </p>

          <!-- File list -->
          <div v-else class="space-y-2">
            <div
              v-for="file in doRelatedUploads"
              :key="file.id"
              class="flex items-center justify-between gap-3 rounded-lg border border-default bg-muted/30 px-3 py-2.5"
            >
              <div class="flex items-center gap-2.5 min-w-0">
                <UIcon
                  :name="fileIcon(file.mime_type)"
                  class="size-5 shrink-0 text-primary"
                />
                <div class="min-w-0">
                  <p class="text-sm font-medium truncate">
                    {{ file.original_filename }}
                  </p>
                  <p class="text-xs text-muted">
                    {{ fmtSize(file.size) }} · {{ file.mime_type }}
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-1.5 shrink-0">
                <!-- Lihat (redirect ke halaman lampiran) -->
                <UButton
                  icon="i-lucide-eye"
                  size="xs"
                  color="neutral"
                  variant="ghost"
                  :to="`/lampiran/${file.id}`"
                  aria-label="Lihat file"
                />
                <!-- Download -->
                <UButton
                  icon="i-lucide-download"
                  size="xs"
                  color="primary"
                  variant="ghost"
                  aria-label="Unduh file"
                  @click="downloadFile(file)"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- ── Lampiran Terkait (DO, PO & Surat Penawaran) untuk Invoice ── -->
        <div
          v-if="type === 'invoice'"
          class="mt-5 border-t border-default pt-4"
        >
          <p
            class="text-xs font-semibold text-muted uppercase tracking-wide mb-3"
          >
            Lampiran Delivery Order & Surat Penawaran
          </p>

          <!-- Loading -->
          <div v-if="invoiceRelatedDosPending || invoiceRelatedUploadsPending" class="space-y-2">
            <USkeleton v-for="i in 2" :key="i" class="h-12 rounded-lg" />
          </div>

          <!-- DO tidak ditemukan -->
          <p v-else-if="!invoiceRelatedDos?.length" class="text-sm text-dimmed">
            Tidak ada Delivery Order terkait Invoice ini.
          </p>

          <!-- Tidak ada file -->
          <p v-else-if="!invoiceRelatedUploads?.length" class="text-sm text-dimmed">
            Tidak ada file lampiran untuk Delivery Order atau Surat Penawaran terkait.
          </p>

          <!-- File list -->
          <div v-else class="space-y-2">
            <div
              v-for="file in invoiceRelatedUploads"
              :key="file.id"
              class="flex items-center justify-between gap-3 rounded-lg border border-default bg-muted/30 px-3 py-2.5"
            >
              <div class="flex items-center gap-2.5 min-w-0">
                <UIcon
                  :name="fileIcon(file.mime_type)"
                  class="size-5 shrink-0 text-primary"
                />
                <div class="min-w-0">
                  <p class="text-sm font-medium truncate">
                    {{ file.original_filename }}
                  </p>
                  <p class="text-xs text-muted">
                    {{ fmtSize(file.size) }} · {{ file.mime_type }}
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-1.5 shrink-0">
                <!-- Lihat (redirect ke halaman lampiran) -->
                <UButton
                  icon="i-lucide-eye"
                  size="xs"
                  color="neutral"
                  variant="ghost"
                  :to="`/lampiran/${file.id}`"
                  aria-label="Lihat file"
                />
                <!-- Download -->
                <UButton
                  icon="i-lucide-download"
                  size="xs"
                  color="primary"
                  variant="ghost"
                  aria-label="Unduh file"
                  @click="downloadFile(file)"
                />
              </div>
            </div>
          </div>
        </div>
      </template>
    </template>
  </UModal>
</template>
