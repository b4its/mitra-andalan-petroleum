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
