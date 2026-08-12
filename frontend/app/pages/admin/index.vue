<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import AdminBarChart from '~/components/admin/charts/AdminBarChart.vue'
import AdminPieChart from '~/components/admin/charts/AdminPieChart.vue'
import type { ChartClickPayload } from '~/components/admin/AdminChartDetailModal.vue'
import type { AdminActivity, AdminBreakdown, AdminDrilldownMetric, AdminStats } from '~/types/admin'
import type {
  AccountingSummary,
  AccountingJournal,
  BalanceSheetResponse,
  CashflowResponse,
  CostRecapResponse,
  MonitoringResponse,
  DailyCashResponse,
  BankInterestResponse
} from '~/types/accounting'
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

// ── Data akuntansi ─────────────────────────────────────────────
const { data: accounting } = await useAsyncData(
  'admin-accounting-summary',
  () => get<AccountingSummary>('/accounting/summary'),
  { default: () => null, server: false }
)

const { data: accountingDetails } = await useAsyncData(
  'admin-accounting-details',
  () =>
    Promise.all([
      get<BalanceSheetResponse>('/accounting/balance-sheet'),
      get<CashflowResponse>('/accounting/cashflow'),
      get<CostRecapResponse>('/accounting/cost-recap'),
      get<MonitoringResponse>('/accounting/monitoring', {
        year: new Date().getFullYear()
      }),
      get<DailyCashResponse>('/accounting/daily-cash'),
      get<BankInterestResponse>('/accounting/bank-interest')
    ]),
  { default: () => [], server: false }
)

const accountingDetail = computed(() => {
  const [balanceSheet, cashflow, costRecap, monitoring, dailyCash, bankInterest] =
    accountingDetails.value || []
  return { balanceSheet, cashflow, costRecap, monitoring, dailyCash, bankInterest }
})

const totalDebit = (journal: AccountingJournal) =>
  journal.lines.reduce((sum, line) => sum + (line.debit || 0), 0)

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

// ── Distribusi tambahan (keseluruhan data sistem) ──────────────
const distributionLabels: Record<string, string> = {
  offering_letters: 'Status Surat Penawaran',
  purchase_orders: 'Tipe Purchase Order',
  delivery_orders: 'Status Delivery Order',
  invoice_deadlines: 'Status Tenggat Invoice',
  users: 'Peran Pengguna',
  notifications: 'Tipe Notifikasi',
  uploads: 'Tipe Dokumen Upload'
}

const distributionIcons: Record<string, string> = {
  offering_letters: 'i-lucide-file-text',
  purchase_orders: 'i-lucide-shopping-cart',
  delivery_orders: 'i-lucide-package-check',
  invoice_deadlines: 'i-lucide-calendar-clock',
  users: 'i-lucide-user-round',
  notifications: 'i-lucide-bell',
  uploads: 'i-lucide-paperclip'
}

const pieColors = [
  'rgba(59,130,246,0.8)',
  'rgba(16,185,129,0.8)',
  'rgba(245,158,11,0.8)',
  'rgba(239,68,68,0.8)',
  'rgba(139,92,246,0.8)',
  'rgba(6,182,212,0.8)',
  'rgba(236,72,153,0.8)',
  'rgba(100,116,139,0.8)'
]

const distributionKeys = [
  'offering_letters',
  'purchase_orders',
  'delivery_orders',
  'invoice_deadlines',
  'users',
  'notifications',
  'uploads'
] as const

function distributionChart(key: string) {
  const dist = data.value?.distributions?.[key] || []
  return {
    labels: dist.map(d => d.label),
    values: dist.map(d => d.value),
    colors: dist.map((_, i) => pieColors[i % pieColors.length])
  }
}

function onDistributionSegmentClick(key: string, payload: {
  label: string
  value: number
  index: number
}) {
  const metricKey: Record<string, string> = {
    offering_letters: 'offering_letters',
    purchase_orders: 'customer_purchase_orders',
    delivery_orders: 'delivery_orders',
    invoice_deadlines: 'outstanding_value',
    users: 'users',
    notifications: 'unread_notifications',
    uploads: 'uploads'
  }
  chartPayload.value = {
    chartType: 'pie',
    segmentLabel: payload.label,
    segmentValue: payload.value
  }
  chartDetailOpen.value = true
}

// ── Kartu akuntansi ────────────────────────────────────────────
const accountingCards = computed(() => [
  {
    title: 'Total Pemasukan',
    value: formatCurrency(accounting.value?.total_income ?? 0),
    icon: 'i-lucide-trending-up',
    color: 'text-success'
  },
  {
    title: 'Total Pengeluaran',
    value: formatCurrency(accounting.value?.total_expense ?? 0),
    icon: 'i-lucide-trending-down',
    color: 'text-error'
  },
  {
    title: 'Laba Bersih',
    value: formatCurrency(accounting.value?.net_income ?? 0),
    icon: 'i-lucide-wallet',
    color: 'text-primary'
  },
  {
    title: 'Saldo Kas & Bank',
    value: formatCurrency(accounting.value?.cash_balance ?? 0),
    icon: 'i-lucide-circle-dollar-sign',
    color: 'text-info'
  }
])

const accountingCountCards = computed(() => [
  {
    title: 'Jumlah Jurnal',
    value: accounting.value?.journal_count ?? 0,
    icon: 'i-lucide-book-open'
  },
  {
    title: 'Jumlah Akun',
    value: accounting.value?.account_count ?? 0,
    icon: 'i-lucide-list-tree'
  },
  {
    title: 'Pemasukan',
    value: accounting.value?.income_count ?? 0,
    icon: 'i-lucide-banknote-arrow-down'
  },
  {
    title: 'Pengeluaran',
    value: accounting.value?.expense_count ?? 0,
    icon: 'i-lucide-banknote-arrow-up'
  }
])

// ── Grafik akuntansi (neraca, cashflow, dll) ─────────────────
const balanceSheetChart = computed(() => {
  const n = accountingDetail.value.balanceSheet
  if (!n) return null
  return {
    labels: ['Aset', 'Kewajiban', 'Ekuitas'],
    datasets: [
      {
        label: 'Nilai',
        data: [n.total_assets, n.total_liabilities, n.total_equity],
        backgroundColor: [
          'rgba(59,130,246,0.8)',
          'rgba(245,158,11,0.8)',
          'rgba(16,185,129,0.8)'
        ]
      }
    ]
  }
})

const cashflowChart = computed(() => {
  const c = accountingDetail.value.cashflow
  if (!c) return null
  return {
    labels: ['Operasi', 'Investasi', 'Pendanaan'],
    datasets: [
      {
        label: 'Arus Kas',
        data: [c.operating.total, c.investing.total, c.financing.total],
        backgroundColor: [
          c.operating.total >= 0 ? 'rgba(16,185,129,0.8)' : 'rgba(239,68,68,0.8)',
          c.investing.total >= 0 ? 'rgba(16,185,129,0.8)' : 'rgba(239,68,68,0.8)',
          c.financing.total >= 0 ? 'rgba(16,185,129,0.8)' : 'rgba(239,68,68,0.8)'
        ]
      }
    ]
  }
})

const dailyCashChart = computed(() => {
  const d = accountingDetail.value.dailyCash
  if (!d) return null
  return {
    labels: ['Saldo Awal', 'Total Masuk', 'Total Keluar', 'Saldo Akhir'],
    datasets: [
      {
        label: 'Nominal',
        data: [d.opening_balance, d.total_debit, d.total_credit, d.closing_balance],
        backgroundColor: [
          'rgba(100,116,139,0.8)',
          'rgba(16,185,129,0.8)',
          'rgba(239,68,68,0.8)',
          'rgba(59,130,246,0.8)'
        ]
      }
    ]
  }
})

const costRecapChart = computed(() => {
  const groups = accountingDetail.value.costRecap?.groups || []
  if (!groups.length) return null
  const top = [...groups].sort((a, b) => b.total - a.total).slice(0, 10)
  return {
    labels: top.map(g => `${g.account_code} · ${g.account_name}`),
    datasets: [
      {
        label: 'Total Biaya',
        data: top.map(g => g.total),
        backgroundColor: 'rgba(239,68,68,0.8)'
      }
    ]
  }
})

const monitoringChart = computed(() => {
  const rows = accountingDetail.value.monitoring?.rows || []
  if (!rows.length) return null
  return {
    labels: rows.map(r => r.bulan),
    datasets: [
      {
        label: 'Penghasilan',
        data: rows.map(r => r.penghasilan),
        backgroundColor: 'rgba(16,185,129,0.8)'
      },
      {
        label: 'Operasional',
        data: rows.map(r => r.operasional),
        backgroundColor: 'rgba(239,68,68,0.8)'
      },
      {
        label: 'Margin Kotor',
        data: rows.map(r => r.gross_margin),
        backgroundColor: 'rgba(59,130,246,0.8)'
      }
    ]
  }
})

const bankInterestChart = computed(() => {
  const b = accountingDetail.value.bankInterest
  if (!b) return null
  return {
    labels: ['Pokok Pinjaman', 'Total Bunga', 'Total Pembayaran'],
    datasets: [
      {
        label: 'Nominal',
        data: [b.total_principal, b.total_interest, b.total_paid],
        backgroundColor: [
          'rgba(59,130,246,0.8)',
          'rgba(245,158,11,0.8)',
          'rgba(16,185,129,0.8)'
        ]
      }
    ]
  }
})

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
        po_received: 'Purchase Order Diterima'
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

          <!-- Distribusi Keseluruhan Data Sistem -->
          <div class="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
            <UCard
              v-for="key in distributionKeys"
              :key="key"
            >
              <template #header>
                <div class="flex items-center justify-between">
                  <p class="font-medium flex items-center gap-2">
                    <UIcon
                      :name="distributionIcons[key] ?? 'i-lucide-chart-pie'"
                      class="size-4 text-primary"
                    />
                    {{ distributionLabels[key] ?? key }}
                  </p>
                  <p class="text-xs text-muted">
                    {{
                      ((data?.distributions || {})[key] || []).length
                    }} kategori
                  </p>
                </div>
              </template>
              <AdminPieChart
                v-if="distributionChart(key).values.length"
                :labels="distributionChart(key).labels"
                :data="distributionChart(key).values"
                :background-color="distributionChart(key).colors"
                :height="220"
                @segment-click="(p) => onDistributionSegmentClick(key, p)"
              />
              <UEmpty v-else icon="i-lucide-chart-pie" title="Belum ada data" />
            </UCard>
          </div>

          <!-- Akuntansi -->
          <div v-if="accounting" class="space-y-6">
            <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <UCard
                v-for="card in accountingCards"
                :key="card.title"
                variant="subtle"
              >
                <template #leading>
                  <UIcon :name="card.icon" class="size-5" :class="card.color" />
                </template>
                <template #title>
                  {{ card.title }}
                </template>
                <p class="text-2xl font-semibold tabular-nums">
                  {{ card.value }}
                </p>
              </UCard>
            </div>

            <div class="grid gap-3 sm:grid-cols-4">
              <UCard
                v-for="c in accountingCountCards"
                :key="c.title"
                variant="subtle"
                class="text-center"
              >
                <UIcon :name="c.icon" class="size-5 text-primary mx-auto mb-1" />
                <p class="text-2xl font-semibold tabular-nums">
                  {{ c.value }}
                </p>
                <p class="text-xs text-muted mt-1">
                  {{ c.title }}
                </p>
              </UCard>
            </div>

            <div class="grid gap-4 lg:grid-cols-2">
              <UCard v-if="balanceSheetChart">
                <template #header>
                  <p class="font-medium">Neraca (Balance Sheet)</p>
                </template>
                <AdminBarChart
                  :labels="balanceSheetChart.labels"
                  :datasets="balanceSheetChart.datasets"
                  :height="200"
                />
              </UCard>

              <UCard v-if="cashflowChart">
                <template #header>
                  <p class="font-medium">Rekap Arus Kas</p>
                </template>
                <AdminBarChart
                  :labels="cashflowChart.labels"
                  :datasets="cashflowChart.datasets"
                  :height="200"
                />
              </UCard>

              <UCard v-if="dailyCashChart">
                <template #header>
                  <p class="font-medium">Kas Harian</p>
                </template>
                <AdminBarChart
                  :labels="dailyCashChart.labels"
                  :datasets="dailyCashChart.datasets"
                  :height="200"
                />
              </UCard>

              <UCard v-if="costRecapChart">
                <template #header>
                  <p class="font-medium">Rekap Biaya per Akun</p>
                </template>
                <AdminBarChart
                  :labels="costRecapChart.labels"
                  :datasets="costRecapChart.datasets"
                  :height="200"
                />
              </UCard>

              <UCard v-if="monitoringChart" class="lg:col-span-2">
                <template #header>
                  <p class="font-medium">Monitoring per Bulan ({{ new Date().getFullYear() }})</p>
                </template>
                <AdminBarChart
                  :labels="monitoringChart.labels"
                  :datasets="monitoringChart.datasets"
                  :height="220"
                />
              </UCard>

              <UCard v-if="bankInterestChart">
                <template #header>
                  <p class="font-medium">Rekap Bunga Bank</p>
                </template>
                <AdminBarChart
                  :labels="bankInterestChart.labels"
                  :datasets="bankInterestChart.datasets"
                  :height="200"
                />
              </UCard>
            </div>

            <UCard>
              <template #header>
                <div class="flex items-center justify-between">
                  <p class="font-medium">
                    Jurnal Terbaru
                  </p>
                  <UButton
                    to="/accounting/jurnal-umum"
                    size="sm"
                    variant="ghost"
                    color="primary"
                  >
                    Lihat Semua
                  </UButton>
                </div>
              </template>

              <div class="flex flex-col divide-y divide-default">
                <div
                  v-for="journal in accounting.recent_journals ?? []"
                  :key="journal.id"
                  class="flex items-center justify-between gap-2 py-2"
                >
                  <div class="min-w-0">
                    <p class="truncate font-medium">
                      {{ journal.description }}
                    </p>
                    <p class="text-xs text-neutral-500 dark:text-neutral-400">
                      {{ journal.entry_number }}
                      · {{ formatDate(journal.entry_date) }}
                    </p>
                  </div>
                  <div class="shrink-0 text-right">
                    <p class="font-semibold">
                      {{ formatCurrency(totalDebit(journal)) }}
                    </p>
                    <p class="text-xs text-neutral-500 dark:text-neutral-400">
                      {{ journal.lines.length }} baris
                    </p>
                  </div>
                </div>

                <p
                  v-if="!accounting.recent_journals?.length"
                  class="py-6 text-center text-sm text-neutral-500"
                >
                  Belum ada jurnal
                </p>
              </div>
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
