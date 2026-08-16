<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { ExportColumn } from '~/composables/useExport'
import type { DailyCashResponse, DailyCashRow, AccountingAccount } from '~/types/accounting'

const { get } = useApi()
const { toCSV, toExcel, toPDF } = useExport()

const dateFrom = ref('')
const dateTo = ref('')
const search = ref('')
const debouncedSearch = refDebounced(search, 300)

const accountFilters = ref<string[]>([])
const { data: accounts } = await useAsyncData(
  'accounting-accounts-options-kas-harian',
  () => get<AccountingAccount[]>('/accounting/accounts'),
  { default: () => [], server: false }
)
const accountItems = computed(() => accounts.value.map(a => ({ label: `${a.code} · ${a.name}`, value: a.id })))

const exportColumns: ExportColumn<DailyCashRow>[] = [
  { header: 'Tanggal', accessor: (row: DailyCashRow) => formatDate(row.entry_date) },
  { header: 'Deskripsi', accessor: (row: DailyCashRow) => row.description },
  { header: 'Akun', accessor: (row: DailyCashRow) => `${row.account_code} · ${row.account_name}` },
  { header: 'Debit', accessor: (row: DailyCashRow) => row.debit },
  { header: 'Kredit', accessor: (row: DailyCashRow) => row.credit },
  { header: 'Saldo', accessor: (row: DailyCashRow) => row.balance }
]

function onExport(format: 'excel' | 'pdf' | 'csv') {
  if (!data.value) return
  const filename = `kas-harian-${new Date().toISOString().slice(0, 10)}`
  const totals = [
    { label: 'Saldo Awal', value: data.value.opening_balance },
    { label: 'Saldo Akhir', value: data.value.closing_balance }
  ]
  if (format === 'excel') toExcel(filename, 'Kas Harian', exportColumns, data.value.rows)
  else if (format === 'pdf') toPDF(filename, 'Kas Harian', exportColumns, data.value.rows, { totals })
  else toCSV(filename, exportColumns, data.value.rows)
}

const { data, refresh, pending } = await useAsyncData(
  'accounting-daily-cash',
  async () => {
    const params: Record<string, string | string[]> = {}
    if (dateFrom.value) params.date_from = dateFrom.value
    if (dateTo.value) params.date_to = dateTo.value
    if (accountFilters.value.length) params.account_ids = accountFilters.value
    return get<DailyCashResponse>('/accounting/daily-cash', params)
  },
  { default: () => null, watch: [dateFrom, dateTo, accountFilters], server: false }
)

const filteredData = computed(() => {
  if (!data.value) return []
  if (!debouncedSearch.value) return data.value.rows
  const q = debouncedSearch.value.toLowerCase()
  return data.value.rows.filter((item: Record<string, unknown>) =>
    Object.values(item).some(v => String(v).toLowerCase().includes(q))
  )
})

const columns: TableColumn<DailyCashRow>[] = [
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
    accessorKey: 'account_code',
    header: 'Akun',
    cell: ({ row }) => `${row.original.account_code} · ${row.original.account_name}`
  },
  {
    accessorKey: 'debit',
    header: 'Debit (Masuk)',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => {
      const val = Number(row.getValue('debit'))
      return val > 0 ? h('span', { class: 'text-success font-medium' }, formatCurrency(val)) : '-'
    }
  },
  {
    accessorKey: 'credit',
    header: 'Kredit (Keluar)',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => {
      const val = Number(row.getValue('credit'))
      return val > 0 ? h('span', { class: 'text-error font-medium' }, formatCurrency(val)) : '-'
    }
  },
  {
    accessorKey: 'balance',
    header: 'Saldo',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => h('span', { class: 'font-semibold' }, formatCurrency(Number(row.getValue('balance'))))
  }
]

definePageMeta({ layout: 'accounting' })
</script>

<template>
  <UDashboardPanel id="accounting-kas-harian">
    <template #header>
      <UDashboardNavbar>
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">
              Kas Harian
            </p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Mutasi kas/bank harian dengan saldo berjalan
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
                  placeholder="Cari deskripsi, akun..."
                  class="w-64"
                />
                <USelectMenu
                  v-model="accountFilters"
                  :items="accountItems"
                  value-key="value"
                  multiple
                  searchable
                  searchable-placeholder="Cari akun..."
                  placeholder="Akun Kas/Bank"
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
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <USkeleton v-for="i in 4" :key="i" class="h-24 rounded-lg" />
            </div>
            <USkeleton class="h-64 rounded-lg" />
          </div>
          <template v-else-if="data">
            <!-- Summary Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <UCard color="neutral" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Saldo Awal
                </p>
                <p class="text-2xl font-bold">
                  {{ formatCurrency(data.opening_balance) }}
                </p>
              </UCard>
              <UCard color="success" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total Masuk
                </p>
                <p class="text-2xl font-bold">
                  {{ formatCurrency(data.total_debit) }}
                </p>
              </UCard>
              <UCard color="error" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total Keluar
                </p>
                <p class="text-2xl font-bold">
                  {{ formatCurrency(data.total_credit) }}
                </p>
              </UCard>
              <UCard color="primary" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Saldo Akhir
                </p>
                <p class="text-2xl font-bold">
                  {{ formatCurrency(data.closing_balance) }}
                </p>
              </UCard>
            </div>

            <UCard>
              <UTable
                :data="filteredData"
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
                Belum ada mutasi kas
              </p>
            </UCard>
          </template>

          <UAlert
            v-else-if="!pending"
            title="Pilih Periode"
            description="Gunakan filter tanggal di atas untuk menampilkan kas harian."
            icon="i-lucide-info"
            color="info"
            variant="soft"
          />
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>
