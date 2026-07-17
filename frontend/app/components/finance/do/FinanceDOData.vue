<script setup lang="ts">
import { getPaginationRowModel } from "@tanstack/vue-table";
import { h, resolveComponent } from "vue";
import type { TableColumn } from "@nuxt/ui";
import type { OperationsDeliveryOrderOverview, Period, Range } from "~/types";

const UBadge = resolveComponent("UBadge");
const UButton = resolveComponent("UButton");
const table = useTemplateRef("table");
const columnPinning = ref({
  right: ["actions"],
});

// col, customer name, do number, po number, transport name, date created, status, action included (do returned document upload)
const sampleDONumber = [
  "722/DO/MAP/VI/26",
  "703/DO/MAP/VI/26",
  "696/DO/MAP/VI/26",
  "697/DO/MAP/VI/26",
];
const samplePONumber = ["112", "300", "115"];

const sampleCustomerAndTransportName = [
  "PT. MAHESA TOTAL SOLUSINDO",
  "PT. BERKAT ANUGERAH SEJAHTERA",
  "PT. BINA SARANA SUKSES",
];

const { data: OlData } = await useAsyncData(
  "offering letters",
  async () => {
    const offeringLetters: OperationsDeliveryOrderOverview[] = [];
    const currentDate = new Date();

    for (let i = 0; i < 15; i++) {
      const hoursAgo = randomInt(0, 48);
      const date = new Date(currentDate.getTime() - hoursAgo * 3600000);

      offeringLetters.push({
        id: (4600 - i).toString(),
        deliveryOrderNumber: randomFrom(sampleDONumber),
        purchaseOrderNumber: randomFrom(samplePONumber),
        customerName: randomFrom(sampleCustomerAndTransportName),
        transportName: randomFrom(sampleCustomerAndTransportName),
        dateCreated: date.toISOString(),
        dateChanged: date.toISOString(),
        status: randomFrom([
          "created",
          "document_returned",
        ]) as OperationsDeliveryOrderOverview["status"],
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

const columns: TableColumn<OperationsDeliveryOrderOverview>[] = [
  {
    accessorKey: "deliveryOrderNumber",
    header: "Nomor DO",
    cell: ({ row }) => `${row.getValue("deliveryOrderNumber")}`,
  },
  {
    accessorKey: "purchaseOrderNumber",
    header: "Nomor PO",
    cell: ({ row }) => `${row.getValue("purchaseOrderNumber")}`,
  },
  {
    accessorKey: "customerName",
    header: "Customer ID",
    cell: ({ row }) => `${row.getValue("customerName")}`,
  },
  {
    accessorKey: "transportName",
    header: "Nama Agen/Transportir",
    cell: ({ row }) => `${row.getValue("transportName")}`,
  },
  {
    accessorKey: "dateCreated",
    header: "Tanggal Dibuat",
    cell: ({ row }) => `${formatDate(row.getValue("dateCreated"))}`,
  },
  {
    accessorKey: "status",
    header: "Status DO",
    cell: ({ row }) => {
      const color = {
        created: "info" as const,
        document_returned: "success" as const,
      }[row.getValue("status") as string];

      const status = {
        created: "DO Telah Dibuat",
        document_returned: "DO Dikembalikan",
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
          { label: 'DO Dibuat', value: 'created' },
          { label: 'DO Dikembalikan', value: 'document_returned' },
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
          ...sampleCustomerAndTransportName.map((name) => ({
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
      :data="OlData"
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
            :to="`/operations/detail/delivery-order-${row.original.id}`"
            variant="solid"
            size="md"
            color="primary"
          >
            Lihat Surat
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
