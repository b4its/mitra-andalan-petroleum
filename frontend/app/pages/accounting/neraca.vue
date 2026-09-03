<script setup lang="ts">
import type { RangeDate } from "~/types";
import type {
  BalanceSheetAccount,
  BalanceSheetResponse,
} from "~/types/accounting";

const { get } = useApi();

const range = ref<RangeDate>({
  start: new Date(Date.now() - 30 * 86400000),
  end: new Date(),
});
const search = ref("");
const debouncedSearch = refDebounced(search, 300);

const {
  data: neraca,
  refresh,
  pending,
} = await useAsyncData(
  "accounting-neraca",
  async () => {
    const params: Record<string, string> = {};
    if (range.value.start)
      params.date_from = range.value.start.toISOString().split("T")[0] || "";
    if (range.value.end)
      params.date_to = range.value.end.toISOString().split("T")[0] || "";
    return get<BalanceSheetResponse>("/accounting/balance-sheet", params);
  },
  { default: () => null, server: false },
);

const isBalanced = computed(() => {
  if (!neraca.value) return true;
  return (
    Math.abs(
      neraca.value.total_assets -
        (neraca.value.total_liabilities + neraca.value.total_equity),
    ) < 1
  );
});

function filterAccounts(accounts: BalanceSheetAccount[]) {
  if (!debouncedSearch.value) return accounts;
  const q = debouncedSearch.value.toLowerCase();
  return accounts.filter(
    (a) =>
      a.account_code.toLowerCase().includes(q) ||
      a.account_name.toLowerCase().includes(q),
  );
}

watch([debouncedSearch, range], () => {
  refresh();
});

definePageMeta({ layout: "accounting" });
</script>

<template>
  <UDashboardPanel id="accounting-neraca">
    <template #header>
      <UDashboardNavbar>
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">Neraca (Balance Sheet)</p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Laporan posisi keuangan: Aset, Kewajiban, dan Ekuitas
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
                placeholder="Cari kode atau nama akun..."
                class="w-64"
              />
              <HomeDateRangePicker v-model="range" />
            </div>
          </UCard>

          <div v-if="pending" class="flex flex-col gap-4">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <USkeleton v-for="i in 3" :key="i" class="h-64 rounded-lg" />
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <USkeleton v-for="i in 3" :key="i" class="h-24 rounded-lg" />
            </div>
          </div>
          <template v-else-if="neraca">
            <!-- Balance Check -->
            <UCard v-if="!isBalanced" color="warning" variant="soft">
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-alert-triangle" class="size-5" />
                <span class="text-sm"
                  >Neraca tidak balance: Aset ({{
                    formatCurrency(neraca.total_assets)
                  }}) &ne; Kewajiban + Ekuitas ({{
                    formatCurrency(
                      neraca.total_liabilities + neraca.total_equity,
                    )
                  }})</span
                >
              </div>
            </UCard>
            <UCard v-else color="success" variant="soft">
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-check-circle" class="size-5" />
                <span class="text-sm"
                  >Neraca balance: Aset = Kewajiban + Ekuitas</span
                >
              </div>
            </UCard>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <!-- Aset -->
              <UCard>
                <template #header>
                  <div class="flex items-center justify-between">
                    <span class="font-semibold text-info">Aset</span>
                    <span class="font-bold text-lg">{{
                      formatCurrency(neraca.assets.total)
                    }}</span>
                  </div>
                </template>
                <div class="flex flex-col divide-y divide-default">
                  <div
                    v-for="acc in filterAccounts(neraca.assets.accounts)"
                    :key="acc.account_id"
                    class="flex items-center justify-between py-2 text-sm"
                  >
                    <span class="text-neutral-500 dark:text-neutral-400"
                      >{{ acc.account_code }} - {{ acc.account_name }}</span
                    >
                    <span class="font-medium">{{
                      formatCurrency(acc.balance)
                    }}</span>
                  </div>
                  <div
                    v-if="!neraca.assets.accounts.length"
                    class="py-4 text-center text-sm text-neutral-500"
                  >
                    Belum ada data aset
                  </div>
                </div>
              </UCard>

              <!-- Kewajiban -->
              <UCard>
                <template #header>
                  <div class="flex items-center justify-between">
                    <span class="font-semibold text-warning">Kewajiban</span>
                    <span class="font-bold text-lg">{{
                      formatCurrency(neraca.liabilities.total)
                    }}</span>
                  </div>
                </template>
                <div class="flex flex-col divide-y divide-default">
                  <div
                    v-for="acc in filterAccounts(neraca.liabilities.accounts)"
                    :key="acc.account_id"
                    class="flex items-center justify-between py-2 text-sm"
                  >
                    <span class="text-neutral-500 dark:text-neutral-400"
                      >{{ acc.account_code }} - {{ acc.account_name }}</span
                    >
                    <span class="font-medium">{{
                      formatCurrency(acc.balance)
                    }}</span>
                  </div>
                  <div
                    v-if="!neraca.liabilities.accounts.length"
                    class="py-4 text-center text-sm text-neutral-500"
                  >
                    Belum ada data kewajiban
                  </div>
                </div>
              </UCard>

              <!-- Ekuitas -->
              <UCard>
                <template #header>
                  <div class="flex items-center justify-between">
                    <span class="font-semibold text-primary">Ekuitas</span>
                    <span class="font-bold text-lg">{{
                      formatCurrency(neraca.equity.total)
                    }}</span>
                  </div>
                </template>
                <div class="flex flex-col divide-y divide-default">
                  <div
                    v-for="acc in filterAccounts(neraca.equity.accounts)"
                    :key="acc.account_id"
                    class="flex items-center justify-between py-2 text-sm"
                  >
                    <span class="text-neutral-500 dark:text-neutral-400"
                      >{{ acc.account_code }} - {{ acc.account_name }}</span
                    >
                    <span class="font-medium">{{
                      formatCurrency(acc.balance)
                    }}</span>
                  </div>
                  <div
                    v-if="!neraca.equity.accounts.length"
                    class="py-4 text-center text-sm text-neutral-500"
                  >
                    Belum ada data ekuitas
                  </div>
                </div>
              </UCard>
            </div>

            <!-- Summary -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <UCard color="info" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total Aset
                </p>
                <p class="text-2xl font-bold">
                  <CurrencyText :value="neraca.total_assets" size="lg" />
                </p>
              </UCard>
              <UCard color="warning" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total Kewajiban
                </p>
                <p class="text-2xl font-bold">
                  <CurrencyText :value="neraca.total_liabilities" size="lg" />
                </p>
              </UCard>
              <UCard color="primary" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total Ekuitas
                </p>
                <p class="text-2xl font-bold">
                  <CurrencyText :value="neraca.total_equity" size="lg" />
                </p>
              </UCard>
            </div>
          </template>

          <UAlert
            v-else-if="!pending"
            title="Pilih Periode"
            description="Gunakan filter tanggal di atas untuk menampilkan neraca."
            icon="i-lucide-info"
            color="info"
            variant="soft"
          />
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>
