<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { ExportColumn } from '~/composables/useExport'
import type { AccountingIncomeExpenseRow, AccountingAccount } from '~/types/accounting'

const { get } = useApi()
const { toCSV, toExcel, toPDF } = useExport()

const entryModalOpen = ref(false)

const dateFrom = ref('')
const dateTo = ref('')
const search = ref('')
const debouncedSearch = refDebounced(search, 300)

const accountFilters = ref<string[]>([])
const { data: accounts } = await useAsyncData(
  'accounting-accounts-options-pemasukan',
  () => get<AccountingAccount[]>('/accounting/accounts'),
  { default: () => [], server: false }
)
const accountItems = computed(() => accounts.value.map(a => ({ label: `${a.code} · ${a.name}`, value: a.id })))

const exportColumns: ExportColumn<AccountingIncomeExpenseRow>[] = [
  { header: 'Tanggal', accessor: (row: AccountingIncomeExpenseRow) => formatDate(row.entry_date) },
  { header: 'Nomor Jurnal', accessor: (row: AccountingIncomeExpenseRow) => row.entry_number },
  { header: 'Deskripsi', accessor: (row: AccountingIncomeExpenseRow) => row.description },
  { header: 'Akun', accessor: (row: AccountingIncomeExpenseRow) => `${row.account_code} · ${row.account_name}` },
  { header: 'Nominal', accessor: (row: AccountingIncomeExpenseRow) => row.amount }
]

function onExport(format: 'excel' | 'pdf' | 'csv') {
  const filename = `pemasukan-${new Date().toISOString().slice(0, 10)}`
  const data = rows.value.items
  const totals = [{ label: 'Total Pemasukan', value: totalAmount.value }]
  if (format === 'excel') toExcel(filename, 'Pemasukan', exportColumns, data)
  else if (format === 'pdf') toPDF(filename, 'Pemasukan', exportColumns, data, { subtitle: 'Mutasi kredit pada akun pendapatan', totals })
  else toCSV(filename, exportColumns, data)
}

const { data: rows, refresh, pending } = await useAsyncData(
  'accounting-income',
  async () => {
    const params: Record<string, string | number | string[]> = { page: 1, page_size: 50 }
    if (dateFrom.value) params.date_from = dateFrom.value
    if (dateTo.value) params.date_to = dateTo.value
    if (debouncedSearch.value) params.search = debouncedSearch.value
    if (accountFilters.value.length) params.account_ids = accountFilters.value
    const res = await get<{ items: AccountingIncomeExpenseRow[], total: number }>(
      '/accounting/income',
      params
    )
    return res
  },
  { default: () => ({ items: [], total: 0 }), watch: [debouncedSearch, dateFrom, dateTo, accountFilters], server: false }
)

// ── Pagination (5 per halaman) ────────────────────────────────
const page = ref(1)
const PAGE_SIZE = 5
const pagedItems = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE
  return (rows.value.items || []).slice(start, start + PAGE_SIZE)
})
watch([debouncedSearch, dateFrom, dateTo, accountFilters], () => {
  page.value = 1
})

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
        { class: 'font-semibold text-success' },
        formatCurrency(row.getValue('amount'))
      )
  }
]

definePageMeta({ layout: 'accounting' })
</script>

<template>
  <UDashboardPanel id="accounting-pemasukan">
    <template #header>
      <UDashboardNavbar>
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">
              Pemasukan
            </p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Mutasi kredit pada akun pendapatan
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
                  placeholder="Cari nomor jurnal, deskripsi..."
                  class="w-64"
                />
                <USelectMenu
                  v-model="accountFilters"
                  :items="accountItems"
                  value-key="value"
                  multiple
                  searchable
                  :search-input="{ placeholder: 'Cari akun...' }"
                  placeholder="Semua Akun"
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
                    { label: 'Ekspor ke Excel', icon: 'i-lucide-file-spreadsheet', onSelect: () => onExport('excel') },
                    { label: 'Ekspor ke PDF', icon: 'i-lucide-file-text', onSelect: () => onExport('pdf') },
                    { label: 'Ekspor ke CSV', icon: 'i-lucide-file-down', onSelect: () => onExport('csv') }
                  ]"
                >
                  <UButton icon="i-lucide-download" color="neutral" variant="soft">
                    Export
                  </UButton>
                </UDropdownMenu>
                <UButton
                  icon="i-lucide-plus"
                  color="primary"
                  @click="entryModalOpen = true"
                >
                  Tambah Pemasukan
                </UButton>
              </div>
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
                  Total Pemasukan
                </p>
                <p class="mt-1 text-xl font-bold text-success">
                  {{ formatCurrency(totalAmount) }}
                </p>
              </UCard>
            </div>

            <UCard>
              <UTable
                :data="pagedItems"
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
                v-if="rows.items.length > PAGE_SIZE"
                class="flex justify-end border-t border-default pt-4 px-4"
              >
                <UPagination
                  v-model="page"
                  :items-per-page="PAGE_SIZE"
                  :total="rows.items.length"
                />
              </div>
              <p
                v-if="rows.items.length === 0"
                class="py-6 text-center text-sm text-neutral-500"
              >
                Belum ada data pemasukan
              </p>
            </UCard>
          </template>
        </section>

        <AccountingEntryModal
          v-model:open="entryModalOpen"
          mode="income"
          @saved="() => refresh()"
        />
      </div>
    </template>
  </UDashboardPanel>
</template>
