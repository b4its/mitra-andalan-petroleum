<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import AdminBarChart from '~/components/admin/charts/AdminBarChart.vue'
import AdminPieChart from '~/components/admin/charts/AdminPieChart.vue'

definePageMeta({ layout: 'admin' })

const UBadge = resolveComponent('UBadge')

const { data, pending } = useAsyncData('admin-operations', async () => {
  const { get } = useApi()
  const [stats, doResult] = await Promise.all([
    get<any>('/stats/admin'),
    get<any>('/delivery-orders', { page: 1, page_size: 10 })
  ])
  return { stats, doList: doResult?.items || [] }
}, { default: () => ({ stats: null, doList: [] }), lazy: true })

const doList = computed(() => data.value?.doList || [])

const doStats = computed(() => {
  if (!data.value?.stats?.stats) return []
  return data.value.stats.stats.filter((s: any) => s.title === 'Delivery Order')
})

const doTrendMonths = computed(() =>
  data.value?.stats?.monthly_trends?.map((m: any) => m.month.split(' ')[0]) || []
)

const doTrendData = computed(() =>
  data.value?.stats?.monthly_trends?.map((m: any) => m.delivery_orders) || []
)

const doDistLabels = computed(() =>
  data.value?.stats?.do_status_distribution?.map((d: any) => d.label) || []
)

const doDistValues = computed(() =>
  data.value?.stats?.do_status_distribution?.map((d: any) => d.value) || []
)

const columns: TableColumn<any>[] = [
  { accessorKey: 'do_number', header: 'Nomor DO' },
  { accessorKey: 'transport_name', header: 'Transportir' },
  {
    accessorKey: 'fuel_total',
    header: 'Total',
    cell: ({ row }: any) =>
      new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(row.getValue('fuel_total'))
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }: any) => {
      const color: Record<string, string> = { created: 'warning', document_returned: 'success' }
      return h(UBadge, { class: 'capitalize', variant: 'subtle', color: color[row.getValue('status') as string] || 'neutral' }, () => row.getValue('status'))
    }
  }
]
</script>

<template>
  <div class="w-full max-w-full overflow-x-hidden p-4 sm:p-6 space-y-4 sm:space-y-6">
    <UDashboardNavbar title="Overview Operations" :ui="{ right: 'gap-2' }">
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
    <h1 class="text-3xl font-bold">
      Operations - Rekap Keseluruhan
    </h1>

    <div v-if="pending" class="flex items-center justify-center py-20">
      <UIcon name="i-lucide-loader" class="size-8 animate-spin text-muted" />
    </div>

    <template v-else>
      <div v-if="doStats.length" class="grid grid-cols-2 gap-4 sm:grid-cols-3">
        <UCard v-for="s in doStats" :key="s.title" variant="subtle">
          <template #title>
            <p class="truncate text-xs text-muted">
              {{ s.title }}
            </p>
          </template>
          <span class="text-2xl font-semibold">{{ s.value }}</span>
        </UCard>
      </div>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <UCard>
          <template #header>
            <p class="text-sm font-medium">
              Tren Delivery Order
            </p>
          </template>
          <AdminBarChart
            v-if="doTrendMonths.length"
            :labels="doTrendMonths"
            :datasets="[
              { label: 'Delivery Order', data: doTrendData, backgroundColor: 'rgba(245,158,11,0.7)' }
            ]"
          />
          <div v-else class="flex h-64 items-center justify-center text-sm text-muted">
            Belum ada data
          </div>
        </UCard>

        <UCard>
          <template #header>
            <p class="text-sm font-medium">
              Status Delivery Order
            </p>
          </template>
          <AdminPieChart
            v-if="doDistLabels.length"
            :labels="doDistLabels"
            :data="doDistValues"
          />
          <div v-else class="flex h-64 items-center justify-center text-sm text-muted">
            Belum ada data
          </div>
        </UCard>
      </div>

      <UCard>
        <template #header>
          <p class="text-sm font-medium">
            Delivery Order Terbaru
          </p>
        </template>
        <UTable :data="doList" :columns="columns" class="shrink-0" />
      </UCard>
    </template>
  </div>
</template>
