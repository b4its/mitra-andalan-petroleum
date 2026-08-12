<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import AdminBarChart from '~/components/admin/charts/AdminBarChart.vue'
import AdminPieChart from '~/components/admin/charts/AdminPieChart.vue'
import type { ChartClickPayload } from '~/components/admin/AdminChartDetailModal.vue'
import type {
  AdminDeliveryOrderRow,
  AdminDrilldownMetric,
  AdminInvoiceRow,
  AdminStats,
  Paginated
} from '~/types/admin'

definePageMeta({ layout: 'admin' })

const UBadge = resolveComponent('UBadge')
const { get } = useApi()

// ── Chart modal state ──────────────────────────────────────────
const chartDetailOpen = ref(false)
const chartPayload = ref<ChartClickPayload | null>(null)
const drillMetric = ref<AdminDrilldownMetric | null>(null)
const drillOpen = ref(false)

function onBarClick(p: {
  label: string
  datasetLabel: string
  value: number
  datasetIndex: number
  labelIndex: number
}) {
  chartPayload.value = {
    chartType: 'bar',
    label: p.label,
    datasetLabel: p.datasetLabel,
    value: p.value
  }
  chartDetailOpen.value = true
}
function onPieClick(p: { label: string, value: number, index: number }) {
  chartPayload.value = {
    chartType: 'pie',
    segmentLabel: p.label,
    segmentValue: p.value
  }
  chartDetailOpen.value = true
}
function onChartViewRecords(metric: AdminDrilldownMetric) {
  drillMetric.value = metric
  drillOpen.value = true
}

// ── Data fetch ────────────────────────────────────────────────
const { data, pending, refresh } = useAsyncData(
  'admin-finance',
  async () => {
    const [stats, invResult, doResult] = await Promise.all([
      get<AdminStats>('/stats/admin'),
      get<Paginated<AdminInvoiceRow>>('/invoices', { page: 1, page_size: 100 }),
      get<Paginated<AdminDeliveryOrderRow>>('/delivery-orders', { page: 1, page_size: 100 })
    ])
    return {
      stats,
      invList: invResult?.items || [],
      doList: doResult?.items || []
    }
  },
  {
    default: () => ({ stats: null, invList: [], doList: [] }),
    lazy: true,
    server: false
  }
)

// ── Stats cards ───────────────────────────────────────────────
const invStats = computed(() => {
  if (!data.value?.stats?.metrics) return []
  return data.value.stats.metrics.filter(m =>
    [
      'invoice_value',
      'paid_value',
      'outstanding_value',
      'overdue_value'
    ].includes(m.key)
  )
})

// ── Ringkasan alur DO dari sisi Finance ──────────────────────
const doFinanceStats = computed(() => {
  const list: AdminDeliveryOrderRow[] = data.value?.doList || []
  return {
    belumRilisDana: list.filter(d => !d.status_rilis_dana).length,
    menantiSelesaiKirim: list.filter(
      d => d.status_rilis_dana && !d.status_selesai_dikirim
    ).length,
    menunggakLunas: list.filter(
      d => d.status_selesai_dikirim && !d.status_lunas_ongkir
    ).length,
    sudahLunas: list.filter(d => d.status_lunas_ongkir).length
  }
})

// ── Charts ────────────────────────────────────────────────────
const trendLabels = computed(
  () => data.value?.stats?.trends?.map(t => t.label) || []
)
const invTrendData = computed(
  () => data.value?.stats?.trends?.map(t => t.invoices) || []
)
const invDistLabels = computed(
  () =>
    data.value?.stats?.distributions?.invoices?.map(d => d.label) || []
)
const invDistValues = computed(
  () =>
    data.value?.stats?.distributions?.invoices?.map(d => d.value) || []
)
const deadlineDistLabels = computed(
  () =>
    data.value?.stats?.distributions?.invoice_deadlines?.map(
      d => d.label
    ) || []
)
const deadlineDistValues = computed(
  () =>
    data.value?.stats?.distributions?.invoice_deadlines?.map(
      d => d.value
    ) || []
)

// ── Invoice table: search + pagination ────────────────────────
const invSearch = ref('')
const invStatusFilter = ref('all')
const deadlineStatusFilter = ref('all')
const invPage = ref(1)
const PAGE_SIZE = 7

const invFiltered = computed(() => {
  const q = invSearch.value.trim().toLowerCase()
  let list: AdminInvoiceRow[] = data.value?.invList || []

  if (invStatusFilter.value !== 'all') {
    list = list.filter(inv => inv.invoice_status === invStatusFilter.value)
  }
  if (deadlineStatusFilter.value !== 'all') {
    list = list.filter(
      inv => inv.deadline_status === deadlineStatusFilter.value
    )
  }

  if (!q) return list
  return list.filter(
    inv =>
      inv.invoice_number?.toLowerCase().includes(q)
      || inv.customer_name?.toLowerCase().includes(q)
      || inv.invoice_status?.toLowerCase().includes(q)
      || inv.deadline_status?.toLowerCase().includes(q)
  )
})
const invPaged = computed(() => {
  const start = (invPage.value - 1) * PAGE_SIZE
  return invFiltered.value.slice(start, start + PAGE_SIZE)
})
watch([invSearch, invStatusFilter, deadlineStatusFilter], () => {
  invPage.value = 1
})

// ── DO table: search + pagination ─────────────────────────────
const doSearch = ref('')
const doFlowFilter = ref('all')
const doPage = ref(1)

const doFiltered = computed(() => {
  const q = doSearch.value.trim().toLowerCase()
  let list: AdminDeliveryOrderRow[] = data.value?.doList || []

  if (doFlowFilter.value === 'belum_rilis')
    list = list.filter(d => !d.status_rilis_dana)
  else if (doFlowFilter.value === 'menanti_selesai')
    list = list.filter(d => d.status_rilis_dana && !d.status_selesai_dikirim)
  else if (doFlowFilter.value === 'menunggu_lunas')
    list = list.filter(
      d => d.status_selesai_dikirim && !d.status_lunas_ongkir
    )
  else if (doFlowFilter.value === 'lunas')
    list = list.filter(d => d.status_lunas_ongkir)

  if (!q) return list
  return list.filter(
    d =>
      d.do_number?.toLowerCase().includes(q)
      || d.customer_name?.toLowerCase().includes(q)
      || d.po_number?.toLowerCase().includes(q)
  )
})
const doPaged = computed(() => {
  const start = (doPage.value - 1) * PAGE_SIZE
  return doFiltered.value.slice(start, start + PAGE_SIZE)
})
watch([doSearch, doFlowFilter], () => {
  doPage.value = 1
})

// ── Status helpers ────────────────────────────────────────────
const invStatusLabel: Record<string, string> = {
  unpaid: 'Belum Lunas',
  paid: 'Lunas',
  overdue: 'Jatuh Tempo'
}
const invStatusColor: Record<string, string> = {
  unpaid: 'warning',
  paid: 'success',
  overdue: 'error'
}
const deadlineLabel: Record<string, string> = {
  on_time: 'Tepat Waktu',
  due_soon: 'Segera Jatuh Tempo',
  overdue: 'Terlewat'
}
const deadlineColor: Record<string, string> = {
  on_time: 'info',
  due_soon: 'warning',
  overdue: 'error'
}
const invStatusOptions = [
  { label: 'Semua Pembayaran', value: 'all' },
  { label: 'Belum Lunas', value: 'unpaid' },
  { label: 'Lunas', value: 'paid' },
  { label: 'Jatuh Tempo', value: 'overdue' }
]
const deadlineStatusOptions = [
  { label: 'Semua Tenggat', value: 'all' },
  { label: 'Tepat Waktu', value: 'on_time' },
  { label: 'Segera Jatuh Tempo', value: 'due_soon' },
  { label: 'Terlewat', value: 'overdue' }
]
const doFlowOptions = [
  { label: 'Semua Alur Delivery Order', value: 'all' },
  { label: 'Belum Rilis Dana', value: 'belum_rilis' },
  { label: 'Menanti Selesai Kirim', value: 'menanti_selesai' },
  { label: 'Menunggu Lunas Ongkir', value: 'menunggu_lunas' },
  { label: 'Ongkir Lunas', value: 'lunas' }
]

function alurBadge(done: boolean, at: string | null) {
  return h('div', { class: 'flex flex-col gap-0.5' }, [
    h(
      UBadge,
      {
        variant: 'subtle',
        color: done ? 'success' : 'neutral',
        class: 'text-xs'
      },
      () => (done ? '✓' : '-')
    ),
    done && at
      ? h('span', { class: 'text-[10px] text-muted' }, formatDate(at))
      : null
  ])
}

const invColumns: TableColumn<AdminInvoiceRow>[] = [
  { accessorKey: 'invoice_number', header: 'Nomor Invoice' },
  { accessorKey: 'customer_name', header: 'Customer' },
  {
    accessorKey: 'grand_total',
    header: 'Total Keseluruhan',
    cell: ({ row }) => formatCurrency(row.getValue('grand_total') ?? 0)
  },
  {
    accessorKey: 'invoice_status',
    header: 'Status Bayar',
    cell: ({ row }) => {
      const s = row.getValue('invoice_status') as string
      return h(
        UBadge,
        { variant: 'subtle', color: invStatusColor[s] ?? 'neutral' },
        () => invStatusLabel[s] ?? s
      )
    }
  },
  {
    accessorKey: 'deadline_status',
    header: 'Tenggat',
    cell: ({ row }) => {
      const s = row.getValue('deadline_status') as string
      return h(
        UBadge,
        { variant: 'subtle', color: deadlineColor[s] ?? 'neutral' },
        () => deadlineLabel[s] ?? s
      )
    }
  },
  {
    accessorKey: 'created_at',
    header: 'Dibuat',
    cell: ({ row }) =>
      row.getValue('created_at') ? formatDate(row.getValue('created_at')) : '-'
  },
  { id: 'invActions', header: 'Aksi' }
]

const doColumns: TableColumn<AdminDeliveryOrderRow>[] = [
  { accessorKey: 'do_number', header: 'Nomor Delivery Order' },
  { accessorKey: 'customer_name', header: 'Customer' },
  { accessorKey: 'po_number', header: 'Nomor Purchase Order' },
  {
    accessorKey: 'status_rilis_dana',
    header: 'Rilis Dana',
    cell: ({ row }) =>
      alurBadge(row.original.status_rilis_dana, row.original.rilis_dana_at)
  },
  {
    accessorKey: 'status_ready_order',
    header: 'Siap Kirim',
    cell: ({ row }) =>
      alurBadge(row.original.status_ready_order, row.original.ready_order_at)
  },
  {
    accessorKey: 'status_selesai_dikirim',
    header: 'Selesai',
    cell: ({ row }) =>
      alurBadge(
        row.original.status_selesai_dikirim,
        row.original.selesai_dikirim_at
      )
  },
  {
    accessorKey: 'status_lunas_ongkir',
    header: 'Lunas Ongkir',
    cell: ({ row }) =>
      alurBadge(row.original.status_lunas_ongkir, row.original.lunas_ongkir_at)
  },
  {
    accessorKey: 'fuel_total',
    header: 'Volume (L)',
    cell: ({ row }) => formatNumber(row.getValue('fuel_total') ?? 0)
  },
  { id: 'doActions', header: 'Aksi' }
]

const detailOpen = ref(false)
const detailId = ref<string | null>(null)
const detailType = ref<'invoice' | 'do'>('invoice')
function openDetail(id: string, type: 'invoice' | 'do') {
  detailId.value = id
  detailType.value = type
  detailOpen.value = true
}
</script>

<template>
  <UDashboardPanel id="admin-finance">
    <template #header>
      <UDashboardNavbar title="Finance — Rekap" :ui="{ right: 'gap-2' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #right>
          <UButton
            icon="i-lucide-refresh-cw"
            color="neutral"
            variant="ghost"
            @click="refresh()"
          />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="space-y-6 p-4 lg:p-6">
        <!-- Skeleton -->
        <template v-if="pending">
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <USkeleton v-for="i in 4" :key="i" class="h-28 rounded-xl" />
          </div>
          <div class="grid gap-4 sm:grid-cols-4">
            <USkeleton v-for="i in 4" :key="i" class="h-20 rounded-xl" />
          </div>
          <div class="grid gap-6 lg:grid-cols-3">
            <USkeleton class="h-72 rounded-xl" />
            <USkeleton class="h-72 rounded-xl" />
            <USkeleton class="h-72 rounded-xl" />
          </div>
          <USkeleton class="h-64 rounded-xl" />
          <USkeleton class="h-64 rounded-xl" />
        </template>

        <template v-else>
          <!-- Stats invoice -->
          <div
            v-if="invStats.length"
            class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
          >
            <UCard v-for="m in invStats" :key="m.key" variant="subtle">
              <template #leading>
                <UIcon :name="m.icon" class="size-5 text-primary" />
              </template>
              <template #title>
                {{ m.title }}
              </template>
              <p class="text-2xl font-semibold tabular-nums">
                {{ formatCurrency(m.value) }}
              </p>
              <p class="text-xs text-muted mt-1">
                {{ m.description }}
              </p>
            </UCard>
          </div>

          <!-- Ringkasan alur DO dari sisi Finance -->
          <div class="grid gap-3 sm:grid-cols-4">
            <UCard variant="subtle" class="text-center">
              <p class="text-xs text-muted mb-1">
                Belum Rilis Dana
              </p>
              <p class="text-2xl font-bold text-warning">
                {{ doFinanceStats.belumRilisDana }}
              </p>
            </UCard>
            <UCard variant="subtle" class="text-center">
              <p class="text-xs text-muted mb-1">
                Menanti Selesai Kirim
              </p>
              <p class="text-2xl font-bold text-info">
                {{ doFinanceStats.menantiSelesaiKirim }}
              </p>
            </UCard>
            <UCard variant="subtle" class="text-center">
              <p class="text-xs text-muted mb-1">
                Menunggu Lunas Ongkir
              </p>
              <p class="text-2xl font-bold text-amber-500">
                {{ doFinanceStats.menunggakLunas }}
              </p>
            </UCard>
            <UCard variant="subtle" class="text-center">
              <p class="text-xs text-muted mb-1">
                Ongkir Lunas
              </p>
              <p class="text-2xl font-bold text-success">
                {{ doFinanceStats.sudahLunas }}
              </p>
            </UCard>
          </div>

          <!-- Charts -->
          <div class="grid gap-6 lg:grid-cols-3">
            <UCard class="lg:col-span-1">
              <template #header>
                <div class="flex items-center justify-between">
                  <p class="font-medium">
                    Tren Invoice per Periode
                  </p>
                  <p class="text-xs text-muted">
                    Klik bar
                  </p>
                </div>
              </template>
              <AdminBarChart
                v-if="trendLabels.length"
                :labels="trendLabels"
                :datasets="[
                  {
                    label: 'Invoice',
                    data: invTrendData,
                    backgroundColor: 'rgba(239,68,68,0.7)'
                  }
                ]"
                @bar-click="onBarClick"
              />
              <UEmpty
                v-else
                icon="i-lucide-chart-bar"
                title="Belum ada data tren"
              />
            </UCard>
            <UCard>
              <template #header>
                <div class="flex items-center justify-between">
                  <p class="font-medium">
                    Status Pembayaran
                  </p>
                  <p class="text-xs text-muted">
                    Klik segment
                  </p>
                </div>
              </template>
              <AdminPieChart
                v-if="invDistLabels.length"
                :labels="invDistLabels"
                :data="invDistValues"
                @segment-click="onPieClick"
              />
              <UEmpty v-else icon="i-lucide-chart-pie" title="Belum ada data" />
            </UCard>
            <UCard>
              <template #header>
                <div class="flex items-center justify-between">
                  <p class="font-medium">
                    Status Tenggat
                  </p>
                  <p class="text-xs text-muted">
                    Klik segment
                  </p>
                </div>
              </template>
              <AdminPieChart
                v-if="deadlineDistLabels.length"
                :labels="deadlineDistLabels"
                :data="deadlineDistValues"
                :background-color="[
                  'rgba(16,185,129,0.8)',
                  'rgba(245,158,11,0.8)',
                  'rgba(239,68,68,0.8)'
                ]"
                @segment-click="onPieClick"
              />
              <UEmpty v-else icon="i-lucide-clock" title="Belum ada data" />
            </UCard>
          </div>

          <!-- Tabel Invoice -->
          <UCard>
            <template #header>
              <div class="flex items-center justify-between gap-3 flex-wrap">
                <p class="font-medium">
                  Data Invoice
                </p>
                <div class="flex flex-wrap items-center gap-2">
                  <USelect
                    v-model="invStatusFilter"
                    :items="invStatusOptions"
                    value-key="value"
                    size="sm"
                    class="w-44"
                  />
                  <USelect
                    v-model="deadlineStatusFilter"
                    :items="deadlineStatusOptions"
                    value-key="value"
                    size="sm"
                    class="w-48"
                  />
                  <UInput
                    v-model="invSearch"
                    icon="i-lucide-search"
                    placeholder="Cari nomor invoice, customer, status..."
                    size="sm"
                    class="w-64"
                  />
                </div>
              </div>
            </template>
            <UTable :data="invPaged" :columns="invColumns">
              <template #invActions-cell="{ row }">
                <UButton
                  icon="i-lucide-eye"
                  size="xs"
                  color="neutral"
                  variant="soft"
                  @click="openDetail(row.original.id, 'invoice')"
                >
                  Selengkapnya
                </UButton>
              </template>
            </UTable>
            <UEmpty
              v-if="!invPaged.length"
              icon="i-lucide-file-search"
              title="Tidak ada data"
            />
            <div
              v-if="invFiltered.length > PAGE_SIZE"
              class="flex items-center justify-between border-t border-default pt-3 px-2 mt-2"
            >
              <p class="text-xs text-muted">
                {{ invFiltered.length }} total
              </p>
              <UPagination
                v-model:page="invPage"
                :total="invFiltered.length"
                :items-per-page="PAGE_SIZE"
              />
            </div>
          </UCard>

          <!-- Tabel Delivery Order + Status Alur -->
          <UCard>
            <template #header>
              <div class="flex items-center justify-between gap-3 flex-wrap">
                <p class="font-medium">
                  Data Delivery Order — Alur & Status Ongkir
                </p>
                <div class="flex flex-wrap items-center gap-2">
                  <USelect
                    v-model="doFlowFilter"
                    :items="doFlowOptions"
                    value-key="value"
                    size="sm"
                    class="w-56"
                  />
                  <UInput
                    v-model="doSearch"
                    icon="i-lucide-search"
                    placeholder="Cari nomor Delivery Order, customer, Purchase Order..."
                    size="sm"
                    class="w-64"
                  />
                </div>
              </div>
            </template>
            <UTable :data="doPaged" :columns="doColumns">
              <template #doActions-cell="{ row }">
                <UButton
                  icon="i-lucide-eye"
                  size="xs"
                  color="neutral"
                  variant="soft"
                  @click="openDetail(row.original.id, 'do')"
                >
                  Selengkapnya
                </UButton>
              </template>
            </UTable>
            <UEmpty
              v-if="!doPaged.length"
              icon="i-lucide-file-search"
              title="Tidak ada data"
            />
            <div
              v-if="doFiltered.length > PAGE_SIZE"
              class="flex items-center justify-between border-t border-default pt-3 px-2 mt-2"
            >
              <p class="text-xs text-muted">
                {{ doFiltered.length }} total
              </p>
              <UPagination
                v-model:page="doPage"
                :total="doFiltered.length"
                :items-per-page="PAGE_SIZE"
              />
            </div>
          </UCard>
        </template>
      </div>
    </template>
  </UDashboardPanel>

  <AdminChartDetailModal
    v-model:open="chartDetailOpen"
    :payload="chartPayload"
    :date-from="new Date(Date.now() - 30 * 86400000).toISOString()"
    :date-to="new Date().toISOString()"
    @view-records="onChartViewRecords"
  />
  <AdminDrilldownModal
    v-if="drillMetric"
    v-model:open="drillOpen"
    :metric="drillMetric"
    :date-from="new Date(Date.now() - 30 * 86400000).toISOString()"
    :date-to="new Date().toISOString()"
  />
  <RecordDetailModal
    :id="detailId"
    v-model:open="detailOpen"
    :type="detailType"
  />
</template>
