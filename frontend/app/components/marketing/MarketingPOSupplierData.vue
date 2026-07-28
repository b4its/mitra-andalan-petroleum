<script setup lang="ts">
import { getPaginationRowModel } from "@tanstack/vue-table";
import { h, resolveComponent } from "vue";
import type { TableColumn } from "@nuxt/ui";
import type { MarketingOfferingLetterOverview } from "~/types";
import type { PurchaseOrdersSupplier } from "~/types/marketing";

const UBadge = resolveComponent("UBadge");
const UButton = resolveComponent("UButton");
const table = useTemplateRef("table");
const columnPinning = ref({ right: ["actions"] });

const { get } = useApi();

const { data: PoData } = await useAsyncData(
  "purchase-orders-supplier",
  async () => {
    const res = await get<{ items: PurchaseOrdersSupplier[] }>(
      "/purchase-orders",
      { page: 1, page_size: 50, type: "supplier" },
    );
    return res.items.map((purchaseOrder: PurchaseOrdersSupplier) => ({
      id: purchaseOrder.id,
      offeringLetterNumber: purchaseOrder.po_number,
      customerName: purchaseOrder.supplier_name,
      fuelTotalQty: purchaseOrder.total,
      transportPrice: 0,
      dateCreated: purchaseOrder.created_at.toString(),
      dateChanged: purchaseOrder.updated_at.toString(),
      status: purchaseOrder.status,
    }));
  },
  { default: () => [] },
);

const columns: TableColumn<MarketingOfferingLetterOverview>[] = [
  {
    accessorKey: "offeringLetterNumber",
    header: "Nomor PO",
    cell: ({ row }) => `${row.getValue("offeringLetterNumber")}`,
  },
  {
    accessorKey: "customerName",
    header: "Supplier",
    cell: ({ row }) => `${row.getValue("customerName")}`,
  },
  {
    accessorKey: "fuelTotalPrice",
    header: "Total",
    cell: ({ row }) => `${formatCurrency(row.getValue("fuelTotalPrice"))}`,
  },
  {
    accessorKey: "dateCreated",
    header: "Dibuat",
    cell: ({ row }) => `${formatDate(row.getValue("dateCreated"))}`,
  },
  {
    id: "actions",
    header: "Aksi",
    size: 220,
  },
];

const pagination = ref({ pageIndex: 0, pageSize: 7 });
</script>

<template>
  <section class="flex flex-col lg:gap-4">
    <UTable
      ref="table"
      :data="PoData"
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
        <div class="flex items-center gap-2">
          <UButton
            :to="`/marketing/detail-supplier/po-supplier-${row.original.id}`"
            variant="solid"
            size="md"
            color="primary"
            >Lihat Surat</UButton
          >
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
