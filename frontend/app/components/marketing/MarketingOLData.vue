<script setup lang="ts">
import { getPaginationRowModel } from "@tanstack/vue-table";
import { h, resolveComponent } from "vue";
import type { TableColumn } from "@nuxt/ui";
import type { MarketingOfferingLetterOverview } from "~/types";
import type { OfferingLetters } from "~/types/marketing";

const UBadge = resolveComponent("UBadge");
const UButton = resolveComponent("UButton");
const table = useTemplateRef("table");
const columnPinning = ref({
  right: ["actions"],
});

const { get } = useApi();

const { data: OlData } = await useAsyncData(
  "offering-letters",
  async () => {
    const res = await get<{ items: OfferingLetters[] }>("/offering-letters", {
      page: 1,
      page_size: 50,
    });
    return res.items.map((ol: OfferingLetters) => ({
      id: ol.id,
      offeringLetterNumber: ol.offering_letter_number,
      customerName: ol.customer_name,
      fuelTotalPrice: ol.fuel_total_price,
      transportPrice: ol.transport_price,
      dateCreated: ol.created_at.toString(),
      dateChanged: ol.updated_at.toString(),
      status: ol.status,
    }));
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
            :to="`/marketing/detail/surat-penawaran-${row.original.id}`"
            variant="solid"
            size="md"
            color="primary"
          >
            Lihat Surat
          </UButton>
          <UButton
            v-if="
              row.original.status === 'created' ||
              row.original.status === 'under_revision'
            "
            :to="`/marketing/detail/revisi-surat-penawaran-${row.original.id}`"
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
