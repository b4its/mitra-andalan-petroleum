<script setup lang="ts">
import { h } from "vue";
import type { TableColumn } from "@nuxt/ui";
import type { ExportColumn } from "~/composables/useExport";
import type { MonitoringResponse, MonitoringRow } from "~/types/accounting";
import type { RangeDate } from "~/types";

const { get } = useApi();
const { toCSV, toExcel, toPDF } = useExport();

const range = ref<RangeDate>({
  start: new Date(Date.now() - 30 * 86400000),
  end: new Date(),
});
const search = ref("");
const debouncedSearch = refDebounced(search, 300);

const filteredRows = computed(() => {
  if (!data.value) return [];
  if (!debouncedSearch.value) return data.value.rows;
  const q = debouncedSearch.value.toLowerCase();
  return data.value.rows.filter((row: MonitoringRow) =>
    Object.values(row).some((v) => String(v).toLowerCase().includes(q)),
  );
});

// ── Pagination (5 per halaman) ────────────────────────────────
const page = ref(1);
const PAGE_SIZE = 5;
const pagedRows = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE;
  return filteredRows.value.slice(start, start + PAGE_SIZE);
});
watch(debouncedSearch, () => {
  page.value = 1;
});

const exportColumns: ExportColumn<MonitoringRow>[] = [
  { header: "Bulan", accessor: (row: MonitoringRow) => row.bulan },
  { header: "Invoice", accessor: (row: MonitoringRow) => row.invoice },
  {
    header: "Modal Elnusa",
    accessor: (row: MonitoringRow) => row.modal_elnusa,
  },
  { header: "OAT", accessor: (row: MonitoringRow) => row.oat },
  {
    header: "Margin Kotor",
    accessor: (row: MonitoringRow) => row.gross_margin,
  },
  { header: "Penghasilan", accessor: (row: MonitoringRow) => row.penghasilan },
  { header: "Operasional", accessor: (row: MonitoringRow) => row.operasional },
  {
    header: "Fee Manajemen",
    accessor: (row: MonitoringRow) => row.fee_manajemen,
  },
];

function onExport(format: "excel" | "pdf" | "csv") {
  if (!data.value) return;
  const rangeLabel = `${range.value.start.toISOString().split("T")[0] || "awal"}_${range.value.end.toISOString().split("T")[0] || "akhir"}`;
  const filename = `rekap-monitoring-${rangeLabel}`;
  const totals = [
    { label: "Total Penghasilan", value: data.value.total_penghasilan },
    { label: "Total Margin Kotor", value: data.value.total_gross_margin },
  ];
  if (format === "excel")
    toExcel(filename, "Rekap Monitoring", exportColumns, data.value.rows);
  else if (format === "pdf")
    toPDF(
      filename,
      `Rekap Monitoring ${range.value.start.toISOString().split("T")[0]} - ${range.value.end.toISOString().split("T")[0]}`,
      exportColumns,
      data.value.rows,
      { totals },
    );
  else toCSV(filename, exportColumns, data.value.rows);
}

const { data, pending } = await useAsyncData(
  "accounting-monitoring",
  () => {
    const params: Record<string, string> = {};
    if (range.value.start)
      params.date_from = range.value.start.toISOString().split("T")[0] || "";
    if (range.value.end)
      params.date_to = range.value.end.toISOString().split("T")[0] || "";
    return get<MonitoringResponse>("/accounting/monitoring", params);
  },
  { default: () => null, watch: [range], server: false },
);

const columns: TableColumn<MonitoringRow>[] = [
  {
    accessorKey: "bulan",
    header: "Bulan",
    cell: ({ row }) =>
      h("span", { class: "font-medium" }, row.getValue("bulan")),
  },
  {
    accessorKey: "invoice",
    header: "Invoice",
    meta: { class: { th: "text-right", td: "text-right" } },
    cell: ({ row }) => formatCurrency(row.getValue("invoice")),
  },
  {
    accessorKey: "modal_elnusa",
    header: "Modal Elnusa",
    meta: { class: { th: "text-right", td: "text-right" } },
    cell: ({ row }) => formatCurrency(row.getValue("modal_elnusa")),
  },
  {
    accessorKey: "oat",
    header: "OAT",
    meta: { class: { th: "text-right", td: "text-right" } },
    cell: ({ row }) => formatCurrency(row.getValue("oat")),
  },
  {
    accessorKey: "gross_margin",
    header: "Margin Kotor",
    meta: { class: { th: "text-right", td: "text-right" } },
    cell: ({ row }) => {
      const val = Number(row.getValue("gross_margin"));
      return h(
        "span",
        {
          class:
            val >= 0
              ? "text-success font-semibold"
              : "text-error font-semibold",
        },
        formatCurrency(val),
      );
    },
  },
  {
    accessorKey: "penghasilan",
    header: "Penghasilan",
    meta: { class: { th: "text-right", td: "text-right" } },
    cell: ({ row }) =>
      h(
        "span",
        { class: "font-semibold text-success" },
        formatCurrency(row.getValue("penghasilan")),
      ),
  },
  {
    accessorKey: "operasional",
    header: "Operasional",
    meta: { class: { th: "text-right", td: "text-right" } },
    cell: ({ row }) =>
      h(
        "span",
        { class: "text-error" },
        formatCurrency(row.getValue("operasional")),
      ),
  },
  {
    accessorKey: "fee_manajemen",
    header: "Fee Manajemen",
    meta: { class: { th: "text-right", td: "text-right" } },
    cell: ({ row }) => formatCurrency(row.getValue("fee_manajemen")),
  },
];

definePageMeta({ layout: "accounting" });
</script>

<template>
  <UDashboardPanel id="accounting-rekap-monitoring">
    <template #header>
      <UDashboardNavbar>
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">Rekap Monitoring</p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Monitoring pendapatan, biaya, dan margin per bulan
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
                  placeholder="Cari bulan, akun, kategori..."
                  class="w-64"
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
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <USkeleton v-for="i in 4" :key="i" class="h-24 rounded-lg" />
            </div>
            <USkeleton class="h-64 rounded-lg" />
          </div>
          <template v-else-if="data && data.rows.length">
            <!-- Summary Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <UCard color="success" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total Penghasilan
                </p>
                <p class="text-2xl font-bold">
                  <CurrencyText :value="data.total_penghasilan" size="lg" />
                </p>
              </UCard>
              <UCard color="error" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total Operasional
                </p>
                <p class="text-2xl font-bold">
                  <CurrencyText :value="data.total_operasional" size="lg" />
                </p>
              </UCard>
              <UCard color="primary" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total Margin Kotor
                </p>
                <p class="text-2xl font-bold">
                  <CurrencyText :value="data.total_gross_margin" size="lg" />
                </p>
              </UCard>
              <UCard color="info" variant="subtle">
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  Total OAT
                </p>
                <p class="text-2xl font-bold">
                  <CurrencyText :value="data.total_oat" size="lg" />
                </p>
              </UCard>
            </div>

            <UCard class="overflow-x-auto">
              <UTable
                :data="pagedRows"
                :columns="columns"
                :ui="{
                  base: 'table-fixed border-separate border-spacing-0 min-w-[800px]',
                  thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
                  tbody: '[&>tr]:last:[&>td]:border-b-0',
                  th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
                  td: 'border-b border-default',
                }"
              />
              <div
                v-if="filteredRows.length > PAGE_SIZE"
                class="flex justify-end border-t border-default pt-4 px-4"
              >
                <UPagination
                  v-model="page"
                  :items-per-page="PAGE_SIZE"
                  :total="filteredRows.length"
                />
              </div>
            </UCard>

            <!-- Total Row -->
            <UCard color="neutral" variant="subtle">
              <div
                class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-4 text-center"
              >
                <div>
                  <p class="text-xs text-muted">Invoice</p>
                  <p class="font-bold">
                    {{ data.total_invoice }}
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted">Modal Elnusa</p>
                  <p class="font-bold">
                    <CurrencyText :value="data.total_modal" size="sm" />
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted">OAT</p>
                  <p class="font-bold">
                    <CurrencyText :value="data.total_oat" size="sm" />
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted">Margin Kotor</p>
                  <p class="font-bold">
                    <CurrencyText :value="data.total_gross_margin" size="sm" />
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted">Penghasilan</p>
                  <p class="font-bold">
                    <CurrencyText :value="data.total_penghasilan" size="sm" />
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted">Operasional</p>
                  <p class="font-bold">
                    <CurrencyText :value="data.total_operasional" size="sm" />
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted">Fee Manajemen</p>
                  <p class="font-bold">
                    <CurrencyText :value="data.total_fee_manajemen" size="sm" />
                  </p>
                </div>
              </div>
            </UCard>

            <!-- Akun Terkait -->
            <UCard color="info" variant="subtle">
              <div class="flex items-start gap-2">
                <UIcon name="i-lucide-book-open" class="mt-0.5 text-info" />
                <div class="text-sm space-y-1">
                  <p class="font-medium">Akun Terkait Laporan Ini</p>
                  <ul
                    class="list-disc list-inside text-neutral-600 dark:text-neutral-300 space-y-0.5"
                  >
                    <li>
                      Penghasilan — akun pendapatan (revenue): kredit jurnal.
                    </li>
                    <li>Operasional — akun beban (expense): debit jurnal.</li>
                    <li>
                      OAT — akun
                      <code class="font-mono">4-1100</code> Pendapatan Jasa
                      Angkut.
                    </li>
                    <li>
                      Modal Elnusa &amp; Fee Manajemen — estimasi dari total
                      penghasilan.
                    </li>
                    <li>
                      Jika data tidak terhubung ke akun, dikategorikan dari alur
                      sistem utama (Marketing → Operations → Finance).
                    </li>
                  </ul>
                </div>
              </div>
            </UCard>
          </template>

          <UAlert
            v-else-if="!pending"
            title="Belum Ada Data"
            description="Belum ada data monitoring untuk tahun ini."
            icon="i-lucide-info"
            color="info"
            variant="soft"
          />
        </section>
      </div>
    </template>
  </UDashboardPanel>
</template>
