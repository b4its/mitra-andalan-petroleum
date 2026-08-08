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

const search = ref("");
const debouncedSearch = refDebounced(search, 300);

const { data: PoData } = await useAsyncData(
  "purchase-orders-supplier",
  async () => {
    const params: Record<string, string | number> = {
      page: 1,
      page_size: 50,
      type: "supplier",
    };
    if (debouncedSearch.value) params.search = debouncedSearch.value;
    const res = await get<{ items: PurchaseOrdersSupplier[] }>(
      "/purchase-orders",
      params,
    );
    return res.items.map((purchaseOrder: PurchaseOrdersSupplier) => ({
      id: purchaseOrder.id,
      offeringLetterNumber: purchaseOrder.po_number,
      customerName: purchaseOrder.supplier_name,
      fuelTotalPrice: purchaseOrder.total,
      transportPrice: 0,
      distanceKm: purchaseOrder?.details.delivery.distance || 0,
      dateCreated: purchaseOrder.created_at.toString(),
      dateChanged: purchaseOrder.updated_at.toString(),
      status: purchaseOrder.status,
    }));
  },
  { default: () => [], watch: [debouncedSearch] },
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
    accessorKey: "fuelTotalQty",
    header: "Total",
    cell: ({ row }) => `${formatCurrency(row.getValue("fuelTotalQty"))}`,
  },
  {
    accessorKey: "distanceKm",
    header: "Jarak KM",
    cell: ({ row }) => `${formatToKm(row.getValue("distanceKm"))}`,
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

const detailOpen = ref(false);
const detailId = ref<string | null>(null);
function openDetail(id: string) {
  detailId.value = id;
  detailOpen.value = true;
}
</script>

<template>
  <section class="flex flex-col lg:gap-4">
    <div class="flex items-center gap-2">
      <UInput
        v-model="search"
        icon="i-lucide-search"
        placeholder="Cari nomor PO atau supplier..."
        class="w-64"
      />
    </div>

    <UTable
      ref="table"
      v-model:pagination="pagination"
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
      :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }"
    >
      <template #actions-cell="{ row }">
        <div class="flex items-center gap-2">
          <UButton
            icon="i-lucide-eye"
            size="sm"
            color="neutral"
            variant="ghost"
            @click="openDetail(row.original.id)"
          >
            Selengkapnya
          </UButton>
          <UButton
            :to="`/marketing/detail-supplier/po-supplier-${row.original.id}`"
            variant="solid"
            size="sm"
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

  <RecordDetailModal v-model:open="detailOpen" type="po" :id="detailId" />
</template>
