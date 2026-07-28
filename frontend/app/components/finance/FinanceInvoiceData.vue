<script setup lang="ts">
import { getPaginationRowModel } from '@tanstack/vue-table'
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { FinanceInvoiceOverview } from '~/types'
import type { Invoices } from '~/types/finance'

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const table = useTemplateRef('table')
const columnPinning = ref({ right: ['actions'] })

const { get } = useApi()

const { data: InvoiceData } = await useAsyncData(
  'invoices',
  async () => {
    const res = await get<{ items: Invoices[] }>('/invoices', {
      page: 1,
      page_size: 50
    })
    return res.items.map((inv: Invoices) => ({
      id: inv.id,
      invoiceNumber: inv.invoice_number,
      customerName: inv.customer_name,
      termsDay: inv.terms_day,
      dateCreated: inv.created_at.toString(),
      grandTotal: inv.grand_total,
      invoiceStatus: inv.invoice_status,
      deadlineStatus: inv.deadline_status
    }))
  },
  { default: () => [] }
)

const columns: TableColumn<FinanceInvoiceOverview>[] = [
  {
    accessorKey: 'invoiceNumber',
    header: 'Nomor Invoice',
    cell: ({ row }) => `${row.getValue('invoiceNumber')}`
  },
  {
    accessorKey: 'customerName',
    header: 'Customer',
    cell: ({ row }) => `${row.getValue('customerName')}`
  },
  {
    accessorKey: 'grandTotal',
    header: 'Grand Total',
    cell: ({ row }) => `${formatCurrency(row.getValue('grandTotal'))}`
  },
  {
    accessorKey: 'dateCreated',
    header: 'Dibuat',
    cell: ({ row }) => `${formatDate(row.getValue('dateCreated'))}`
  },
  {
    accessorKey: 'invoiceStatus',
    header: 'Status Invoice',
    cell: ({ row }) => {
      const color = {
        unpaid: 'warning' as const,
        paid: 'success' as const,
        overdue: 'error' as const
      }[row.getValue('invoiceStatus') as string]
      const label = {
        unpaid: 'Belum Lunas',
        paid: 'Lunas',
        overdue: 'Jatuh Tempo'
      }[row.getValue('invoiceStatus') as string]
      return h(
        UBadge,
        { class: 'capitalize', variant: 'soft', color },
        () => label
      )
    }
  },
  {
    accessorKey: 'deadlineStatus',
    header: 'Tenggat',
    cell: ({ row }) => {
      const color = {
        on_time: 'info' as const,
        due_soon: 'warning' as const,
        overdue: 'error' as const
      }[row.getValue('deadlineStatus') as string]
      const label = {
        on_time: 'Tepat Waktu',
        due_soon: 'Segera',
        overdue: 'Terlewat'
      }[row.getValue('deadlineStatus') as string]
      return h(
        UBadge,
        { class: 'capitalize', variant: 'soft', color },
        () => label
      )
    }
  },
  {
    id: 'actions',
    header: 'Aksi',
    size: 180
  }
]

const pagination = ref({ pageIndex: 0, pageSize: 7 })
</script>

<template>
  <section class="flex flex-col lg:gap-4">
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
        td: 'border-b border-default'
      }"
      :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }"
    >
      <template #actions-cell="{ row }">
        <UButton
          :to="`/finance/detail/invoice-${row.original.id}`"
          variant="solid"
          size="md"
          color="primary"
        >
          Detail
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
  </section>
</template>
