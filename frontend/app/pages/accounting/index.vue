<script setup lang="ts">
import type { AccountingJournal, AccountingSummary } from '~/types/accounting'

const { get } = useApi()
const toast = useToast()

function totalDebit(journal: AccountingJournal): number {
  return journal.lines.reduce((sum, line) => sum + (line.debit || 0), 0)
}

const { data: summary, refresh } = await useAsyncData(
  'accounting-summary',
  () => get<AccountingSummary>('/accounting/summary'),
  { default: () => null, server: false }
)

const cards = computed(() => [
  {
    title: 'Total Pemasukan',
    value: formatCurrency(summary.value?.total_income ?? 0),
    icon: 'i-lucide-trending-up',
    color: 'success' as const,
    to: '/accounting/pemasukan'
  },
  {
    title: 'Total Pengeluaran',
    value: formatCurrency(summary.value?.total_expense ?? 0),
    icon: 'i-lucide-trending-down',
    color: 'error' as const,
    to: '/accounting/pengeluaran'
  },
  {
    title: 'Laba Bersih',
    value: formatCurrency(summary.value?.net_income ?? 0),
    icon: 'i-lucide-wallet',
    color: 'primary' as const,
    to: '/accounting/jurnal-umum'
  },
  {
    title: 'Saldo Kas & Bank',
    value: formatCurrency(summary.value?.cash_balance ?? 0),
    icon: 'i-lucide-circle-dollar-sign',
    color: 'info' as const,
    to: '/accounting/buku-besar'
  }
])

const countCards = computed(() => [
  {
    title: 'Jumlah Jurnal',
    value: summary.value?.journal_count ?? 0,
    icon: 'i-lucide-book-open'
  },
  {
    title: 'Jumlah Akun',
    value: summary.value?.account_count ?? 0,
    icon: 'i-lucide-list-tree'
  },
  {
    title: 'Pemasukan',
    value: summary.value?.income_count ?? 0,
    icon: 'i-lucide-arrow-down-to-line'
  },
  {
    title: 'Pengeluaran',
    value: summary.value?.expense_count ?? 0,
    icon: 'i-lucide-arrow-up-from-line'
  }
])

function onError(err: unknown) {
  toast.add({
    title: 'Gagal',
    description: err instanceof Error ? err.message : 'Terjadi kesalahan',
    icon: 'i-lucide-alert-triangle',
    color: 'error'
  })
}

definePageMeta({ layout: 'accounting' })
</script>

<template>
  <UDashboardPanel id="accounting-dashboard">
    <template #header>
      <UDashboardNavbar :ui="{ right: 'gap-2' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">Akuntansi</p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Rekap pemasukan, pengeluaran, dan jurnal umum
            </p>
          </div>
        </template>
        <template #right>
          <UButton
            icon="i-lucide-refresh-cw"
            color="neutral"
            variant="ghost"
            @click="refresh().catch(onError)"
          >
            Muat Ulang
          </UButton>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-4 lg:p-6">
        <section class="flex flex-col gap-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <UCard v-for="card in cards" :key="card.title">
        <div class="flex items-center justify-between gap-2">
          <div>
            <p class="text-sm text-neutral-500 dark:text-neutral-400">
              {{ card.title }}
            </p>
            <p class="mt-1 text-2xl font-bold">
              {{ card.value }}
            </p>
          </div>
          <UBadge
            :color="card.color"
            variant="soft"
            :ui="{ base: 'size-10 rounded-full' }"
          >
            <UIcon :name="card.icon" class="size-5" />
          </UBadge>
        </div>
      </UCard>
    </div>

    <div class="grid grid-cols-2 xl:grid-cols-4 gap-4">
      <UCard v-for="card in countCards" :key="card.title">
        <div class="flex items-center gap-3">
          <UIcon :name="card.icon" class="size-6 text-primary" />
          <div>
            <p class="text-2xl font-bold">
              {{ card.value }}
            </p>
            <p class="text-sm text-neutral-500 dark:text-neutral-400">
              {{ card.title }}
            </p>
          </div>
        </div>
      </UCard>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
      <UCard>
        <template #header>
          <span class="font-semibold">Jurnal Terbaru</span>
          <UButton
            to="/accounting/jurnal-umum"
            size="sm"
            variant="ghost"
            color="primary"
          >
            Lihat Semua
          </UButton>
        </template>

        <div class="flex flex-col divide-y divide-default">
          <div
            v-for="journal in summary?.recent_journals ?? []"
            :key="journal.id"
            class="flex items-center justify-between gap-2 py-2"
          >
            <div class="min-w-0">
              <p class="truncate font-medium">
                {{ journal.description }}
              </p>
              <p class="text-xs text-neutral-500 dark:text-neutral-400">
                {{ journal.entry_number }} · {{ formatDate(journal.entry_date) }}
              </p>
            </div>
            <div class="shrink-0 text-right">
              <p class="font-semibold">
                {{ formatCurrency(totalDebit(journal)) }}
              </p>
              <p
                class="text-xs text-neutral-500 dark:text-neutral-400"
              >
                {{ journal.lines.length }} baris
              </p>
            </div>
          </div>

          <p
            v-if="!summary?.recent_journals?.length"
            class="py-6 text-center text-sm text-neutral-500"
          >
            Belum ada jurnal
          </p>
        </div>
      </UCard>

      <UCard>
        <template #header>
          <span class="font-semibold">Menu Cepat</span>
        </template>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <UButton
            to="/accounting/jurnal-umum"
            icon="i-lucide-book-open"
            block
            color="neutral"
            variant="soft"
          >
            Jurnal Umum
          </UButton>
          <UButton
            to="/accounting/buku-besar"
            icon="i-lucide-book-copy"
            block
            color="neutral"
            variant="soft"
          >
            Buku Besar
          </UButton>
          <UButton
            to="/accounting/pemasukan"
            icon="i-lucide-trending-up"
            block
            color="success"
            variant="soft"
          >
            Pemasukan
          </UButton>
          <UButton
            to="/accounting/pengeluaran"
            icon="i-lucide-trending-down"
            block
            color="error"
            variant="soft"
          >
            Pengeluaran
          </UButton>
          <UButton
            to="/accounting/akun"
            icon="i-lucide-list-tree"
            block
            color="neutral"
            variant="soft"
          >
            Chart of Accounts
          </UButton>
          <UButton
            to="/accounting/neraca"
            icon="i-lucide-scale"
            block
            color="primary"
            variant="soft"
          >
            Neraca
          </UButton>
          <UButton
            to="/accounting/rekap-cashflow"
            icon="i-lucide-arrow-left-right"
            block
            color="neutral"
            variant="soft"
          >
            Rekap Cashflow
          </UButton>
          <UButton
            to="/accounting/rekap-biaya"
            icon="i-lucide-receipt"
            block
            color="error"
            variant="soft"
          >
            Rekap Biaya
          </UButton>
          <UButton
            to="/accounting/rekap-monitoring"
            icon="i-lucide-monitor"
            block
            color="neutral"
            variant="soft"
          >
            Rekap Monitoring
          </UButton>
          <UButton
            to="/accounting/kas-harian"
            icon="i-lucide-wallet"
            block
            color="neutral"
            variant="soft"
          >
            Kas Harian
          </UButton>
          <UButton
            to="/accounting/rekap-bunga-bank"
            icon="i-lucide-percent"
            block
            color="neutral"
            variant="soft"
          >
            Rekap Bunga Bank
          </UButton>
        </div>
      </UCard>
    </div>
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>
