<script setup lang="ts">
import { h } from "vue";
import type { TableColumn } from "@nuxt/ui";
import type { CashflowResponse, CashflowItem } from "~/types/accounting";
import type { RangeDate } from "~/types";

const { get } = useApi();

const range = ref<RangeDate>({
  start: new Date(Date.now() - 30 * 86400000),
  end: new Date(),
});
const search = ref("");
const debouncedSearch = refDebounced(search, 300);

const {
  data: cashflow,
  refresh,
  pending,
} = await useAsyncData(
  "accounting-cashflow",
  async () => {
    const params: Record<string, string> = {};
    if (range.value.start)
      params.date_from = range.value.start.toISOString().split("T")[0] || "";
    if (range.value.end)
      params.date_to = range.value.end.toISOString().split("T")[0] || "";
    return get<CashflowResponse>("/accounting/cashflow", params);
  },
  { default: () => null, server: false },
);

const filteredOperating = computed(() => {
  if (!cashflow.value) return [];
  if (!debouncedSearch.value) return cashflow.value.operating.items;
  const q = debouncedSearch.value.toLowerCase();
  return cashflow.value.operating.items.filter((item: CashflowItem) =>
    Object.values(item).some((v) => String(v).toLowerCase().includes(q)),
  );
});

// ── Pagination (5 per halaman) ────────────────────────────────
const page = ref(1);
const PAGE_SIZE = 5;
const pagedData = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE;
  return filteredOperating.value.slice(start, start + PAGE_SIZE);
});
watch(debouncedSearch, () => {
  page.value = 1;
});

const columns: TableColumn<CashflowItem>[] = [
  {
    accessorKey: "account_code",
    header: "Akun",
    cell: ({ row }) => {
      const code = row.getValue("account_code") as string;
      const name = row.getValue("account_name") as string;
      return h("div", { class: "flex flex-col gap-0.5" }, [
        h("span", { class: "text-xs font-medium text-muted" }, code || "—"),
        h("span", { class: "text-xs text-muted" }, name || "Alur Sistem Utama"),
      ]);
    },
  },
  {
    accessorKey: "description",
    header: "Deskripsi",
    cell: ({ row }) => {
      const desc = row.getValue("description") as string;
      return h("span", { class: "truncate block max-w-96" }, desc);
    },
  },
  {
    accessorKey: "category",
    header: "Kategori",
    cell: ({ row }) => {
      const cat = row.getValue("category") as string;
      return h("span", { class: "text-xs text-muted" }, cat);
    },
  },
  {
    accessorKey: "amount",
    header: "Jumlah",
    meta: { class: { th: "text-right", td: "text-right" } },
    cell: ({ row }) => {
      const amount = Number(row.getValue("amount"));
      const color = amount >= 0 ? "text-success" : "text-error";
      return h(
        "span",
        { class: `font-semibold ${color}` },
        formatCurrency(amount),
      );
    },
  },
];

watch([range], () => {
  refresh();
});

definePageMeta({ layout: "accounting" });
</script>

<template>
  <UDashboardPanel id="accounting-cashflow">
    <template #header>
      <UDashboardNavbar>
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">Rekap Arus Kas (Cashflow)</p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Laporan arus kas: operasi, investasi, dan pendanaan
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
                placeholder="Cari deskripsi, kategori..."
                class="w-full sm:w-64"
              />
              <HomeDateRangePicker v-model="range" />

              <UButton
                icon="i-lucide-search"
                :loading="pending"
                @click="() => refresh()"
              >
                Tampilkan
              </UButton>
            </div>
          </UCard>

          <div v-if="pending" class="flex flex-col gap-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <USkeleton v-for="i in 4" :key="i" class="h-24 rounded-lg" />
            </div>
            <USkeleton class="h-64 rounded-lg" />
          </div>
          <template v-else-if="cashflow">
            <!-- Summary Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <UCard color="neutral" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Saldo Awal
                </p>
                <p class="text-2xl font-bold">
                  <CurrencyText :value="cashflow.opening_balance" size="lg" />
                </p>
              </UCard>
              <UCard color="success" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Arus Kas Bersih
                </p>
                <p
                  class="text-2xl font-bold"
                  :class="
                    cashflow.net_cashflow >= 0 ? 'text-success' : 'text-error'
                  "
                >
                  <CurrencyText :value="cashflow.net_cashflow" size="lg" />
                </p>
              </UCard>
              <UCard color="primary" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Saldo Akhir
                </p>
                <p class="text-2xl font-bold">
                  <CurrencyText :value="cashflow.closing_balance" size="lg" />
                </p>
              </UCard>
              <UCard color="info" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Arus Kas Operasi
                </p>
                <p
                  class="text-2xl font-bold"
                  :class="
                    cashflow.operating.total >= 0
                      ? 'text-success'
                      : 'text-error'
                  "
                >
                  <CurrencyText :value="cashflow.operating.total" size="lg" />
                </p>
              </UCard>
            </div>

            <!-- Operating Cashflow -->
            <UCard>
              <template #header>
                <div class="flex items-center justify-between">
                  <span class="font-semibold">Arus Kas Operasi</span>
                  <span
                    class="font-bold text-lg"
                    :class="
                      cashflow.operating.total >= 0
                        ? 'text-success'
                        : 'text-error'
                    "
                  >
                  <CurrencyText :value="cashflow.operating.total" size="md" />
                  </span>
                </div>
              </template>
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
              />
              <div
                v-if="filteredOperating.length > PAGE_SIZE"
                class="flex justify-end border-t border-default pt-4 px-4"
              >
                <UPagination
                  v-model="page"
                  :items-per-page="PAGE_SIZE"
                  :total="filteredOperating.length"
                />
              </div>
              <p
                v-if="!cashflow.operating.items.length"
                class="py-6 text-center text-sm text-neutral-500"
              >
                Belum ada data arus kas operasi
              </p>
            </UCard>

            <!-- Investing & Financing -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <UCard>
                <template #header>
                  <div class="flex items-center justify-between">
                    <span class="font-semibold">Arus Kas Investasi</span>
                    <span class="font-bold text-lg">
                      <CurrencyText :value="cashflow.investing.total" size="md" />
                    </span>
                  </div>
                </template>
                <p class="py-6 text-center text-sm text-neutral-500">
                  Belum ada data arus kas investasi
                </p>
              </UCard>
              <UCard>
                <template #header>
                  <div class="flex items-center justify-between">
                    <span class="font-semibold">Arus Kas Pendanaan</span>
                    <span class="font-bold text-lg">
                      <CurrencyText :value="cashflow.financing.total" size="md" />
                    </span>
                  </div>
                </template>
                <p class="py-6 text-center text-sm text-neutral-500">
                  Belum ada data arus kas pendanaan
                </p>
              </UCard>
            </div>
          </template>

          <UAlert
            v-else-if="!pending"
            title="Pilih Periode"
            description="Gunakan filter tanggal di atas untuk menampilkan arus kas."
            icon="i-lucide-info"
            color="info"
            variant="soft"
          />
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>
