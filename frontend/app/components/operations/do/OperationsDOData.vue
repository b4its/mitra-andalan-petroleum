<script setup lang="ts">
import { getPaginationRowModel } from "@tanstack/vue-table";
import { h, resolveComponent } from "vue";
import type { TableColumn } from "@nuxt/ui";
import type { OperationsDeliveryOrderOverview } from "~/types";

const UBadge = resolveComponent("UBadge");
const UButton = resolveComponent("UButton");
const table = useTemplateRef("table");
const columnPinning = ref({ right: ["actions"] });

const { get } = useApi();

const { data: DoData } = await useAsyncData(
  "delivery-orders",
  async () => {
    const res = await get<{ items: any[] }>("/delivery-orders", { page: 1, page_size: 50 })
    return (res.items || []).map((d: any) => ({
      id: d.id,
      deliveryOrderNumber: d.do_number,
      customerName: d.customer_name,
      purchaseOrderNumber: d.po_number,
      transportName: d.transport_name,
      dateCreated: d.created_at,
      dateChanged: d.updated_at,
      status: d.status,
    }))
  },
  { default: () => [] },
);

const columns: TableColumn<OperationsDeliveryOrderOverview>[] = [
  {
    accessorKey: "deliveryOrderNumber",
    header: "Nomor DO",
    cell: ({ row }) => `${row.getValue("deliveryOrderNumber")}`,
  },
  {
    accessorKey: "customerName",
    header: "Customer",
    cell: ({ row }) => `${row.getValue("customerName")}`,
  },
  {
    accessorKey: "purchaseOrderNumber",
    header: "Nomor PO",
    cell: ({ row }) => `${row.getValue("purchaseOrderNumber")}`,
  },
  {
    accessorKey: "transportName",
    header: "Transportir",
    cell: ({ row }) => `${row.getValue("transportName")}`,
  },
  {
    accessorKey: "dateCreated",
    header: "Dibuat",
    cell: ({ row }) => `${formatDate(row.getValue("dateCreated"))}`,
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const color = { created: "info" as const, document_returned: "success" as const }[row.getValue("status") as string];
      const label = { created: "Dibuat", document_returned: "Dokumen Kembali" }[row.getValue("status") as string];
      return h(UBadge, { class: "capitalize", variant: "soft", color }, () => label);
    },
  },
  {
    id: "actions",
    header: "Aksi",
    size: 180,
  },
];

const pagination = ref({ pageIndex: 0, pageSize: 7 });
</script>

<template>
  <section class="flex flex-col lg:gap-4">
    <UTable
      ref="table"
      :data="DoData"
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
      :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }"
    >
      <template #actions-cell="{ row }">
        <UButton
          :to="`/operations/detail/delivery-order-${row.original.id}`"
          variant="solid" size="md" color="primary"
        >Detail</UButton>
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
