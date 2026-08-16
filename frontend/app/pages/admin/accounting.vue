<script setup lang="ts">
import { h } from 'vue'
import type { DropdownMenuItem, TableColumn } from '@nuxt/ui'
import type { ExportColumn } from '~/composables/useExport'
import type {
  AccountingAccount,
  AccountingJournal,
  AccountingSummary,
  AccountingTrialBalance,
  AccountingTrialBalanceRow,
  BalanceSheetResponse,
  DailyCashResponse,
  DailyCashRow,
  CashflowResponse,
  CashflowItem,
  CostRecapResponse,
  MonitoringResponse,
  MonitoringRow,
  BankInterestResponse,
  BankInterestRow
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
    const [
      summary,
      journalResult,
      trial,
      accounts,
      balanceSheet,
      cashflow,
      costRecap,
      monitoring,
      dailyCash,
      bankInterest
    ] = await Promise.all([
      get<AccountingSummary>('/accounting/summary'),
      get<{ items: AccountingJournal[] }>('/accounting/journal', {
        page: 1,
        page_size: 500
      }),
      get<AccountingTrialBalance>('/accounting/trial-balance'),
      get<AccountingAccount[]>('/accounting/accounts', {
        include_inactive: true
      }),
      get<BalanceSheetResponse>('/accounting/balance-sheet'),
      get<CashflowResponse>('/accounting/cashflow'),
      get<CostRecapResponse>('/accounting/cost-recap'),
      get<MonitoringResponse>('/accounting/monitoring', {
        year: new Date().getFullYear()
      }),
      get<DailyCashResponse>('/accounting/daily-cash'),
      get<BankInterestResponse>('/accounting/bank-interest')
    ])
    return {
      summary,
      journals: journalResult?.items || [],
      trial,
      accounts,
      balanceSheet,
      cashflow,
      costRecap,
      monitoring,
      dailyCash,
      bankInterest
    }
  },
  {
    default: () => ({
      summary: null,
      journals: [],
      trial: null,
      accounts: [],
      balanceSheet: null,
      cashflow: null,
      costRecap: null,
      monitoring: null,
      dailyCash: null,
      bankInterest: null
    }),
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

// ── Neraca ───────────────────────────────────────────────────
const isBalanced = computed(() => {
  const n = data.value?.balanceSheet
  if (!n) return true
  return Math.abs(n.total_assets - (n.total_liabilities + n.total_equity)) < 1
})

const balanceSheetChart = computed(() => {
  const n = data.value?.balanceSheet
  if (!n) return null
  return {
    labels: ['Aset', 'Kewajiban', 'Ekuitas'],
    datasets: [
      {
        label: 'Nilai',
        data: [n.total_assets, n.total_liabilities, n.total_equity],
        backgroundColor: [
          'rgba(59,130,246,0.8)',
          'rgba(245,158,11,0.8)',
          'rgba(16,185,129,0.8)'
        ]
      }
    ]
  }
})

// ── Rekap Cashflow ───────────────────────────────────────────
const cashflowChart = computed(() => {
  const c = data.value?.cashflow
  if (!c) return null
  return {
    labels: ['Operasi', 'Investasi', 'Pendanaan'],
    datasets: [
      {
        label: 'Arus Kas',
        data: [c.operating.total, c.investing.total, c.financing.total],
        backgroundColor: [
          c.operating.total >= 0 ? 'rgba(16,185,129,0.8)' : 'rgba(239,68,68,0.8)',
          c.investing.total >= 0 ? 'rgba(16,185,129,0.8)' : 'rgba(239,68,68,0.8)',
          c.financing.total >= 0 ? 'rgba(16,185,129,0.8)' : 'rgba(239,68,68,0.8)'
        ]
      }
    ]
  }
})

// ── Kas Harian ───────────────────────────────────────────────
const dailyCashChart = computed(() => {
  const d = data.value?.dailyCash
  if (!d) return null
  return {
    labels: ['Saldo Awal', 'Total Masuk', 'Total Keluar', 'Saldo Akhir'],
    datasets: [
      {
        label: 'Nominal',
        data: [d.opening_balance, d.total_debit, d.total_credit, d.closing_balance],
        backgroundColor: [
          'rgba(100,116,139,0.8)',
          'rgba(16,185,129,0.8)',
          'rgba(239,68,68,0.8)',
          'rgba(59,130,246,0.8)'
        ]
      }
    ]
  }
})

// ── Rekap Biaya ──────────────────────────────────────────────
const costRecapChart = computed(() => {
  const groups = data.value?.costRecap?.groups || []
  if (!groups.length) return null
  const top = [...groups].sort((a, b) => b.total - a.total).slice(0, 10)
  return {
    labels: top.map(g => `${g.account_code} · ${g.account_name}`),
    datasets: [
      {
        label: 'Total Biaya',
        data: top.map(g => g.total),
        backgroundColor: 'rgba(239,68,68,0.8)'
      }
    ]
  }
})

// ── Rekap Monitoring ─────────────────────────────────────────
const monitoringChart = computed(() => {
  const rows = data.value?.monitoring?.rows || []
  if (!rows.length) return null
  return {
    labels: rows.map(r => r.bulan),
    datasets: [
      {
        label: 'Penghasilan',
        data: rows.map(r => r.penghasilan),
        backgroundColor: 'rgba(16,185,129,0.8)'
      },
      {
        label: 'Operasional',
        data: rows.map(r => r.operasional),
        backgroundColor: 'rgba(239,68,68,0.8)'
      },
      {
        label: 'Margin Kotor',
        data: rows.map(r => r.gross_margin),
        backgroundColor: 'rgba(59,130,246,0.8)'
      }
    ]
  }
})

// ── Rekap Bunga Bank ─────────────────────────────────────────
const bankInterestChart = computed(() => {
  const b = data.value?.bankInterest
  if (!b) return null
  return {
    labels: ['Pokok Pinjaman', 'Total Bunga', 'Total Pembayaran'],
    datasets: [
      {
        label: 'Nominal',
        data: [b.total_principal, b.total_interest, b.total_paid],
        backgroundColor: [
          'rgba(59,130,246,0.8)',
          'rgba(245,158,11,0.8)',
          'rgba(16,185,129,0.8)'
        ]
      }
    ]
  }
})

// ── Kas Harian ───────────────────────────────────────────────
const dailyCashColumns: TableColumn<DailyCashRow>[] = [
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
    cell: ({ row }) =>
      `${row.original.account_code} · ${row.original.account_name}`
  },
  {
    accessorKey: 'debit',
    header: 'Debit (Masuk)',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => {
      const val = Number(row.getValue('debit'))
      return val > 0
        ? h('span', { class: 'text-success font-medium' }, formatCurrency(val))
        : '-'
    }
  },
  {
    accessorKey: 'credit',
    header: 'Kredit (Keluar)',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => {
      const val = Number(row.getValue('credit'))
      return val > 0
        ? h('span', { class: 'text-error font-medium' }, formatCurrency(val))
        : '-'
    }
  },
  {
    accessorKey: 'balance',
    header: 'Saldo',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) =>
      h(
        'span',
        { class: 'font-semibold' },
        formatCurrency(Number(row.getValue('balance')))
      )
  }
]

// ── Rekap Cashflow ───────────────────────────────────────────
const cashflowColumns: TableColumn<CashflowItem>[] = [
  {
    accessorKey: 'description',
    header: 'Deskripsi',
    cell: ({ row }) => {
      const desc = row.getValue('description') as string
      return h('span', { class: 'truncate block max-w-96' }, desc)
    }
  },
  {
    accessorKey: 'category',
    header: 'Kategori',
    cell: ({ row }) =>
      h('span', { class: 'text-xs text-muted' }, row.getValue('category'))
  },
  {
    accessorKey: 'amount',
    header: 'Jumlah',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => {
      const amount = Number(row.getValue('amount'))
      const color = amount >= 0 ? 'text-success' : 'text-error'
      return h(
        'span',
        { class: `font-semibold ${color}` },
        formatCurrency(amount)
      )
    }
  }
]

// ── Rekap Biaya ──────────────────────────────────────────────
const expandedGroups = ref<Set<string>>(new Set())
function toggleGroup(code: string) {
  if (expandedGroups.value.has(code)) {
    expandedGroups.value.delete(code)
  } else {
    expandedGroups.value.add(code)
  }
}

// ── Rekap Monitoring ─────────────────────────────────────────
const monitoringColumns: TableColumn<MonitoringRow>[] = [
  {
    accessorKey: 'bulan',
    header: 'Bulan',
    cell: ({ row }) =>
      h('span', { class: 'font-medium' }, row.getValue('bulan'))
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
      return h(
        'span',
        {
          class: val >= 0
            ? 'text-success font-semibold'
            : 'text-error font-semibold'
        },
        formatCurrency(val)
      )
    }
  },
  {
    accessorKey: 'penghasilan',
    header: 'Penghasilan',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) =>
      h(
        'span',
        { class: 'font-semibold text-success' },
        formatCurrency(row.getValue('penghasilan'))
      )
  },
  {
    accessorKey: 'operasional',
    header: 'Operasional',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) =>
      h(
        'span',
        { class: 'text-error' },
        formatCurrency(row.getValue('operasional'))
      )
  },
  {
    accessorKey: 'fee_manajemen',
    header: 'Fee Manajemen',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => formatCurrency(row.getValue('fee_manajemen'))
  }
]

// ── Rekap Bunga Bank ─────────────────────────────────────────
const bankInterestColumns: TableColumn<BankInterestRow>[] = [
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
    cell: ({ row }) =>
      h(
        'span',
        { class: 'font-medium' },
        formatCurrency(Number(row.getValue('amount')))
      )
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
    cell: ({ row }) =>
      h(
        'span',
        { class: 'font-semibold text-warning' },
        formatCurrency(Number(row.getValue('interest_amount')))
      )
  }
]

// ── Bagan Akun ────────────────────────────────────────
const accountColumns: TableColumn<AccountingAccount>[] = [
  { accessorKey: 'code', header: 'Kode' },
  { accessorKey: 'name', header: 'Nama Akun' },
  {
    accessorKey: 'type',
    header: 'Tipe',
    cell: ({ row }) =>
      h(
        'span',
        { class: 'text-xs text-muted' },
        typeLabels[String(row.getValue('type'))] ?? row.getValue('type')
      )
  },
  {
    accessorKey: 'is_active',
    header: 'Status',
    cell: ({ row }) =>
      h(
        'span',
        {
          class: row.getValue('is_active')
            ? 'text-xs text-success'
            : 'text-xs text-muted'
        },
        row.getValue('is_active') ? 'Aktif' : 'Nonaktif'
      )
  }
]

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
  { label: 'Draf', value: 'draft' },
  { label: 'Dibatalkan', value: 'void' }
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
  { type: 'label', label: 'Ekspor Data' },
  { type: 'separator' },
  {
    label: 'Ekspor ke Excel',
    icon: 'i-lucide-file-spreadsheet',
    onSelect: () => onSelect('excel')
  },
  {
    label: 'Ekspor ke PDF',
    icon: 'i-lucide-file-text',
    onSelect: () => onSelect('pdf')
  },
  {
    label: 'Ekspor ke CSV',
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
              <p class="text-lg font-bold tabular-nums">
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

          <!-- Neraca (Balance Sheet) -->
          <UCard v-if="data?.balanceSheet">
            <template #header>
              <div class="flex flex-wrap items-center justify-between gap-2">
                <p class="font-medium">
                  Neraca (Balance Sheet)
                </p>
                <p
                  v-if="data.balanceSheet"
                  class="text-xs font-semibold"
                  :class="isBalanced ? 'text-success' : 'text-error'"
                >
                  {{ isBalanced ? 'Balance' : 'Tidak Balance' }}
                </p>
              </div>
            </template>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <!-- Aset -->
              <div class="rounded-lg border border-default p-4">
                <div class="flex items-center justify-between mb-3">
                  <span class="font-semibold text-info">Aset</span>
                  <span class="font-bold text-lg">{{
                    formatCurrency(data.balanceSheet.assets.total)
                  }}</span>
                </div>
                <div class="flex flex-col divide-y divide-default">
                  <div
                    v-for="acc in data.balanceSheet.assets.accounts"
                    :key="acc.account_id"
                    class="flex items-center justify-between py-2 text-sm"
                  >
                    <span class="text-muted">{{ acc.account_code }} - {{ acc.account_name }}</span>
                    <span class="font-medium">{{ formatCurrency(acc.balance) }}</span>
                  </div>
                  <p
                    v-if="!data.balanceSheet.assets.accounts.length"
                    class="py-4 text-center text-sm text-muted"
                  >
                    Belum ada data aset
                  </p>
                </div>
              </div>

              <!-- Kewajiban -->
              <div class="rounded-lg border border-default p-4">
                <div class="flex items-center justify-between mb-3">
                  <span class="font-semibold text-warning">Kewajiban</span>
                  <span class="font-bold text-lg">{{
                    formatCurrency(data.balanceSheet.liabilities.total)
                  }}</span>
                </div>
                <div class="flex flex-col divide-y divide-default">
                  <div
                    v-for="acc in data.balanceSheet.liabilities.accounts"
                    :key="acc.account_id"
                    class="flex items-center justify-between py-2 text-sm"
                  >
                    <span class="text-muted">{{ acc.account_code }} - {{ acc.account_name }}</span>
                    <span class="font-medium">{{ formatCurrency(acc.balance) }}</span>
                  </div>
                  <p
                    v-if="!data.balanceSheet.liabilities.accounts.length"
                    class="py-4 text-center text-sm text-muted"
                  >
                    Belum ada data kewajiban
                  </p>
                </div>
              </div>

              <!-- Ekuitas -->
              <div class="rounded-lg border border-default p-4">
                <div class="flex items-center justify-between mb-3">
                  <span class="font-semibold text-primary">Ekuitas</span>
                  <span class="font-bold text-lg">{{
                    formatCurrency(data.balanceSheet.equity.total)
                  }}</span>
                </div>
                <div class="flex flex-col divide-y divide-default">
                  <div
                    v-for="acc in data.balanceSheet.equity.accounts"
                    :key="acc.account_id"
                    class="flex items-center justify-between py-2 text-sm"
                  >
                    <span class="text-muted">{{ acc.account_code }} - {{ acc.account_name }}</span>
                    <span class="font-medium">{{ formatCurrency(acc.balance) }}</span>
                  </div>
                  <p
                    v-if="!data.balanceSheet.equity.accounts.length"
                    class="py-4 text-center text-sm text-muted"
                  >
                    Belum ada data ekuitas
                  </p>
                </div>
              </div>
            </div>

            <div class="mt-4">
              <p class="text-xs font-semibold text-muted uppercase tracking-wide mb-2">
                Grafik Neraca
              </p>
              <AdminBarChart
                v-if="balanceSheetChart"
                :labels="balanceSheetChart.labels"
                :datasets="balanceSheetChart.datasets"
                :height="220"
              />
            </div>
          </UCard>

          <!-- Kas Harian -->
          <UCard v-if="data?.dailyCash">
            <template #header>
              <div class="flex flex-wrap items-center justify-between gap-2">
                <p class="font-medium">
                  Kas Harian
                </p>
                <p class="text-xs text-muted">
                  Mutasi kas/bank dengan saldo berjalan
                </p>
              </div>
            </template>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">
                  Saldo Awal
                </p>
                <p class="text-xl font-bold">
                  {{ formatCurrency(data.dailyCash.opening_balance) }}
                </p>
              </div>
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">
                  Total Masuk
                </p>
                <p class="text-xl font-bold text-success">
                  {{ formatCurrency(data.dailyCash.total_debit) }}
                </p>
              </div>
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">
                  Total Keluar
                </p>
                <p class="text-xl font-bold text-error">
                  {{ formatCurrency(data.dailyCash.total_credit) }}
                </p>
              </div>
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">
                  Saldo Akhir
                </p>
                <p class="text-xl font-bold">
                  {{ formatCurrency(data.dailyCash.closing_balance) }}
                </p>
              </div>
            </div>

            <div class="mt-4">
              <p class="text-xs font-semibold text-muted uppercase tracking-wide mb-2">
                Grafik Kas Harian
              </p>
              <AdminBarChart
                v-if="dailyCashChart"
                :labels="dailyCashChart.labels"
                :datasets="dailyCashChart.datasets"
                :height="220"
              />
            </div>

            <UTable :data="data.dailyCash.rows.slice(0, 10)" :columns="dailyCashColumns" />
            <p
              v-if="!data.dailyCash.rows.length"
              class="py-4 text-center text-sm text-muted"
            >
              Belum ada mutasi kas
            </p>
          </UCard>

          <!-- Rekap Cashflow -->
          <UCard v-if="data?.cashflow">
            <template #header>
              <div class="flex flex-wrap items-center justify-between gap-2">
                <p class="font-medium">
                  Rekap Arus Kas (Cashflow)
                </p>
                <p class="text-xs text-muted">
                  Operasi, investasi, dan pendanaan
                </p>
              </div>
            </template>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">
                  Saldo Awal
                </p>
                <p class="text-xl font-bold">
                  {{ formatCurrency(data.cashflow.opening_balance) }}
                </p>
              </div>
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">
                  Arus Kas Bersih
                </p>
                <p
                  class="text-xl font-bold"
                  :class="data.cashflow.net_cashflow >= 0 ? 'text-success' : 'text-error'"
                >
                  {{ formatCurrency(data.cashflow.net_cashflow) }}
                </p>
              </div>
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">
                  Saldo Akhir
                </p>
                <p class="text-xl font-bold">
                  {{ formatCurrency(data.cashflow.closing_balance) }}
                </p>
              </div>
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">
                  Arus Kas Operasi
                </p>
                <p
                  class="text-xl font-bold"
                  :class="data.cashflow.operating.total >= 0 ? 'text-success' : 'text-error'"
                >
                  {{ formatCurrency(data.cashflow.operating.total) }}
                </p>
              </div>
            </div>

            <p class="text-xs font-semibold text-muted uppercase tracking-wide mb-2">
              Arus Kas Operasi
            </p>
            <div class="mt-4 mb-4">
              <AdminBarChart
                v-if="cashflowChart"
                :labels="cashflowChart.labels"
                :datasets="cashflowChart.datasets"
                :height="220"
              />
            </div>
            <UTable :data="data.cashflow.operating.items" :columns="cashflowColumns" />
            <p
              v-if="!data.cashflow.operating.items.length"
              class="py-4 text-center text-sm text-muted"
            >
              Belum ada data arus kas operasi
            </p>
          </UCard>

          <!-- Rekap Biaya -->
          <UCard v-if="data?.costRecap">
            <template #header>
              <div class="flex flex-wrap items-center justify-between gap-2">
                <p class="font-medium">
                  Rekap Biaya
                </p>
                <p class="text-sm font-bold text-error">
                  {{ formatCurrency(data.costRecap.total_cost) }}
                </p>
              </div>
            </template>

            <div class="flex flex-col gap-3">
              <div
                v-for="group in data.costRecap.groups"
                :key="group.account_code"
                class="rounded-lg border border-default"
              >
                <button
                  class="flex items-center justify-between w-full text-left px-4 py-3"
                  @click="toggleGroup(group.account_code)"
                >
                  <div class="flex items-center gap-2">
                    <UIcon
                      :name="expandedGroups.has(group.account_code)
                        ? 'i-lucide-chevron-down'
                        : 'i-lucide-chevron-right'"
                      class="size-4 text-muted"
                    />
                    <span class="font-medium">{{ group.account_code }} · {{ group.account_name }}</span>
                  </div>
                  <span class="font-bold text-error">{{ formatCurrency(group.total) }}</span>
                </button>

                <div
                  v-if="expandedGroups.has(group.account_code)"
                  class="flex flex-col divide-y divide-default border-t border-default"
                >
                  <div
                    v-for="item in group.items"
                    :key="item.id"
                    class="flex items-center justify-between py-2 px-4 text-sm"
                  >
                    <div class="min-w-0">
                      <p class="truncate max-w-96">
                        {{ item.description }}
                      </p>
                      <p class="text-xs text-muted">
                        {{ formatDate(item.entry_date) }}
                        <span v-if="item.reference">· {{ item.reference }}</span>
                      </p>
                    </div>
                    <span class="font-medium shrink-0">{{ formatCurrency(item.amount) }}</span>
                  </div>
                </div>
                <p
                  v-else
                  class="text-sm text-muted px-4 py-2 border-t border-default"
                >
                  {{ group.items.length }} transaksi — klik untuk detail
                </p>
              </div>

              <p
                v-if="!data.costRecap.groups.length"
                class="py-4 text-center text-sm text-muted"
              >
                Belum ada data biaya
              </p>

              <div class="mt-4">
                <p class="text-xs font-semibold text-muted uppercase tracking-wide mb-2">
                  Grafik Rekap Biaya per Akun
                </p>
                <AdminBarChart
                  v-if="costRecapChart"
                  :labels="costRecapChart.labels"
                  :datasets="costRecapChart.datasets"
                  :height="240"
                />
              </div>
            </div>
          </UCard>

          <!-- Rekap Monitoring -->
          <UCard v-if="data?.monitoring">
            <template #header>
              <div class="flex flex-wrap items-center justify-between gap-2">
                <p class="font-medium">
                  Rekap Monitoring ({{ new Date().getFullYear() }})
                </p>
                <p class="text-xs text-muted">
                  Pendapatan, biaya, dan margin per bulan
                </p>
              </div>
            </template>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">
                  Total Penghasilan
                </p>
                <p class="text-xl font-bold text-success">
                  {{ formatCurrency(data.monitoring.total_penghasilan) }}
                </p>
              </div>
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">
                  Total Operasional
                </p>
                <p class="text-xl font-bold text-error">
                  {{ formatCurrency(data.monitoring.total_operasional) }}
                </p>
              </div>
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">
                  Total Margin Kotor
                </p>
                <p class="text-xl font-bold">
                  {{ formatCurrency(data.monitoring.total_gross_margin) }}
                </p>
              </div>
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">
                  Total OAT
                </p>
                <p class="text-xl font-bold">
                  {{ formatCurrency(data.monitoring.total_oat) }}
                </p>
              </div>
            </div>

            <div class="mt-4">
              <p class="text-xs font-semibold text-muted uppercase tracking-wide mb-2">
                Grafik Monitoring per Bulan
              </p>
              <AdminBarChart
                v-if="monitoringChart"
                :labels="monitoringChart.labels"
                :datasets="monitoringChart.datasets"
                :height="260"
              />
            </div>

            <UTable :data="data.monitoring.rows" :columns="monitoringColumns" />
            <p
              v-if="!data.monitoring.rows.length"
              class="py-4 text-center text-sm text-muted"
            >
              Belum ada data monitoring
            </p>
          </UCard>

          <!-- Rekap Bunga Bank -->
          <UCard v-if="data?.bankInterest">
            <template #header>
              <div class="flex flex-wrap items-center justify-between gap-2">
                <p class="font-medium">
                  Rekap Bunga Bank
                </p>
                <p class="text-xs text-muted">
                  Pinjaman dan kalkulasi bunga
                </p>
              </div>
            </template>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">
                  Total Pokok Pinjaman
                </p>
                <p class="text-xl font-bold">
                  {{ formatCurrency(data.bankInterest.total_principal) }}
                </p>
              </div>
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">
                  Total Bunga
                </p>
                <p class="text-xl font-bold text-warning">
                  {{ formatCurrency(data.bankInterest.total_interest) }}
                </p>
              </div>
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">
                  Total Pembayaran
                </p>
                <p class="text-xl font-bold text-success">
                  {{ formatCurrency(data.bankInterest.total_paid) }}
                </p>
              </div>
            </div>

            <div class="mt-4">
              <p class="text-xs font-semibold text-muted uppercase tracking-wide mb-2">
                Grafik Rekap Bunga Bank
              </p>
              <AdminBarChart
                v-if="bankInterestChart"
                :labels="bankInterestChart.labels"
                :datasets="bankInterestChart.datasets"
                :height="220"
              />
            </div>

            <UTable :data="data.bankInterest.rows.slice(0, 10)" :columns="bankInterestColumns" />
            <p
              v-if="!data.bankInterest.rows.length"
              class="py-4 text-center text-sm text-muted"
            >
              Belum ada data bunga bank
            </p>
          </UCard>

          <!-- Bagan Akun -->
          <UCard v-if="data?.accounts?.length">
            <template #header>
              <div class="flex flex-wrap items-center justify-between gap-2">
                <p class="font-medium">
                  Bagan Akun
                </p>
                <p class="text-xs text-muted">
                  {{ (data.accounts || []).length }} akun
                </p>
              </div>
            </template>
            <UTable :data="data.accounts" :columns="accountColumns" />
          </UCard>
        </template>
      </div>
    </template>
  </UDashboardPanel>
</template>
