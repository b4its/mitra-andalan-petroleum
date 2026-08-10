<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import AdminBarChart from '~/components/admin/charts/AdminBarChart.vue'
import AdminPieChart from '~/components/admin/charts/AdminPieChart.vue'
import type { ChartClickPayload } from '~/components/admin/AdminChartDetailModal.vue'
import type { AdminActivity, AdminBreakdown, AdminDrilldownMetric, AdminStats } from '~/types/admin'
import type { Range } from '~/types'

definePageMeta({ layout: 'admin' })
const UBadge = resolveComponent('UBadge')
const carousel = useTemplateRef('carousel')
const range = ref<Range>({
  start: new Date(Date.now() - 30 * 86400000),
  end: new Date()
})
const selectedMetric = ref<AdminDrilldownMetric>()
const modalOpen = ref(false)
const { get } = useApi()

// ── Chart modal state ──────────────────────────────────────────
const chartDetailOpen = ref(false)
const chartPayload = ref<ChartClickPayload | null>(null)

function onBarClick(payload: {
  label: string
  datasetLabel: string
  value: number
  datasetIndex: number
  labelIndex: number
}) {
  chartPayload.value = {
    chartType: 'bar',
    label: payload.label,
    datasetLabel: payload.datasetLabel,
    value: payload.value
  }
  chartDetailOpen.value = true
}

function onPieSegmentClick(payload: {
  label: string
  value: number
  index: number
}) {
  chartPayload.value = {
    chartType: 'pie',
    segmentLabel: payload.label,
    segmentValue: payload.value
  }
  chartDetailOpen.value = true
}

function onChartViewRecords(metric: {
  key: string
  title: string
  value: number
  unit: string
  description: string
}) {
  selectedMetric.value = metric
  modalOpen.value = true
}

const { data, pending, error, refresh } = await useAsyncData(
  'admin-system-analytics',
  () =>
    get<AdminStats>('/stats/admin', {
      date_from: range.value.start.toISOString(),
      date_to: range.value.end.toISOString()
    }),
  {
    default: () => ({
      date_from: '',
      date_to: '',
      metrics: [],
      trends: [],
      distributions: {} as Record<string, AdminBreakdown[]>,
      notifications: [],
      activities: []
    }),
    watch: [range]
  }
)

interface MetricCard {
  key: string
  icon: string
  title: string
  description: string
  unit: string
  value: number
}

const mappedAnalytics = computed<MetricCard[]>(
  () => data.value?.metrics ?? []
)

function showMetric(metric: MetricCard) {
  selectedMetric.value = metric
  modalOpen.value = true
}

function reloadDashboard() {
  refresh()
}

// ── Metric formatting ──────────────────────────────────────────
function metricValue(metric: MetricCard): string {
  if (metric.unit === 'currency') return formatCurrency(metric.value)
  if (metric.unit === 'volume') return `${formatNumber(metric.value)} Liter`
  return formatNumber(metric.value)
}

function onPrev() {
  carousel.value?.emblaApi?.scrollPrev()
}

function onNext() {
  carousel.value?.emblaApi?.scrollNext()
}

// Colour hint per metric group
const metricColor: Record<string, string> = {
  customers: 'text-blue-500',
  suppliers: 'text-cyan-500',
  users: 'text-violet-500',
  offering_letters: 'text-indigo-500',
  customer_purchase_orders: 'text-emerald-500',
  supplier_purchase_orders: 'text-teal-500',
  delivery_orders: 'text-amber-500',
  fuel_volume: 'text-orange-500',
  invoice_value: 'text-red-500',
  paid_value: 'text-green-500',
  outstanding_value: 'text-yellow-500',
  overdue_value: 'text-rose-500',
  sales_value: 'text-purple-500',
  unread_notifications: 'text-sky-500',
  uploads: 'text-slate-500'
}

// ── Charts ────────────────────────────────────────────────────
const trendLabels = computed(
  () => data.value?.trends?.map(t => t.label) || []
)
const trendDatasets = computed(() => [
  {
    label: 'Surat Penawaran',
    data: data.value?.trends?.map(t => t.offering_letters) || [],
    backgroundColor: 'rgba(59,130,246,.7)'
  },
  {
    label: 'Purchase Order Customer',
    data: data.value?.trends?.map(t => t.purchase_orders) || [],
    backgroundColor: 'rgba(16,185,129,.7)'
  },
  {
    label: 'Delivery Order',
    data: data.value?.trends?.map(t => t.delivery_orders) || [],
    backgroundColor: 'rgba(245,158,11,.7)'
  },
  {
    label: 'Invoice',
    data: data.value?.trends?.map(t => t.invoices) || [],
    backgroundColor: 'rgba(139,92,246,.7)'
  }
])
const invoiceLabels = computed(
  () => data.value?.distributions?.invoices?.map(d => d.label) || []
)
const invoiceValues = computed(
  () => data.value?.distributions?.invoices?.map(d => d.value) || []
)

// ── Notifikasi tabel + search + pagination ─────────────────────
const notifSearch = ref('')
const notifPage = ref(1)
const NOTIF_PAGE_SIZE = 5

const filteredNotifications = computed(() => {
  const q = notifSearch.value.trim().toLowerCase()
  const list: AdminActivity[] = data.value?.notifications || []
  return q
    ? list.filter(
        n =>
          n.title?.toLowerCase().includes(q)
          || n.subtitle?.toLowerCase().includes(q)
      )
    : list
})
const pagedNotifications = computed(() => {
  const start = (notifPage.value - 1) * NOTIF_PAGE_SIZE
  return filteredNotifications.value.slice(start, start + NOTIF_PAGE_SIZE)
})
watch(notifSearch, () => {
  notifPage.value = 1
})

const notificationColumns: TableColumn<AdminActivity>[] = [
  {
    accessorKey: 'title',
    header: 'Judul',
    cell: ({ row }) =>
      h('div', { class: 'truncate max-w-[200px]' }, row.getValue('title'))
  },
  {
    accessorKey: 'subtitle',
    header: 'Pesan',
    cell: ({ row }) =>
      h('div', { class: 'truncate' }, row.getValue('subtitle'))
  },
  {
    accessorKey: 'created_at',
    header: 'Waktu',
    cell: ({ row }) =>
      h(
        'div',
        { class: 'truncate' },
        row.getValue('created_at')
          ? formatDate(row.getValue('created_at'))
          : '-'
      )
  }
]

// ── Aktivitas tabel + search + pagination ──────────────────────
const actSearch = ref('')
const actPage = ref(1)
const ACT_PAGE_SIZE = 5

const filteredActivities = computed(() => {
  const q = actSearch.value.trim().toLowerCase()
  const list: AdminActivity[] = data.value?.activities || []
  return q
    ? list.filter(
        a =>
          a.domain?.toLowerCase().includes(q)
          || a.title?.toLowerCase().includes(q)
          || a.subtitle?.toLowerCase().includes(q)
      )
    : list
})
const pagedActivities = computed(() => {
  const start = (actPage.value - 1) * ACT_PAGE_SIZE
  return filteredActivities.value.slice(start, start + ACT_PAGE_SIZE)
})
watch(actSearch, () => {
  actPage.value = 1
})

const activityColumns: TableColumn<AdminActivity>[] = [
  { accessorKey: 'domain', header: 'Domain' },
  { accessorKey: 'title', header: 'Dokumen' },
  {
    accessorKey: 'subtitle',
    header: 'Status',
    cell: ({ row }) => {
      const color = {
        created: 'info' as const,
        under_revision: 'warning' as const,
        po_received: 'success' as const
      }[row.getValue('subtitle') as string]

      const status = {
        created: 'Penawaran Telah Dibuat',
        under_revision: 'Penawaran Dalam Revisi',
        po_received: 'PO Diterima'
      }[row.getValue('subtitle') as string]

      return h(
        UBadge,
        { variant: 'subtle', color: color, class: 'capitalize' },
        () => status
      )
    }
  },
  {
    accessorKey: 'created_at',
    header: 'Waktu',
    cell: ({ row }) =>
      row.getValue('created_at') ? formatDate(row.getValue('created_at')) : '-'
  }
]
</script>

<template>
  <UDashboardPanel id="admin-overview">
    <template #header>
      <UDashboardNavbar title="Overview Sistem" :ui="{ right: 'gap-2' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #right>
          <UButton
            icon="i-lucide-refresh-cw"
            color="neutral"
            variant="ghost"
            @click="reloadDashboard"
          />
        </template>
      </UDashboardNavbar>
      <UDashboardToolbar>
        <template #left>
          <HomeDateRangePicker v-model="range" />
        </template>
      </UDashboardToolbar>
    </template>

    <template #body>
      <div class="space-y-6 p-4 lg:p-6">
        <!-- Header -->
        <div class="flex justify-between">
          <div>
            <h1 class="text-2xl font-semibold">
              Monitoring Keseluruhan Sistem
            </h1>
            <p class="mt-1 text-sm text-muted">
              Setiap kartu menampilkan metrik berbeda sesuai domain. Klik kartu
              untuk melihat data penyusunnya.
            </p>
          </div>

          <div class="space-x-2">
            <UButton
              variant="subtle"
              color="neutral"
              icon="i-lucide-chevron-left"
              @click="onPrev"
            />
            <UButton
              variant="subtle"
              color="neutral"
              icon="i-lucide-chevron-right"
              @click="onNext"
            />
          </div>
        </div>

        <!-- Error -->
        <UAlert
          v-if="error"
          color="error"
          title="Gagal memuat dashboard"
          :description="error.message"
        />

        <!-- Skeleton loading -->
        <template v-else-if="pending">
          <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <USkeleton v-for="i in 16" :key="i" class="h-28 rounded-xl" />
          </div>
          <div class="grid gap-6 xl:grid-cols-3">
            <USkeleton class="xl:col-span-2 h-72 rounded-xl" />
            <USkeleton class="h-72 rounded-xl" />
          </div>
          <div class="grid gap-6 xl:grid-cols-2">
            <USkeleton class="h-64 rounded-xl" />
            <USkeleton class="h-64 rounded-xl" />
          </div>
        </template>

        <!-- Content -->
        <template v-else>
          <!-- KPI Cards — setiap kartu menampilkan unit, deskripsi, dan warna ikon berbeda -->
          <UCarousel
            ref="carousel"
            v-slot="{ item }"
            :items="mappedAnalytics"
            :ui="{ item: 'basis-1/4', root: 'w-full' }"
            :arrows="false"
            :slides-to-scroll="4"
            loop
          >
            <UPageCard
              variant="subtle"
              class="cursor-pointer transition"
              @click="showMetric(item)"
            >
              <template #leading>
                <UIcon
                  :name="item.icon"
                  class="size-5"
                  :class="metricColor[item.key] ?? 'text-primary'"
                />
              </template>
              <template #title>
                {{ item.title }}
              </template>
              <p class="text-2xl font-semibold tabular-nums">
                {{ metricValue(item) }}
              </p>

              <p class="mt-1 text-xs text-muted leading-snug">
                {{ item.description }}
              </p>
            </UPageCard>
          </UCarousel>

          <!-- Charts -->
          <div class="grid gap-6 xl:grid-cols-3">
            <UCard class="xl:col-span-2">
              <template #header>
                <div class="flex items-center justify-between">
                  <p class="font-medium">
                    Tren Dokumen per Periode
                  </p>
                  <p class="text-xs text-muted">
                    Klik bar untuk detail
                  </p>
                </div>
              </template>
              <AdminBarChart
                v-if="trendLabels.length"
                :labels="trendLabels"
                :datasets="trendDatasets"
                @bar-click="onBarClick"
              />
              <UEmpty
                v-else
                icon="i-lucide-chart-no-axes-combined"
                title="Belum ada tren"
              />
            </UCard>
            <UCard>
              <template #header>
                <div class="flex items-center justify-between">
                  <p class="font-medium">
                    Distribusi Status Invoice
                  </p>
                  <p class="text-xs text-muted">
                    Klik segment untuk detail
                  </p>
                </div>
              </template>
              <AdminPieChart
                v-if="invoiceLabels.length"
                :labels="invoiceLabels"
                :data="invoiceValues"
                @segment-click="onPieSegmentClick"
              />
              <UEmpty v-else icon="i-lucide-chart-pie" title="Belum ada data" />
            </UCard>
          </div>

          <!-- Tabel Notifikasi + Search + Pagination -->
          <div class="grid gap-6 xl:grid-cols-2">
            <UCard>
              <template #header>
                <div class="flex items-center justify-between gap-3 flex-wrap">
                  <p class="font-medium">
                    Notifikasi Sistem
                  </p>
                  <UInput
                    v-model="notifSearch"
                    icon="i-lucide-search"
                    placeholder="Cari notifikasi..."
                    size="sm"
                    class="w-48"
                  />
                </div>
              </template>
              <UTable
                :data="pagedNotifications"
                :columns="notificationColumns"
              />
              <UEmpty
                v-if="!pagedNotifications.length"
                icon="i-lucide-bell-off"
                title="Tidak ada notifikasi"
              />
              <div
                v-if="filteredNotifications.length > NOTIF_PAGE_SIZE"
                class="flex justify-end border-t border-default pt-3 mt-2"
              >
                <UPagination
                  v-model:page="notifPage"
                  :total="filteredNotifications.length"
                  :items-per-page="NOTIF_PAGE_SIZE"
                />
              </div>
            </UCard>

            <!-- Tabel Aktivitas + Search + Pagination -->
            <UCard>
              <template #header>
                <div class="flex items-center justify-between gap-3 flex-wrap">
                  <p class="font-medium">
                    Aktivitas Dokumen Terbaru
                  </p>
                  <UInput
                    v-model="actSearch"
                    icon="i-lucide-search"
                    placeholder="Cari aktivitas..."
                    size="sm"
                    class="w-48"
                  />
                </div>
              </template>
              <UTable :data="pagedActivities" :columns="activityColumns" />
              <UEmpty
                v-if="!pagedActivities.length"
                icon="i-lucide-history"
                title="Tidak ada aktivitas"
              />
              <div
                v-if="filteredActivities.length > ACT_PAGE_SIZE"
                class="flex justify-end border-t border-default pt-3 mt-2"
              >
                <UPagination
                  v-model:page="actPage"
                  :total="filteredActivities.length"
                  :items-per-page="ACT_PAGE_SIZE"
                />
              </div>
            </UCard>
          </div>
        </template>
      </div>
    </template>
  </UDashboardPanel>

  <AdminChartDetailModal
    v-model:open="chartDetailOpen"
    :payload="chartPayload"
    :date-from="range.start.toISOString()"
    :date-to="range.end.toISOString()"
    @view-records="onChartViewRecords"
  />

  <AdminDrilldownModal
    v-if="selectedMetric"
    v-model:open="modalOpen"
    :metric="selectedMetric"
    :date-from="range.start.toISOString()"
    :date-to="range.end.toISOString()"
  />
</template>
