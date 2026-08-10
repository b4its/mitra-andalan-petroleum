<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { ExportColumn } from '~/composables/useExport'
import type {
  AccountingAccount,
  AccountingLedger,
  AccountingLedgerRow
} from '~/types/accounting'

const { get } = useApi()

const { toCSV, toExcel, toPDF } = useExport()

const exportColumns: ExportColumn<AccountingLedgerRow>[] = [
  { header: 'Tanggal', accessor: (row: AccountingLedgerRow) => formatDate(row.entry_date) },
  { header: 'Nomor Jurnal', accessor: (row: AccountingLedgerRow) => row.entry_number },
  { header: 'Deskripsi', accessor: (row: AccountingLedgerRow) => row.description },
  { header: 'Debit', accessor: (row: AccountingLedgerRow) => row.debit },
  { header: 'Kredit', accessor: (row: AccountingLedgerRow) => row.credit },
  { header: 'Saldo', accessor: (row: AccountingLedgerRow) => row.balance }
]

function onExport(format: 'excel' | 'pdf' | 'csv') {
  if (!ledger.value) return
  const account = ledger.value
  const filename = `buku-besar-${account.account_code}-${new Date().toISOString().slice(0, 10)}`
  const totals = [
    { label: 'Saldo Awal', value: account.opening_balance },
    { label: 'Saldo Akhir', value: account.closing_balance }
  ]
  if (format === 'excel') toExcel(filename, 'Buku Besar', exportColumns, account.rows)
  else if (format === 'pdf') toPDF(filename, `Buku Besar — ${account.account_code} · ${account.account_name}`, exportColumns, account.rows, { totals })
  else toCSV(filename, exportColumns, account.rows)
}

const { data: accounts, pending: pendingAccounts } = await useAsyncData(
  'accounting-accounts-ledger',
  () => get<AccountingAccount[]>('/accounting/accounts'),
  { default: () => [], server: false }
)

const accountItems = computed(() =>
  accounts.value.map(account => ({
    label: `${account.code} · ${account.name}`,
    value: account.id
  }))
)

const accountId = ref<string | undefined>(undefined)
const dateFrom = ref('')
const dateTo = ref('')

const { data: ledger, refresh, status } = await useAsyncData(
  'accounting-ledger',
  async () => {
    if (!accountId.value) return null
    const params: Record<string, string | number> = {
      account_id: accountId.value
    }
    if (dateFrom.value) params.date_from = dateFrom.value
    if (dateTo.value) params.date_to = dateTo.value
    return get<AccountingLedger>('/accounting/ledger', params)
  },
  { default: () => null, watch: [accountId], server: false }
)

async function onSearch() {
  await refresh()
}

const columns: TableColumn<AccountingLedgerRow>[] = [
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
    accessorKey: 'debit',
    header: 'Debit',
    meta: {
      class: { th: 'text-right', td: 'text-right' }
    },
    cell: ({ row }) =>
      Number(row.getValue('debit')) > 0
        ? formatCurrency(Number(row.getValue('debit')))
        : '-'
  },
  {
    accessorKey: 'credit',
    header: 'Kredit',
    meta: {
      class: { th: 'text-right', td: 'text-right' }
    },
    cell: ({ row }) =>
      Number(row.getValue('credit')) > 0
        ? formatCurrency(Number(row.getValue('credit')))
        : '-'
  },
  {
    accessorKey: 'balance',
    header: 'Saldo',
    meta: {
      class: { th: 'text-right', td: 'text-right' }
    },
    cell: ({ row }) =>
      h(
        'span',
        { class: 'font-semibold' },
        formatCurrency(Number(row.getValue('balance')))
      )
  }
]

const summaryCards = computed(() => {
  const data = ledger.value
  return [
    {
      title: 'Saldo Awal',
      value: formatCurrency(data?.opening_balance ?? 0),
      color: 'neutral' as const
    },
    {
      title: 'Saldo Akhir',
      value: formatCurrency(data?.closing_balance ?? 0),
      color: 'primary' as const
    },
    {
      title: 'Jumlah Mutasi',
      value: `${data?.rows.length ?? 0} transaksi`,
      color: 'info' as const
    }
  ]
})

definePageMeta({ layout: 'accounting' })
</script>

<template>
  <UDashboardPanel id="accounting-buku-besar">
    <template #header>
      <UDashboardNavbar>
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">
              Buku Besar
            </p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Riwayat mutasi per akun dengan saldo berjalan
            </p>
          </div>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-4 lg:p-6">
        <section class="flex flex-col lg:gap-4">
          <UCard>
            <div v-if="pendingAccounts" class="flex flex-wrap items-end gap-3">
              <div class="space-y-2">
                <USkeleton class="h-4 w-16 rounded" />
                <USkeleton class="h-10 w-72 rounded-lg" />
              </div>
              <div class="space-y-2">
                <USkeleton class="h-4 w-24 rounded" />
                <USkeleton class="h-10 w-40 rounded-lg" />
              </div>
              <div class="space-y-2">
                <USkeleton class="h-4 w-24 rounded" />
                <USkeleton class="h-10 w-40 rounded-lg" />
              </div>
              <USkeleton class="h-10 w-32 rounded-lg" />
            </div>
            <div v-else class="flex flex-wrap items-end gap-3">
              <UFormField label="Akun" class="w-72">
                <USelect
                  v-model="accountId"
                  :items="accountItems"
                  value-key="value"
                  placeholder="Pilih akun"
                />
              </UFormField>
              <UFormField label="Dari Tanggal">
                <UInput v-model="dateFrom" type="date" />
              </UFormField>
              <UFormField label="Sampai Tanggal">
                <UInput v-model="dateTo" type="date" />
              </UFormField>
              <UButton
                icon="i-lucide-search"
                :disabled="!accountId"
                @click="onSearch"
              >
                Tampilkan
              </UButton>
              <UDropdownMenu
                :items="[
                  { type: 'label', label: 'Export Data' },
                  { type: 'separator' },
                  { label: 'Export to Excel', icon: 'i-lucide-file-spreadsheet', disabled: !ledger, onSelect: () => onExport('excel') },
                  { label: 'Export to PDF', icon: 'i-lucide-file-text', disabled: !ledger, onSelect: () => onExport('pdf') },
                  { label: 'Export to CSV', icon: 'i-lucide-file-down', disabled: !ledger, onSelect: () => onExport('csv') }
                ]"
              >
                <UButton
                  icon="i-lucide-download"
                  color="neutral"
                  variant="soft"
                  :disabled="!ledger"
                >
                  Export
                </UButton>
              </UDropdownMenu>
            </div>
          </UCard>

          <template v-if="ledger">
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <UCard v-for="card in summaryCards" :key="card.title">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  {{ card.title }}
                </p>
                <p class="mt-1 text-xl font-bold">
                  {{ card.value }}
                </p>
              </UCard>
            </div>

            <UCard>
              <UTable
                :data="ledger.rows"
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
                v-if="ledger.rows.length === 0"
                class="py-6 text-center text-sm text-neutral-500"
              >
                Belum ada mutasi untuk akun ini
              </p>
            </UCard>
          </template>

          <UAlert
            v-else-if="status !== 'pending'"
            title="Pilih Akun"
            description="Pilih akun di atas untuk melihat buku besarnya."
            icon="i-lucide-info"
            color="info"
            variant="soft"
          />
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>
