<script setup lang="ts">
import type { ExportColumn } from "~/composables/useExport";
import type { RangeDate } from "~/types";
import type { CostRecapResponse, CostRecapRow } from "~/types/accounting";

const { get } = useApi();
const { toCSV, toExcel, toPDF } = useExport();

const range = ref<RangeDate>({
  start: new Date(Date.now() - 30 * 86400000),
  end: new Date(),
});
const search = ref("");
const debouncedSearch = refDebounced(search, 300);
const expandedGroups = ref<Set<string>>(new Set());

const exportColumns: ExportColumn<CostRecapRow>[] = [
  {
    header: "Tanggal",
    accessor: (row: CostRecapRow) => formatDate(row.entry_date),
  },
  { header: "Deskripsi", accessor: (row: CostRecapRow) => row.description },
  {
    header: "Akun",
    accessor: (row: CostRecapRow) =>
      `${row.account_code} · ${row.account_name}`,
  },
  { header: "Jumlah", accessor: (row: CostRecapRow) => row.amount },
  {
    header: "Referensi",
    accessor: (row: CostRecapRow) => row.reference ?? "-",
  },
];

function onExport(format: "excel" | "pdf" | "csv") {
  if (!data.value) return;
  const allRows = data.value.groups.flatMap((g) => g.items);
  const filename = `rekap-biaya-${new Date().toISOString().slice(0, 10)}`;
  const totals = [{ label: "Total Biaya", value: data.value.total_cost }];
  if (format === "excel")
    toExcel(filename, "Rekap Biaya", exportColumns, allRows);
  else if (format === "pdf")
    toPDF(filename, "Rekap Biaya", exportColumns, allRows, { totals });
  else toCSV(filename, exportColumns, allRows);
}

const { data, refresh, pending } = await useAsyncData(
  "accounting-cost-recap",
  async () => {
    const params: Record<string, string> = {};
    if (range.value.start)
      params.date_from = range.value.start.toISOString().split("T")[0] || "";
    if (range.value.end)
      params.date_to = range.value.end.toISOString().split("T")[0] || "";
    return get<CostRecapResponse>("/accounting/cost-recap", params);
  },
  { default: () => null, server: false },
);

const filteredGroups = computed(() => {
  if (!data.value) return [];
  if (!debouncedSearch.value) return data.value.groups;
  const q = debouncedSearch.value.toLowerCase();
  return data.value.groups
    .map((group) => ({
      ...group,
      items: group.items.filter((item: CostRecapRow) =>
        Object.values(item).some((v) => String(v).toLowerCase().includes(q)),
      ),
    }))
    .filter((group) => group.items.length > 0);
});

const totalCost = computed(() => data.value?.total_cost ?? 0);

function toggleGroup(code: string) {
  if (expandedGroups.value.has(code)) {
    expandedGroups.value.delete(code);
  } else {
    expandedGroups.value.add(code);
  }
}

watch([debouncedSearch, range], () => {
  refresh();
});

definePageMeta({ layout: "accounting" });
</script>

<template>
  <UDashboardPanel id="accounting-rekap-biaya">
    <template #header>
      <UDashboardNavbar>
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">Rekap Biaya</p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Seluruh biaya (expense) yang dikelompokkan per akun
            </p>
          </div>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-4 lg:p-6">
        <section class="flex flex-col lg:gap-4">
          <UCard>
            <div class="flex flex-col gap-3">
              <div class="flex flex-wrap items-end gap-3">
                <UInput
                  v-model="search"
                  icon="i-lucide-search"
                  placeholder="Cari deskripsi, akun..."
                  class="w-full sm:w-64"
                />
                <HomeDateRangePicker v-model="range" />
              </div>
              <div class="flex flex-wrap justify-end gap-2">
                <UDropdownMenu
                  :items="[
                    { type: 'label', label: 'Ekspor Data' },
                    { type: 'separator' },
                    {
                      label: 'Ekspor ke Excel',
                      icon: 'i-lucide-file-spreadsheet',
                      disabled: !data,
                      onSelect: () => onExport('excel'),
                    },
                    {
                      label: 'Ekspor ke PDF',
                      icon: 'i-lucide-file-text',
                      disabled: !data,
                      onSelect: () => onExport('pdf'),
                    },
                    {
                      label: 'Ekspor ke CSV',
                      icon: 'i-lucide-file-down',
                      disabled: !data,
                      onSelect: () => onExport('csv'),
                    },
                  ]"
                >
                  <UButton
                    icon="i-lucide-download"
                    color="neutral"
                    variant="soft"
                    :disabled="!data"
                  >
                    Export
                  </UButton>
                </UDropdownMenu>
              </div>
            </div>
          </UCard>

          <div v-if="pending" class="flex flex-col gap-4">
            <USkeleton class="h-20 rounded-lg" />
            <USkeleton v-for="i in 4" :key="i" class="h-28 rounded-lg" />
          </div>
          <template v-else-if="data">
            <UCard color="error" variant="subtle">
              <div class="flex items-center justify-between">
                <span class="text-sm text-neutral-500 dark:text-neutral-400"
                  >Total Biaya</span
                >
                <span class="text-2xl font-bold">{{
                  formatCurrency(totalCost)
                }}</span>
              </div>
            </UCard>

            <div class="flex flex-col gap-3">
              <UCard v-for="group in filteredGroups" :key="group.account_code">
                <template #header>
                  <button
                    class="flex items-center justify-between w-full text-left"
                    @click="toggleGroup(group.account_code)"
                  >
                    <div class="flex items-center gap-2">
                      <UIcon
                        :name="
                          expandedGroups.has(group.account_code)
                            ? 'i-lucide-chevron-down'
                            : 'i-lucide-chevron-right'
                        "
                        class="size-4 text-muted"
                      />
                      <span class="font-medium"
                        >{{ group.account_code }} ·
                        {{ group.account_name }}</span
                      >
                    </div>
                    <span class="font-bold text-error">{{
                      formatCurrency(group.total)
                    }}</span>
                  </button>
                </template>

                <template v-if="expandedGroups.has(group.account_code)">
                  <div class="flex flex-col divide-y divide-default">
                    <div
                      v-for="item in group.items"
                      :key="item.id"
                      class="flex items-center justify-between py-2 text-sm"
                    >
                      <div class="min-w-0">
                        <p class="truncate max-w-96">
                          {{ item.description }}
                        </p>
                        <p
                          class="text-xs text-neutral-500 dark:text-neutral-400"
                        >
                          {{ formatDate(item.entry_date) }}
                          <span v-if="item.reference"
                            >· {{ item.reference }}</span
                          >
                        </p>
                      </div>
                      <span class="font-medium shrink-0">{{
                        formatCurrency(item.amount)
                      }}</span>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <p class="text-sm text-neutral-500 py-1">
                    {{ group.items.length }} transaksi — klik untuk detail
                  </p>
                </template>
              </UCard>
            </div>

            <p
              v-if="!filteredGroups.length"
              class="py-6 text-center text-sm text-neutral-500"
            >
              Belum ada data biaya
            </p>
          </template>

          <UAlert
            v-else-if="!pending"
            title="Pilih Periode"
            description="Gunakan filter tanggal di atas untuk menampilkan rekap biaya."
            icon="i-lucide-info"
            color="info"
            variant="soft"
          />
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>
