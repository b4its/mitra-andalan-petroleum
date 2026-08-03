<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import AdminBarChart from '~/components/admin/charts/AdminBarChart.vue'
import AdminPieChart from '~/components/admin/charts/AdminPieChart.vue'
import type { ChartClickPayload } from '~/components/admin/AdminChartDetailModal.vue'

definePageMeta({ layout: 'admin' })

const UBadge = resolveComponent('UBadge')
const { get } = useApi()

// ── Chart modal state ──────────────────────────────────────────
const chartDetailOpen = ref(false)
const chartPayload = ref<ChartClickPayload | null>(null)
const drillMetric = ref<any>(null)
const drillOpen = ref(false)

function onBarClick(p: { label: string, datasetLabel: string, value: number, datasetIndex: number, labelIndex: number }) {
  chartPayload.value = { chartType: 'bar', label: p.label, datasetLabel: p.datasetLabel, value: p.value }
  chartDetailOpen.value = true
}
function onPieClick(p: { label: string, value: number, index: number }) {
  chartPayload.value = { chartType: 'pie', segmentLabel: p.label, segmentValue: p.value }
  chartDetailOpen.value = true
}
function onChartViewRecords(metric: any) {
  drillMetric.value = metric
  drillOpen.value = true
}

// ── Data fetch ────────────────────────────────────────────────
const { data, pending, refresh } = useAsyncData('admin-operations', async () => {
  const [stats, doResult] = await Promise.all([
    get<any>('/stats/admin'),
    get<any>('/delivery-orders', { page: 1, page_size: 100 })
  ])
  return { stats, doList: doResult?.items || [] }
}, { default: () => ({ stats: null, doList: [] }), lazy: true, server: false })

// ── Stats cards ───────────────────────────────────────────────
const doStats = computed(() => {
  if (!data.value?.stats?.metrics) return []
  return (data.value.stats.metrics as any[]).filter(m =>
    ['delivery_orders', 'fuel_volume'].includes(m.key)
  )
})

// ── Ringkasan status alur DO ──────────────────────────────────
const doAlurStats = computed(() => {
  const list: any[] = data.value?.doList || []
  return {
    belumRilisDana: list.filter(d => !d.status_rilis_dana).length,
    sudahRilisDana: list.filter(d => d.status_rilis_dana && !d.status_ready_order).length,
    sudahReadyOrder: list.filter(d => d.status_ready_order && !d.status_selesai_dikirim).length,
    sudahSelesaiDikirim: list.filter(d => d.status_selesai_dikirim && !d.status_lunas_ongkir).length,
    sudahLunasOngkir: list.filter(d => d.status_lunas_ongkir).length,
  }
})

// ── Charts ────────────────────────────────────────────────────
const trendLabels = computed(() => data.value?.stats?.trends?.map((t: any) => t.label) || [])
const doTrendData = computed(() => data.value?.stats?.trends?.map((t: any) => t.delivery_orders) || [])
const doDistLabels = computed(() => data.value?.stats?.distributions?.delivery_orders?.map((d: any) => d.label) || [])
const doDistValues = computed(() => data.value?.stats?.distributions?.delivery_orders?.map((d: any) => d.value) || [])

// ── Table: search + pagination ────────────────────────────────
const search = ref('')
const page = ref(1)
const PAGE_SIZE = 7

// Filter tab
const filterTab = ref<'all' | 'rilis' | 'ready' | 'selesai' | 'lunas'>('all')

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  let list: any[] = data.value?.doList || []

  // Filter berdasarkan tab status alur
  if (filterTab.value === 'rilis') list = list.filter(d => d.status_rilis_dana && !d.status_ready_order)
  else if (filterTab.value === 'ready') list = list.filter(d => d.status_ready_order && !d.status_selesai_dikirim)
  else if (filterTab.value === 'selesai') list = list.filter(d => d.status_selesai_dikirim && !d.status_lunas_ongkir)
  else if (filterTab.value === 'lunas') list = list.filter(d => d.status_lunas_ongkir)

  if (!q) return list
  return list.filter(d =>
    d.do_number?.toLowerCase().includes(q) ||
    d.customer_name?.toLowerCase().includes(q) ||
    d.transport_name?.toLowerCase().includes(q) ||
    d.status?.toLowerCase().includes(q)
  )
})
const paged = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE
  return filtered.value.slice(start, start + PAGE_SIZE)
})
watch([search, filterTab], () => { page.value = 1 })

// ── Status helpers ────────────────────────────────────────────
const doStatusLabel: Record<string, string> = { created: 'Dibuat', draft: 'Draft', document_returned: 'Dokumen Kembali' }
const doStatusColor: Record<string, string> = { created: 'info', draft: 'warning', document_returned: 'success' }

function alurBadge(done: boolean, at: any) {
  return h('div', { class: 'flex flex-col gap-0.5' }, [
    h(UBadge, { variant: 'subtle', color: done ? 'success' : 'neutral', class: 'text-xs' }, () => done ? '✓' : '-'),
    done && at ? h('span', { class: 'text-[10px] text-muted' }, formatDate(at)) : null,
  ])
}

const columns: TableColumn<any>[] = [
  { accessorKey: 'do_number', header: 'Nomor DO' },
  { accessorKey: 'customer_name', header: 'Customer' },
  { accessorKey: 'transport_name', header: 'Transportir' },
  {
    accessorKey: 'fuel_total',
    header: 'Volume (L)',
    cell: ({ row }: any) => formatNumber(row.getValue('fuel_total') ?? 0)
  },
  {
    accessorKey: 'status_rilis_dana',
    header: 'Rilis Dana',
    cell: ({ row }: any) => alurBadge(row.original.status_rilis_dana, row.original.rilis_dana_at)
  },
  {
    accessorKey: 'status_ready_order',
    header: 'Siap Kirim',
    cell: ({ row }: any) => alurBadge(row.original.status_ready_order, row.original.ready_order_at)
  },
  {
    accessorKey: 'status_selesai_dikirim',
    header: 'Selesai',
    cell: ({ row }: any) => alurBadge(row.original.status_selesai_dikirim, row.original.selesai_dikirim_at)
  },
  {
    accessorKey: 'status_lunas_ongkir',
    header: 'Lunas Ongkir',
    cell: ({ row }: any) => alurBadge(row.original.status_lunas_ongkir, row.original.lunas_ongkir_at)
  },
  {
    accessorKey: 'status',
    header: 'Status DO',
    cell: ({ row }: any) => {
      const s = row.getValue('status') as string
      return h(UBadge, { variant: 'soft', color: doStatusColor[s] ?? 'neutral' }, () => doStatusLabel[s] ?? s)
    }
  },
  { id: 'actions', header: 'Aksi' }
]

const detailOpen = ref(false)
const detailId = ref<string | null>(null)
function openDetail(id: string) { detailId.value = id; detailOpen.value = true }

const filterTabs = [
  { key: 'all', label: 'Semua' },
  { key: 'rilis', label: 'Dana Dirilis' },
  { key: 'ready', label: 'Siap Kirim' },
  { key: 'selesai', label: 'Selesai Kirim' },
  { key: 'lunas', label: 'Lunas Ongkir' },
]
</script>

<template>
  <UDashboardPanel id="admin-operations">
    <template #header>
      <UDashboardNavbar title="Operations — Rekap" :ui="{ right: 'gap-2' }">
        <template #leading><UDashboardSidebarCollapse /></template>
        <template #right>
          <UButton icon="i-lucide-refresh-cw" color="neutral" variant="ghost" @click="refresh()" />
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
          <!-- Stats KPI -->
          <div v-if="doStats.length" class="grid gap-4 sm:grid-cols-2">
            <UCard v-for="m in doStats" :key="m.key" variant="subtle">
              <template #leading>
                <UIcon :name="m.icon" class="size-5 text-primary" />
              </template>
              <template #title>{{ m.title }}</template>
              <p class="text-2xl font-semibold tabular-nums">
                {{ m.unit === 'volume' ? `${formatNumber(m.value)} L` : formatNumber(m.value) }}
              </p>
              <p class="text-xs text-muted mt-1">{{ m.description }}</p>
            </UCard>
          </div>

          <!-- Ringkasan Alur DO -->
          <div class="grid gap-3 sm:grid-cols-5">
            <UCard variant="subtle" class="text-center">
              <p class="text-xs text-muted mb-1">Belum Rilis Dana</p>
              <p class="text-2xl font-bold text-warning">{{ doAlurStats.belumRilisDana }}</p>
            </UCard>
            <UCard variant="subtle" class="text-center">
              <p class="text-xs text-muted mb-1">Dana Dirilis</p>
              <p class="text-2xl font-bold text-info">{{ doAlurStats.sudahRilisDana }}</p>
            </UCard>
            <UCard variant="subtle" class="text-center">
              <p class="text-xs text-muted mb-1">Siap Dikirim</p>
              <p class="text-2xl font-bold text-primary">{{ doAlurStats.sudahReadyOrder }}</p>
            </UCard>
            <UCard variant="subtle" class="text-center">
              <p class="text-xs text-muted mb-1">Selesai Kirim</p>
              <p class="text-2xl font-bold text-success">{{ doAlurStats.sudahSelesaiDikirim }}</p>
            </UCard>
            <UCard variant="subtle" class="text-center">
              <p class="text-xs text-muted mb-1">Lunas Ongkir</p>
              <p class="text-2xl font-bold text-success">{{ doAlurStats.sudahLunasOngkir }}</p>
            </UCard>
          </div>

          <!-- Charts -->
          <div class="grid gap-6 lg:grid-cols-2">
            <UCard>
              <template #header>
                <div class="flex items-center justify-between">
                  <p class="font-medium">Tren Delivery Order per Periode</p>
                  <p class="text-xs text-muted">Klik bar untuk detail</p>
                </div>
              </template>
              <AdminBarChart
                v-if="trendLabels.length"
                :labels="trendLabels"
                :datasets="[{ label: 'Delivery Order', data: doTrendData, backgroundColor: 'rgba(245,158,11,0.7)' }]"
                @bar-click="onBarClick"
              />
              <UEmpty v-else icon="i-lucide-chart-bar" title="Belum ada data tren" />
            </UCard>
            <UCard>
              <template #header>
                <div class="flex items-center justify-between">
                  <p class="font-medium">Distribusi Status DO</p>
                  <p class="text-xs text-muted">Klik segment untuk detail</p>
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

          <!-- Tabel DO dengan status alur lengkap -->
          <UCard>
            <template #header>
              <div class="flex flex-wrap items-center justify-between gap-3">
                <p class="font-medium">Data Delivery Order — Alur Pengiriman</p>
                <UInput
                  v-model="search"
                  icon="i-lucide-search"
                  placeholder="Cari nomor DO, customer..."
                  size="sm"
                  class="w-64"
                />
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
                  variant="ghost"
                  @click="openDetail(row.original.id)"
                >
                  Selengkapnya
                </UButton>
              </template>
            </UTable>
            <UEmpty v-if="!paged.length" icon="i-lucide-file-search" title="Tidak ada data" />
            <div v-if="filtered.length > PAGE_SIZE" class="flex items-center justify-between border-t border-default pt-3 px-2 mt-2">
              <p class="text-xs text-muted">{{ filtered.length }} total</p>
              <UPagination v-model:page="page" :total="filtered.length" :items-per-page="PAGE_SIZE" />
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
  <RecordDetailModal v-model:open="detailOpen" type="do" :id="detailId" />
</template>
