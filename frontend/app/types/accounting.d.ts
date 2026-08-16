export interface AccountingAccount {
  id: string
  code: string
  name: string
  type: AccountType
  description: string | null
  is_active: boolean
  parent_id: string | null
  created_at: string | null
  updated_at: string | null
}

export type AccountType = 'asset' | 'liability' | 'equity' | 'revenue' | 'expense'

export interface AccountingJournalLine {
  id: string
  journal_entry_id: string
  account_id: string
  account_code: string
  account_name: string
  description: string | null
  debit: number
  credit: number
}

export interface AccountingJournal {
  id: string
  entry_number: string
  entry_date: string
  description: string
  reference: string | null
  status: string
  lines: AccountingJournalLine[]
  created_at: string | null
  updated_at: string | null
}

export interface AccountingJournalPostLine {
  account_id: string
  description?: string | null
  debit: number
  credit: number
}

export interface AccountingJournalPost {
  entry_date: string
  description: string
  reference?: string | null
  status?: string
  lines: AccountingJournalPostLine[]
}

export interface AccountingLedgerRow {
  id: string
  entry_number: string
  entry_date: string
  description: string
  account_code: string
  account_name: string
  debit: number
  credit: number
  balance: number
}

export interface AccountingLedger {
  account_id: string
  account_code: string
  account_name: string
  account_type: AccountType
  opening_balance: number
  closing_balance: number
  rows: AccountingLedgerRow[]
}

export interface AccountingTrialBalanceRow {
  account_id: string
  account_code: string
  account_name: string
  account_type: AccountType
  debit: number
  credit: number
}

export interface AccountingTrialBalance {
  rows: AccountingTrialBalanceRow[]
  total_debit: number
  total_credit: number
}

export interface AccountingIncomeExpenseRow {
  id: string
  entry_number: string
  entry_date: string
  description: string
  account_code: string
  account_name: string
  amount: number
  reference: string | null
}

export interface AccountingSummary {
  total_income: number
  total_expense: number
  net_income: number
  cash_balance: number
  income_count: number
  expense_count: number
  journal_count: number
  account_count: number
  recent_journals: AccountingJournal[]
}

// ── Neraca (Balance Sheet) ──────────────────────────────────
export interface BalanceSheetAccount {
  account_id: string
  account_code: string
  account_name: string
  balance: number
}

export interface BalanceSheetSection {
  section: string
  total: number
  accounts: BalanceSheetAccount[]
}

export interface BalanceSheetResponse {
  assets: BalanceSheetSection
  liabilities: BalanceSheetSection
  equity: BalanceSheetSection
  total_assets: number
  total_liabilities: number
  total_equity: number
}

// ── Rekap Cashflow ──────────────────────────────────────────
export interface CashflowItem {
  description: string
  amount: number
  category: string
  account_code: string
  account_name: string
}

export interface CashflowSection {
  section: string
  total: number
  items: CashflowItem[]
}

export interface CashflowResponse {
  operating: CashflowSection
  investing: CashflowSection
  financing: CashflowSection
  net_cashflow: number
  opening_balance: number
  closing_balance: number
}

// ── Rekap Biaya (Cost Recap) ────────────────────────────────
export interface CostRecapRow {
  id: string
  entry_date: string
  description: string
  account_code: string
  account_name: string
  amount: number
  reference: string | null
}

export interface CostRecapGroup {
  account_code: string
  account_name: string
  total: number
  items: CostRecapRow[]
}

export interface CostRecapResponse {
  total_cost: number
  groups: CostRecapGroup[]
}

// ── Rekap Monitoring ────────────────────────────────────────
export interface MonitoringRow {
  bulan: string
  invoice: number
  modal_elnusa: number
  oat: number
  gross_margin: number
  penghasilan: number
  operasional: number
  fee_manajemen: number
}

export interface MonitoringResponse {
  rows: MonitoringRow[]
  total_invoice: number
  total_modal: number
  total_oat: number
  total_gross_margin: number
  total_penghasilan: number
  total_operasional: number
  total_fee_manajemen: number
}

// ── Kas Harian (Daily Cash) ────────────────────────────────
export interface DailyCashRow {
  id: string
  entry_date: string
  description: string
  account_code: string
  account_name: string
  debit: number
  credit: number
  balance: number
  reference: string | null
}

export interface DailyCashResponse {
  opening_balance: number
  closing_balance: number
  total_debit: number
  total_credit: number
  rows: DailyCashRow[]
}

// ── Rekap Bunga Bank ────────────────────────────────────────
export interface BankInterestRow {
  id: string
  entry_date: string
  description: string
  account_code: string
  account_name: string
  amount: number
  interest_rate: number
  days: number
  interest_amount: number
  reference: string | null
}

export interface BankInterestResponse {
  total_principal: number
  total_interest: number
  total_paid: number
  rows: BankInterestRow[]
}
