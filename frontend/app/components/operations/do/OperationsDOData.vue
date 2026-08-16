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
  details?: Record<string, unknown> | null
  status_rilis_dana?: boolean
  rilis_dana_at?: string | null
  status_ready_order?: boolean
  ready_order_at?: string | null
  status_selesai_dikirim?: boolean
  selesai_dikirim_at?: string | null
  status_lunas_ongkir?: boolean
  lunas_ongkir_at?: string | null
}

interface DoRow {
  id: string
  deliveryOrderNumber: string
  customerName: string
  purchaseOrderNumber: string
  transportName: string
  dateCreated: string
  status: string
  detailsLengkap: boolean
  statusRilisDana: boolean
  rilisDanaAt?: string | null
  statusReadyOrder: boolean
  readyOrderAt?: string | null
  statusSelesaiDikirim: boolean
  selesaiDikirimAt?: string | null
  statusLunasOngkir: boolean
  lunasOngkirAt?: string | null
}

interface DeliveryOrderDetailData {
  doInformation?: {
    doNumber?: string
    doDateCreated?: string
    soNumber?: string
  }
  companyInformation?: {
    name?: string
    nameSub?: string
    address?: string
    phoneNumber?: string
  }
  customerAddress?: string
  receiverInformation?: {
    name?: string
    phoneNumber?: string
  }
  receiverDateReceived?: string
  transportDateReceived?: string
  transportName?: string
  transportId?: string
  transportAddress?: string
  transportInformation?: {
    transportNumber?: string
    transportType?: string
    startKm?: string
    endKm?: string
    sgMeter?: string
    timeInformation?: {
      departureTime?: string
      arrivalTime?: string
      depotArrivalTime?: string
      unloadingTime?: string
    }
  }
  driverInformation?: {
    name?: string
    phoneNumber?: string
  }
  productInformation?: {
    name?: string
    qty?: number
    topSeal?: string
    bottomSeal?: string
    temperature?: number
  }
  dueDate?: string
  companyCoordinator?: string
  distributionAdmin?: string
  receiver?: string
  driver?: string
  total?: number
  t2Depot?: number
  t2Unloading?: number
  indexSensitivity?: number
  fuelReceived?: number
  notes?: Array<{ note?: string }>
}

interface DeliveryOrderDetail {
  details?: DeliveryOrderDetailData | null
  total?: number
}

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const table = useTemplateRef('table')
const columnPinning = ref({ right: ['actions'] })

const toast = useToast()
const { get, put, post } = useApi()

const search = ref('')
const debouncedSearch = refDebounced(search, 300)

const { data: DoData, pending, refresh } = await useAsyncData(
  'delivery-orders',
  async () => {
    const params: Record<string, string | number | boolean> = {
      page: 1,
      page_size: 50
    }
    if (debouncedSearch.value) params.search = debouncedSearch.value
    const res = await get<{ items: DeliveryOrderItem[] }>('/delivery-orders', params)
    return (res.items || [])
      .map((d: DeliveryOrderItem) => ({
        id: d.id,
        deliveryOrderNumber: d.do_number,
        customerName: d.customer_name,
        purchaseOrderNumber: d.po_number,
        transportName: d.transport_name,
        dateCreated: d.created_at?.toString() || '',
        status: d.status,
        // Cek apakah details sudah lengkap (ada companyInformation = dibuat via form)
        detailsLengkap: !!(d.details && d.details.companyInformation),
        statusRilisDana: d.status_rilis_dana ?? false,
        rilisDanaAt: d.rilis_dana_at,
        statusReadyOrder: d.status_ready_order ?? false,
        readyOrderAt: d.ready_order_at,
        statusSelesaiDikirim: d.status_selesai_dikirim ?? false,
        selesaiDikirimAt: d.selesai_dikirim_at,
        statusLunasOngkir: d.status_lunas_ongkir ?? false,
        lunasOngkirAt: d.lunas_ongkir_at
      }))
      .sort((a, b) => {
        // Rilis dana di atas, lalu urut terbaru
        if (a.statusRilisDana !== b.statusRilisDana) {
          return a.statusRilisDana ? -1 : 1
        }
        return b.dateCreated.localeCompare(a.dateCreated)
      })
  },
  { default: () => [], watch: [debouncedSearch] }
)

// ── Modal Lengkapi Data Delivery Order ────────────────────────────────────
const lengkapiOpen = ref(false)
const lengkapiTarget = ref<DoRow | null>(null)
const lengkapiSaving = ref(false)

const editLoading = ref(false)

const lengkapiCompany = ref<{
  name: string
  nameSub?: string
  address: string
  phoneNumber: string
}>({ name: '', address: '', phoneNumber: '' })

async function openEdit(row: DoRow) {
  editLoading.value = true
  lengkapiTarget.value = row
  try {
    // Fetch detail DO untuk pre-fill form dengan data yang sudah ada
    const detail = await get<DeliveryOrderDetail>(`/delivery-orders/${row.id}`)
    const d = detail?.details || {}

    lengkapiCompany.value = {
      name: d.companyInformation?.name || '',
      nameSub: d.companyInformation?.nameSub || '',
      address: d.companyInformation?.address || '',
      phoneNumber: d.companyInformation?.phoneNumber || ''
    }

    lengkapiForm.do_number
      = d.doInformation?.doNumber || row.deliveryOrderNumber || ''
    lengkapiForm.do_date
      = d.doInformation?.doDateCreated
        || new Date().toISOString().split('T')[0]
        || ''
    lengkapiForm.so_number = d.doInformation?.soNumber || ''
    lengkapiForm.customer_address = d.customerAddress || ''
    lengkapiForm.receiver_name = d.receiverInformation?.name || ''
    lengkapiForm.receiver_phone = d.receiverInformation?.phoneNumber || ''
    lengkapiForm.receiver_date
      = d.receiverDateReceived || new Date().toISOString().split('T')[0] || ''
    lengkapiForm.transport_name = d.transportName || row.transportName || ''
    lengkapiForm.transport_id = d.transportId || ''
    lengkapiForm.transport_address = d.transportAddress || ''
    lengkapiForm.transport_number
      = d.transportInformation?.transportNumber || ''
    lengkapiForm.transport_type = d.transportInformation?.transportType || ''
    lengkapiForm.transport_date
      = d.transportDateReceived || new Date().toISOString().split('T')[0] || ''
    lengkapiForm.driver_name = d.driverInformation?.name || ''
    lengkapiForm.driver_phone = d.driverInformation?.phoneNumber || ''
    lengkapiForm.product_name = d.productInformation?.name || ''
    lengkapiForm.fuel_qty = d.productInformation?.qty || d.total || 0
    lengkapiForm.due_date
      = d.dueDate || new Date().toISOString().split('T')[0] || ''
    lengkapiForm.top_seal = d.productInformation?.topSeal || ''
    lengkapiForm.bottom_seal = d.productInformation?.bottomSeal || ''
    lengkapiForm.temperature = d.productInformation?.temperature || 0
    lengkapiForm.start_km = d.transportInformation?.startKm || ''
    lengkapiForm.end_km = d.transportInformation?.endKm || ''
    lengkapiForm.sg_meter = d.transportInformation?.sgMeter || ''
    lengkapiForm.departure_time
      = d.transportInformation?.timeInformation?.departureTime || ''
    lengkapiForm.arrival_time
      = d.transportInformation?.timeInformation?.arrivalTime || ''
    lengkapiForm.depot_arrival_time
      = d.transportInformation?.timeInformation?.depotArrivalTime || ''
    lengkapiForm.unloading_time
      = d.transportInformation?.timeInformation?.unloadingTime || ''
    lengkapiForm.company_coordinator = d.companyCoordinator || ''
    lengkapiForm.distribution_admin
      = d.distributionAdmin || user.value?.name || ''
    lengkapiForm.receiver_sign = d.receiver || ''
    lengkapiForm.driver_sign = d.driver || ''
    lengkapiForm.t2_depot = d.t2Depot ?? 0
    lengkapiForm.t2_unloading = d.t2Unloading ?? 0
    lengkapiForm.index_sensitivity = d.indexSensitivity ?? 0
    lengkapiForm.fuel_received = d.fuelReceived ?? d.productInformation?.qty ?? 0
    lengkapiForm.notes = d.notes?.length
      ? d.notes.map(n => ({ note: n.note || '' }))
      : defaultLengkapiNotes()

    lengkapiOpen.value = true
  } catch {
    toast.add({
      title: 'Gagal',
      description: 'Gagal memuat data Delivery Order.',
      color: 'error'
    })
  } finally {
    editLoading.value = false
  }
}

function openLengkapi(row: DoRow) {
  lengkapiTarget.value = row
  lengkapiForm.do_number = row.deliveryOrderNumber || ''
  lengkapiForm.transport_name = row.transportName || ''
  lengkapiForm.do_date = new Date().toISOString().split('T')[0] || ''
  lengkapiForm.due_date = new Date().toISOString().split('T')[0] || ''
  lengkapiForm.receiver_date = new Date().toISOString().split('T')[0] || ''
  lengkapiForm.transport_date = new Date().toISOString().split('T')[0] || ''
  lengkapiForm.product_name = ''
  lengkapiForm.fuel_qty = 0
  lengkapiForm.distribution_admin = user.value?.name || ''
  lengkapiForm.t2_depot = 0
  lengkapiForm.t2_unloading = 0
  lengkapiForm.index_sensitivity = 0
  lengkapiForm.fuel_received = 0
  lengkapiForm.notes = defaultLengkapiNotes()
  lengkapiOpen.value = true
}

const lengkapiForm = reactive({
  // Header
  do_number: '',
  do_date: new Date().toISOString().split('T')[0] || '',
  so_number: '',
  // Customer (penerima)
  customer_address: '',
  receiver_name: '',
  receiver_phone: '',
  receiver_date: new Date().toISOString().split('T')[0] || '',
  // Transportir
  transport_name: '',
  transport_id: '',
  transport_address: '',
  transport_number: '',
  transport_type: '',
  transport_date: new Date().toISOString().split('T')[0] || '',
  // Driver
  driver_name: '',
  driver_phone: '',
  // Produk
  product_name: '',
  fuel_qty: 0,
  due_date: new Date().toISOString().split('T')[0] || '',
  top_seal: '',
  bottom_seal: '',
  temperature: 0,
  // Transport info
  start_km: '',
  end_km: '',
  sg_meter: '',
  departure_time: '',
  arrival_time: '',
  depot_arrival_time: '',
  unloading_time: '',
  // Footer
  company_coordinator: '',
  distribution_admin: '',
  receiver_sign: '',
  driver_sign: '',
  // Catatan pengiriman & tambahan
  t2_depot: 0,
  t2_unloading: 0,
  index_sensitivity: 0,
  fuel_received: 0,
  notes: [] as Array<{ note: string }>
})

function defaultLengkapiNotes() {
  return [
    {
      note: 'Sebelum BBM diserahterimakan, mohon periksa terlebih dahulu surat tera, jarum tera, segel, kualitas, SGMeter, kuantitas, kadar air, flow meter yang digunakan'
    },
    {
      note: 'Setelah pembongkaran, BBM industri yang sudah diterima dengan baik dan ditanda tangani kedua belah pihak, tidak dapat dikembalikan dan BBM tersebut sudah tidak menjadi tanggung jawab kami'
    },
    { note: 'Lainnya :' }
  ]
}

function addLengkapiNote() {
  lengkapiForm.notes.push({ note: '' })
}

function removeLengkapiNote(index: number) {
  lengkapiForm.notes.splice(index, 1)
}

const { user } = useAuth()

async function submitLengkapi() {
  if (lengkapiSaving.value || !lengkapiTarget.value) return
  if (
    !lengkapiForm.do_number
    || !lengkapiForm.transport_name
    || !lengkapiForm.fuel_qty
  ) {
    toast.add({
      title: 'Validasi',
      description: 'Nomor Delivery Order, Transportir, dan Volume wajib diisi.',
      color: 'warning'
    })
    return
  }
  lengkapiSaving.value = true
  try {
    const doId = lengkapiTarget.value.id

    // ── Simpan data DO ─────────────────────────────────────────
    const details = {
      companyInformation: {
        name: lengkapiCompany.value.name,
        nameSub: lengkapiCompany.value.nameSub || '',
        address: lengkapiCompany.value.address,
        phoneNumber: lengkapiCompany.value.phoneNumber
      },
      doInformation: {
        doNumber: lengkapiForm.do_number,
        doDateCreated: lengkapiForm.do_date,
        poCustomerNumber: {
          purchaseOrderNumber: lengkapiTarget.value.purchaseOrderNumber || ''
        },
        soNumber: lengkapiForm.so_number || ''
      },
      customerName: lengkapiTarget.value.customerName || '',
      customerId: lengkapiTarget.value.customerName || '',
      customerAddress: lengkapiForm.customer_address || '',
      receiverInformation: {
        name: lengkapiForm.receiver_name || '',
        phoneNumber: lengkapiForm.receiver_phone || ''
      },
      receiverDateReceived: lengkapiForm.receiver_date,
      transportName: lengkapiForm.transport_name,
      transportId: lengkapiForm.transport_id || '',
      transportAddress: lengkapiForm.transport_address || '',
      driverInformation: {
        name: lengkapiForm.driver_name || '',
        phoneNumber: lengkapiForm.driver_phone || ''
      },
      transportDateReceived: lengkapiForm.transport_date,
      dueDate: lengkapiForm.due_date,
      total: lengkapiForm.fuel_qty,
      productInformation: {
        name: lengkapiForm.product_name,
        qty: lengkapiForm.fuel_qty,
        topSeal: lengkapiForm.top_seal || '',
        bottomSeal: lengkapiForm.bottom_seal || '',
        temperature: lengkapiForm.temperature || 0
      },
      transportInformation: {
        startKm: lengkapiForm.start_km || '',
        endKm: lengkapiForm.end_km || '',
        sgMeter: lengkapiForm.sg_meter || '',
        timeInformation: {
          departureTime: lengkapiForm.departure_time || null,
          arrivalTime: lengkapiForm.arrival_time || null,
          depotArrivalTime: lengkapiForm.depot_arrival_time || null,
          unloadingTime: lengkapiForm.unloading_time || null
        },
        transportNumber: lengkapiForm.transport_number || '',
        transportType: lengkapiForm.transport_type || ''
      },
      notes: lengkapiForm.notes.length ? lengkapiForm.notes : defaultLengkapiNotes(),
      fuelReceived: lengkapiForm.fuel_received || lengkapiForm.fuel_qty,
      t2Depot: lengkapiForm.t2_depot,
      t2Unloading: lengkapiForm.t2_unloading,
      indexSensitivity: lengkapiForm.index_sensitivity,
      companyCoordinator: lengkapiForm.company_coordinator || '',
      distributionAdmin:
        lengkapiForm.distribution_admin || user.value?.name || '',
      receiver: lengkapiForm.receiver_sign || '',
      driver: lengkapiForm.driver_sign || ''
    }

    await put(`/delivery-orders/${doId}`, {
      do_number: lengkapiForm.do_number,
      transport_name: lengkapiForm.transport_name,
      fuel_total: lengkapiForm.fuel_qty,
      details
    })

    toast.add({
      title: 'Berhasil',
      description: 'Data Delivery Order berhasil dilengkapi. Surat siap dirender.',
      color: 'success'
    })
    lengkapiOpen.value = false
    refresh()
  } catch (err) {
    toast.add({
      title: 'Gagal',
      description: err instanceof Error ? err.message : 'Terjadi kesalahan',
      color: 'error'
    })
  } finally {
    lengkapiSaving.value = false
  }
}

// ── Modal Siapkan Pengantaran ─────────────────────────────────
const readyOrderOpen = ref(false)
const readyOrderTarget = ref<DoRow | null>(null)
const readyOrderLoading = ref(false)

function openReadyOrder(row: DoRow) {
  readyOrderTarget.value = row
  readyOrderOpen.value = true
}

async function confirmReadyOrder() {
  if (readyOrderLoading.value || !readyOrderTarget.value) return
  readyOrderLoading.value = true
  try {
    await post(`/delivery-orders/${readyOrderTarget.value.id}/ready-order`, {})
    toast.add({
      title: 'Berhasil',
      description: 'Pengantaran telah disiapkan.',
      color: 'success'
    })
    readyOrderOpen.value = false
    readyOrderTarget.value = null
    refresh()
  } catch (err) {
    toast.add({
      title: 'Gagal',
      description: err instanceof Error ? err.message : 'Terjadi kesalahan',
      color: 'error'
    })
  } finally {
    readyOrderLoading.value = false
  }
}

// ── Modal Selesai Dikirim ─────────────────────────────────────
const selesaiDikirimOpen = ref(false)
const selesaiDikirimTarget = ref<DoRow | null>(null)
const selesaiDikirimLoading = ref(false)

function openSelesaiDikirim(row: DoRow) {
  selesaiDikirimTarget.value = row
  selesaiDikirimOpen.value = true
}

async function confirmSelesaiDikirim() {
  if (selesaiDikirimLoading.value || !selesaiDikirimTarget.value) return
  selesaiDikirimLoading.value = true
  try {
    await post(
      `/delivery-orders/${selesaiDikirimTarget.value.id}/selesai-dikirim`,
      {}
    )
    toast.add({
      title: 'Berhasil',
      description: 'Pengiriman ditandai selesai.',
      color: 'success'
    })
    selesaiDikirimOpen.value = false
    selesaiDikirimTarget.value = null
    refresh()
  } catch (err) {
    toast.add({
      title: 'Gagal',
      description: err instanceof Error ? err.message : 'Terjadi kesalahan',
      color: 'error'
    })
  } finally {
    selesaiDikirimLoading.value = false
  }
}

// ── Tandai Dokumen Kembali ────────────────────────────────────
const loading = ref(false)

async function updateDoStatus(doId: string) {
  if (loading.value) return
  loading.value = true
  try {
    await put(`/delivery-orders/${doId}`, { status: 'document_returned' })
    toast.add({
      title: 'Berhasil',
      description: 'Status Delivery Order berhasil diperbarui',
      icon: 'i-lucide-check-circle',
      color: 'success'
    })
  } catch {
    toast.add({
      title: 'Gagal',
      description: 'Gagal memperbarui status Delivery Order.',
      color: 'error'
    })
  } finally {
    loading.value = false
    refresh()
  }
}

const pagination = ref({ pageIndex: 0, pageSize: 7 })

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

const columns: TableColumn<DoRow>[] = [
  { accessorKey: 'deliveryOrderNumber', header: 'Nomor Delivery Order' },
  { accessorKey: 'customerName', header: 'Customer' },
  { accessorKey: 'purchaseOrderNumber', header: 'Nomor Purchase Order' },
  {
    accessorKey: 'statusRilisDana',
    header: 'Rilis Dana',
    cell: ({ row }) =>
      statusBadge(
        row.original.statusRilisDana,
        'Rilis',
        row.original.rilisDanaAt
      )
  },
  {
    accessorKey: 'detailsLengkap',
    header: 'Surat',
    cell: ({ row }) => {
      const ok = row.original.detailsLengkap as boolean
      return h(
        UBadge,
        {
          variant: 'subtle',
          color: ok ? 'success' : 'warning',
          class: 'text-xs'
        },
        () => (ok ? 'Siap Cetak' : 'Belum Lengkap')
      )
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
    accessorKey: 'status',
    header: 'Status Delivery Order',
    cell: ({ row }) => {
      const s = row.getValue('status') as string
      const colorMap: Record<string, 'info' | 'success' | 'warning'> = {
        created: 'info',
        draft: 'warning',
        document_returned: 'success'
      }
      const labelMap: Record<string, string> = {
        created: 'Dibuat',
        draft: 'Draf',
        document_returned: 'Dokumen Kembali'
      }
      return h(
        UBadge,
        { variant: 'soft', color: colorMap[s] ?? 'neutral' },
        () => labelMap[s] ?? s
      )
    }
  },
  { id: 'actions', header: 'Aksi', size: 260 }
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
        <div class="flex flex-wrap gap-1.5">
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
            :to="`/operations/detail/delivery-order-${row.original.id}`"
            size="xs"
            color="primary"
            variant="outline"
          >
            Surat
          </UButton>
          <!-- Edit Data: selalu ada, pre-fill dari data yang sudah ada -->
          <UButton
            size="xs"
            color="neutral"
            variant="soft"
            icon="i-lucide-pencil"
            :loading="editLoading && lengkapiTarget?.id === row.original.id"
            @click="openEdit(row.original)"
          >
            Edit
          </UButton>
          <!-- Lengkapi Data: jika details belum lengkap -->
          <UButton
            v-if="!row.original.detailsLengkap"
            size="xs"
            color="warning"
            variant="soft"
            icon="i-lucide-clipboard-pen"
            @click="openLengkapi(row.original)"
          >
            Lengkapi Data
          </UButton>
          <!-- Siapkan Pengantaran: setelah rilis dana, belum ready -->
          <UButton
            v-if="
              row.original.statusRilisDana && !row.original.statusReadyOrder
            "
            size="xs"
            color="info"
            variant="soft"
            icon="i-lucide-package"
            :disabled="!row.original.detailsLengkap"
            :title="
              !row.original.detailsLengkap
                ? 'Lengkapi data Delivery Order terlebih dahulu'
                : ''
            "
            @click="openReadyOrder(row.original)"
          >
            Siapkan Kirim
          </UButton>
          <!-- Selesai Dikirim: setelah ready, belum selesai -->
          <UButton
            v-if="
              row.original.statusReadyOrder
                && !row.original.statusSelesaiDikirim
            "
            size="xs"
            color="success"
            variant="soft"
            icon="i-lucide-check-circle"
            @click="openSelesaiDikirim(row.original)"
          >
            Selesai Dikirim
          </UButton>
          <!-- Tandai Dokumen Kembali -->
          <UButton
            v-if="
              row.original.status === 'created'
                || row.original.status === 'draft'
            "
            :loading="loading"
            size="xs"
            color="warning"
            variant="soft"
            @click="updateDoStatus(row.original.id)"
          >
            Dok. Kembali
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

  <!-- ── Modal Siapkan Pengantaran ── -->
  <UModal v-model:open="readyOrderOpen" :ui="{ content: 'max-w-md' }">
    <template #title>
      <div class="flex items-center gap-2 text-info">
        <UIcon name="i-lucide-package" class="size-5" />
        Siapkan Pengantaran
      </div>
    </template>
    <template #body>
      <p class="text-sm text-muted">
        Apakah pengantaran untuk Delivery Order
        <span class="font-semibold text-highlighted">{{
          readyOrderTarget?.deliveryOrderNumber
        }}</span>
        sudah disiapkan dan siap untuk dikirim?
      </p>
      <p class="mt-2 text-xs text-dimmed">
        Waktu penyiapan akan dicatat (WITA).
      </p>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          color="info"
          :loading="readyOrderLoading"
          icon="i-lucide-check"
          @click="confirmReadyOrder"
        >
          Konfirmasi
        </UButton>

        <UButton
          color="neutral"
          variant="ghost"
          @click="readyOrderOpen = false"
        >
          Batal
        </UButton>
      </div>
    </template>
  </UModal>

  <!-- ── Modal Selesai Dikirim ── -->
  <UModal v-model:open="selesaiDikirimOpen" :ui="{ content: 'max-w-md' }">
    <template #title>
      <div class="flex items-center gap-2 text-success">
        <UIcon name="i-lucide-check-circle" class="size-5" />
        Konfirmasi Selesai Dikirim
      </div>
    </template>
    <template #body>
      <p class="text-sm text-muted">
        Apakah pengiriman untuk Delivery Order
        <span class="font-semibold text-highlighted">{{
          selesaiDikirimTarget?.deliveryOrderNumber
        }}</span>
        sudah selesai?
      </p>
      <p class="mt-2 text-xs text-dimmed">
        Setelah dikonfirmasi, Finance dapat melunasi ongkir. Waktu akan dicatat
        (WITA).
      </p>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          color="success"
          :loading="selesaiDikirimLoading"
          icon="i-lucide-check"
          @click="confirmSelesaiDikirim"
        >
          Konfirmasi Selesai
        </UButton>

        <UButton
          color="neutral"
          variant="ghost"
          @click="selesaiDikirimOpen = false"
        >
          Batal
        </UButton>
      </div>
    </template>
  </UModal>

  <RecordDetailModal :id="detailId" v-model:open="detailOpen" type="do" />

  <!-- ── Modal Edit / Lengkapi Data Delivery Order ── -->
  <UModal v-model:open="lengkapiOpen" :ui="{ content: 'max-w-2xl' }">
    <template #title>
      <div class="flex items-center gap-2">
        <UIcon name="i-lucide-clipboard-pen" class="size-4 text-primary" />
        {{
          lengkapiTarget?.detailsLengkap
            ? "Ubah Data Delivery Order"
            : "Lengkapi Data Delivery Order"
        }}
      </div>
    </template>

    <template #body>
      <div
        v-if="!lengkapiTarget?.detailsLengkap"
        class="mb-4 rounded-lg bg-warning/10 border border-warning/30 px-4 py-3 text-sm"
      >
        <p class="font-medium text-warning">
          Data Delivery Order belum lengkap untuk dicetak.
        </p>
        <p class="text-xs mt-1 text-muted">
          Isi data berikut sesuai surat Delivery Order yang akan dicetak.
        </p>
      </div>

      <div class="space-y-5 text-sm">
        <!-- Header DO -->
        <div>
          <p
            class="text-xs font-semibold text-muted uppercase tracking-wide mb-2"
          >
            Header Surat
          </p>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-xs text-muted mb-1">Nomor Delivery Order <span class="text-error">*</span></label>
              <UInput
                v-model="lengkapiForm.do_number"
                placeholder="0000/DO/MAP/I/0000"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Tanggal Delivery Order <span class="text-error">*</span></label>
              <UInput v-model="lengkapiForm.do_date" type="date" size="sm" />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">No. Sales Order</label>
              <UInput
                v-model="lengkapiForm.so_number"
                placeholder="Opsional"
                size="sm"
              />
            </div>
          </div>
        </div>

        <!-- Penerima / Customer -->
        <div>
          <p
            class="text-xs font-semibold text-muted uppercase tracking-wide mb-2"
          >
            Penerima (Customer)
          </p>
          <div class="grid grid-cols-2 gap-3">
            <div class="col-span-2">
              <label class="block text-xs text-muted mb-1">Alamat Customer</label>
              <UInput
                v-model="lengkapiForm.customer_address"
                placeholder="Alamat customer"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Penerima BBM (Nama)</label>
              <UInput
                v-model="lengkapiForm.receiver_name"
                placeholder="Nama penerima"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">HP Penerima</label>
              <UInput
                v-model="lengkapiForm.receiver_phone"
                placeholder="08xxxxxxxxxx"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Tanggal Terima</label>
              <UInput
                v-model="lengkapiForm.receiver_date"
                type="date"
                size="sm"
              />
            </div>
          </div>
        </div>

        <!-- Transportir / Agen -->
        <div>
          <p
            class="text-xs font-semibold text-muted uppercase tracking-wide mb-2"
          >
            Agen / Transportir
          </p>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-muted mb-1">Nama Transportir <span class="text-error">*</span></label>
              <UInput
                v-model="lengkapiForm.transport_name"
                placeholder="PT. Armada Kaltim Sejahtera"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">ID Transportir</label>
              <UInput
                v-model="lengkapiForm.transport_id"
                placeholder="ID / nama lengkap"
                size="sm"
              />
            </div>
            <div class="col-span-2">
              <label class="block text-xs text-muted mb-1">Alamat Transportir</label>
              <UInput
                v-model="lengkapiForm.transport_address"
                placeholder="Alamat transportir"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Nama Driver</label>
              <UInput
                v-model="lengkapiForm.driver_name"
                placeholder="Nama driver"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">HP Driver</label>
              <UInput
                v-model="lengkapiForm.driver_phone"
                placeholder="08xxxxxxxxxx"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Tanggal Transportir Terima</label>
              <UInput
                v-model="lengkapiForm.transport_date"
                type="date"
                size="sm"
              />
            </div>
          </div>
        </div>

        <!-- Produk & Volume -->
        <div>
          <p
            class="text-xs font-semibold text-muted uppercase tracking-wide mb-2"
          >
            Produk & Volume
          </p>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-xs text-muted mb-1">Nama Produk <span class="text-error">*</span></label>
              <UInput
                v-model="lengkapiForm.product_name"
                placeholder="Nama Produk"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Volume (Liter) <span class="text-error">*</span></label>
              <UInput
                v-model.number="lengkapiForm.fuel_qty"
                type="number"
                placeholder="5000"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Tanggal Berlaku</label>
              <UInput v-model="lengkapiForm.due_date" type="date" size="sm" />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Segel Atas</label>
              <UInput
                v-model="lengkapiForm.top_seal"
                placeholder="No. segel atas"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Segel Bawah</label>
              <UInput
                v-model="lengkapiForm.bottom_seal"
                placeholder="No. segel bawah"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Temperatur</label>
              <UInput
                v-model.number="lengkapiForm.temperature"
                type="number"
                placeholder="0"
                size="sm"
              />
            </div>
          </div>
        </div>

        <!-- Kendaraan & Waktu -->
        <div>
          <p
            class="text-xs font-semibold text-muted uppercase tracking-wide mb-2"
          >
            Kendaraan & Waktu
          </p>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-xs text-muted mb-1">No. Kendaraan</label>
              <UInput
                v-model="lengkapiForm.transport_number"
                placeholder="KT 1832 AJ"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Jenis Kendaraan</label>
              <UInput
                v-model="lengkapiForm.transport_type"
                placeholder="Truk Tangki"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">SG Meter</label>
              <UInput
                v-model="lengkapiForm.sg_meter"
                placeholder="0.000"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Km. Awal</label>
              <UInput
                v-model="lengkapiForm.start_km"
                placeholder="0"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Km. Akhir</label>
              <UInput v-model="lengkapiForm.end_km" placeholder="0" size="sm" />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Jam Berangkat</label>
              <UInput
                v-model="lengkapiForm.departure_time"
                type="time"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Jam Tiba</label>
              <UInput
                v-model="lengkapiForm.arrival_time"
                type="time"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Jam Tiba di Depo</label>
              <UInput
                v-model="lengkapiForm.depot_arrival_time"
                type="time"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Jam Mulai Bongkar</label>
              <UInput
                v-model="lengkapiForm.unloading_time"
                type="time"
                size="sm"
              />
            </div>
          </div>
        </div>

        <!-- Catatan Pengiriman -->
        <div>
          <p
            class="text-xs font-semibold text-muted uppercase tracking-wide mb-2"
          >
            Catatan Pengiriman
          </p>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-xs text-muted mb-1">T2 Depo</label>
              <UInputNumber
                v-model="lengkapiForm.t2_depot"
                :min="0"
                placeholder="125.1"
                size="sm"
                class="w-full"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">T2 Bongkar</label>
              <UInputNumber
                v-model="lengkapiForm.t2_unloading"
                :min="0"
                placeholder="125.1"
                size="sm"
                class="w-full"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Kepekaan Index (buku tera mobil)</label>
              <UInputNumber
                v-model="lengkapiForm.index_sensitivity"
                :min="0"
                size="sm"
                class="w-full"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">BBM Diterima</label>
              <UInputNumber
                v-model="lengkapiForm.fuel_received"
                :min="0"
                placeholder="5000"
                size="sm"
                class="w-full"
              />
            </div>
          </div>
        </div>

        <!-- Catatan Tambahan -->
        <div>
          <p
            class="text-xs font-semibold text-muted uppercase tracking-wide mb-2"
          >
            Catatan Tambahan
          </p>
          <div class="space-y-3">
            <div
              v-for="(note, index) in lengkapiForm.notes"
              :key="`lengkapi-note-${index}`"
              class="flex items-end gap-2"
            >
              <UInput
                v-model="note.note"
                placeholder="Ketentuan..."
                size="sm"
                class="w-full"
              />
              <UButton
                icon="i-lucide-trash-2"
                color="error"
                variant="ghost"
                size="sm"
                :disabled="lengkapiForm.notes.length === 1"
                @click="removeLengkapiNote(index)"
              />
            </div>

            <UButton
              icon="i-lucide-plus"
              color="neutral"
              variant="subtle"
              size="sm"
              label="Tambah Catatan"
              @click="addLengkapiNote"
            />
          </div>
        </div>

        <!-- Footer / Tanda Tangan -->
        <div>
          <p
            class="text-xs font-semibold text-muted uppercase tracking-wide mb-2"
          >
            Footer Surat
          </p>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-muted mb-1">Koordinator MAP</label>
              <UInput
                v-model="lengkapiForm.company_coordinator"
                placeholder="Nama Koordinator"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Admin Distribusi</label>
              <UInput
                v-model="lengkapiForm.distribution_admin"
                :placeholder="user?.name || ''"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Nama Penerima</label>
              <UInput
                v-model="lengkapiForm.receiver_sign"
                placeholder="Nama penerima"
                size="sm"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1">Nama Driver/Officer</label>
              <UInput
                v-model="lengkapiForm.driver_sign"
                placeholder="Nama driver"
                size="sm"
              />
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          color="primary"
          icon="i-lucide-save"
          :loading="lengkapiSaving"
          @click="submitLengkapi"
        >
          {{
            lengkapiTarget?.detailsLengkap
              ? "Simpan Perubahan"
              : "Simpan & Aktifkan Surat"
          }}
        </UButton>

        <UButton
          color="neutral"
          variant="ghost"
          @click="lengkapiOpen = false"
        >
          Batal
        </UButton>
      </div>
    </template>
  </UModal>
</template>
