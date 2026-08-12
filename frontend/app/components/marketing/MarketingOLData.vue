<script setup lang="ts">
import { getPaginationRowModel } from '@tanstack/vue-table'
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { MarketingOfferingLetterOverview } from '~/types'
import type { OfferingLetters } from '~/types/marketing'
import type { OfferingLetterPurchaseOrdersResponse } from '~/types/marketing'

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const table = useTemplateRef('table')
const columnPinning = ref({
  right: ['actions']
})

const { get } = useApi()

const search = ref('')
const debouncedSearch = refDebounced(search, 300)

const { data: OlData, pending } = await useAsyncData(
  'offering-letters-data',
  async () => {
    const params: Record<string, string | number> = { page: 1, page_size: 50 }
    if (debouncedSearch.value) params.search = debouncedSearch.value
    const res = await get<{ items: OfferingLetters[] }>('/offering-letters', params)
    return res.items.map((ol: OfferingLetters) => ({
      id: ol.id,
      offeringLetterNumber: ol.offering_letter_number,
      customerName: ol.customer_name,
      fuelTotalPrice: ol.fuel_total_price,
      transportPrice: ol.transport_price,
      dateCreated: ol.created_at.toString(),
      dateChanged: ol.updated_at.toString(),
      status: ol.status
    }))
  },
  { default: () => [], watch: [debouncedSearch] }
)

const columns: TableColumn<MarketingOfferingLetterOverview>[] = [
  {
    accessorKey: 'offeringLetterNumber',
    header: 'Nomor Penawaran',
    cell: ({ row }) => `${row.getValue('offeringLetterNumber')}`
  },
  {
    accessorKey: 'customerName',
    header: 'Customer ID',
    cell: ({ row }) => `${row.getValue('customerName')}`
  },
  {
    accessorKey: 'fuelTotalPrice',
    header: 'Harga Dasar',
    cell: ({ row }) => `${formatCurrency(row.getValue('fuelTotalPrice'))}`
  },
  {
    accessorKey: 'transportPrice',
    header: 'Ongkos Transportir',
    cell: ({ row }) => `${formatCurrency(row.getValue('transportPrice'))}`
  },
  {
    accessorKey: 'dateCreated',
    header: 'Penawaran Dibuat',
    cell: ({ row }) => `${formatDate(row.getValue('dateCreated'))}`
  },
  {
    accessorKey: 'dateChanged',
    header: 'Penawaran Direvisi',
    cell: ({ row }) => `${formatDate(row.getValue('dateChanged'))}`
  },
  {
    accessorKey: 'status',
    header: 'Status Penawaran',
    cell: ({ row }) => {
      const color = {
        created: 'info' as const,
        under_revision: 'warning' as const,
        po_received: 'success' as const,
        do_completed: 'primary' as const
      }[row.getValue('status') as string]

      const status = {
        created: 'Penawaran Telah Dibuat',
        under_revision: 'Penawaran Dalam Revisi',
        po_received: 'Purchase Order Diterima',
        do_completed: 'Delivery Order Selesai'
      }[row.getValue('status') as string]

      return h(
        UBadge,
        { class: 'capitalize', variant: 'soft', color },
        () => status
      )
    }
  },
  {
    id: 'actions',
    header: 'Aksi',
    size: 220
  }
]

const statusFilter = ref('all')

watch(
  () => statusFilter.value,
  (newVal) => {
    if (!table?.value?.tableApi) return
    const statusColumn = table.value.tableApi.getColumn('status')
    if (!statusColumn) return
    if (newVal === 'all') {
      statusColumn.setFilterValue(undefined)
    } else {
      statusColumn.setFilterValue(newVal)
    }
  }
)

const pagination = ref({
  pageIndex: 0,
  pageSize: 7
})

const detailOpen = ref(false)
const detailId = ref<string | null>(null)

function openDetail(id: string) {
  detailId.value = id
  detailOpen.value = true
}

// ── Delivery Order terkait purchase order ─────────────────────

const doModalOpen = ref(false)
const doModalOLId = ref<string | null>(null)
const doLoading = ref(false)
const relatedData = ref<OfferingLetterPurchaseOrdersResponse>({ items: [] })

const doStatusBadge = (status: string) => {
  const color = {
    created: 'info' as const,
    document_returned: 'warning' as const,
    completed: 'success' as const
  }[status] ?? 'neutral'
  const label = {
    created: 'Dibuat',
    document_returned: 'Dokumen Dikembalikan',
    completed: 'Selesai'
  }[status] ?? status
  return h(UBadge, { variant: 'soft', color }, () => label)
}

const poStatusBadge = (status: string) => {
  const color = {
    created: 'info' as const,
    under_revision: 'warning' as const,
    po_received: 'success' as const
  }[status] ?? 'neutral'
  const label = {
    created: 'Dibuat',
    under_revision: 'Dalam Revisi',
    po_received: 'Purchase Order Diterima'
  }[status] ?? status
  return h(UBadge, { variant: 'soft', color }, () => label)
}

async function openDeliveryOrders(id: string) {
  doModalOLId.value = id
  relatedData.value = { items: [] }
  doModalOpen.value = true
  doLoading.value = true
  try {
    const res = await get<OfferingLetterPurchaseOrdersResponse>(
      `/offering-letters/${id}/purchase-orders`
    )
    relatedData.value = res
  } catch {
    relatedData.value = { items: [] }
  } finally {
    doLoading.value = false
  }
}
</script>

<template>
  <section class="flex flex-col lg:gap-4">
    <div class="flex flex-wrap items-center gap-2">
      <UInput
        v-model="search"
        icon="i-lucide-search"
        placeholder="Cari nomor penawaran atau customer..."
        class="w-64"
        @keyup.enter="() => {}"
      />
      <USelect
        v-model="statusFilter"
        :items="[
          { label: 'Semua Status', value: 'all' },
          { label: 'Penawaran Telah Dibuat', value: 'created' },
          { label: 'Penawaran Dalam Revisi', value: 'under_revision' },
          { label: 'Purchase Order Diterima', value: 'po_received' }
        ]"
        :ui="{
          trailingIcon:
            'group-data-[state=open]:rotate-180 transition-transform duration-200'
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
      :data="OlData"
      :columns="columns"
      :column-pinning="columnPinning"
      :ui="{
        base: 'table-fixed border-separate border-spacing-0',
        thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
        tbody: '[&>tr]:last:[&>td]:border-b-0',
        th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
        td: 'border-b border-default'
      }"
      :pagination-options="{
        getPaginationRowModel: getPaginationRowModel()
      }"
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
            icon="i-lucide-truck"
            size="sm"
            color="neutral"
            variant="soft"
            @click="openDeliveryOrders(row.original.id)"
          >
            Delivery Order
          </UButton>
          <UButton
            :to="`/marketing/detail/surat-penawaran-${row.original.id}`"
            variant="solid"
            size="sm"
            color="primary"
          >
            Lihat Surat
          </UButton>
          <UButton
            v-if="
              row.original.status === 'created'
                || row.original.status === 'under_revision'
            "
            :to="`/marketing/detail/revisi-surat-penawaran-${row.original.id}`"
            variant="soft"
            size="sm"
            color="neutral"
          >
            Revisi
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

  <RecordDetailModal :id="detailId" v-model:open="detailOpen" type="ol" />

  <UModal v-model:open="doModalOpen" :ui="{ content: 'max-w-4xl' }">
    <template #title>
      <h3 class="font-semibold">
        Delivery Order Terkait Purchase Order
      </h3>
    </template>

    <template #body>
      <div v-if="doLoading" class="space-y-3">
        <USkeleton v-for="i in 3" :key="i" class="h-20 rounded-lg" />
      </div>
      <div v-else-if="relatedData.items.length === 0" class="py-8 text-center text-sm text-neutral-500">
        Belum ada purchase order atau delivery order terkait surat penawaran ini.
      </div>
      <div v-else class="flex flex-col gap-4">
        <div
          v-for="po in relatedData.items"
          :key="po.id"
          class="rounded-lg border border-default p-4"
        >
          <div class="flex flex-wrap items-center gap-2 mb-3">
            <p class="text-sm font-semibold">
              Purchase Order: {{ po.po_number }}
            </p>
            <component :is="poStatusBadge(po.status)" />
            <span v-if="po.date" class="text-xs text-neutral-500 dark:text-neutral-400">
              Tanggal: {{ formatDate(po.date) }}
            </span>
            <span class="text-xs text-neutral-500 dark:text-neutral-400">
              Total: {{ formatCurrency(po.total) }}
            </span>
          </div>

          <UTable
            :data="po.delivery_orders"
            :columns="[
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
                accessorKey: 'fuel_total',
                header: 'Volume BBM',
                cell: ({ row }) => `${formatNumber(row.getValue('fuel_total'))} L`
              },
              {
                accessorKey: 'status',
                header: 'Status',
                cell: ({ row }) => doStatusBadge(row.getValue('status') as string)
              }
            ]"
            :ui="{
              base: 'table-fixed border-separate border-spacing-0',
              thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
              tbody: '[&>tr]:last:[&>td]:border-b-0',
              th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
              td: 'border-b border-default'
            }"
          />
          <p
            v-if="po.delivery_orders.length === 0"
            class="py-3 text-center text-sm text-neutral-500"
          >
            Belum ada delivery order untuk purchase order ini
          </p>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end">
        <UButton color="neutral" variant="ghost" @click="doModalOpen = false">
          Tutup
        </UButton>
      </div>
    </template>
  </UModal>
</template>
