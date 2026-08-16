<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import AdminBarChart from '~/components/admin/charts/AdminBarChart.vue'
import AdminPieChart from '~/components/admin/charts/AdminPieChart.vue'
import type { ChartClickPayload } from '~/components/admin/AdminChartDetailModal.vue'
import type { ApiOfferingLetter } from '~/composables/useApi'
import type {
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
  'admin-marketing',
  async () => {
    const [stats, olResult] = await Promise.all([
      get<AdminStats>('/stats/admin', {
        ...(dateFrom.value ? { date_from: new Date(dateFrom.value + 'T00:00:00').toISOString() } : {}),
        ...(dateTo.value ? { date_to: new Date(dateTo.value + 'T23:59:59').toISOString() } : {})
      }),
      get<Paginated<ApiOfferingLetter>>('/offering-letters', {
        page: 1,
        page_size: 100
      })
    ])
    return { stats, olList: olResult?.items || [] }
  },
  {
    default: () => ({ stats: null, olList: [] }),
    lazy: true,
    server: false,
    watch: [dateFrom, dateTo]
  }
)

// ── Stats cards ───────────────────────────────────────────────
const olStats = computed(() => {
  if (!data.value?.stats?.metrics) return []
  return data.value.stats.metrics.filter(m =>
    [
      'offering_letters',
      'customer_purchase_orders',
      'supplier_purchase_orders'
    ].includes(m.key)
  )
})

// ── Charts ────────────────────────────────────────────────────
const trendLabels = computed(
  () => data.value?.stats?.trends?.map(t => t.label) || []
)
const olTrendData = computed(
  () => data.value?.stats?.trends?.map(t => t.offering_letters) || []
)
const poTrendData = computed(
  () => data.value?.stats?.trends?.map(t => t.purchase_orders) || []
)
const olDistLabels = computed(
  () =>
    data.value?.stats?.distributions?.offering_letters?.map(d => d.label)
    || []
)
const olDistValues = computed(
  () =>
    data.value?.stats?.distributions?.offering_letters?.map(d => d.value)
    || []
)

// ── Table: search + pagination ────────────────────────────────
const search = ref('')
const statusFilter = ref('all')
const page = ref(1)
const PAGE_SIZE = 7

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  let list: ApiOfferingLetter[] = data.value?.olList || []

  if (statusFilter.value !== 'all') {
    list = list.filter(ol => ol.status === statusFilter.value)
  }

  if (!q) return list
  return list.filter(
    ol =>
      ol.offering_letter_number?.toLowerCase().includes(q)
      || ol.customer_name?.toLowerCase().includes(q)
      || ol.status?.toLowerCase().includes(q)
  )
})
const paged = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE
  return filtered.value.slice(start, start + PAGE_SIZE)
})
watch([search, statusFilter], () => {
  page.value = 1
})

const statusLabel: Record<string, string> = {
  created: 'Dibuat',
  under_revision: 'Dalam Revisi',
  po_received: 'Purchase Order Customer Diterima'
}
const statusColor: Record<string, string> = {
  created: 'info',
  under_revision: 'warning',
  po_received: 'success'
}

const statusOptions = [
  { label: 'Semua Status', value: 'all' },
  { label: 'Dibuat', value: 'created' },
  { label: 'Dalam Revisi', value: 'under_revision' },
  { label: 'Purchase Order Customer Diterima', value: 'po_received' }
]

const columns: TableColumn<ApiOfferingLetter>[] = [
  { accessorKey: 'offering_letter_number', header: 'Nomor Surat' },
  { accessorKey: 'customer_name', header: 'Customer' },
  {
    accessorKey: 'fuel_total_price',
    header: 'Nilai Penawaran',
    cell: ({ row }) =>
      formatCurrency(row.getValue('fuel_total_price') ?? 0)
  },
  {
    accessorKey: 'transport_price',
    header: 'Ongkos Transportir',
    cell: ({ row }) =>
      formatCurrency(row.getValue('transport_price') ?? 0)
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => {
      const s = row.getValue('status') as string
      return h(
        UBadge,
        { variant: 'subtle', color: statusColor[s] ?? 'neutral' },
        () => statusLabel[s] ?? s
      )
    }
  },
  {
    accessorKey: 'created_at',
    header: 'Dibuat',
    cell: ({ row }) =>
      row.getValue('created_at') ? formatDate(row.getValue('created_at')) : '-'
  },
  { id: 'actions', header: 'Aksi' }
]

const detailOpen = ref(false)
const detailId = ref<string | null>(null)
function openDetail(id: string) {
  detailId.value = id
  detailOpen.value = true
}
</script>

<template>
  <UDashboardPanel id="admin-marketing">
    <template #header>
      <UDashboardNavbar title="Marketing — Rekap" :ui="{ right: 'gap-2' }">
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
          <div class="grid gap-4 sm:grid-cols-3">
            <USkeleton v-for="i in 3" :key="i" class="h-28 rounded-xl" />
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

          <!-- Stats -->
          <div v-if="olStats.length" class="grid gap-4 sm:grid-cols-3">
            <UCard v-for="m in olStats" :key="m.key" variant="subtle">
              <template #leading>
                <UIcon :name="m.icon" class="size-5 text-primary" />
              </template>
              <template #title>
                {{ m.title }}
              </template>
              <p class="text-2xl font-semibold tabular-nums">
                {{ formatNumber(m.value) }}
              </p>
              <p class="text-xs text-muted mt-1">
                {{ m.description }}
              </p>
            </UCard>
          </div>

          <!-- Tabel SP + Search + Pagination -->
          <UCard>
            <template #header>
              <div class="flex items-center justify-between gap-3 flex-wrap">
                <p class="font-medium">
                  Data Surat Penawaran
                </p>
                <div class="flex flex-wrap items-center gap-2">
                  <USelect
                    v-model="statusFilter"
                    :items="statusOptions"
                    value-key="value"
                    size="sm"
                    class="w-44"
                  />
                  <UInput
                    v-model="search"
                    icon="i-lucide-search"
                    placeholder="Cari nomor Surat Penawaran, customer, status..."
                    size="sm"
                    class="w-64"
                  />
                </div>
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
                Visualisasi data marketing
              </p>
            </div>
            <div class="grid gap-6 lg:grid-cols-2">
              <UCard>
                <template #header>
                  <div class="flex items-center justify-between">
                    <p class="font-medium">
                      Tren Surat Penawaran & Purchase Order per Periode
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
                      label: 'Surat Penawaran',
                      data: olTrendData,
                      backgroundColor: 'rgba(59,130,246,0.7)'
                    },
                    {
                      label: 'Purchase Order',
                      data: poTrendData,
                      backgroundColor: 'rgba(16,185,129,0.7)'
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
                      Distribusi Status Surat Penawaran
                    </p>
                    <p class="text-xs text-muted">
                      Klik segment untuk detail
                    </p>
                  </div>
                </template>
                <AdminPieChart
                  v-if="olDistLabels.length"
                  :labels="olDistLabels"
                  :data="olDistValues"
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
  <RecordDetailModal :id="detailId" v-model:open="detailOpen" type="ol" />
</template>
