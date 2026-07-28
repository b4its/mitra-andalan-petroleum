<script setup lang="ts">
import { getPaginationRowModel } from '@tanstack/vue-table'
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { OperationsDeliveryOrderOverview } from '~/types'
import type { DeliveryOrders } from '~/types/operations'

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const table = useTemplateRef('table')
const columnPinning = ref({ right: ['actions'] })

const toast = useToast()
const { get, put } = useApi()
const loading = ref(false)

const search = ref('')
const debouncedSearch = refDebounced(search, 300)

const { data: DoData, refresh } = await useAsyncData(
  'delivery-orders',
  async () => {
    const params: Record<string, string | number> = { page: 1, page_size: 50 }
    if (debouncedSearch.value) params.search = debouncedSearch.value
    const res = await get<{ items: DeliveryOrders[] }>('/delivery-orders', params)
    return (res.items || []).map((d: DeliveryOrders) => ({
      id: d.id,
      deliveryOrderNumber: d.do_number,
      customerName: d.customer_name,
      purchaseOrderNumber: d.po_number,
      transportName: d.transport_name,
      dateCreated: d.created_at.toString(),
      dateChanged: d.updated_at.toString(),
      status: d.status
    }))
  },
  { default: () => [], watch: [debouncedSearch] }
)

const columns: TableColumn<OperationsDeliveryOrderOverview>[] = [
  {
    accessorKey: 'deliveryOrderNumber',
    header: 'Nomor DO',
    cell: ({ row }) => `${row.getValue('deliveryOrderNumber')}`
  },
  {
    accessorKey: 'customerName',
    header: 'Customer',
    cell: ({ row }) => `${row.getValue('customerName')}`
  },
  {
    accessorKey: 'purchaseOrderNumber',
    header: 'Nomor PO',
    cell: ({ row }) => `${row.getValue('purchaseOrderNumber')}`
  },
  {
    accessorKey: 'transportName',
    header: 'Transportir',
    cell: ({ row }) => `${row.getValue('transportName')}`
  },
  {
    accessorKey: 'dateCreated',
    header: 'Dibuat',
    cell: ({ row }) => `${formatDate(row.getValue('dateCreated'))}`
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => {
      const color = {
        created: 'info' as const,
        document_returned: 'success' as const
      }[row.getValue('status') as string]
      const label = { created: 'Dibuat', document_returned: 'Dokumen Kembali' }[
        row.getValue('status') as string
      ]
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

async function updateDoStatus(doId: string) {
  try {
    if (loading.value) return

    loading.value = true

    const res = await put(`/delivery-orders/${doId}`, {
      status: 'document_returned'
    })

    console.log(res)

    toast.add({
      title: 'Berhasil',
      description: 'Status DO berhasil diperbarui',
      icon: 'i-lucide-check',
      color: 'success'
    })
  } catch (err) {
    toast.add({
      title: 'Gagal',
      description: 'Status DO gagal diperbarui',
      icon: 'i-lucide-x',
      color: 'error'
    })
  } finally {
    loading.value = false
    refresh()
  }
}

const pagination = ref({ pageIndex: 0, pageSize: 7 })
</script>

<template>
  <section class="flex flex-col lg:gap-4">
    <div class="flex items-center gap-2">
      <UInput
        v-model="search"
        icon="i-lucide-search"
        placeholder="Cari nomor DO, PO, atau transportir..."
        class="w-72"
      />
    </div>

    <UTable
      ref="table"
      v-model:pagination="pagination"
      :data="DoData"
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
        <div class="flex gap-2">
          <UButton
            :to="`/operations/detail/delivery-order-${row.original.id}`"
            variant="solid"
            size="md"
            color="primary"
          >
            Detail
          </UButton>

          <UButton
            v-if="row.original.status === 'created'"
            :loading="loading"
            variant="soft"
            size="md"
            color="success"
            @click="updateDoStatus(row.original.id)"
          >
            Tandai Dokumen Kembali
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
