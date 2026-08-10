<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { ExportColumn } from '~/composables/useExport'
import type { BankInterestResponse, BankInterestRow } from '~/types/accounting'

const { get } = useApi()
const { toCSV, toExcel, toPDF } = useExport()

const dateFrom = ref('')
const dateTo = ref('')

const exportColumns: ExportColumn<BankInterestRow>[] = [
  { header: 'Tanggal', accessor: (row: BankInterestRow) => formatDate(row.entry_date) },
  { header: 'Deskripsi', accessor: (row: BankInterestRow) => row.description },
  { header: 'Pokok Pinjaman', accessor: (row: BankInterestRow) => row.amount },
  { header: 'Bunga (%)', accessor: (row: BankInterestRow) => `${row.interest_rate}%` },
  { header: 'Hari', accessor: (row: BankInterestRow) => row.days },
  { header: 'Jumlah Bunga', accessor: (row: BankInterestRow) => row.interest_amount }
]

function onExport(format: 'excel' | 'pdf' | 'csv') {
  if (!data.value) return
  const filename = `rekap-bunga-bank-${new Date().toISOString().slice(0, 10)}`
  const totals = [
    { label: 'Total Pokok', value: data.value.total_principal },
    { label: 'Total Bunga', value: data.value.total_interest }
  ]
  if (format === 'excel') toExcel(filename, 'Rekap Bunga Bank', exportColumns, data.value.rows)
  else if (format === 'pdf') toPDF(filename, 'Rekap Bunga Bank', exportColumns, data.value.rows, { totals })
  else toCSV(filename, exportColumns, data.value.rows)
}

const { data, refresh, pending } = await useAsyncData(
  'accounting-bank-interest',
  async () => {
    const params: Record<string, string> = {}
    if (dateFrom.value) params.date_from = dateFrom.value
    if (dateTo.value) params.date_to = dateTo.value
    return get<BankInterestResponse>('/accounting/bank-interest', params)
  },
  { default: () => null, server: false }
)

const columns: TableColumn<BankInterestRow>[] = [
  {
    accessorKey: 'entry_date',
    header: 'Tanggal',
    cell: ({ row }) => formatDate(row.getValue('entry_date'))
  },
  {
    accessorKey: 'description',
    header: 'Deskripsi',
    cell: ({ row }) => {
      const desc = row.getValue('description') as string
      return h('span', { class: 'truncate block max-w-72' }, desc)
    }
  },
  {
    accessorKey: 'amount',
    header: 'Pokok Pinjaman',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => h('span', { class: 'font-medium' }, formatCurrency(Number(row.getValue('amount'))))
  },
  {
    accessorKey: 'interest_rate',
    header: 'Bunga (%)',
    meta: { class: { th: 'text-center', td: 'text-center' } },
    cell: ({ row }) => `${row.getValue('interest_rate')}%`
  },
  {
    accessorKey: 'days',
    header: 'Hari',
    meta: { class: { th: 'text-center', td: 'text-center' } },
    cell: ({ row }) => row.getValue('days')
  },
  {
    accessorKey: 'interest_amount',
    header: 'Jumlah Bunga',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => h('span', { class: 'font-semibold text-warning' }, formatCurrency(Number(row.getValue('interest_amount'))))
  }
]

definePageMeta({ layout: 'accounting' })
</script>

<template>
  <UDashboardPanel id="accounting-rekap-bunga-bank">
    <template #header>
      <UDashboardNavbar>
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">
              Rekap Bunga Bank
            </p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Rekap bunga bank: pinjaman, pembayaran, dan kalkulasi bunga
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
              <UButton
                icon="i-lucide-search"
                :loading="pending"
                @click="() => refresh()"
              >
                Tampilkan
              </UButton>
              <UDropdownMenu
                :items="[
                  { type: 'label', label: 'Export Data' },
                  { type: 'separator' },
                  { label: 'Export to Excel', icon: 'i-lucide-file-spreadsheet', disabled: !data, onSelect: () => onExport('excel') },
                  { label: 'Export to PDF', icon: 'i-lucide-file-text', disabled: !data, onSelect: () => onExport('pdf') },
                  { label: 'Export to CSV', icon: 'i-lucide-file-down', disabled: !data, onSelect: () => onExport('csv') }
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
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <USkeleton v-for="i in 3" :key="i" class="h-24 rounded-lg" />
            </div>
            <USkeleton class="h-64 rounded-lg" />
          </div>
          <template v-else-if="data">
            <!-- Summary Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <UCard color="info" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total Pokok Pinjaman
                </p>
                <p class="text-2xl font-bold">
                  {{ formatCurrency(data.total_principal) }}
                </p>
              </UCard>
              <UCard color="warning" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total Bunga
                </p>
                <p class="text-2xl font-bold">
                  {{ formatCurrency(data.total_interest) }}
                </p>
              </UCard>
              <UCard color="success" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total Pembayaran
                </p>
                <p class="text-2xl font-bold">
                  {{ formatCurrency(data.total_paid) }}
                </p>
              </UCard>
            </div>

            <UCard>
              <UTable
                :data="data.rows"
                :columns="columns"
                :ui="{
                  base: 'table-fixed border-separate border-spacing-0',
                  thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
                  tbody: '[&>tr]:last:[&>td]:border-b-0',
                  th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
                  td: 'border-b border-default'
                }"
              />
              <p
                v-if="!data.rows.length"
                class="py-6 text-center text-sm text-neutral-500"
              >
                Belum ada data bunga bank
              </p>
            </UCard>
          </template>

          <UAlert
            v-else-if="!pending"
            title="Pilih Periode"
            description="Gunakan filter tanggal di atas untuk menampilkan rekap bunga bank."
            icon="i-lucide-info"
            color="info"
            variant="soft"
          />
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>
