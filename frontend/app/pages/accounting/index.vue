<script setup lang="ts">
import { h } from "vue";
import type { TableColumn } from "@nuxt/ui";
import type {
  AccountingAccount,
  AccountingJournal,
  AccountingSummary,
  DailyCashResponse,
  CashflowResponse,
  CostRecapResponse,
  MonitoringResponse,
  BankInterestResponse,
} from "~/types/accounting";
import AdminBarChart from "~/components/admin/charts/AdminBarChart.vue";
import AdminPieChart from "~/components/admin/charts/AdminPieChart.vue";
import type { RangeDate } from "~/types";

const { get } = useApi();
const toast = useToast();

// ── Filter ────────────────────────────────────────────────────
const range = ref<RangeDate>({
  start: new Date(Date.now() - 30 * 86400000),
  end: new Date(),
});
const accountFilters = ref<string[]>([]);
const { data: accountOptions } = await useAsyncData(
  "accounting-dash-account-options",
  () =>
    get<AccountingAccount[]>("/accounting/accounts", {
      include_inactive: true,
    }),
  { default: () => [], server: false },
);
const accountItems = computed(() =>
  accountOptions.value.map((a) => ({
    label: `${a.code} · ${a.name}`,
    value: a.id,
  })),
);

function totalDebit(journal: AccountingJournal): number {
  return journal.lines.reduce((sum, line) => sum + (line.debit || 0), 0);
}

const {
  data: summary,
  refresh,
  pending,
} = await useAsyncData(
  "accounting-summary",
  async () => {
    const params: Record<string, string | number | string[]> = {};
    if (range.value.start)
      params.date_from = range.value.start.toISOString().split("T")[0] || "";
    if (range.value.end)
      params.date_to = range.value.end.toISOString().split("T")[0] || "";
    return get<AccountingSummary>("/accounting/summary", params);
  },
  { default: () => null, server: false, watch: [range] },
);

const { data: dailyCash } = await useAsyncData(
  "accounting-dash-daily-cash",
  async () => {
    const params: Record<string, string> = {};
    if (range.value.start)
      params.date_from = range.value.start.toISOString().split("T")[0] || "";
    if (range.value.end)
      params.date_to = range.value.end.toISOString().split("T")[0] || "";
    return get<DailyCashResponse>("/accounting/daily-cash", params);
  },
  { default: () => null, server: false, watch: [range] },
);

const { data: cashflow } = await useAsyncData(
  "accounting-dash-cashflow",
  async () => {
    const params: Record<string, string> = {};
    if (range.value.start)
      params.date_from = range.value.start.toISOString().split("T")[0] || "";
    if (range.value.end)
      params.date_to = range.value.end.toISOString().split("T")[0] || "";
    return get<CashflowResponse>("/accounting/cashflow", params);
  },
  { default: () => null, server: false, watch: [range] },
);

const { data: costRecap } = await useAsyncData(
  "accounting-dash-cost-recap",
  async () => {
    const params: Record<string, string> = {};
    if (range.value.start)
      params.date_from = range.value.start.toISOString().split("T")[0] || "";
    if (range.value.end)
      params.date_to = range.value.end.toISOString().split("T")[0] || "";
    return get<CostRecapResponse>("/accounting/cost-recap", params);
  },
  { default: () => null, server: false, watch: [range] },
);

const { data: monitoring } = await useAsyncData(
  "accounting-dash-monitoring",
  async () => {
    const params: Record<string, string> = {};
    if (range.value.start)
      params.date_from = range.value.start.toISOString().split("T")[0] || "";
    if (range.value.end)
      params.date_to = range.value.end.toISOString().split("T")[0] || "";
    return get<MonitoringResponse>("/accounting/monitoring", params);
  },
  { default: () => null, server: false, watch: [range] },
);

const { data: bankInterest } = await useAsyncData(
  "accounting-dash-bank-interest",
  async () => {
    const params: Record<string, string> = {};
    if (range.value.start)
      params.date_from = range.value.start.toISOString().split("T")[0] || "";
    if (range.value.end)
      params.date_to = range.value.end.toISOString().split("T")[0] || "";
    return get<BankInterestResponse>("/accounting/bank-interest", params);
  },
  { default: () => null, server: false, watch: [range] },
);

const { data: journals } = await useAsyncData(
  "accounting-dash-journals",
  async () => {
    const params: Record<string, string | number | string[]> = {
      page: 1,
      page_size: 50,
    };
    if (range.value.start)
      params.date_from = range.value.start.toISOString().split("T")[0] || "";
    if (range.value.end)
      params.date_to = range.value.end.toISOString().split("T")[0] || "";
    if (accountFilters.value.length) params.account_ids = accountFilters.value;
    const res = await get<{ items: AccountingJournal[] }>(
      "/accounting/journal",
      params,
    );
    return res.items || [];
  },
  { default: () => [], server: false, watch: [range, accountFilters] },
);

// ── Pagination (5 per halaman) ────────────────────────────────
const journalPage = ref(1);
const JOURNAL_PAGE_SIZE = 5;
const pagedJournals = computed(() => {
  const start = (journalPage.value - 1) * JOURNAL_PAGE_SIZE;
  return journals.value.slice(start, start + JOURNAL_PAGE_SIZE);
});
watch([range, accountFilters], () => {
  journalPage.value = 1;
});

// ── Bento cards ──────────────────────────────────────────────
const cards = computed(() => [
  {
    title: "Total Pemasukan",
    value: formatCurrency(summary.value?.total_income ?? 0),
    icon: "i-lucide-trending-up",
    color: "success" as const,
    to: "/accounting/pemasukan",
  },
  {
    title: "Total Pengeluaran",
    value: formatCurrency(summary.value?.total_expense ?? 0),
    icon: "i-lucide-trending-down",
    color: "error" as const,
    to: "/accounting/pengeluaran",
  },
  {
    title: "Laba Bersih",
    value: formatCurrency(summary.value?.net_income ?? 0),
    icon: "i-lucide-wallet",
    color: "primary" as const,
    to: "/accounting/jurnal-umum",
  },
  {
    title: "Saldo Kas & Bank",
    value: formatCurrency(summary.value?.cash_balance ?? 0),
    icon: "i-lucide-circle-dollar-sign",
    color: "info" as const,
    to: "/accounting/buku-besar",
  },
]);

const countCards = computed(() => [
  {
    title: "Jumlah Jurnal",
    value: summary.value?.journal_count ?? 0,
    icon: "i-lucide-book-open",
  },
  {
    title: "Jumlah Akun",
    value: summary.value?.account_count ?? 0,
    icon: "i-lucide-list-tree",
  },
  {
    title: "Pemasukan",
    value: summary.value?.income_count ?? 0,
    icon: "i-lucide-arrow-down-to-line",
  },
  {
    title: "Pengeluaran",
    value: summary.value?.expense_count ?? 0,
    icon: "i-lucide-arrow-up-from-line",
  },
]);

// ── Grafik ───────────────────────────────────────────────────
const incomeExpenseLabels = ["Pemasukan", "Pengeluaran"];
const incomeExpenseValues = computed(() => {
  const s = summary.value;
  return s ? [s.total_income, s.total_expense] : [];
});

const typeLabels: Record<string, string> = {
  asset: "Aset",
  liability: "Kewajiban",
  equity: "Ekuitas",
  revenue: "Pendapatan",
  expense: "Beban",
};
const typeColors: Record<string, string> = {
  asset: "rgba(59,130,246,0.8)",
  liability: "rgba(245,158,11,0.8)",
  equity: "rgba(16,185,129,0.8)",
  revenue: "rgba(16,185,129,0.8)",
  expense: "rgba(239,68,68,0.8)",
};

const accountDistLabels = computed(() => {
  const list: AccountingAccount[] = accountOptions.value || [];
  const map = new Map<string, number>();
  for (const acc of list) map.set(acc.type, (map.get(acc.type) || 0) + 1);
  return [...map.keys()].map((k) => typeLabels[k] ?? k);
});
const accountDistValues = computed(() => {
  const list: AccountingAccount[] = accountOptions.value || [];
  const map = new Map<string, number>();
  for (const acc of list) map.set(acc.type, (map.get(acc.type) || 0) + 1);
  return [...map.values()];
});
const accountDistColors = computed(() => {
  const list: AccountingAccount[] = accountOptions.value || [];
  const map = new Map<string, number>();
  for (const acc of list) map.set(acc.type, (map.get(acc.type) || 0) + 1);
  return [...map.keys()].map((k) => typeColors[k] ?? "rgba(100,116,139,0.8)");
});

const cashflowChart = computed(() => {
  const c = cashflow.value;
  if (!c) return null;
  return {
    labels: ["Operasi", "Investasi", "Pendanaan"],
    datasets: [
      {
        label: "Arus Kas",
        data: [c.operating.total, c.investing.total, c.financing.total],
        backgroundColor: [
          c.operating.total >= 0
            ? "rgba(16,185,129,0.8)"
            : "rgba(239,68,68,0.8)",
          c.investing.total >= 0
            ? "rgba(16,185,129,0.8)"
            : "rgba(239,68,68,0.8)",
          c.financing.total >= 0
            ? "rgba(16,185,129,0.8)"
            : "rgba(239,68,68,0.8)",
        ],
      },
    ],
  };
});

const costRecapChart = computed(() => {
  const groups = costRecap.value?.groups || [];
  if (!groups.length) return null;
  const top = [...groups].sort((a, b) => b.total - a.total).slice(0, 8);
  return {
    labels: top.map((g) => `${g.account_code} · ${g.account_name}`),
    datasets: [
      {
        label: "Total Biaya",
        data: top.map((g) => g.total),
        backgroundColor: "rgba(239,68,68,0.8)",
      },
    ],
  };
});

const monitoringChart = computed(() => {
  const rows = monitoring.value?.rows || [];
  if (!rows.length) return null;
  return {
    labels: rows.map((r) => r.bulan),
    datasets: [
      {
        label: "Penghasilan",
        data: rows.map((r) => r.penghasilan),
        backgroundColor: "rgba(16,185,129,0.8)",
      },
      {
        label: "Operasional",
        data: rows.map((r) => r.operasional),
        backgroundColor: "rgba(239,68,68,0.8)",
      },
      {
        label: "Margin Kotor",
        data: rows.map((r) => r.gross_margin),
        backgroundColor: "rgba(59,130,246,0.8)",
      },
    ],
  };
});

const bankInterestChart = computed(() => {
  const b = bankInterest.value;
  if (!b) return null;
  return {
    labels: ["Pokok Pinjaman", "Total Bunga", "Total Pembayaran"],
    datasets: [
      {
        label: "Nominal",
        data: [b.total_principal, b.total_interest, b.total_paid],
        backgroundColor: [
          "rgba(59,130,246,0.8)",
          "rgba(245,158,11,0.8)",
          "rgba(16,185,129,0.8)",
        ],
      },
    ],
  };
});

const dailyCashChart = computed(() => {
  const d = dailyCash.value;
  if (!d) return null;
  return {
    labels: ["Saldo Awal", "Total Masuk", "Total Keluar", "Saldo Akhir"],
    datasets: [
      {
        label: "Nominal",
        data: [
          d.opening_balance,
          d.total_debit,
          d.total_credit,
          d.closing_balance,
        ],
        backgroundColor: [
          "rgba(100,116,139,0.8)",
          "rgba(16,185,129,0.8)",
          "rgba(239,68,68,0.8)",
          "rgba(59,130,246,0.8)",
        ],
      },
    ],
  };
});

// ── Tabel ────────────────────────────────────────────────────
const journalColumns: TableColumn<AccountingJournal>[] = [
  { accessorKey: "entry_number", header: "Nomor Jurnal" },
  {
    accessorKey: "entry_date",
    header: "Tanggal",
    cell: ({ row }) =>
      row.getValue("entry_date") ? formatDate(row.getValue("entry_date")) : "-",
  },
  {
    accessorKey: "description",
    header: "Deskripsi",
    cell: ({ row }) => {
      const desc = row.getValue("description") as string;
      return h("div", { class: "flex flex-col gap-0.5 min-w-0" }, [
        h("span", { class: "truncate max-w-64" }, desc),
        h(
          "span",
          { class: "text-xs text-muted" },
          row.original.lines.map((l) => l.account_code).join(", "),
        ),
      ]);
    },
  },
  {
    accessorKey: "amount",
    header: "Nominal",
    meta: { class: { th: "text-right", td: "text-right" } },
    cell: ({ row }) => formatCurrency(totalDebit(row.original)),
  },
];

function onError(err: unknown) {
  toast.add({
    title: "Gagal",
    description: err instanceof Error ? err.message : "Terjadi kesalahan",
    icon: "i-lucide-alert-triangle",
    color: "error",
  });
}

definePageMeta({ layout: "accounting" });
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
      <div v-if="pending" class="p-4 lg:p-6 space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          <USkeleton v-for="i in 4" :key="i" class="h-24 rounded-lg" />
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          <USkeleton v-for="i in 4" :key="i" class="h-24 rounded-lg" />
        </div>
        <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
          <USkeleton class="h-64 rounded-lg" />
          <USkeleton class="h-64 rounded-lg" />
        </div>
      </div>
      <div v-else class="p-4 lg:p-6">
        <section class="flex flex-col gap-4">
          <!-- Filter -->
          <UCard>
            <div class="flex flex-col gap-3">
              <p class="text-sm font-medium">Filter Data Accounting</p>
              <div class="flex flex-wrap items-end gap-3">
                <HomeDateRangePicker v-model="range" />

                <USelectMenu
                  v-model="accountFilters"
                  :items="accountItems"
                  value-key="value"
                  multiple
                  searchable
                  :search-input="{ placeholder: 'Cari akun...' }"
                  placeholder="Semua Akun"
                  class="w-full sm:w-64"
                />
              </div>
            </div>
          </UCard>

          <!-- Bento: data utama -->
          <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            <UCard v-for="card in cards" :key="card.title">
              <div class="flex items-center justify-between gap-2">
                <div>
                  <p class="text-sm text-neutral-500 dark:text-neutral-400">
                    {{ card.title }}
                  </p>
                  <p class="mt-1 text-2xl font-bold">
                    <CurrencyText :value="card.value" size="lg" />
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

          <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
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

          <!-- Tabel: jurnal terbaru -->
          <UCard>
            <template #header>
              <div class="flex flex-col gap-3">
                <div class="flex items-center justify-between">
                  <span class="font-semibold">Jurnal Terbaru</span>
                  <UButton
                    to="/accounting/jurnal-umum"
                    size="sm"
                    variant="ghost"
                    color="primary"
                  >
                    Lihat Semua
                  </UButton>
                </div>
              </div>
            </template>

            <UTable
              :data="pagedJournals"
              :columns="journalColumns"
              :ui="{
                base: 'table-fixed border-separate border-spacing-0',
                thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
                tbody: '[&>tr]:last:[&>td]:border-b-0',
                th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
                td: 'border-b border-default',
              }"
            />
            <div
              v-if="journals.length > JOURNAL_PAGE_SIZE"
              class="flex justify-end border-t border-default pt-4 px-4"
            >
              <UPagination
                v-model="journalPage"
                :items-per-page="JOURNAL_PAGE_SIZE"
                :total="journals.length"
              />
            </div>
            <p
              v-if="!journals.length"
              class="py-6 text-center text-sm text-neutral-500"
            >
              Belum ada jurnal
            </p>
          </UCard>

          <!-- Tabel: ringkasan kas harian -->
          <UCard v-if="dailyCash">
            <template #header>
              <span class="font-semibold">Ringkasan Kas Harian</span>
            </template>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">Saldo Awal</p>
                <p class="text-xl font-bold">
                  <CurrencyText :value="dailyCash.opening_balance" size="md" />
                </p>
              </div>
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">Total Masuk</p>
                <p class="text-xl font-bold text-success">
                  <CurrencyText :value="dailyCash.total_debit" size="md" />
                </p>
              </div>
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">Total Keluar</p>
                <p class="text-xl font-bold text-error">
                  <CurrencyText :value="dailyCash.total_credit" size="md" />
                </p>
              </div>
              <div class="rounded-lg border border-default p-3">
                <p class="text-sm text-muted">Saldo Akhir</p>
                <p class="text-xl font-bold">
                  <CurrencyText :value="dailyCash.closing_balance" size="md" />
                </p>
              </div>
            </div>
          </UCard>

          <!-- Grafik -->
          <div>
            <div class="mb-3 flex items-center justify-between">
              <p
                class="text-sm font-semibold uppercase tracking-wide text-muted"
              >
                Grafik
              </p>
              <p class="text-xs text-muted">
                Visualisasi data accounting (terfilter)
              </p>
            </div>
            <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
              <UCard>
                <template #header>
                  <div class="flex items-center justify-between">
                    <span class="font-semibold">Pemasukan vs Pengeluaran</span>
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
                        'rgba(239,68,68,0.8)',
                      ],
                    },
                  ]"
                />
                <UEmpty
                  v-else
                  icon="i-lucide-chart-bar"
                  title="Belum ada data"
                />
              </UCard>

              <UCard>
                <template #header>
                  <span class="font-semibold">Distribusi Akun per Tipe</span>
                </template>
                <AdminPieChart
                  v-if="accountDistLabels.length"
                  :labels="accountDistLabels"
                  :data="accountDistValues"
                  :background-color="accountDistColors"
                />
                <UEmpty
                  v-else
                  icon="i-lucide-chart-pie"
                  title="Belum ada data"
                />
              </UCard>

              <UCard v-if="cashflowChart">
                <template #header>
                  <span class="font-semibold">Grafik Arus Kas</span>
                </template>
                <AdminBarChart
                  :labels="cashflowChart.labels"
                  :datasets="cashflowChart.datasets"
                  :height="220"
                />
              </UCard>

              <UCard v-if="dailyCashChart">
                <template #header>
                  <span class="font-semibold">Grafik Kas Harian</span>
                </template>
                <AdminBarChart
                  :labels="dailyCashChart.labels"
                  :datasets="dailyCashChart.datasets"
                  :height="220"
                />
              </UCard>

              <UCard v-if="costRecapChart">
                <template #header>
                  <span class="font-semibold">Grafik Rekap Biaya</span>
                </template>
                <AdminBarChart
                  :labels="costRecapChart.labels"
                  :datasets="costRecapChart.datasets"
                  :height="240"
                />
              </UCard>

              <UCard v-if="monitoringChart">
                <template #header>
                  <span class="font-semibold">Grafik Monitoring per Bulan</span>
                </template>
                <AdminBarChart
                  :labels="monitoringChart.labels"
                  :datasets="monitoringChart.datasets"
                  :height="260"
                />
              </UCard>

              <UCard v-if="bankInterestChart">
                <template #header>
                  <span class="font-semibold">Grafik Rekap Bunga Bank</span>
                </template>
                <AdminBarChart
                  :labels="bankInterestChart.labels"
                  :datasets="bankInterestChart.datasets"
                  :height="220"
                />
              </UCard>
            </div>
          </div>
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>
