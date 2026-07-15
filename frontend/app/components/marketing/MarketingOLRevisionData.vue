<script setup lang="ts">
import { getPaginationRowModel } from "@tanstack/vue-table";
import { h, resolveComponent } from "vue";
import type { TableColumn } from "@nuxt/ui";
import type { MarketingOfferingLetterOverview, Period, Range } from "~/types";

const UBadge = resolveComponent("UBadge");
const UButton = resolveComponent("UButton");
const table = useTemplateRef("table");
const columnPinning = ref({
  right: ["actions"],
});

// col, customer name, ol number, date created, date changed, status, action included (ol revision, upload po from customer)
const sampleOLNumber = [
  "722/MAP/II-06/26",
  "703/MAP/I-06/26",
  "696/MAP/I-06/26",
  "697/MAP/I-06/26",
];

const sampleCustomerName = [
  "PT. MAHESA TOTAL SOLUSINDO",
  "PT. BERKAT ANUGERAH SEJAHTERA",
  "PT. BINA SARANA SUKSES",
];

const { data: OlData } = await useAsyncData(
  "offering letters",
  async () => {
    const offeringLetters: MarketingOfferingLetterOverview[] = [];
    const currentDate = new Date();

    for (let i = 0; i < 15; i++) {
      const hoursAgo = randomInt(0, 48);
      const date = new Date(currentDate.getTime() - hoursAgo * 3600000);

      offeringLetters.push({
        id: (4600 - i).toString(),
        offeringLetterNumber: randomFrom(sampleOLNumber),
        customerName: randomFrom(sampleCustomerName),
        dateCreated: date.toISOString(),
        dateChanged: date.toISOString(),
        status: randomFrom([
          "created",
          "under_revision",
          "po_received",
        ]) as MarketingOfferingLetterOverview["status"],
        fuelTotalPrice: randomInt(15000, 20000),
        transportPrice: randomInt(1000, 3000),
      });
    }

    return offeringLetters.sort(
      (a, b) =>
        new Date(b.dateCreated).getTime() - new Date(a.dateCreated).getTime(),
    );
  },
  {
    default: () => [],
  },
);

const columns: TableColumn<MarketingOfferingLetterOverview>[] = [
  {
    accessorKey: "offeringLetterNumber",
    header: "Nomor Penawaran",
    cell: ({ row }) => `${row.getValue("offeringLetterNumber")}`,
  },
  {
    accessorKey: "customerName",
    header: "Customer ID",
    cell: ({ row }) => `${row.getValue("customerName")}`,
  },
  {
    accessorKey: "fuelTotalPrice",
    header: "Harga Dasar",
    cell: ({ row }) => `${formatCurrency(row.getValue("fuelTotalPrice"))}`,
  },
  {
    accessorKey: "transportPrice",
    header: "Ongkos Transportir",
    cell: ({ row }) => `${formatCurrency(row.getValue("transportPrice"))}`,
  },
  {
    accessorKey: "dateCreated",
    header: "Penawaran Dibuat",
    cell: ({ row }) => `${formatDate(row.getValue("dateCreated"))}`,
  },
  {
    accessorKey: "dateChanged",
    header: "Penawaran Direvisi",
    cell: ({ row }) => `${formatDate(row.getValue("dateChanged"))}`,
  },
  {
    accessorKey: "status",
    header: "Status Penawaran",
    cell: ({ row }) => {
      const color = {
        created: "info" as const,
        under_revision: "warning" as const,
        po_received: "success" as const,
      }[row.getValue("status") as string];

      const status = {
        created: "Penawaran Telah Dibuat",
        under_revision: "Penawaran Dalam Revisi",
        po_received: "PO Diterima",
      }[row.getValue("status") as string];

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
    size: 220,
  },
];

const statusFilter = ref("all");
const customerNameFilter = ref("all");

watch(
  () => statusFilter.value,
  (newVal) => {
    if (!table?.value?.tableApi) return;

    const statusColumn = table.value.tableApi.getColumn("status");
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
          { label: 'Penawaran Telah Dibuat', value: 'created' },
          { label: 'Penawaran Dalam Revisi', value: 'under_revision' },
          { label: 'PO Diterima', value: 'po_received' },
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
          ...sampleCustomerName.map((name) => ({ label: name, value: name })),
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
      :data="OlData"
      :columns="columns"
      :column-pinning="columnPinning"
      :ui="{
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
            :to="`/marketing/customer/surat-penawaran-${row.original.id}`"
            variant="solid"
            size="md"
            color="primary"
          >
            Lihat Surat
          </UButton>
          <UButton
            :to="`/marketing/customer/revisi-surat-penawaran-${row.original.id}`"
            variant="soft"
            size="md"
            color="neutral"
          >
            Revisi Penawaran
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
