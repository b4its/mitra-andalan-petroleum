<script setup lang="ts">
import { getPaginationRowModel } from "@tanstack/vue-table";
import { h, resolveComponent } from "vue";
import type { TableColumn } from "@nuxt/ui";
import type { FinanceInvoiceOverview } from "~/types";

const UBadge = resolveComponent("UBadge");
const UButton = resolveComponent("UButton");
const table = useTemplateRef("table");
const columnPinning = ref({
  right: ["actions"],
});

const sampleInvoiceNumber = [
  "1086/INV/MAP/V/2026",
  "1085/INV/MAP/V/2026",
  "1084/INV/MAP/IV/2026",
  "1083/INV/MAP/IV/2026",
  "1082/INV/MAP/III/2026",
];

const sampleCustomerName = [
  "PT. MAHESA TOTAL SOLUSINDO",
  "PT. BERKAT ANUGERAH SEJAHTERA",
  "PT. BINA SARANA SUKSES",
  "PT. MIGAS KUKAR MANDIRI",
];

const { data: invoiceData } = await useAsyncData(
  "finance invoices",
  async () => {
    const financeInvoices: FinanceInvoiceOverview[] = [];
    const currentDate = new Date();

    for (let i = 0; i < 15; i++) {
      const daysAgo = randomInt(0, 60);
      const dateCreated = new Date(currentDate.getTime() - daysAgo * 86400000);
      const invoiceStatus = randomFrom([
        "paid",
        "unpaid",
        "overdue",
      ]) as FinanceInvoiceOverview["invoiceStatus"];

      financeInvoices.push({
        id: (1100 - i).toString(),
        customerName: randomFrom(sampleCustomerName),
        invoiceNumber: randomFrom(sampleInvoiceNumber),
        termsDay: randomFrom([14, 30, 45, 60]),
        dateCreated: dateCreated.toISOString(),
        grandTotal: randomInt(45000000, 250000000),
        invoiceStatus,
        deadlineStatus:
          invoiceStatus === "overdue"
            ? "overdue"
            : invoiceStatus === "paid"
              ? "on_time"
              : randomFrom(["on_time", "due_soon"]),
      });
    }

    return financeInvoices.sort(
      (a, b) =>
        new Date(b.dateCreated).getTime() - new Date(a.dateCreated).getTime(),
    );
  },
  {
    default: () => [],
  },
);

const columns: TableColumn<FinanceInvoiceOverview>[] = [
  {
    accessorKey: "customerName",
    header: "Nama Customer",
    cell: ({ row }) => `${row.getValue("customerName")}`,
  },
  {
    accessorKey: "invoiceNumber",
    header: "Nomor Invoice",
    cell: ({ row }) => `${row.getValue("invoiceNumber")}`,
  },
  {
    accessorKey: "termsDay",
    header: "Terms",
    cell: ({ row }) => `${row.getValue("termsDay")} hari`,
  },
  {
    accessorKey: "dateCreated",
    header: "Tanggal Dibuat",
    cell: ({ row }) => `${formatDate(row.getValue("dateCreated"))}`,
  },
  {
    accessorKey: "grandTotal",
    header: "Grand Total",
    cell: ({ row }) =>
      `${new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        maximumFractionDigits: 0,
      }).format(Number(row.getValue("grandTotal")))}`,
  },
  {
    accessorKey: "invoiceStatus",
    header: "Status Invoice",
    cell: ({ row }) => {
      const color = {
        unpaid: "warning" as const,
        paid: "success" as const,
        overdue: "error" as const,
      }[row.getValue("invoiceStatus") as string];

      const status = {
        unpaid: "Belum Dibayar",
        paid: "Lunas",
        overdue: "Jatuh Tempo",
      }[row.getValue("invoiceStatus") as string];

      return h(
        UBadge,
        { class: "capitalize", variant: "soft", color },
        () => status,
      );
    },
  },
  {
    accessorKey: "deadlineStatus",
    header: "Status Deadline",
    cell: ({ row }) => {
      const color = {
        on_time: "success" as const,
        due_soon: "warning" as const,
        overdue: "error" as const,
      }[row.getValue("deadlineStatus") as string];

      const status = {
        on_time: "Tepat Waktu",
        due_soon: "Segera Jatuh Tempo",
        overdue: "Terlambat",
      }[row.getValue("deadlineStatus") as string];

      return h(
        UBadge,
        { class: "capitalize", variant: "soft", color },
        () => status,
      );
    },
  },
  {
    id: "actions",
    header: "Aksi",
  },
];

const statusFilter = ref("all");
const customerNameFilter = ref("all");

watch(
  () => statusFilter.value,
  (newVal) => {
    if (!table?.value?.tableApi) return;

    const statusColumn = table.value.tableApi.getColumn("invoiceStatus");
    if (!statusColumn) return;

    if (newVal === "all") {
      statusColumn.setFilterValue(undefined);
    } else {
      statusColumn.setFilterValue(newVal);
    }
  },
);

watch(
  () => customerNameFilter.value,
  (newVal) => {
    if (!table?.value?.tableApi) return;

    const customerNameColumn = table.value.tableApi.getColumn("customerName");
    if (!customerNameColumn) return;

    if (newVal === "all") {
      customerNameColumn.setFilterValue(undefined);
    } else {
      customerNameColumn.setFilterValue(newVal);
    }
  },
);

const pagination = ref({
  pageIndex: 0,
  pageSize: 7,
});
</script>

<template>
  <section class="flex flex-col lg:gap-4">
    <div class="flex justify-start gap-2">
      <USelect
        v-model="statusFilter"
        :items="[
          { label: 'Semua Status', value: 'all' },
          { label: 'Belum Dibayar', value: 'unpaid' },
          { label: 'Lunas', value: 'paid' },
          { label: 'Jatuh Tempo', value: 'overdue' },
        ]"
        :ui="{
          trailingIcon:
            'group-data-[state=open]:rotate-180 transition-transform duration-200',
        }"
        placeholder="Filter status"
        class="min-w-28"
      />
      <USelect
        v-model="customerNameFilter"
        :items="[
          { label: 'Semua Customer', value: 'all' },
          ...sampleCustomerName.map((name) => ({
            label: name,
            value: name,
          })),
        ]"
        :ui="{
          trailingIcon:
            'group-data-[state=open]:rotate-180 transition-transform duration-200',
        }"
        placeholder="Filter status"
        class="min-w-28"
      />
    </div>

    <UTable
      ref="table"
      :data="invoiceData"
      :columns="columns"
      :column-pinning="columnPinning"
      :ui="{
        // root: 'max-w-7xl',
        base: 'table-fixed border-separate border-spacing-0',
        thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
        tbody: '[&>tr]:last:[&>td]:border-b-0',
        th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
        td: 'border-b border-default',
      }"
      v-model:pagination="pagination"
      :pagination-options="{
        getPaginationRowModel: getPaginationRowModel(),
      }"
    >
      <template #actions-cell="{ row }">
        <div class="flex items-center gap-2">
          <UButton
            :to="`/finance/detail/invoice-${row.original.id}`"
            variant="solid"
            size="md"
            color="primary"
          >
            Lihat Invoice
          </UButton>
        </div>
      </template>
    </UTable>

    <div class="flex justify-end border-t border-default pt-4 px-4">
      <UPagination
        :page="(table?.tableApi?.getState().pagination.pageIndex || 0) + 1"
        :items-per-page="table?.tableApi?.getState().pagination.pageSize"
        :total="table?.tableApi?.getFilteredRowModel().rows.length"
        @update:page="(p) => table?.tableApi?.setPageIndex(p - 1)"
      />
    </div>
  </section>
</template>
