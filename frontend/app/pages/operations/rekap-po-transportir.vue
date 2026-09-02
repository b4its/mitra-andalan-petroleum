<script setup lang="ts">
import { getPaginationRowModel } from "@tanstack/vue-table";
import { h } from "vue";
import type { TableColumn } from "@nuxt/ui";
import type { PoTransportirs } from "~/types/operations";

const table = useTemplateRef("table");
const UBadge = resolveComponent("UBadge");
const { get } = useApi();

const search = ref("");
const debouncedSearch = refDebounced(search, 300);

const { data: rows, pending } = await useAsyncData(
  "operations-po-transportir",
  async () => {
    const params: Record<string, string | number> = { page: 1, page_size: 50 };
    if (debouncedSearch.value) params.search = debouncedSearch.value;

    const res = await get<{ items: PoTransportirs[] }>(
      "/po-transportir",
      params,
    );
    return res.items || [];
  },
  { default: () => [], server: false, watch: [debouncedSearch] },
);

const columns: TableColumn<PoTransportirs>[] = [
  {
    accessorKey: "po_number",
    header: "Nomor PO Transportir",
    cell: ({ row }) => `${row.getValue("po_number")}`,
  },
  {
    accessorKey: "date",
    header: "Tanggal",
    cell: ({ row }) => {
      const date = String(row.getValue("date") || "");
      return date ? formatDateDoc(new Date(date)) : "-";
    },
  },
  {
    accessorKey: "receiver",
    header: "Transportir",
    cell: ({ row }) => row.getValue("receiver") || "-",
  },
  {
    accessorKey: "pic_person",
    header: "PIC",
    cell: ({ row }) => row.getValue("pic_person") || "-",
  },
  {
    accessorKey: "total",
    header: "Total",
    cell: ({ row }) => formatCurrency(row.getValue("total") as number),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const color =
        {
          created: "info" as const,
          document_returned: "warning" as const,
          completed: "success" as const,
        }[row.getValue("status") as string] ?? "neutral";
      const label = statusLabel(row.getValue("status") as string);
      return h(UBadge, { variant: "subtle", color: color }, label);
    },
  },
  { id: "actions", header: "Aksi" },
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

const pagination = ref({ pageIndex: 0, pageSize: 5 });

definePageMeta({ layout: "operations" });
</script>

<template>
  <UDashboardPanel id="operations-po-transportir">
    <template #header>
      <UDashboardNavbar>
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #title>
          <div>
            <p class="text-base font-semibold">
              Surat Purchase Order Transportir
            </p>
          </div>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-4 lg:p-6">
        <div class="flex flex-wrap items-center gap-2 mb-4">
          <UInput
            v-model="search"
            icon="i-lucide-search"
            placeholder="Cari nomor PO atau nama transportir..."
            class="w-full sm:w-64"
            @keyup.enter="() => {}"
          />
          <USelect
            v-model="statusFilter"
            :items="[
              { label: 'Semua Status', value: 'all' },
              { label: 'PO Telah Dibuat', value: 'created' },
              { label: 'PO Dikembalikan', value: 'document_returned' },
              { label: 'PO Selesai', value: 'completed' },
            ]"
            :ui="{
              trailingIcon:
                'group-data-[state=open]:rotate-180 transition-transform duration-200',
            }"
            placeholder="Filter status"
            class="min-w-28"
          />
        </div>

        <div v-if="pending" class="space-y-3">
          <USkeleton v-for="i in 5" :key="i" class="h-12 rounded-lg" />
        </div>
        <UTable
          v-else
          ref="table"
          v-model:pagination="pagination"
          :data="rows"
          :columns="columns"
          :ui="{
            base: 'table-fixed border-separate border-spacing-0',
            thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
            tbody: '[&>tr]:last:[&>td]:border-b-0',
            th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
            td: 'border-b border-default',
          }"
          :pagination-options="{
            getPaginationRowModel: getPaginationRowModel(),
          }"
        >
          <template #actions-cell="{ row }">
            <UButton
              :to="`/operations/detail-transport/po-transportir-${row.original.id}`"
              variant="solid"
              size="sm"
              color="primary"
              icon="i-lucide-file-text"
            >
              Lihat Surat
            </UButton>
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

        <p
          v-if="!pending && rows.length === 0"
          class="py-6 text-center text-sm text-neutral-500"
        >
          Belum ada PO Transportir. Buat melalui menu "Pembuatan PO
          Transportir".
        </p>
      </div>
    </template>
  </UDashboardPanel>
</template>
