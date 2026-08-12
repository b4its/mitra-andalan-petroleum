<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { ExportColumn } from '~/composables/useExport'
import type { MonitoringResponse, MonitoringRow } from '~/types/accounting'

const { get } = useApi()
const { toCSV, toExcel, toPDF } = useExport()

const dateFrom = ref('')
const dateTo = ref('')

const exportColumns: ExportColumn<MonitoringRow>[] = [
  { header: 'Bulan', accessor: (row: MonitoringRow) => row.bulan },
  { header: 'Invoice', accessor: (row: MonitoringRow) => row.invoice },
  { header: 'Modal Elnusa', accessor: (row: MonitoringRow) => row.modal_elnusa },
  { header: 'OAT', accessor: (row: MonitoringRow) => row.oat },
  { header: 'Margin Kotor', accessor: (row: MonitoringRow) => row.gross_margin },
  { header: 'Penghasilan', accessor: (row: MonitoringRow) => row.penghasilan },
  { header: 'Operasional', accessor: (row: MonitoringRow) => row.operasional },
  { header: 'Fee Manajemen', accessor: (row: MonitoringRow) => row.fee_manajemen }
]

function onExport(format: 'excel' | 'pdf' | 'csv') {
  if (!data.value) return
  const rangeLabel = `${dateFrom.value || 'awal'}_${dateTo.value || 'akhir'}`
  const filename = `rekap-monitoring-${rangeLabel}`
  const totals = [
    { label: 'Total Penghasilan', value: data.value.total_penghasilan },
    { label: 'Total Margin Kotor', value: data.value.total_gross_margin }
  ]
  if (format === 'excel') toExcel(filename, 'Rekap Monitoring', exportColumns, data.value.rows)
  else if (format === 'pdf') toPDF(filename, `Rekap Monitoring ${dateFrom.value} - ${dateTo.value}`, exportColumns, data.value.rows, { totals })
  else toCSV(filename, exportColumns, data.value.rows)
}

const { data, pending } = await useAsyncData(
  'accounting-monitoring',
  () => {
    const params: Record<string, string> = {}
    if (dateFrom.value) params.date_from = dateFrom.value
    if (dateTo.value) params.date_to = dateTo.value
    return get<MonitoringResponse>('/accounting/monitoring', params)
  },
  { default: () => null, watch: [dateFrom, dateTo], server: false }
)

const columns: TableColumn<MonitoringRow>[] = [
  {
    accessorKey: 'bulan',
    header: 'Bulan',
    cell: ({ row }) => h('span', { class: 'font-medium' }, row.getValue('bulan'))
  },
  {
    accessorKey: 'invoice',
    header: 'Invoice',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => formatCurrency(row.getValue('invoice'))
  },
  {
    accessorKey: 'modal_elnusa',
    header: 'Modal Elnusa',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => formatCurrency(row.getValue('modal_elnusa'))
  },
  {
    accessorKey: 'oat',
    header: 'OAT',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => formatCurrency(row.getValue('oat'))
  },
  {
    accessorKey: 'gross_margin',
    header: 'Margin Kotor',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => {
      const val = Number(row.getValue('gross_margin'))
      return h('span', { class: val >= 0 ? 'text-success font-semibold' : 'text-error font-semibold' }, formatCurrency(val))
    }
  },
  {
    accessorKey: 'penghasilan',
    header: 'Penghasilan',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => h('span', { class: 'font-semibold text-success' }, formatCurrency(row.getValue('penghasilan')))
  },
  {
    accessorKey: 'operasional',
    header: 'Operasional',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => h('span', { class: 'text-error' }, formatCurrency(row.getValue('operasional')))
  },
  {
    accessorKey: 'fee_manajemen',
    header: 'Fee Manajemen',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => formatCurrency(row.getValue('fee_manajemen'))
  }
]

definePageMeta({ layout: 'accounting' })
</script>

<template>
  <UDashboardPanel id="accounting-rekap-monitoring">
    <template #header>
      <UDashboardNavbar>
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">
              Rekap Monitoring
            </p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Monitoring pendapatan, biaya, dan margin per bulan
            </p>
          </div>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-4 lg:p-6">
        <section class="flex flex-col lg:gap-4">
          <UCard>
            <div class="flex flex-wrap items-end gap-3">
              <UFormField label="Dari Tanggal">
                <UInput v-model="dateFrom" type="date" />
              </UFormField>
              <UFormField label="Sampai Tanggal">
                <UInput v-model="dateTo" type="date" />
              </UFormField>
              <UDropdownMenu
                :items="[
                  { type: 'label', label: 'Ekspor Data' },
                  { type: 'separator' },
                  { label: 'Ekspor ke Excel', icon: 'i-lucide-file-spreadsheet', disabled: !data, onSelect: () => onExport('excel') },
                  { label: 'Ekspor ke PDF', icon: 'i-lucide-file-text', disabled: !data, onSelect: () => onExport('pdf') },
                  { label: 'Ekspor ke CSV', icon: 'i-lucide-file-down', disabled: !data, onSelect: () => onExport('csv') }
                ]"
              >
                <UButton
                  icon="i-lucide-download"
                  color="neutral"
                  variant="soft"
                  :disabled="!data"
                >
                  Export
                </UButton>
              </UDropdownMenu>
            </div>
          </UCard>

          <div v-if="pending" class="flex flex-col gap-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <USkeleton v-for="i in 4" :key="i" class="h-24 rounded-lg" />
            </div>
            <USkeleton class="h-64 rounded-lg" />
          </div>
          <template v-else-if="data && data.rows.length">
            <!-- Summary Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <UCard color="success" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total Penghasilan
                </p>
                <p class="text-2xl font-bold">
                  {{ formatCurrency(data.total_penghasilan) }}
                </p>
              </UCard>
              <UCard color="error" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total Operasional
                </p>
                <p class="text-2xl font-bold">
                  {{ formatCurrency(data.total_operasional) }}
                </p>
              </UCard>
              <UCard color="primary" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total Margin Kotor
                </p>
                <p class="text-2xl font-bold">
                  {{ formatCurrency(data.total_gross_margin) }}
                </p>
              </UCard>
              <UCard color="info" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total OAT
                </p>
                <p class="text-2xl font-bold">
                  {{ formatCurrency(data.total_oat) }}
                </p>
              </UCard>
            </div>

            <UCard class="overflow-x-auto">
              <UTable
                :data="data.rows"
                :columns="columns"
                :ui="{
                  base: 'table-fixed border-separate border-spacing-0 min-w-[800px]',
                  thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
                  tbody: '[&>tr]:last:[&>td]:border-b-0',
                  th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
                  td: 'border-b border-default'
                }"
              />
            </UCard>

            <!-- Total Row -->
            <UCard color="neutral" variant="subtle">
              <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-4 text-center">
                <div>
                  <p class="text-xs text-muted">
                    Invoice
                  </p>
                  <p class="font-bold">
                    {{ data.total_invoice }}
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted">
                    Modal Elnusa
                  </p>
                  <p class="font-bold">
                    {{ formatCurrency(data.total_modal) }}
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted">
                    OAT
                  </p>
                  <p class="font-bold">
                    {{ formatCurrency(data.total_oat) }}
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted">
                    Margin Kotor
                  </p>
                  <p class="font-bold">
                    {{ formatCurrency(data.total_gross_margin) }}
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted">
                    Penghasilan
                  </p>
                  <p class="font-bold">
                    {{ formatCurrency(data.total_penghasilan) }}
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted">
                    Operasional
                  </p>
                  <p class="font-bold">
                    {{ formatCurrency(data.total_operasional) }}
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted">
                    Fee Manajemen
                  </p>
                  <p class="font-bold">
                    {{ formatCurrency(data.total_fee_manajemen) }}
                  </p>
                </div>
              </div>
            </UCard>
          </template>

          <UAlert
            v-else-if="!pending"
            title="Belum Ada Data"
            description="Belum ada data monitoring untuk tahun ini."
            icon="i-lucide-info"
            color="info"
            variant="soft"
          />
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>
