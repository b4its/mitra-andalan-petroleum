<script setup lang="ts">
import { h } from "vue";
import type { TableColumn } from "@nuxt/ui";
import type { AccountingLedger, AccountingLedgerRow } from "~/types/accounting";
import type { RangeDate } from "~/types";

const { get } = useApi();

const range = ref<RangeDate>({
  start: new Date(Date.now() - 30 * 86400000),
  end: new Date(),
});
const search = ref("");
const debouncedSearch = refDebounced(search, 300);

const {
  data: ledgers,
  refresh,
  pending,
} = await useAsyncData(
  "accounting-ledger-all",
  async () => {
    const params: Record<string, string | number> = {};
    if (range.value.start)
      params.date_from = range.value.start.toISOString().split("T")[0] || "";
    if (range.value.end)
      params.date_to = range.value.end.toISOString().split("T")[0] || "";
    const res = await get<{ items: AccountingLedger[] }>(
      "/accounting/ledger-all",
      params,
    );
    return res.items || [];
  },
  { default: () => [], server: false, watch: [range] },
);

async function onSearch() {
  await refresh();
}

const filteredData = computed(() => {
  if (!ledgers.value) return [];
  if (!debouncedSearch.value) return ledgers.value;
  const q = debouncedSearch.value.toLowerCase();
  return ledgers.value.filter((item: AccountingLedger) =>
    Object.values(item).some((v) => String(v).toLowerCase().includes(q)),
  );
});

// ── Pagination (5 per halaman) ────────────────────────────────
const page = ref(1);
const PAGE_SIZE = 5;
const pagedData = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE;
  return filteredData.value.slice(start, start + PAGE_SIZE);
});
watch(debouncedSearch, () => {
  page.value = 1;
});

const expandedAccount = ref<string | null>(null);

function toggleExpand(accountId: string) {
  expandedAccount.value =
    expandedAccount.value === accountId ? null : accountId;
}

const totalOpening = computed(() =>
  ledgers.value.reduce((sum, item) => sum + (item.opening_balance || 0), 0),
);
const totalClosing = computed(() =>
  ledgers.value.reduce((sum, item) => sum + (item.closing_balance || 0), 0),
);

const columns: TableColumn<AccountingLedger>[] = [
  {
    id: "expand",
    header: "",
    cell: ({ row }) =>
      h(
        "button",
        {
          class: "p-1",
          onClick: () => toggleExpand(row.original.account_id),
        },
        h(
          "span",
          expandedAccount.value === row.original.account_id ? "▾" : "▸",
        ),
      ),
  },
  {
    accessorKey: "account_code",
    header: "Kode Akun",
    cell: ({ row }) => `${row.getValue("account_code")}`,
  },
  {
    accessorKey: "account_name",
    header: "Nama Akun",
    cell: ({ row }) => `${row.getValue("account_name")}`,
  },
  {
    accessorKey: "account_type",
    header: "Tipe",
    cell: ({ row }) => {
      const typeMap: Record<string, string> = {
        asset: "Aset",
        liability: "Kewajiban",
        equity: "Ekuitas",
        revenue: "Pendapatan",
        expense: "Beban",
      };
      return (
        typeMap[row.getValue("account_type") as string] ??
        row.getValue("account_type")
      );
    },
  },
  {
    accessorKey: "opening_balance",
    header: "Saldo Awal",
    meta: {
      class: { th: "text-right", td: "text-right" },
    },
    cell: ({ row }) =>
      formatCurrency(Number(row.getValue("opening_balance")) || 0),
  },
  {
    accessorKey: "closing_balance",
    header: "Saldo Akhir",
    meta: {
      class: { th: "text-right", td: "text-right" },
    },
    cell: ({ row }) =>
      h(
        "span",
        { class: "font-semibold" },
        formatCurrency(Number(row.getValue("closing_balance")) || 0),
      ),
  },
  { id: "actions", header: "Aksi" },
];

const detailColumns: TableColumn<AccountingLedgerRow>[] = [
  {
    accessorKey: "entry_date",
    header: "Tanggal",
    cell: ({ row }) => `${formatDate(row.getValue("entry_date"))}`,
  },
  {
    accessorKey: "entry_number",
    header: "Nomor Jurnal",
    cell: ({ row }) => `${row.getValue("entry_number")}`,
  },
  {
    accessorKey: "description",
    header: "Deskripsi",
    cell: ({ row }) => {
      const desc = row.getValue("description") as string;
      return h("span", { class: "truncate block max-w-72" }, desc);
    },
  },
  {
    accessorKey: "debit",
    header: "Debit",
    meta: {
      class: { th: "text-right", td: "text-right" },
    },
    cell: ({ row }) =>
      Number(row.getValue("debit")) > 0
        ? formatCurrency(Number(row.getValue("debit")))
        : "-",
  },
  {
    accessorKey: "credit",
    header: "Kredit",
    meta: {
      class: { th: "text-right", td: "text-right" },
    },
    cell: ({ row }) =>
      Number(row.getValue("credit")) > 0
        ? formatCurrency(Number(row.getValue("credit")))
        : "-",
  },
  {
    accessorKey: "balance",
    header: "Saldo",
    meta: {
      class: { th: "text-right", td: "text-right" },
    },
    cell: ({ row }) =>
      h(
        "span",
        { class: "font-semibold" },
        formatCurrency(Number(row.getValue("balance"))),
      ),
  },
];

definePageMeta({ layout: "accounting" });
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
            <p class="text-base font-semibold">Buku Besar</p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Seluruh akun beserta mutasi dan saldonya (mirip neraca)
            </p>
          </div>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-4 lg:p-6">
        <section class="flex flex-col lg:gap-4">
          <UCard>
            <div class="flex flex-wrap items-end gap-3">
              <UInput
                v-model="search"
                icon="i-lucide-search"
                placeholder="Cari nomor jurnal, deskripsi..."
                class="w-64"
              />
              <HomeDateRangePicker v-model="range" />
            </div>
          </UCard>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <UCard>
              <p class="text-sm text-neutral-500 dark:text-neutral-400">
                Total Saldo Awal
              </p>
              <p class="mt-1 text-xl font-bold">
                {{ formatCurrency(totalOpening) }}
              </p>
            </UCard>
            <UCard>
              <p class="text-sm text-neutral-500 dark:text-neutral-400">
                Total Saldo Akhir
              </p>
              <p class="mt-1 text-xl font-bold">
                {{ formatCurrency(totalClosing) }}
              </p>
            </UCard>
          </div>

          <UCard>
            <div v-if="pending" class="space-y-3">
              <USkeleton v-for="i in 5" :key="i" class="h-12 rounded-lg" />
            </div>
            <template v-else>
              <UTable
                :data="pagedData"
                :columns="columns"
                :ui="{
                  base: 'table-fixed border-separate border-spacing-0',
                  thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
                  tbody: '[&>tr]:last:[&>td]:border-b-0',
                  th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
                  td: 'border-b border-default',
                }"
              >
                <template #actions-cell="{ row }">
                  <UButton
                    size="sm"
                    color="neutral"
                    variant="ghost"
                    :icon="
                      expandedAccount === row.original.account_id
                        ? 'i-lucide-chevron-up'
                        : 'i-lucide-chevron-down'
                    "
                    @click="toggleExpand(row.original.account_id)"
                  >
                    Detail
                  </UButton>
                </template>
              </UTable>
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
                v-if="ledgers.length === 0"
                class="py-6 text-center text-sm text-neutral-500"
              >
                Belum ada mutasi pada rentang tanggal ini
              </p>

              <!-- Detail mutasi per akun yang diekspansi -->
              <div
                v-for="item in ledgers"
                v-show="expandedAccount === item.account_id"
                :key="item.account_id"
                class="mt-4 border-t border-default pt-4"
              >
                <p class="mb-2 text-sm font-semibold">
                  {{ item.account_code }} · {{ item.account_name }}
                  <span class="text-neutral-500 dark:text-neutral-400">
                    (Saldo Awal: {{ formatCurrency(item.opening_balance) }} →
                    Saldo Akhir: {{ formatCurrency(item.closing_balance) }})
                  </span>
                </p>
                <UTable
                  :data="item.rows"
                  :columns="detailColumns"
                  :ui="{
                    base: 'table-fixed border-separate border-spacing-0',
                    thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
                    tbody: '[&>tr]:last:[&>td]:border-b-0',
                    th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
                    td: 'border-b border-default',
                  }"
                />
                <p
                  v-if="item.rows.length === 0"
                  class="py-3 text-center text-sm text-neutral-500"
                >
                  Tidak ada mutasi untuk akun ini pada rentang tanggal tersebut
                </p>
              </div>
            </template>
          </UCard>
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>
