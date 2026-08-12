<script setup lang="ts">
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { DeliveryOrders } from '~/types/operations'

const { get } = useApi()

const { data: rows, refresh, pending } = await useAsyncData(
  'operations-po-transportir',
  async () => {
    const res = await get<{ items: DeliveryOrders[] }>('/delivery-orders', {
      page: 1,
      page_size: 100
    })
    return res.items || []
  },
  { default: () => [], server: false }
)

const columns: TableColumn<DeliveryOrders>[] = [
  {
    accessorKey: 'do_number',
    header: 'Nomor Delivery Order',
    cell: ({ row }) => `${row.getValue('do_number')}`
  },
  {
    accessorKey: 'transport_name',
    header: 'Transportir',
    cell: ({ row }) => row.getValue('transport_name') || '-'
  },
  {
    accessorKey: 'customer_name',
    header: 'Customer',
    cell: ({ row }) => row.getValue('customer_name') || '-'
  },
  {
    accessorKey: 'fuel_total',
    header: 'Volume BBM',
    cell: ({ row }) => `${formatNumber(row.getValue('fuel_total'))} L`
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => {
      const color = {
        created: 'info' as const,
        document_returned: 'warning' as const,
        completed: 'success' as const
      }[row.getValue('status') as string] ?? 'neutral'
      const label = {
        created: 'Dibuat',
        document_returned: 'Dokumen Dikembalikan',
        completed: 'Selesai'
      }[row.getValue('status') as string] ?? row.getValue('status')
      return h(
        'span',
        { class: `text-${color}` },
        label
      )
    }
  },
  { id: 'actions', header: 'Aksi' }
]

definePageMeta({ layout: 'operations' })
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
            <p class="text-xs text-neutral-500 dark:text-neutral-400">
              Buat surat Purchase Order untuk transportir dari data Delivery Order
            </p>
          </div>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-4 lg:p-6">
        <UCard>
          <div v-if="pending" class="space-y-3">
            <USkeleton v-for="i in 5" :key="i" class="h-12 rounded-lg" />
          </div>
          <UTable
            v-else
            :data="rows"
            :columns="columns"
            :ui="{
              base: 'table-fixed border-separate border-spacing-0',
              thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
              tbody: '[&>tr]:last:[&>td]:border-b-0',
              th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
              td: 'border-b border-default'
            }"
          >
            <template #actions-cell="{ row }">
              <UButton
                :to="`/operations/detail/po-transportir-${row.original.id}`"
                variant="soft"
                size="sm"
                color="primary"
                icon="i-lucide-file-text"
              >
                Lihat Surat
              </UButton>
            </template>
          </UTable>
          <p
            v-if="!pending && rows.length === 0"
            class="py-6 text-center text-sm text-neutral-500"
          >
            Belum ada Delivery Order untuk dibuatkan surat transportir
          </p>
        </UCard>
      </div>
    </template>
  </UDashboardPanel>
</template>
