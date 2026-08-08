<script setup lang="ts">
import { getPaginationRowModel } from "@tanstack/vue-table";
import { h, resolveComponent } from "vue";
import type { TableColumn } from "@nuxt/ui";
import type { FinanceInvoiceOverview } from "~/types";
import type { Invoices } from "~/types/finance";

const UBadge = resolveComponent("UBadge");
const UButton = resolveComponent("UButton");
const table = useTemplateRef("table");
const columnPinning = ref({ right: ["actions"] });

const toast = useToast();
const { get, put } = useApi();
const loading = ref(false);

const search = ref("");
const debouncedSearch = refDebounced(search, 300);

const { data: InvoiceData, refresh } = await useAsyncData(
  "invoices",
  async () => {
    const params: Record<string, string | number> = { page: 1, page_size: 50 };
    if (debouncedSearch.value) params.search = debouncedSearch.value;
    const res = await get<{ items: Invoices[] }>("/invoices", params);
    return res.items.map((inv: Invoices) => {
      // Check the real-time status every time data is fetched
      const { invoiceStatus, deadlineStatus } = calculateDynamicStatus(
        inv.created_at,
        inv.terms_day,
        inv.invoice_status,
      );

      return {
        id: inv.id,
        invoiceNumber: inv.invoice_number,
        customerName: inv.customer_name,
        termsDay: inv.terms_day,
        dateCreated: inv.created_at.toString(),
        grandTotal: inv.grand_total,
        invoiceStatus: invoiceStatus,
        deadlineStatus: deadlineStatus,
      };
    });
  },
  { default: () => [], watch: [debouncedSearch] },
);

const columns: TableColumn<FinanceInvoiceOverview>[] = [
  {
    accessorKey: "invoiceNumber",
    header: "Nomor Invoice",
    cell: ({ row }) => `${row.getValue("invoiceNumber")}`,
  },
  {
    accessorKey: "customerName",
    header: "Customer",
    cell: ({ row }) => `${row.getValue("customerName")}`,
  },
  {
    accessorKey: "grandTotal",
    header: "Grand Total",
    cell: ({ row }) => `${formatCurrency(row.getValue("grandTotal"))}`,
  },
  {
    accessorKey: "dateCreated",
    header: "Dibuat",
    cell: ({ row }) => `${formatDate(row.getValue("dateCreated"))}`,
  },
  {
    accessorKey: "termsDay",
    header: "Tenggat Hari",
    meta: {
      class: {
        th: "text-center",
        td: "text-center",
      },
    },
    cell: ({ row }) => `${row.getValue("termsDay")} Hari`,
  },
  {
    accessorKey: "invoiceStatus",
    header: "Status Invoice",
    meta: {
      class: {
        th: "text-center",
        td: "text-center",
      },
    },
    cell: ({ row }) => {
      const color = {
        unpaid: "warning" as const,
        paid: "success" as const,
        overdue: "error" as const,
      }[row.getValue("invoiceStatus") as string];
      const label = {
        unpaid: "Belum Lunas",
        paid: "Lunas",
        overdue: "Jatuh Tempo",
      }[row.getValue("invoiceStatus") as string];
      return h(
        UBadge,
        { class: "capitalize", variant: "soft", color },
        () => label,
      );
    },
  },
  {
    accessorKey: "deadlineStatus",
    header: "Status Tenggat Waktu",
    meta: {
      class: {
        th: "text-center",
        td: "text-center",
      },
    },
    cell: ({ row }) => {
      const color = {
        on_time: "info" as const,
        due_soon: "warning" as const,
        overdue: "error" as const,
      }[row.getValue("deadlineStatus") as string];
      const label = {
        on_time: "Tepat Waktu",
        due_soon: "Segera",
        overdue: "Terlewat",
      }[row.getValue("deadlineStatus") as string];
      return h(
        UBadge,
        { class: "capitalize", variant: "soft", color },
        () => label,
      );
    },
  },

  {
    id: "actions",
    header: "Aksi",
  },
];

async function updateInvoiceStatus(
  invoiceId: string,
  invoiceData: {
    dateCreated: string;
    terms: number;
    currentStatus: string;
  },
) {
  try {
    if (loading.value) return;
    loading.value = true;

    const { deadlineStatus } = calculateDynamicStatus(
      invoiceData.dateCreated,
      invoiceData.terms,
      invoiceData.currentStatus,
    );

    const res = await put(`/invoices/${invoiceId}`, {
      invoice_status: "paid",
      deadline_status: deadlineStatus,
    });

    console.log(res);

    toast.add({
      title: "Berhasil",
      description: "Status Invoice berhasil diperbarui",
      icon: "i-lucide-check-circle",
      color: "success",
    });
  } catch (err) {
    toast.add({
      title: "Gagal",
      description: "Status Invoice gagal diperbarui",
      icon: "i-lucide-x",
      color: "error",
    });
  } finally {
    loading.value = false;
    refresh();
  }
}

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
        placeholder="Cari nomor invoice atau customer..."
        class="w-72"
      />
    </div>

    <UTable
      ref="table"
      v-model:pagination="pagination"
      :data="InvoiceData"
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
            :to="`/finance/detail/invoice-${row.original.id}`"
            variant="solid"
            size="sm"
            color="primary"
          >
            Detail
          </UButton>
          <UButton
            v-if="
              row.original.invoiceStatus === 'unpaid' ||
              row.original.invoiceStatus === 'overdue'
            "
            :loading="loading"
            @click="
              updateInvoiceStatus(row.original.id, {
                dateCreated: row.original.dateCreated,
                terms: row.original.termsDay,
                currentStatus: row.original.invoiceStatus,
              })
            "
            variant="soft"
            size="sm"
            color="success"
          >
            Tandai Lunas
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

  <RecordDetailModal v-model:open="detailOpen" type="invoice" :id="detailId" />
</template>
