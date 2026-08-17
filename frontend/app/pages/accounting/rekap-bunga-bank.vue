<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { ExportColumn } from '~/composables/useExport'
import type { BankInterestResponse, BankInterestRow } from '~/types/accounting'

const { get } = useApi()
const { toCSV, toExcel, toPDF } = useExport()

const dateFrom = ref('')
const dateTo = ref('')
const search = ref('')
const debouncedSearch = refDebounced(search, 300)

const exportColumns: ExportColumn<BankInterestRow>[] = [
  { header: 'Tanggal', accessor: (row: BankInterestRow) => formatDate(row.entry_date) },
  { header: 'Akun', accessor: (row: BankInterestRow) => `${row.account_code} · ${row.account_name}` },
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

const filteredData = computed(() => {
  if (!data.value) return []
  if (!debouncedSearch.value) return data.value.rows
  const q = debouncedSearch.value.toLowerCase()
  return data.value.rows.filter((item: Record<string, unknown>) =>
    Object.values(item).some(v => String(v).toLowerCase().includes(q))
  )
})

// ── Pagination (5 per halaman) ────────────────────────────────
const page = ref(1)
const PAGE_SIZE = 5
const pagedData = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE
  return filteredData.value.slice(start, start + PAGE_SIZE)
})
watch(debouncedSearch, () => {
  page.value = 1
})

const columns: TableColumn<BankInterestRow>[] = [
  {
    accessorKey: 'entry_date',
    header: 'Tanggal',
    cell: ({ row }) => formatDate(row.getValue('entry_date'))
  },
  {
    accessorKey: 'account_code',
    header: 'Akun',
    cell: ({ row }) => {
      const code = row.getValue('account_code') as string
      const name = row.getValue('account_name') as string
      return h('div', { class: 'flex flex-col gap-0.5' }, [
        h('span', { class: 'text-xs font-medium text-muted' }, code || '—'),
        h('span', { class: 'text-xs text-muted' }, name || 'Alur Sistem Utama')
      ])
    }
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
            <div class="flex flex-col gap-3">
              <div class="flex flex-wrap items-end gap-3">
                <UInput
                  v-model="search"
                  icon="i-lucide-search"
                  placeholder="Cari deskripsi..."
                  class="w-64"
                />
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
              </div>
              <div class="flex flex-wrap justify-end gap-2">
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
                :data="pagedData"
                :columns="columns"
                :ui="{
                  base: 'table-fixed border-separate border-spacing-0',
                  thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
                  tbody: '[&>tr]:last:[&>td]:border-b-0',
                  th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
                  td: 'border-b border-default'
                }"
              />
              <div
                v-if="filteredData.length > PAGE_SIZE"
                class="flex justify-end border-t border-default pt-4 px-4"
              >
                <UPagination
                  v-model="page"
                  :items-per-page="PAGE_SIZE"
                  :total="filteredData.length"
                />
              </div>
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
