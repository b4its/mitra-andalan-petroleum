<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'

const props = defineProps<{
  open: boolean
  metric?: {
    key: string
    title: string
    value: number
    unit: string
    description: string
  }
  dateFrom: string
  dateTo: string
}>()

const emit = defineEmits<{ 'update:open': [value: boolean] }>()

const page = ref(1)
const search = ref('')
const { get } = useApi()
const UBadge = resolveComponent('UBadge')

const { data, pending, error, refresh } = await useAsyncData(
  () =>
    `admin-drilldown-${props.metric?.key}-${props.dateFrom}-${props.dateTo}-${page.value}`,
  () => {
    if (!props.metric?.key) return Promise.resolve(null)
    return get<any>('/stats/admin/drilldown', {
      metric: props.metric.key,
      date_from: props.dateFrom,
      date_to: props.dateTo,
      page: page.value,
      page_size: 50 // load lebih banyak untuk search frontend
    })
  },
  {
    watch: [
      () => props.metric?.key,
      () => props.dateFrom,
      () => props.dateTo,
      page
    ]
  }
)

watch(
  () => props.open,
  (open) => {
    if (open) {
      page.value = 1
      search.value = ''
      refresh()
    }
  }
)

// ── Search frontend ────────────────────────────────────────────
const filteredItems = computed(() => {
  const items: any[] = data.value?.items || []
  const q = search.value.trim().toLowerCase()
  if (!q) return items
  return items.filter(
    item =>
      item.title?.toLowerCase().includes(q)
      || item.subtitle?.toLowerCase().includes(q)
      || item.status?.toLowerCase().includes(q)
  )
})

// ── Subtotal dari item yang tampil ─────────────────────────────
const hasValueColumn = computed(() => {
  const key = props.metric?.key ?? ''
  return [
    'offering_letters',
    'customer_purchase_orders',
    'supplier_purchase_orders',
    'delivery_orders',
    'fuel_volume',
    'invoice_value',
    'paid_value',
    'outstanding_value',
    'overdue_value',
    'sales_value'
  ].includes(key)
})

const filteredSubtotal = computed(() => {
  if (!hasValueColumn.value) return 0
  return filteredItems.value.reduce(
    (sum, item) => sum + (Number(item.value) || 0),
    0
  )
})

// ── Total value summary ────────────────────────────────────────
function formatSummaryValue(value: number) {
  if (props.metric?.unit === 'currency') return formatCurrency(value)
  if (props.metric?.unit === 'volume') return `${formatNumber(value)} L`
  return formatNumber(value)
}

// ── Kolom dinamis per metric ──────────────────────────────────
const statusColors: Record<
  string,
  Record<string, 'neutral' | 'success' | 'warning' | 'error' | 'info'>
> = {
  offering_letter: {
    created: 'info',
    under_revision: 'warning',
    po_received: 'success'
  },
  purchase_order: { created: 'info', approved: 'success', rejected: 'error' },
  delivery_order: { created: 'info', document_returned: 'success' },
  invoice: { unpaid: 'warning', paid: 'success', overdue: 'error' },
  deadline: { on_time: 'info', due_soon: 'warning', overdue: 'error' },
  sale: { paid: 'success', failed: 'error', refunded: 'warning' },
  notification: {
    info: 'info',
    success: 'success',
    warning: 'warning',
    error: 'error'
  },
  user: {
    admin: 'neutral',
    marketing: 'info',
    operations: 'warning',
    finance: 'success'
  }
}

function statusBadge(status: string, group: string) {
  const map = statusColors[group] || {}
  const color = map[status] ?? 'neutral'
  return h(
    UBadge,
    { variant: 'subtle', color, class: 'capitalize' },
    () => status?.replace(/_/g, ' ') ?? '-'
  )
}

const columns = computed((): TableColumn<any>[] => {
  const key = props.metric?.key ?? ''

  // ── Customers ────────────────────────────────────────────────
  if (key === 'customers')
    return [
      { accessorKey: 'title', header: 'Nama Customer' },
      {
        accessorKey: 'created_at',
        header: 'Terdaftar',
        cell: ({ row }) =>
          row.getValue('created_at')
            ? formatDate(row.getValue('created_at'))
            : '-'
      }
    ]

  // ── Suppliers ────────────────────────────────────────────────
  if (key === 'suppliers')
    return [
      { accessorKey: 'title', header: 'Nama Supplier' },
      {
        accessorKey: 'created_at',
        header: 'Terdaftar',
        cell: ({ row }) =>
          row.getValue('created_at')
            ? formatDate(row.getValue('created_at'))
            : '-'
      }
    ]

  // ── Users / Profiles ─────────────────────────────────────────
  if (key === 'users')
    return [
      { accessorKey: 'title', header: 'Nama' },
      {
        accessorKey: 'status',
        header: 'Peran',
        cell: ({ row }) => statusBadge(row.getValue('status') ?? '', 'user')
      },
      {
        accessorKey: 'created_at',
        header: 'Dibuat',
        cell: ({ row }) =>
          row.getValue('created_at')
            ? formatDate(row.getValue('created_at'))
            : '-'
      }
    ]

  // ── Offering Letters ─────────────────────────────────────────
  if (key === 'offering_letters')
    return [
      { accessorKey: 'title', header: 'Nomor Surat' },
      // { accessorKey: "subtitle", header: "Customer" },
      {
        accessorKey: 'value',
        header: 'Nilai Penawaran',
        cell: ({ row }) => formatCurrency(row.getValue('value') ?? 0)
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) =>
          statusBadge(row.getValue('status') ?? '', 'offering_letter')
      },
      {
        accessorKey: 'created_at',
        header: 'Dibuat',
        cell: ({ row }) =>
          row.getValue('created_at')
            ? formatDate(row.getValue('created_at'))
            : '-'
      }
    ]

  // ── Purchase Order Customer & Purchase Order Supplier ────────────────────────────────
  if (key === 'customer_purchase_orders' || key === 'supplier_purchase_orders')
    return [
      { accessorKey: 'title', header: 'Nomor Purchase Order' },
      // {
      //   accessorKey: "subtitle",
      //   header: key === "customer_purchase_orders" ? "Customer" : "Supplier",
      // },
      {
        accessorKey: 'value',
        header: 'Nilai Purchase Order',
        cell: ({ row }) => formatCurrency(row.getValue('value') ?? 0)
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) =>
          statusBadge(row.getValue('status') ?? '', 'purchase_order')
      },
      {
        accessorKey: 'created_at',
        header: 'Dibuat',
        cell: ({ row }) =>
          row.getValue('created_at')
            ? formatDate(row.getValue('created_at'))
            : '-'
      }
    ]

  // ── Delivery Orders & Fuel Volume ────────────────────────────
  if (key === 'delivery_orders' || key === 'fuel_volume')
    return [
      { accessorKey: 'title', header: 'Nomor Delivery Order' },
      // { accessorKey: "subtitle", header: "Transportir" },
      {
        accessorKey: 'value',
        header: 'Volume (L)',
        cell: ({ row }) => formatNumber(row.getValue('value') ?? 0)
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) =>
          statusBadge(row.getValue('status') ?? '', 'delivery_order')
      },
      {
        accessorKey: 'created_at',
        header: 'Dibuat',
        cell: ({ row }) =>
          row.getValue('created_at')
            ? formatDate(row.getValue('created_at'))
            : '-'
      }
    ]

  // ── Invoice Value / Paid / Outstanding / Overdue ─────────────
  if (
    [
      'invoice_value',
      'paid_value',
      'outstanding_value',
      'overdue_value'
    ].includes(key)
  )
    return [
      { accessorKey: 'title', header: 'Nomor Invoice' },
      // { accessorKey: "subtitle", header: "Customer" },
      {
        accessorKey: 'value',
        header: 'Total Keseluruhan',
        cell: ({ row }) => formatCurrency(row.getValue('value') ?? 0)
      },
      {
        accessorKey: 'status',
        header: 'Status Bayar',
        cell: ({ row }) => statusBadge(row.getValue('status') ?? '', 'invoice')
      },
      {
        accessorKey: 'created_at',
        header: 'Dibuat',
        cell: ({ row }) =>
          row.getValue('created_at')
            ? formatDate(row.getValue('created_at'))
            : '-'
      }
    ]

  // ── Sales ─────────────────────────────────────────────────────
  if (key === 'sales_value')
    return [
      { accessorKey: 'title', header: 'Email' },
      {
        accessorKey: 'value',
        header: 'Jumlah Transaksi',
        cell: ({ row }) => formatCurrency(row.getValue('value') ?? 0)
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => statusBadge(row.getValue('status') ?? '', 'sale')
      },
      {
        accessorKey: 'created_at',
        header: 'Tanggal',
        cell: ({ row }) =>
          row.getValue('created_at')
            ? formatDate(row.getValue('created_at'))
            : '-'
      }
    ]

  // ── Notifikasi belum dibaca ───────────────────────────────────
  if (key === 'unread_notifications')
    return [
      { accessorKey: 'title', header: 'Judul' },
      { accessorKey: 'subtitle', header: 'Pesan' },
      {
        accessorKey: 'status',
        header: 'Tipe',
        cell: ({ row }) =>
          statusBadge(row.getValue('status') ?? '', 'notification')
      },
      {
        accessorKey: 'created_at',
        header: 'Waktu',
        cell: ({ row }) =>
          row.getValue('created_at')
            ? formatDate(row.getValue('created_at'))
            : '-'
      }
    ]

  // ── Uploads ───────────────────────────────────────────────────
  if (key === 'uploads')
    return [
      { accessorKey: 'title', header: 'Nama File' },
      { accessorKey: 'subtitle', header: 'Keterangan' },
      {
        accessorKey: 'status',
        header: 'Tipe Dokumen',
        cell: ({ row }) =>
          h(
            UBadge,
            { variant: 'soft', color: 'neutral' },
            () => row.getValue('status') ?? '-'
          )
      },
      {
        accessorKey: 'value',
        header: 'Ukuran (bytes)',
        cell: ({ row }) =>
          row.getValue('value') ? formatNumber(row.getValue('value')) : '-'
      },
      {
        accessorKey: 'created_at',
        header: 'Diupload',
        cell: ({ row }) =>
          row.getValue('created_at')
            ? formatDate(row.getValue('created_at'))
            : '-'
      }
    ]

  // ── Fallback ──────────────────────────────────────────────────
  return [
    { accessorKey: 'title', header: 'Data' },
    { accessorKey: 'subtitle', header: 'Keterangan' },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) =>
        row.getValue('status')
          ? h(UBadge, { variant: 'subtle', color: 'neutral' }, () =>
              row.getValue('status')
            )
          : '-'
    },
    {
      accessorKey: 'created_at',
      header: 'Dibuat',
      cell: ({ row }) =>
        row.getValue('created_at')
          ? formatDate(row.getValue('created_at'))
          : '-'
    }
  ]
})

// ── Search placeholder per metric ─────────────────────────────
const searchPlaceholder = computed(() => {
  const key = props.metric?.key ?? ''
  if (key === 'customers') return 'Cari nama customer...'
  if (key === 'suppliers') return 'Cari nama supplier...'
  if (key === 'users') return 'Cari nama atau role...'
  if (key === 'offering_letters') return 'Cari nomor Surat Penawaran atau customer...'
  if (key === 'customer_purchase_orders' || key === 'supplier_purchase_orders')
    return 'Cari nomor Purchase Order...'
  if (key === 'delivery_orders' || key === 'fuel_volume')
    return 'Cari nomor Delivery Order atau transportir...'
  if (
    [
      'invoice_value',
      'paid_value',
      'outstanding_value',
      'overdue_value'
    ].includes(key)
  )
    return 'Cari nomor invoice atau customer...'
  if (key === 'sales_value') return 'Cari email atau status...'
  if (key === 'unread_notifications') return 'Cari judul atau pesan...'
  if (key === 'uploads') return 'Cari nama file...'
  return 'Cari data...'
})
</script>

<template>
  <UModal
    :open="open"
    :ui="{ content: 'max-w-3xl' }"
    @update:open="emit('update:open', $event)"
  >
    <template #title>
      <div class="flex items-center gap-2">
        <UIcon
          v-if="metric?.key"
          name="i-lucide-table-2"
          class="size-4 text-primary"
        />
        {{ metric?.title ?? "Rincian Data" }}
      </div>
    </template>

    <template #body>
      <div v-if="metric" class="space-y-4">
        <!-- Summary metric -->
        <div class="rounded-lg bg-muted/50 p-4 space-y-1">
          <div class="flex items-center justify-between">
            <p class="text-sm font-medium text-highlighted">
              {{ metric.title }}
            </p>
            <p class="text-2xl font-semibold tabular-nums text-primary">
              {{ formatSummaryValue(metric.value) }}
            </p>
          </div>
          <p class="text-xs text-muted">
            {{ metric.description }}
          </p>
          <p class="text-xs text-dimmed">
            Periode: {{ formatDate(dateFrom) }} — {{ formatDate(dateTo) }}
          </p>
          <!-- Total value dari backend jika tersedia -->
          <p
            v-if="data?.total_value && data.total_value !== metric.value"
            class="text-xs text-muted pt-1 border-t border-default mt-2"
          >
            Total pada halaman ini:
            <span class="font-medium text-highlighted">{{
              formatSummaryValue(data.total_value)
            }}</span>
          </p>
        </div>

        <!-- Error -->
        <UAlert
          v-if="error"
          color="error"
          title="Gagal memuat rincian"
          :description="error.message"
        />

        <!-- Skeleton -->
        <div v-else-if="pending" class="space-y-3">
          <USkeleton class="h-8 w-full rounded" />
          <USkeleton class="h-40 w-full rounded" />
        </div>

        <template v-else>
          <!-- Header: search + jumlah record -->
          <div class="flex flex-wrap items-center justify-between gap-3">
            <UInput
              v-model="search"
              icon="i-lucide-search"
              :placeholder="searchPlaceholder"
              size="sm"
              class="w-64"
            />
            <span class="text-xs text-muted">
              {{ filteredItems.length }} dari {{ data?.total || 0 }} record
            </span>
          </div>

          <!-- Tabel kolom dinamis -->
          <UTable :data="filteredItems" :columns="columns" />

          <!-- Subtotal nilai dari item yang tampil -->
          <div
            v-if="hasValueColumn && filteredItems.length > 0"
            class="flex items-center justify-between rounded-lg bg-muted/40 px-4 py-2 text-sm"
          >
            <span class="text-muted">
              Subtotal
              {{
                search
                  ? `(${filteredItems.length} hasil pencarian)`
                  : `(${filteredItems.length} record)`
              }}
            </span>
            <span class="font-semibold tabular-nums text-highlighted">
              {{ formatSummaryValue(filteredSubtotal) }}
            </span>
          </div>

          <UEmpty
            v-if="!filteredItems.length"
            icon="i-lucide-search-x"
            title="Tidak ada data"
            description="Coba ubah kata kunci pencarian."
          />

          <!-- Pagination (server-side untuk load lebih banyak) -->
          <div
            v-if="(data?.total || 0) > 50"
            class="flex items-center justify-between border-t border-default pt-3"
          >
            <p class="text-xs text-muted">
              {{ data?.total }} total record
            </p>
            <UPagination
              v-model:page="page"
              :total="data.total"
              :items-per-page="50"
            />
          </div>
        </template>
      </div>
    </template>
  </UModal>
</template>
