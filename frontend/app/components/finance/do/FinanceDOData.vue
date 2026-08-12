<script setup lang="ts">
import { getPaginationRowModel } from '@tanstack/vue-table'
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'

interface DeliveryOrderItem {
  id: string
  do_number: string
  customer_name: string
  po_number: string
  transport_name: string
  created_at?: string
  status: string
  status_rilis_dana?: boolean
  rilis_dana_at?: string | null
  status_ready_order?: boolean
  ready_order_at?: string | null
  status_selesai_dikirim?: boolean
  selesai_dikirim_at?: string | null
  status_lunas_ongkir?: boolean
  lunas_ongkir_at?: string | null
}

interface FinanceDoRow {
  id: string
  deliveryOrderNumber: string
  customerName: string
  purchaseOrderNumber: string
  transportName: string
  dateCreated: string
  status: string
  statusRilisDana: boolean
  rilisDanaAt?: string | null
  statusReadyOrder: boolean
  readyOrderAt?: string | null
  statusSelesaiDikirim: boolean
  selesaiDikirimAt?: string | null
  statusLunasOngkir: boolean
  lunasOngkirAt?: string | null
}

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const table = useTemplateRef('table')
const columnPinning = ref({ right: ['actions'] })
const toast = useToast()
const { get, post } = useApi()

const search = ref('')
const debouncedSearch = refDebounced(search, 300)

const { data: DoData, pending, refresh } = await useAsyncData(
  'finance-delivery-orders',
  async () => {
    const params: Record<string, string | number> = { page: 1, page_size: 100 }
    if (debouncedSearch.value) params.search = debouncedSearch.value
    const res = await get<{ items: DeliveryOrderItem[] }>('/delivery-orders', params)
    return (res.items || []).map((d: DeliveryOrderItem) => ({
      id: d.id,
      deliveryOrderNumber: d.do_number,
      customerName: d.customer_name,
      purchaseOrderNumber: d.po_number,
      transportName: d.transport_name,
      dateCreated: d.created_at?.toString() || '',
      status: d.status,
      statusRilisDana: d.status_rilis_dana ?? false,
      rilisDanaAt: d.rilis_dana_at,
      statusReadyOrder: d.status_ready_order ?? false,
      readyOrderAt: d.ready_order_at,
      statusSelesaiDikirim: d.status_selesai_dikirim ?? false,
      selesaiDikirimAt: d.selesai_dikirim_at,
      statusLunasOngkir: d.status_lunas_ongkir ?? false,
      lunasOngkirAt: d.lunas_ongkir_at
    }))
  },
  { default: () => [], watch: [debouncedSearch] }
)

// ── Modal Rilis Dana ──────────────────────────────────────────
const rilisDanaOpen = ref(false)
const rilisDanaTarget = ref<FinanceDoRow | null>(null)
const rilisDanaLoading = ref(false)

function openRilisDana(row: FinanceDoRow) {
  rilisDanaTarget.value = row
  rilisDanaOpen.value = true
}

async function confirmRilisDana() {
  if (rilisDanaLoading.value || !rilisDanaTarget.value) return
  rilisDanaLoading.value = true
  try {
    await post(`/delivery-orders/${rilisDanaTarget.value.id}/rilis-dana`, {})
    toast.add({
      title: 'Berhasil',
      description: 'Dana telah dirilis. Delivery Order tersedia di Operations.',
      color: 'success'
    })
    rilisDanaOpen.value = false
    rilisDanaTarget.value = null
    refresh()
  } catch (err) {
    toast.add({
      title: 'Gagal',
      description: err instanceof Error ? err.message : 'Gagal merilis dana.',
      color: 'error'
    })
  } finally {
    rilisDanaLoading.value = false
  }
}

// ── Modal Lunas Ongkir ────────────────────────────────────────
const lunasOngkirOpen = ref(false)
const lunasOngkirTarget = ref<FinanceDoRow | null>(null)
const lunasOngkirLoading = ref(false)

function openLunasOngkir(row: FinanceDoRow) {
  lunasOngkirTarget.value = row
  lunasOngkirOpen.value = true
}

async function confirmLunasOngkir() {
  if (lunasOngkirLoading.value || !lunasOngkirTarget.value) return
  lunasOngkirLoading.value = true
  try {
    await post(
      `/delivery-orders/${lunasOngkirTarget.value.id}/lunas-ongkir`,
      {}
    )
    toast.add({
      title: 'Berhasil',
      description: 'Ongkir telah dilunasi.',
      color: 'success'
    })
    lunasOngkirOpen.value = false
    lunasOngkirTarget.value = null
    refresh()
  } catch (err) {
    toast.add({
      title: 'Gagal',
      description: err instanceof Error ? err.message : 'Gagal melunasi ongkir.',
      color: 'error'
    })
  } finally {
    lunasOngkirLoading.value = false
  }
}

// ── Detail modal ──────────────────────────────────────────────
const detailOpen = ref(false)
const detailId = ref<string | null>(null)
function openDetail(id: string) {
  detailId.value = id
  detailOpen.value = true
}

// ── Status badge helper ───────────────────────────────────────
function statusBadge(done: boolean, label: string, at?: string | null) {
  return h('div', { class: 'flex flex-col gap-0.5' }, [
    h(
      UBadge,
      {
        variant: 'subtle',
        color: done ? 'success' : 'neutral',
        class: 'text-xs'
      },
      () => (done ? label : '-')
    ),
    done && at
      ? h('span', { class: 'text-[10px] text-muted' }, formatDate(at))
      : null
  ])
}

const pagination = ref({ pageIndex: 0, pageSize: 7 })

const columns: TableColumn<FinanceDoRow>[] = [
  { accessorKey: 'deliveryOrderNumber', header: 'Nomor Delivery Order' },
  { accessorKey: 'customerName', header: 'Customer' },
  { accessorKey: 'purchaseOrderNumber', header: 'Nomor Purchase Order' },
  {
    accessorKey: 'statusRilisDana',
    header: 'Rilis Dana',
    cell: ({ row }) => {
      const val = row.original.statusRilisDana as boolean
      return h('div', { class: 'flex flex-col gap-0.5' }, [
        h(
          UBadge,
          {
            variant: 'subtle',
            color: val ? 'success' : 'warning',
            class: 'text-xs'
          },
          () => (val ? 'Dirilis' : 'Belum')
        ),
        val && row.original.rilisDanaAt
          ? h(
              'span',
              { class: 'text-[10px] text-muted' },
              formatDate(row.original.rilisDanaAt)
            )
          : null
      ])
    }
  },
  {
    accessorKey: 'statusReadyOrder',
    header: 'Siap Kirim',
    cell: ({ row }) =>
      statusBadge(
        row.original.statusReadyOrder,
        'Siap',
        row.original.readyOrderAt
      )
  },
  {
    accessorKey: 'statusSelesaiDikirim',
    header: 'Selesai Kirim',
    cell: ({ row }) =>
      statusBadge(
        row.original.statusSelesaiDikirim,
        'Selesai',
        row.original.selesaiDikirimAt
      )
  },
  {
    accessorKey: 'statusLunasOngkir',
    header: 'Lunas Ongkir',
    cell: ({ row }) =>
      statusBadge(
        row.original.statusLunasOngkir,
        'Lunas',
        row.original.lunasOngkirAt
      )
  },
  { id: 'actions', header: 'Aksi', size: 220 }
]
</script>

<template>
  <section class="flex flex-col lg:gap-4">
    <div class="flex items-center gap-2">
      <UInput
        v-model="search"
        icon="i-lucide-search"
        placeholder="Cari nomor Delivery Order, Purchase Order, atau transportir..."
        class="w-72"
      />
    </div>

    <div v-if="pending" class="space-y-3">
      <USkeleton v-for="i in 5" :key="i" class="h-12 rounded-lg" />
    </div>
    <UTable
      v-else
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
        <div class="flex flex-wrap items-center gap-1.5">
          <UButton
            icon="i-lucide-eye"
            size="xs"
            color="neutral"
            variant="ghost"
            @click="openDetail(row.original.id)"
          >
            Lihat
          </UButton>
          <UButton
            :to="`/finance/detail-operations/delivery-order-${row.original.id}`"
            size="xs"
            color="primary"
            variant="outline"
          >
            Surat
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

  <!-- ── Modal Konfirmasi Rilis Dana ── -->
  <UModal v-model:open="rilisDanaOpen" :ui="{ content: 'max-w-md' }">
    <template #title>
      <div class="flex items-center gap-2 text-success">
        <UIcon name="i-lucide-circle-dollar-sign" class="size-5" />
        Konfirmasi Rilis Dana
      </div>
    </template>
    <template #body>
      <p class="text-sm text-muted">
        Apakah Anda yakin ingin
        <span class="font-semibold text-highlighted">merilis dana</span>
        untuk Delivery Order
        <span class="font-semibold text-highlighted">{{
          rilisDanaTarget?.deliveryOrderNumber
        }}</span>?
      </p>
      <p class="mt-2 text-xs text-dimmed">
        Setelah dirilis, Delivery Order akan muncul di halaman Operations dan tim dapat
        menyiapkan pengantaran.
      </p>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          color="success"
          :loading="rilisDanaLoading"
          icon="i-lucide-check"
          @click="confirmRilisDana"
        >
          Konfirmasi Rilis Dana
        </UButton>
        <UButton
          color="neutral"
          variant="ghost"
          @click="rilisDanaOpen = false"
        >
          Batal
        </UButton>
      </div>
    </template>
  </UModal>

  <!-- ── Modal Konfirmasi Lunas Ongkir ── -->
  <UModal v-model:open="lunasOngkirOpen" :ui="{ content: 'max-w-md' }">
    <template #title>
      <div class="flex items-center gap-2 text-warning">
        <UIcon name="i-lucide-truck" class="size-5" />
        Konfirmasi Pelunasan Ongkir
      </div>
    </template>
    <template #body>
      <p class="text-sm text-muted">
        Apakah Anda ingin
        <span class="font-semibold text-highlighted">melunasi ongkir</span>
        untuk Delivery Order
        <span class="font-semibold text-highlighted">{{
          lunasOngkirTarget?.deliveryOrderNumber
        }}</span>?
      </p>
      <p class="mt-2 text-xs text-dimmed">
        Tindakan ini akan menandai pelunasan ongkir dengan waktu saat ini (WITA)
        dan tidak dapat dibatalkan.
      </p>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          color="warning"
          :loading="lunasOngkirLoading"
          icon="i-lucide-check"
          @click="confirmLunasOngkir"
        >
          Konfirmasi Lunasi Ongkir
        </UButton>

        <UButton
          color="neutral"
          variant="ghost"
          @click="lunasOngkirOpen = false"
        >
          Batal
        </UButton>
      </div>
    </template>
  </UModal>

  <RecordDetailModal :id="detailId" v-model:open="detailOpen" type="do" />
</template>
