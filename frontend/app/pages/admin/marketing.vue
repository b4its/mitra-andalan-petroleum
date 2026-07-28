<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import AdminBarChart from '~/components/admin/charts/AdminBarChart.vue'
import AdminPieChart from '~/components/admin/charts/AdminPieChart.vue'

definePageMeta({ layout: 'admin' })

const UBadge = resolveComponent('UBadge')

const { data, pending } = useAsyncData('admin-marketing', async () => {
  const { get } = useApi()
  const [stats, olResult] = await Promise.all([
    get<any>('/stats/admin'),
    get<any>('/offering-letters', { page: 1, page_size: 10 })
  ])
  return { stats, olList: olResult?.items || [] }
}, { default: () => ({ stats: null, olList: [] }), lazy: true })

const olList = computed(() => data.value?.olList || [])

const olStats = computed(() => {
  if (!data.value?.stats?.stats) return []
  const all = data.value.stats.stats
  return all.filter((s: any) =>
    ['Surat Penawaran', 'Purchase Order'].includes(s.title)
  )
})

const olTrendMonths = computed(() =>
  data.value?.stats?.monthly_trends?.map((m: any) => m.month.split(' ')[0]) || []
)

const olTrendData = computed(() =>
  data.value?.stats?.monthly_trends?.map((m: any) => m.offering_letters) || []
)

const poTrendData = computed(() =>
  data.value?.stats?.monthly_trends?.map((m: any) => m.purchase_orders) || []
)

const olDistLabels = computed(() =>
  data.value?.stats?.ol_status_distribution?.map((d: any) => d.label) || []
)

const olDistValues = computed(() =>
  data.value?.stats?.ol_status_distribution?.map((d: any) => d.value) || []
)

const columns: TableColumn<any>[] = [
  { accessorKey: 'offering_letter_number', header: 'Nomor' },
  { accessorKey: 'receiver', header: 'Penerima' },
  {
    accessorKey: 'fuel_total_price',
    header: 'Total',
    cell: ({ row }: any) =>
      new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(row.getValue('fuel_total_price'))
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }: any) => {
      const color: Record<string, string> = { created: 'warning', under_revision: 'info', po_received: 'success' }
      return h(UBadge, { class: 'capitalize', variant: 'subtle', color: color[row.getValue('status') as string] || 'neutral' }, () => row.getValue('status'))
    }
  }
]
</script>

<template>

  <div class="w-full max-w-full overflow-x-hidden p-4 sm:p-6 space-y-4 sm:space-y-6">
    <UDashboardNavbar title="Overview Marketing" :ui="{ right: 'gap-2' }">
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
    <h1 class="text-2xl sm:text-3xl font-bold">
      Marketing - Rekap Keseluruhan
    </h1>

    <div v-if="pending" class="flex items-center justify-center py-20">
      <UIcon name="i-lucide-loader" class="size-8 animate-spin text-muted" />
    </div>

    <template v-else>
      <!-- 2. Stats Grid: Dibuat 1 kolom di mobile, 2 di tablet, 4 di desktop besar untuk mencegah teks terhimpit -->
      <div v-if="olStats.length" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <!-- Tambahkan min-w-0 untuk mencegah overflow dari text-truncate -->
        <UCard v-for="s in olStats" :key="s.title" variant="subtle" class="min-w-0">
          <template #title>
            <p class="truncate text-xs text-muted">
              {{ s.title }}
            </p>
          </template>
          <span class="text-2xl font-semibold">{{ s.value }}</span>
        </UCard>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:gap-6 lg:grid-cols-2">
        <!-- 3. Chart Cards: Tambahkan min-w-0 agar canvas chart tidak memaksa grid membesar melampaui layar -->
        <UCard class="min-w-0">
          <template #header>
            <p class="text-sm font-medium">
              Tren Surat Penawaran
            </p>
          </template>
          <!-- Pastikan Chart component Anda memiliki attribute responsive: true pada config Chart.js nya -->
          <AdminBarChart
            v-if="olTrendMonths.length"
            :labels="olTrendMonths"
            :datasets="[
              { label: 'Surat Penawaran', data: olTrendData, backgroundColor: 'rgba(59,130,246,0.7)' },
              { label: 'Purchase Order', data: poTrendData, backgroundColor: 'rgba(16,185,129,0.7)' }
            ]"
          />
          <div v-else class="flex h-64 items-center justify-center text-sm text-muted">
            Belum ada data
          </div>
        </UCard>

        <UCard class="min-w-0">
          <template #header>
            <p class="text-sm font-medium">
              Status Surat Penawaran
            </p>
          </template>
          <AdminPieChart
            v-if="olDistLabels.length"
            :labels="olDistLabels"
            :data="olDistValues"
          />
          <div v-else class="flex h-64 items-center justify-center text-sm text-muted">
            Belum ada data
          </div>
        </UCard>
      </div>

      <!-- 4. Table Card: Perbaikan utama pada layout tabel -->
      <UCard class="min-w-0 overflow-hidden">
        <template #header>
          <p class="text-sm font-medium">
            Surat Penawaran Terbaru
          </p>
        </template>
        
        <!-- Hapus class 'shrink-0', ganti dengan wrapper overflow-x-auto dan w-full -->
        <div class="w-full overflow-x-auto">
          <!-- Gunakan min-w-full agar tabel memenuhi ruang, namun bisa di-scroll jika layar terlalu kecil -->
          <UTable :data="olList" :columns="columns" class="min-w-full whitespace-nowrap" />
        </div>
      </UCard>
    </template>
  </div>
</template>
