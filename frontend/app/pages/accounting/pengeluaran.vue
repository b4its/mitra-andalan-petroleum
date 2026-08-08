<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { ExportColumn } from '~/composables/useExport'
import type { AccountingIncomeExpenseRow } from '~/types/accounting'

const { get } = useApi()
const { toCSV, toExcel, toPDF } = useExport()

const dateFrom = ref('')
const dateTo = ref('')

const exportColumns: ExportColumn[] = [
  { header: 'Tanggal', accessor: (row: AccountingIncomeExpenseRow) => formatDate(row.entry_date) },
  { header: 'Nomor Jurnal', accessor: (row: AccountingIncomeExpenseRow) => row.entry_number },
  { header: 'Deskripsi', accessor: (row: AccountingIncomeExpenseRow) => row.description },
  { header: 'Akun', accessor: (row: AccountingIncomeExpenseRow) => `${row.account_code} · ${row.account_name}` },
  { header: 'Nominal', accessor: (row: AccountingIncomeExpenseRow) => row.amount }
]

function onExport(format: 'excel' | 'pdf' | 'csv') {
  const filename = `pengeluaran-${new Date().toISOString().slice(0, 10)}`
  const data = rows.value.items
  const totals = [{ label: 'Total Pengeluaran', value: totalAmount.value }]
  if (format === 'excel') toExcel(filename, 'Pengeluaran', exportColumns, data)
  else if (format === 'pdf') toPDF(filename, 'Pengeluaran', exportColumns, data, { subtitle: 'Mutasi debit pada akun beban', totals })
  else toCSV(filename, exportColumns, data)
}

const { data: rows, refresh, pending } = await useAsyncData(
  'accounting-expenses',
  async () => {
    const params: Record<string, string | number> = { page: 1, page_size: 50 }
    if (dateFrom.value) params.date_from = dateFrom.value
    if (dateTo.value) params.date_to = dateTo.value
    const res = await get<{ items: AccountingIncomeExpenseRow[], total: number }>(
      '/accounting/expenses',
      params
    )
    return res
  },
  { default: () => ({ items: [], total: 0 }), server: false }
)

const totalAmount = computed(() =>
  (rows.value.items ?? []).reduce((sum, row) => sum + (row.amount || 0), 0)
)

const columns: TableColumn<AccountingIncomeExpenseRow>[] = [
  {
    accessorKey: 'entry_date',
    header: 'Tanggal',
    cell: ({ row }) => `${formatDate(row.getValue('entry_date'))}`
  },
  {
    accessorKey: 'entry_number',
    header: 'Nomor Jurnal',
    cell: ({ row }) => `${row.getValue('entry_number')}`
  },
  {
    accessorKey: 'description',
    header: 'Deskripsi',
    cell: ({ row }) => {
      const desc = row.getValue('description') as string
      return h(
        'span',
        { class: 'truncate block max-w-72' },
        desc
      )
    }
  },
  {
    accessorKey: 'account_code',
    header: 'Akun',
    meta: {
      class: { th: 'text-center', td: 'text-center' }
    },
    cell: ({ row }) =>
      `${row.original.account_code} · ${row.original.account_name}`
  },
  {
    accessorKey: 'amount',
    header: 'Nominal',
    meta: {
      class: { th: 'text-right', td: 'text-right' }
    },
    cell: ({ row }) =>
      h(
        'span',
        { class: 'font-semibold text-error' },
        formatCurrency(row.getValue('amount'))
      )
  }
]

definePageMeta({ layout: 'accounting' })
</script>

<template>
  <UDashboardPanel id="accounting-pengeluaran">
    <template #header>
      <UDashboardNavbar>
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">Pengeluaran</p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Mutasi debit pada akun beban
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
            { label: 'Export to Excel', icon: 'i-lucide-file-spreadsheet', onSelect: () => onExport('excel') },
            { label: 'Export to PDF', icon: 'i-lucide-file-text', onSelect: () => onExport('pdf') },
            { label: 'Export to CSV', icon: 'i-lucide-file-down', onSelect: () => onExport('csv') }
          ]"
        >
          <UButton icon="i-lucide-download" color="neutral" variant="soft">
            Export
          </UButton>
        </UDropdownMenu>
      </div>
    </UCard>

    <div v-if="pending" class="flex flex-col gap-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <USkeleton v-for="i in 2" :key="i" class="h-24 rounded-lg" />
      </div>
      <USkeleton class="h-64 rounded-lg" />
    </div>
    <template v-else>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <UCard>
        <p class="text-sm text-neutral-500 dark:text-neutral-400">
          Total Transaksi
        </p>
        <p class="mt-1 text-xl font-bold">
          {{ rows.total }} transaksi
        </p>
      </UCard>
      <UCard>
        <p class="text-sm text-neutral-500 dark:text-neutral-400">
          Total Pengeluaran
        </p>
        <p class="mt-1 text-xl font-bold text-error">
          {{ formatCurrency(totalAmount) }}
        </p>
      </UCard>
    </div>

    <UCard>
      <UTable
        :data="rows.items"
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
        v-if="rows.items.length === 0"
        class="py-6 text-center text-sm text-neutral-500"
      >
        Belum ada data pengeluaran
      </p>
    </UCard>
    </template>
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>
