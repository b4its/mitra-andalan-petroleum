<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import AdminBarChart from '~/components/admin/charts/AdminBarChart.vue'
import AdminPieChart from '~/components/admin/charts/AdminPieChart.vue'
import type { ChartClickPayload } from '~/components/admin/AdminChartDetailModal.vue'
import type {
  AdminDeliveryOrderRow,
  AdminDrilldownMetric,
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
const dateFrom = ref('')
const dateTo = ref('')

const { data, pending, refresh } = useAsyncData(
  'admin-operations',
  async () => {
    const [stats, doResult] = await Promise.all([
      get<AdminStats>('/stats/admin', {
        ...(dateFrom.value ? { date_from: new Date(dateFrom.value + 'T00:00:00').toISOString() } : {}),
        ...(dateTo.value ? { date_to: new Date(dateTo.value + 'T23:59:59').toISOString() } : {})
      }),
      get<Paginated<AdminDeliveryOrderRow>>('/delivery-orders', {
        page: 1,
        page_size: 100
      })
    ])
    return { stats, doList: doResult?.items || [] }
  },
  {
    default: () => ({ stats: null, doList: [] }),
    lazy: true,
    server: false,
    watch: [dateFrom, dateTo]
  }
)

// ── Stats cards ───────────────────────────────────────────────
const doStats = computed(() => {
  if (!data.value?.stats?.metrics) return []
  return data.value.stats.metrics.filter(m =>
    ['delivery_orders', 'fuel_volume'].includes(m.key)
  )
})

// ── Ringkasan status alur DO ──────────────────────────────────
const doAlurStats = computed(() => {
  const list: AdminDeliveryOrderRow[] = data.value?.doList || []
  return {
    menungguLunas: list.filter(
      d => d.status_selesai_dikirim && !d.status_lunas_ongkir
    ).length,
    sudahLunasOngkir: list.filter(d => d.status_lunas_ongkir).length
  }
})

// ── Charts ────────────────────────────────────────────────────
const trendLabels = computed(
  () => data.value?.stats?.trends?.map(t => t.label) || []
)
const doTrendData = computed(
  () => data.value?.stats?.trends?.map(t => t.delivery_orders) || []
)
const doDistLabels = computed(
  () =>
    data.value?.stats?.distributions?.delivery_orders?.map(d => d.label)
    || []
)
const doDistValues = computed(
  () =>
    data.value?.stats?.distributions?.delivery_orders?.map(d => d.value)
    || []
)

// ── Table: search + pagination ────────────────────────────────
const search = ref('')
const page = ref(1)
const PAGE_SIZE = 7

// Filter tab
const filterTab = ref<'all' | 'lunas'>('all')
const statusFilter = ref('all')

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  let list: AdminDeliveryOrderRow[] = data.value?.doList || []

  // Filter berdasarkan tab status alur
  if (filterTab.value === 'lunas')
    list = list.filter(
      d => d.status_selesai_dikirim && !d.status_lunas_ongkir
    )

  if (statusFilter.value !== 'all') {
    list = list.filter(d => d.status === statusFilter.value)
  }

  if (!q) return list
  return list.filter(
    d =>
      d.do_number?.toLowerCase().includes(q)
      || d.customer_name?.toLowerCase().includes(q)
      || d.transport_name?.toLowerCase().includes(q)
      || d.status?.toLowerCase().includes(q)
  )
})
const paged = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE
  return filtered.value.slice(start, start + PAGE_SIZE)
})
watch([search, filterTab, statusFilter], () => {
  page.value = 1
})

// ── Status helpers ────────────────────────────────────────────
const doStatusLabel: Record<string, string> = {
  created: 'Dibuat',
  draft: 'Draf',
  document_returned: 'Dokumen Kembali'
}
const doStatusColor: Record<string, string> = {
  created: 'info',
  draft: 'warning',
  document_returned: 'success'
}
const doStatusOptions = [
  { label: 'Semua Status', value: 'all' },
  { label: 'Dibuat', value: 'created' },
  { label: 'Draf', value: 'draft' },
  { label: 'Dokumen Kembali', value: 'document_returned' }
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

const columns: TableColumn<AdminDeliveryOrderRow>[] = [
  { accessorKey: 'do_number', header: 'Nomor Delivery Order' },
  { accessorKey: 'customer_name', header: 'Customer' },
  { accessorKey: 'transport_name', header: 'Transportir' },
  {
    accessorKey: 'fuel_total',
    header: 'Volume (L)',
    cell: ({ row }) => formatNumber(row.getValue('fuel_total') ?? 0)
  },
  {
    accessorKey: 'status_lunas_ongkir',
    header: 'Lunas Ongkir',
    cell: ({ row }) =>
      alurBadge(row.original.status_lunas_ongkir, row.original.lunas_ongkir_at)
  },
  {
    accessorKey: 'status',
    header: 'Status Delivery Order',
    cell: ({ row }) => {
      const s = row.getValue('status') as string
      return h(
        UBadge,
        { variant: 'soft', color: doStatusColor[s] ?? 'neutral' },
        () => doStatusLabel[s] ?? s
      )
    }
  },
  { id: 'actions', header: 'Aksi' }
]

const detailOpen = ref(false)
const detailId = ref<string | null>(null)
function openDetail(id: string) {
  detailId.value = id
  detailOpen.value = true
}

const filterTabs = [
  { key: 'all', label: 'Semua' },
  { key: 'lunas', label: 'Menunggu Lunas Ongkir' }
]
</script>

<template>
  <UDashboardPanel id="admin-operations">
    <template #header>
      <UDashboardNavbar title="Operations — Rekap" :ui="{ right: 'gap-2' }">
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
          <div class="grid gap-4 sm:grid-cols-2">
            <USkeleton v-for="i in 2" :key="i" class="h-28 rounded-xl" />
          </div>
          <div class="grid gap-4 sm:grid-cols-5">
            <USkeleton v-for="i in 5" :key="i" class="h-20 rounded-xl" />
          </div>
          <div class="grid gap-6 lg:grid-cols-2">
            <USkeleton class="h-72 rounded-xl" />
            <USkeleton class="h-72 rounded-xl" />
          </div>
          <USkeleton class="h-64 rounded-xl" />
        </template>

        <template v-else>
          <UCard>
            <div class="flex flex-col gap-3">
              <p class="text-sm font-medium">
                Filter Periode Data
              </p>
              <div class="flex flex-wrap items-end gap-3">
                <UFormField label="Dari Tanggal">
                  <UInput v-model="dateFrom" type="date" />
                </UFormField>
                <UFormField label="Sampai Tanggal">
                  <UInput v-model="dateTo" type="date" />
                </UFormField>
                <UButton icon="i-lucide-search" :loading="pending" @click="() => refresh()">
                  Terapkan
                </UButton>
                <UButton
                  icon="i-lucide-rotate-ccw"
                  color="neutral"
                  variant="soft"
                  @click="dateFrom = ''; dateTo = ''"
                >
                  Reset
                </UButton>
              </div>
            </div>
          </UCard>

          <!-- Stats KPI -->
          <div v-if="doStats.length" class="grid gap-4 sm:grid-cols-2">
            <UCard v-for="m in doStats" :key="m.key" variant="subtle">
              <template #leading>
                <UIcon :name="m.icon" class="size-5 text-primary" />
              </template>
              <template #title>
                {{ m.title }}
              </template>
              <p class="text-2xl font-semibold tabular-nums">
                {{
                  m.unit === "volume"
                    ? `${formatNumber(m.value)} L`
                    : formatNumber(m.value)
                }}
              </p>
              <p class="text-xs text-muted mt-1">
                {{ m.description }}
              </p>
            </UCard>
          </div>

          <!-- Ringkasan Alur DO -->
          <div class="grid gap-3 sm:grid-cols-2">
            <UCard variant="subtle" class="text-center">
              <p class="text-xs text-muted mb-1">
                Menunggu Lunas Ongkir
              </p>
              <p class="text-2xl font-bold text-warning">
                {{ doAlurStats.menungguLunas }}
              </p>
            </UCard>
            <UCard variant="subtle" class="text-center">
              <p class="text-xs text-muted mb-1">
                Ongkir Lunas
              </p>
              <p class="text-2xl font-bold text-success">
                {{ doAlurStats.sudahLunasOngkir }}
              </p>
            </UCard>
          </div>

          <!-- Tabel DO dengan status alur lengkap -->
          <UCard>
            <template #header>
              <div class="flex flex-wrap items-center justify-between gap-3">
                <p class="font-medium">
                  Data Delivery Order — Alur Pengiriman
                </p>
                <div class="flex flex-wrap items-center gap-2">
                  <USelect
                    v-model="statusFilter"
                    :items="doStatusOptions"
                    value-key="value"
                    size="sm"
                    class="w-48"
                  />
                  <UInput
                    v-model="search"
                    icon="i-lucide-search"
                    placeholder="Cari nomor Delivery Order, customer..."
                    size="sm"
                    class="w-64"
                  />
                </div>
              </div>
              <!-- Filter tab alur -->
              <div class="flex flex-wrap gap-2 mt-3">
                <UButton
                  v-for="tab in filterTabs"
                  :key="tab.key"
                  size="xs"
                  :color="filterTab === tab.key ? 'primary' : 'neutral'"
                  :variant="filterTab === tab.key ? 'solid' : 'soft'"
                  @click="filterTab = tab.key as any"
                >
                  {{ tab.label }}
                </UButton>
              </div>
            </template>

            <UTable :data="paged" :columns="columns">
              <template #actions-cell="{ row }">
                <UButton
                  icon="i-lucide-eye"
                  size="xs"
                  color="neutral"
                  variant="soft"
                  @click="openDetail(row.original.id)"
                >
                  Selengkapnya
                </UButton>
              </template>
            </UTable>
            <UEmpty
              v-if="!paged.length"
              icon="i-lucide-file-search"
              title="Tidak ada data"
            />
            <div
              v-if="filtered.length > PAGE_SIZE"
              class="flex items-center justify-between border-t border-default pt-3 px-2 mt-2"
            >
              <p class="text-xs text-muted">
                {{ filtered.length }} total
              </p>
              <UPagination
                v-model:page="page"
                :total="filtered.length"
                :items-per-page="PAGE_SIZE"
              />
            </div>
          </UCard>

          <!-- Grafik (penutup halaman) -->
          <div>
            <div class="mb-3 flex items-center justify-between">
              <p class="text-sm font-semibold uppercase tracking-wide text-muted">
                Grafik
              </p>
              <p class="text-xs text-muted">
                Visualisasi data operations
              </p>
            </div>
            <div class="grid gap-6 lg:grid-cols-2">
              <UCard>
                <template #header>
                  <div class="flex items-center justify-between">
                    <p class="font-medium">
                      Tren Delivery Order per Periode
                    </p>
                    <p class="text-xs text-muted">
                      Klik bar untuk detail
                    </p>
                  </div>
                </template>
                <AdminBarChart
                  v-if="trendLabels.length"
                  :labels="trendLabels"
                  :datasets="[
                    {
                      label: 'Delivery Order',
                      data: doTrendData,
                      backgroundColor: 'rgba(245,158,11,0.7)'
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
                      Distribusi Status Delivery Order
                    </p>
                    <p class="text-xs text-muted">
                      Klik segment untuk detail
                    </p>
                  </div>
                </template>
                <AdminPieChart
                  v-if="doDistLabels.length"
                  :labels="doDistLabels"
                  :data="doDistValues"
                  @segment-click="onPieClick"
                />
                <UEmpty v-else icon="i-lucide-chart-pie" title="Belum ada data" />
              </UCard>
            </div>
          </div>
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
  <RecordDetailModal :id="detailId" v-model:open="detailOpen" type="do" />
</template>
