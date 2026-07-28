<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import AdminBarChart from '~/components/admin/charts/AdminBarChart.vue'
import AdminPieChart from '~/components/admin/charts/AdminPieChart.vue'

definePageMeta({ layout: 'admin' })

const presets = [
  { label: '1 Minggu', days: 7 },
  { label: '2 Minggu', days: 14 },
  { label: '3 Minggu', days: 21 },
  { label: '1 Bulan', days: 30 }
]
const dateTo = ref(new Date().toISOString())
const dateFrom = ref(new Date(Date.now() - 30 * 86400000).toISOString())
const selectedMetric = ref<any>()
const modalOpen = ref(false)
const { get } = useApi()

const { data, pending, error, refresh } = await useAsyncData(
  'admin-system-analytics',
  () => get<any>('/stats/admin', { date_from: dateFrom.value, date_to: dateTo.value }),
  { default: () => null, watch: [dateFrom, dateTo] }
)

function applyPreset(days: number) {
  dateTo.value = new Date().toISOString()
  dateFrom.value = new Date(Date.now() - days * 86400000).toISOString()
}

function showMetric(metric: any) {
  selectedMetric.value = metric
  modalOpen.value = true
}

function reloadDashboard() {
  refresh()
}

const trendLabels = computed(() => data.value?.trends?.map((item: any) => item.label) || [])
const trendDatasets = computed(() => [
  { label: 'OL', data: data.value?.trends?.map((item: any) => item.offering_letters) || [], backgroundColor: 'rgba(59, 130, 246, .7)' },
  { label: 'PO', data: data.value?.trends?.map((item: any) => item.purchase_orders) || [], backgroundColor: 'rgba(16, 185, 129, .7)' },
  { label: 'DO', data: data.value?.trends?.map((item: any) => item.delivery_orders) || [], backgroundColor: 'rgba(245, 158, 11, .7)' },
  { label: 'Invoice', data: data.value?.trends?.map((item: any) => item.invoices) || [], backgroundColor: 'rgba(139, 92, 246, .7)' }
])
const invoiceLabels = computed(() => data.value?.distributions?.invoices?.map((item: any) => item.label) || [])
const invoiceValues = computed(() => data.value?.distributions?.invoices?.map((item: any) => item.value) || [])
const notificationColumns: TableColumn<any>[] = [
  { accessorKey: 'title', header: 'Notifikasi' },
  { accessorKey: 'subtitle', header: 'Pesan' },
  { accessorKey: 'created_at', header: 'Waktu', cell: ({ row }) => formatDate(row.getValue('created_at')) }
]
const activityColumns: TableColumn<any>[] = [
  { accessorKey: 'domain', header: 'Domain' },
  { accessorKey: 'title', header: 'Dokumen' },
  { accessorKey: 'subtitle', header: 'Status' },
  { accessorKey: 'created_at', header: 'Waktu', cell: ({ row }) => formatDate(row.getValue('created_at')) }
]

function metricValue(metric: any) {
  return metric.unit === 'currency' ? formatCurrency(metric.value) : formatNumber(metric.value)
}
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
          <div class="flex flex-wrap items-center gap-2 p-4">
            <UButton
              v-for="preset in presets"
              :key="preset.days"
              size="sm"
              color="neutral"
              variant="soft"
              @click="applyPreset(preset.days)"
            >
              {{ preset.label }}
            </UButton>
            <UInput v-model="dateFrom" type="datetime-local" aria-label="Tanggal awal" />
            <span class="text-muted">sampai</span>
            <UInput v-model="dateTo" type="datetime-local" aria-label="Tanggal akhir" />
          </div>
        </template>
      </UDashboardToolbar>
    </template>

    <template #body>
      <div class="space-y-6 p-4 lg:p-6">
        <div>
          <h1 class="text-2xl font-semibold">
            Monitoring Keseluruhan Sistem
          </h1>
          <p class="mt-1 text-sm text-muted">
            Klik kartu untuk melihat record dan alasan pembentuk nilainya.
          </p>
        </div>
        <UAlert
          v-if="error"
          color="error"
          title="Gagal memuat dashboard"
          :description="error.message"
        />
        <div v-else-if="pending" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <USkeleton v-for="item in 12" :key="item" class="h-32" />
        </div>
        <template v-else>
          <UPageGrid class="sm:grid-cols-2 xl:grid-cols-4">
            <UPageCard
              v-for="metric in data?.metrics || []"
              :key="metric.key"
              variant="subtle"
              class="cursor-pointer transition hover:ring-2 hover:ring-primary"
              @click="showMetric(metric)"
            >
              <template #leading>
                <UIcon :name="metric.icon" class="size-5 text-primary" />
              </template>
              <template #title>
                {{ metric.title }}
              </template>
              <p class="text-2xl font-semibold">
                {{ metricValue(metric) }}
              </p>
              <p class="mt-2 text-xs text-muted">
                {{ metric.description }}
              </p>
            </UPageCard>
          </UPageGrid>
          <div class="grid gap-6 xl:grid-cols-3">
            <UCard class="xl:col-span-2">
              <template #header>
                <p class="font-medium">
                  Tren Dokumen per Minggu
                </p>
              </template><AdminBarChart v-if="trendLabels.length" :labels="trendLabels" :datasets="trendDatasets" /><UEmpty v-else icon="i-lucide-chart-no-axes-combined" title="Belum ada tren" />
            </UCard>
            <UCard>
              <template #header>
                <p class="font-medium">
                  Status Invoice
                </p>
              </template><AdminPieChart v-if="invoiceLabels.length" :labels="invoiceLabels" :data="invoiceValues" /><UEmpty v-else icon="i-lucide-chart-pie" title="Belum ada status" />
            </UCard>
          </div>
          <div class="grid gap-6 xl:grid-cols-2">
            <UCard>
              <template #header>
                <p class="font-medium">
                  Notifikasi Sistem
                </p>
              </template><UTable :data="data?.notifications || []" :columns="notificationColumns" /><UEmpty v-if="!data?.notifications?.length" icon="i-lucide-bell-off" title="Tidak ada notifikasi" />
            </UCard>
            <UCard>
              <template #header>
                <p class="font-medium">
                  Aktivitas Dokumen Terbaru
                </p>
              </template><UTable :data="data?.activities || []" :columns="activityColumns" /><UEmpty v-if="!data?.activities?.length" icon="i-lucide-history" title="Tidak ada aktivitas" />
            </UCard>
          </div>
        </template>
      </div>
    </template>
  </UDashboardPanel>
  <AdminDrilldownModal
    v-if="selectedMetric"
    v-model:open="modalOpen"
    :metric="selectedMetric"
    :date-from="dateFrom"
    :date-to="dateTo"
  />
</template>
