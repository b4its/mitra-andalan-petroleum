<script setup lang="ts">
import { getPaginationRowModel } from '@tanstack/vue-table'
import { h } from 'vue'
import type { TableColumn } from '@nuxt/ui'

definePageMeta({ layout: 'admin' })

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const table = useTemplateRef('table')
const columnPinning = ref({ right: ['actions'] })
const toast = useToast()
const { get, post } = useApi()

const search = ref('')
const debouncedSearch = refDebounced(search, 300)

interface PoSupplierRow {
  id: string
  po_number: string
  type: string
  supplier_id: string | null
  supplier_name: string
  total: number
  status: string
  rilis_dana_at: string | null
  status_rilis_dana: boolean
  created_at: string | null
}

const { data: pos, refresh, pending } = await useAsyncData(
  'admin-po-supplier',
  async () => {
    const params: Record<string, string | number> = {
      page: 1,
      page_size: 100,
      type: 'supplier'
    }
    if (debouncedSearch.value) params.search = debouncedSearch.value
    const res = await get<{ items: PoSupplierRow[] }>(
      '/purchase-orders',
      params
    )
    return res.items || []
  },
  { default: () => [], watch: [debouncedSearch], server: false }
)

const columns: TableColumn<PoSupplierRow>[] = [
  {
    accessorKey: 'po_number',
    header: 'Nomor PO',
    cell: ({ row }) => `${row.getValue('po_number')}`
  },
  {
    accessorKey: 'supplier_name',
    header: 'Supplier',
    cell: ({ row }) => row.getValue('supplier_name') || '-'
  },
  {
    accessorKey: 'total',
    header: 'Total',
    meta: { class: { th: 'text-right', td: 'text-right' } },
    cell: ({ row }) => formatCurrency(Number(row.getValue('total')) || 0)
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => {
      const s = row.getValue('status') as string
      const colorMap: Record<string, string> = {
        created: 'info',
        under_revision: 'warning',
        po_received: 'success'
      }
      return h(UBadge, {
        variant: 'soft',
        color: colorMap[s] || 'neutral'
      }, () => statusLabel(s))
    }
  },
  {
    accessorKey: 'status_rilis_dana',
    header: 'Rilis Dana',
    cell: ({ row }) => {
      const isReleased = row.getValue('status_rilis_dana') as boolean
      return h(UBadge, {
        variant: 'soft',
        color: isReleased ? 'success' : 'warning'
      }, () => isReleased ? 'Sudah Dirilis' : 'Belum Dirilis')
    }
  },
  {
    accessorKey: 'created_at',
    header: 'Dibuat',
    cell: ({ row }) => row.getValue('created_at')
      ? formatDate(row.getValue('created_at') as string)
      : '-'
  },
  { id: 'actions', header: 'Aksi' }
]

const rilisLoading = ref(false)

const pagination = ref({ pageIndex: 0, pageSize: 5 })

async function onRilisDana(id: string) {
  if (rilisLoading.value) return
  rilisLoading.value = true
  try {
    await post(`/purchase-orders/${id}/rilis-dana`, {})
    toast.add({
      title: 'Berhasil',
      description: 'Dana berhasil dirilis',
      icon: 'i-lucide-check-circle',
      color: 'success'
    })
    refresh()
  } catch (err: unknown) {
    toast.add({
      title: 'Gagal',
      description: (err as Error).message || 'Gagal merilis dana',
      color: 'error'
    })
  } finally {
    rilisLoading.value = false
  }
}
</script>

<template>
  <UDashboardPanel id="admin-data-po-supplier">
    <template #header>
      <UDashboardNavbar title="Data Purchase Order Supplier">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #right>
          <div class="flex items-center gap-2">
            <UInput
              v-model="search"
              icon="i-lucide-search"
              placeholder="Cari nomor PO atau status..."
              class="w-64"
            />
            <UButton
              icon="i-lucide-refresh-cw"
              color="neutral"
              variant="ghost"
              @click="refresh()"
            />
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
            ref="table"
            v-model:pagination="pagination"
            :data="pos"
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
                  v-if="!row.original.status_rilis_dana"
                  icon="i-lucide-hand-coins"
                  size="sm"
                  color="warning"
                  variant="soft"
                  :loading="rilisLoading"
                  @click="onRilisDana(row.original.id)"
                >
                  Rilis Dana
                </UButton>
                <UButton
                  v-else
                  :to="`/marketing/detail-supplier/po-supplier-${row.original.id}`"
                  variant="solid"
                  size="sm"
                  color="primary"
                  icon="i-lucide-file-text"
                >
                  Lihat Surat
                </UButton>
              </div>
            </template>
          </UTable>
          <p
            v-if="!pending && pos.length === 0"
            class="py-6 text-center text-sm text-neutral-500"
          >
            Belum ada data Purchase Order Supplier
          </p>
          <div class="flex justify-end border-t border-default pt-4 px-4">
            <UPagination
              :page="
                (table?.tableApi?.getState().pagination.pageIndex || 0) + 1
              "
              :items-per-page="table?.tableApi?.getState().pagination.pageSize"
              :total="table?.tableApi?.getFilteredRowModel().rows.length"
              @update:page="(p) => table?.tableApi?.setPageIndex(p - 1)"
            />
          </div>
        </UCard>
      </div>
    </template>
  </UDashboardPanel>
</template>
