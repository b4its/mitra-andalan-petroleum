<script setup lang="ts">
import { h } from 'vue'
import type { DropdownMenuItem, TableColumn } from '@nuxt/ui'
import type { ExportColumn } from '~/composables/useExport'
import type {
  AccountingAccount,
  AccountingJournal,
  AccountingSummary,
  AccountingTrialBalance,
  AccountingTrialBalanceRow
} from '~/types/accounting'
import AdminBarChart from '~/components/admin/charts/AdminBarChart.vue'
import AdminPieChart from '~/components/admin/charts/AdminPieChart.vue'

definePageMeta({ layout: 'admin' })

const { get } = useApi()
const { toCSV, toExcel, toPDF } = useExport()

// ── Data fetch ────────────────────────────────────────────────
const { data, pending, refresh } = await useAsyncData(
  'admin-accounting',
  async () => {
    const [summary, journalResult, trial, accounts] = await Promise.all([
      get<AccountingSummary>('/accounting/summary'),
      get<{ items: AccountingJournal[] }>('/accounting/journal', {
        page: 1,
        page_size: 100
      }),
      get<AccountingTrialBalance>('/accounting/trial-balance'),
      get<AccountingAccount[]>('/accounting/accounts')
    ])
    return {
      summary,
      journals: journalResult?.items || [],
      trial,
      accounts
    }
  },
  {
    default: () => ({ summary: null, journals: [], trial: null, accounts: [] }),
    lazy: true,
    server: false
  }
)

// ── Cards ────────────────────────────────────────────────────
const valueCards = computed(() => [
  {
    title: 'Total Pemasukan',
    value: data.value?.summary?.total_income ?? 0,
    icon: 'i-lucide-trending-up',
    color: 'text-success'
  },
  {
    title: 'Total Pengeluaran',
    value: data.value?.summary?.total_expense ?? 0,
    icon: 'i-lucide-trending-down',
    color: 'text-error'
  },
  {
    title: 'Laba Bersih',
    value: data.value?.summary?.net_income ?? 0,
    icon: 'i-lucide-wallet',
    color: 'text-primary'
  },
  {
    title: 'Saldo Kas & Bank',
    value: data.value?.summary?.cash_balance ?? 0,
    icon: 'i-lucide-circle-dollar-sign',
    color: 'text-info'
  }
])

const countCards = computed(() => [
  {
    title: 'Jumlah Jurnal',
    value: data.value?.summary?.journal_count ?? 0,
    icon: 'i-lucide-book-open'
  },
  {
    title: 'Jumlah Akun',
    value: data.value?.summary?.account_count ?? 0,
    icon: 'i-lucide-list-tree'
  },
  {
    title: 'Pemasukan',
    value: data.value?.summary?.income_count ?? 0,
    icon: 'i-lucide-banknote-arrow-down'
  },
  {
    title: 'Pengeluaran',
    value: data.value?.summary?.expense_count ?? 0,
    icon: 'i-lucide-banknote-arrow-up'
  }
])

// ── Charts ───────────────────────────────────────────────────
const incomeExpenseLabels = ['Pemasukan', 'Pengeluaran']
const incomeExpenseValues = computed(() => {
  const s = data.value?.summary
  return s ? [s.total_income, s.total_expense] : []
})

const typeLabels: Record<string, string> = {
  asset: 'Aset',
  liability: 'Kewajiban',
  equity: 'Ekuitas',
  revenue: 'Pendapatan',
  expense: 'Beban'
}
const typeColors: Record<string, string> = {
  asset: 'rgba(59,130,246,0.8)',
  liability: 'rgba(245,158,11,0.8)',
  equity: 'rgba(16,185,129,0.8)',
  revenue: 'rgba(16,185,129,0.8)',
  expense: 'rgba(239,68,68,0.8)'
}

const accountDistLabels = computed(() => {
  const list: AccountingAccount[] = data.value?.accounts || []
  const map = new Map<string, number>()
  for (const acc of list) map.set(acc.type, (map.get(acc.type) || 0) + 1)
  return [...map.keys()].map(k => typeLabels[k] ?? k)
})
const accountDistValues = computed(() => {
  const list: AccountingAccount[] = data.value?.accounts || []
  const map = new Map<string, number>()
  for (const acc of list) map.set(acc.type, (map.get(acc.type) || 0) + 1)
  return [...map.values()]
})
const accountDistColors = computed(() => {
  const list: AccountingAccount[] = data.value?.accounts || []
  const map = new Map<string, number>()
  for (const acc of list) map.set(acc.type, (map.get(acc.type) || 0) + 1)
  return [...map.keys()].map(k => typeColors[k] ?? 'rgba(100,116,139,0.8)')
})

// ── Tabel Jurnal: search + pagination ────────────────────────
const journalSearch = ref('')
const journalStatusFilter = ref('all')
const journalPage = ref(1)
const PAGE_SIZE = 7

const totalDebit = (journal: AccountingJournal) =>
  journal.lines.reduce((sum, line) => sum + (line.debit || 0), 0)

const journalFiltered = computed(() => {
  const q = journalSearch.value.trim().toLowerCase()
  let list: AccountingJournal[] = data.value?.journals || []

  if (journalStatusFilter.value !== 'all') {
    list = list.filter(
      j => (j.status ?? 'posted') === journalStatusFilter.value
    )
  }

  if (!q) return list
  return list.filter(
    j =>
      j.entry_number?.toLowerCase().includes(q)
      || j.description?.toLowerCase().includes(q)
      || j.reference?.toLowerCase().includes(q)
      || j.lines.some(line =>
        `${line.account_code} ${line.account_name}`.toLowerCase().includes(q)
      )
  )
})
const journalPaged = computed(() => {
  const start = (journalPage.value - 1) * PAGE_SIZE
  return journalFiltered.value.slice(start, start + PAGE_SIZE)
})
watch([journalSearch, journalStatusFilter], () => {
  journalPage.value = 1
})

const journalStatusOptions = [
  { label: 'Semua Status', value: 'all' },
  { label: 'Posted', value: 'posted' },
  { label: 'Draft', value: 'draft' },
  { label: 'Void', value: 'void' }
]

// ── Tabel Neraca Saldo ──────────────────────────────────────
const trialSearch = ref('')
const trialFiltered = computed(() => {
  const q = trialSearch.value.trim().toLowerCase()
  const list: AccountingTrialBalanceRow[] = data.value?.trial?.rows || []
  if (!q) return list
  return list.filter(
    r =>
      r.account_code?.toLowerCase().includes(q)
      || r.account_name?.toLowerCase().includes(q)
      || r.account_type?.toLowerCase().includes(q)
  )
})

// ── Export ───────────────────────────────────────────────────
const journalExportColumns: ExportColumn<AccountingJournal>[] = [
  {
    header: 'Nomor Jurnal',
    accessor: (row: AccountingJournal) => row.entry_number
  },
  {
    header: 'Tanggal',
    accessor: (row: AccountingJournal) => formatDate(row.entry_date)
  },
  {
    header: 'Deskripsi',
    accessor: (row: AccountingJournal) => row.description
  },
  {
    header: 'Referensi',
    accessor: (row: AccountingJournal) => row.reference ?? '-'
  },
  { header: 'Nominal', accessor: (row: AccountingJournal) => totalDebit(row) },
  {
    header: 'Akun',
    accessor: (row: AccountingJournal) =>
      row.lines.map(l => l.account_code).join(', ')
  }
]

const trialExportColumns: ExportColumn<AccountingTrialBalanceRow>[] = [
  { header: 'Kode', accessor: (row: AccountingTrialBalanceRow) => row.account_code },
  { header: 'Nama Akun', accessor: (row: AccountingTrialBalanceRow) => row.account_name },
  {
    header: 'Tipe',
    accessor: (row: AccountingTrialBalanceRow) =>
      typeLabels[row.account_type] ?? row.account_type
  },
  { header: 'Debit', accessor: (row: AccountingTrialBalanceRow) => row.debit },
  { header: 'Kredit', accessor: (row: AccountingTrialBalanceRow) => row.credit }
]

function onJournalExport(format: 'excel' | 'pdf' | 'csv') {
  const filename = `rekap-jurnal-${new Date().toISOString().slice(0, 10)}`
  if (format === 'excel')
    toExcel(
      filename,
      'Jurnal Umum',
      journalExportColumns,
      journalFiltered.value
    )
  else if (format === 'pdf')
    toPDF(
      filename,
      'Jurnal Umum',
      journalExportColumns,
      journalFiltered.value,
      { subtitle: 'Catatan transaksi keuangan (debit & kredit)' }
    )
  else toCSV(filename, journalExportColumns, journalFiltered.value)
}

function onTrialExport(format: 'excel' | 'pdf' | 'csv') {
  const filename = `neraca-saldo-${new Date().toISOString().slice(0, 10)}`
  if (format === 'excel')
    toExcel(filename, 'Neraca Saldo', trialExportColumns, trialFiltered.value)
  else if (format === 'pdf')
    toPDF(filename, 'Neraca Saldo', trialExportColumns, trialFiltered.value, {
      subtitle: 'Saldo debit/credit seluruh akun aktif'
    })
  else toCSV(filename, trialExportColumns, trialFiltered.value)
}

// ── Kolom tabel ─────────────────────────────────────────────
const journalColumns: TableColumn<AccountingJournal>[] = [
  { accessorKey: 'entry_number', header: 'Nomor Jurnal' },
  {
    accessorKey: 'entry_date',
    header: 'Tanggal',
    cell: ({ row }) =>
      row.getValue('entry_date') ? formatDate(row.getValue('entry_date')) : '-'
  },
  {
    accessorKey: 'description',
    header: 'Deskripsi',
    cell: ({ row }) => {
      const desc = row.getValue('description') as string
      return h('div', { class: 'flex flex-col gap-0.5 min-w-0' }, [
        h('span', { class: 'truncate max-w-64' }, desc),
        h(
          'span',
          { class: 'text-xs text-muted' },
          row.original.lines.map(l => l.account_code).join(', ')
        )
      ])
    }
  },
  {
    accessorKey: 'amount',
    header: 'Nominal',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => formatCurrency(totalDebit(row.original))
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) =>
      h(
        'span',
        { class: 'text-xs text-muted capitalize' },
        String(row.getValue('status') ?? 'posted')
      )
  }
]

const trialColumns: TableColumn<AccountingTrialBalanceRow>[] = [
  { accessorKey: 'account_code', header: 'Kode' },
  { accessorKey: 'account_name', header: 'Nama Akun' },
  {
    accessorKey: 'account_type',
    header: 'Tipe',
    cell: ({ row }) =>
      h(
        'span',
        { class: 'text-xs text-muted' },
        typeLabels[String(row.getValue('account_type'))]
        ?? row.getValue('account_type')
      )
  },
  {
    accessorKey: 'debit',
    header: 'Debit',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => formatCurrency(row.getValue('debit') ?? 0)
  },
  {
    accessorKey: 'credit',
    header: 'Kredit',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => formatCurrency(row.getValue('credit') ?? 0)
  }
]

const exportItems = (
  onSelect: (format: 'excel' | 'pdf' | 'csv') => void
): DropdownMenuItem[] => [
  { type: 'label', label: 'Export Data' },
  { type: 'separator' },
  {
    label: 'Export to Excel',
    icon: 'i-lucide-file-spreadsheet',
    onSelect: () => onSelect('excel')
  },
  {
    label: 'Export to PDF',
    icon: 'i-lucide-file-text',
    onSelect: () => onSelect('pdf')
  },
  {
    label: 'Export to CSV',
    icon: 'i-lucide-file-down',
    onSelect: () => onSelect('csv')
  }
]
</script>

<template>
  <UDashboardPanel id="admin-accounting">
    <template #header>
      <UDashboardNavbar title="Accounting — Rekap" :ui="{ right: 'gap-2' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #right>
          <UButton
            icon="i-lucide-refresh-cw"
            color="neutral"
            variant="ghost"
            @click="refresh()"
          />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="space-y-6 p-4 lg:p-6">
        <!-- Skeleton -->
        <template v-if="pending">
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <USkeleton v-for="i in 4" :key="i" class="h-28 rounded-xl" />
          </div>
          <div class="grid gap-4 sm:grid-cols-4">
            <USkeleton v-for="i in 4" :key="i" class="h-20 rounded-xl" />
          </div>
          <div class="grid gap-6 lg:grid-cols-2">
            <USkeleton class="h-72 rounded-xl" />
            <USkeleton class="h-72 rounded-xl" />
          </div>
          <USkeleton class="h-64 rounded-xl" />
          <USkeleton class="h-64 rounded-xl" />
        </template>

        <template v-else>
          <!-- Stat cards -->
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <UCard
              v-for="card in valueCards"
              :key="card.title"
              variant="subtle"
            >
              <template #leading>
                <UIcon :name="card.icon" class="size-5 text-primary" />
              </template>
              <template #title>
                {{ card.title }}
              </template>
              <p class="text-2xl font-semibold tabular-nums">
                {{ formatCurrency(card.value) }}
              </p>
              <p class="text-xs text-muted mt-1">
                Data akuntansi keseluruhan
              </p>
            </UCard>
          </div>

          <!-- Count cards -->
          <div class="grid gap-3 sm:grid-cols-4">
            <UCard
              v-for="c in countCards"
              :key="c.title"
              variant="subtle"
              class="text-center"
            >
              <UIcon :name="c.icon" class="size-5 text-primary mx-auto mb-1" />
              <p class="text-2xl font-semibold tabular-nums">
                {{ c.value }}
              </p>
              <p class="text-xs text-muted mt-1">
                {{ c.title }}
              </p>
            </UCard>
          </div>

          <!-- Charts -->
          <div class="grid gap-6 lg:grid-cols-2">
            <UCard class="lg:col-span-1">
              <template #header>
                <div class="flex items-center justify-between">
                  <p class="font-medium">
                    Pemasukan vs Pengeluaran
                  </p>
                  <p class="text-xs text-muted">
                    Total nominal
                  </p>
                </div>
              </template>
              <AdminBarChart
                v-if="incomeExpenseValues.length"
                :labels="incomeExpenseLabels"
                :datasets="[
                  {
                    label: 'Nominal',
                    data: incomeExpenseValues,
                    backgroundColor: [
                      'rgba(16,185,129,0.8)',
                      'rgba(239,68,68,0.8)'
                    ]
                  }
                ]"
              />
              <UEmpty v-else icon="i-lucide-chart-bar" title="Belum ada data" />
            </UCard>
            <UCard>
              <template #header>
                <div class="flex items-center justify-between">
                  <p class="font-medium">
                    Distribusi Akun per Tipe
                  </p>
                  <p class="text-xs text-muted">
                    {{ (data?.accounts || []).length }} akun
                  </p>
                </div>
              </template>
              <AdminPieChart
                v-if="accountDistLabels.length"
                :labels="accountDistLabels"
                :data="accountDistValues"
                :background-color="accountDistColors"
              />
              <UEmpty v-else icon="i-lucide-chart-pie" title="Belum ada data" />
            </UCard>
          </div>

          <!-- Tabel Jurnal -->
          <UCard>
            <template #header>
              <div class="flex items-center justify-between gap-3 flex-wrap">
                <p class="font-medium">
                  Data Jurnal Umum
                </p>
                <div class="flex items-center gap-2">
                  <USelect
                    v-model="journalStatusFilter"
                    :items="journalStatusOptions"
                    value-key="value"
                    size="sm"
                    class="w-36"
                  />
                  <UInput
                    v-model="journalSearch"
                    icon="i-lucide-search"
                    placeholder="Cari nomor, deskripsi, akun..."
                    size="sm"
                    class="w-64"
                  />
                  <UDropdownMenu :items="exportItems(onJournalExport)">
                    <UButton
                      icon="i-lucide-download"
                      color="neutral"
                      variant="soft"
                      size="sm"
                    >
                      Export
                    </UButton>
                  </UDropdownMenu>
                </div>
              </div>
            </template>
            <UTable :data="journalPaged" :columns="journalColumns" />
            <UEmpty
              v-if="!journalPaged.length"
              icon="i-lucide-file-search"
              title="Tidak ada jurnal"
            />
            <div
              v-if="journalFiltered.length > PAGE_SIZE"
              class="flex items-center justify-between border-t border-default pt-3 px-2 mt-2"
            >
              <p class="text-xs text-muted">
                {{ journalFiltered.length }} total
              </p>
              <UPagination
                v-model:page="journalPage"
                :total="journalFiltered.length"
                :items-per-page="PAGE_SIZE"
              />
            </div>
          </UCard>

          <!-- Tabel Neraca Saldo -->
          <UCard>
            <template #header>
              <div class="flex items-center justify-between gap-3 flex-wrap">
                <p class="font-medium">
                  Neraca Saldo
                </p>
                <div class="flex items-center gap-2">
                  <UInput
                    v-model="trialSearch"
                    icon="i-lucide-search"
                    placeholder="Cari kode, nama akun..."
                    size="sm"
                    class="w-64"
                  />
                  <UDropdownMenu :items="exportItems(onTrialExport)">
                    <UButton
                      icon="i-lucide-download"
                      color="neutral"
                      variant="soft"
                      size="sm"
                    >
                      Export
                    </UButton>
                  </UDropdownMenu>
                </div>
              </div>
            </template>
            <UTable :data="trialFiltered" :columns="trialColumns" />
            <UEmpty
              v-if="!trialFiltered.length"
              icon="i-lucide-file-search"
              title="Neraca saldo kosong"
            />

            <!-- Total debit/credit -->
            <div
              v-if="data?.trial"
              class="flex items-center justify-end gap-6 border-t border-default pt-3 px-2 mt-2 tabular-nums"
            >
              <div class="flex items-center gap-2 text-sm">
                <span class="text-muted">Total Debit</span>
                <span class="font-semibold text-highlighted">{{
                  formatCurrency(data.trial.total_debit)
                }}</span>
              </div>
              <div class="flex items-center gap-2 text-sm">
                <span class="text-muted">Total Kredit</span>
                <span class="font-semibold text-highlighted">{{
                  formatCurrency(data.trial.total_credit)
                }}</span>
              </div>
            </div>
          </UCard>
        </template>
      </div>
    </template>
  </UDashboardPanel>
</template>
