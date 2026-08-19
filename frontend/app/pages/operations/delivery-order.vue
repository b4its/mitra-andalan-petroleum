<script setup lang="ts">
import type { StepperItem, NavigationMenuItem } from '@nuxt/ui'
import type { Customer } from '~/types/marketing'
import type {
  DeliveryOrderPost,
  DeliveryOrdersDetails,
  PoTransportirDetails,
  PoTransportirsDetails
} from '~/types/operations'
import type {
  OperationsDOAdditionalState,
  OperationsDODetailsTransportState,
  OperationsDOFooterState,
  OperationsDOHeaderState,
  OperationsDOReceiverState,
  OperationsDOTransportState
} from '~/types/schemas'
import { useDeliveryOrderPdf } from '~/composables/useDeliveryOrderPdf'

const { user } = useAuth()
const { get, put, post } = useApi()
const toast = useToast()
const route = useRoute()
const loading = ref(false)
const previewOpen = ref(false)
const { buildDeliveryOrderPdf } = useDeliveryOrderPdf()
const selectedDoId = ref('')
const selectedPoId = ref('')
const selectedPoTransportirId = ref<string | null>(null)
const editingDoId = computed(
  () =>
    (typeof route.query.do_id === 'string' ? route.query.do_id : '')
    || selectedDoId.value
)

// ── PO Transportir sebagai data source (alur baru: PO Customer → PO Transportir → DO) ──
const { data: poTransportirList, pending: pendingLinked } = await useAsyncData(
  'po-transportir-for-do',
  async () => {
    const res = await get<{ items: PoTransportirsDetails[] }>(
      '/po-transportir',
      { page: 1, page_size: 100 }
    )
    return (res.items || []).map(pt => ({
      id: pt.id,
      poTransportirNumber: pt.po_number,
      customerName: pt.customer_name || '',
      customerId: pt.customer_id || '',
      purchaseOrderId: pt.id_purchase_order || '',
      purchaseOrderNumber: pt.purchase_order_number || '',
      transportName: pt.receiver || '',
      total: pt.total || 0,
      details: pt.details || {}
    }))
  },
  { default: () => [], server: false }
)

// Daftar customer untuk melengkapi alamat otomatis pada "Informasi Customer"
const { data: customerList } = await useAsyncData(
  'do-customers',
  () => get<Customer[]>('/customers'),
  { default: () => [], server: false }
)

const customersById = computed(
  () => new Map(customerList.value.map(c => [c.id, c] as const))
)

const items: StepperItem[] = [
  { title: 'Kop Surat Delivery Order', slot: 'doHeader' },
  { title: 'Customer Penerima', slot: 'doReceiver' },
  { title: 'Agen/Transportir', slot: 'doTransport' },
  { title: 'Rincian Pengiriman', slot: 'doDetailsTransport' },
  { title: 'Catatan Tambahan', slot: 'doAdditional' },
  { title: 'Penutup Surat Delivery Order', slot: 'doFooter' }
]

const doHeader = reactive<OperationsDOHeaderState>({
  companyInformation: {
    name: 'PT. Mitra Andalan Petroleum',
    nameSub: 'Distributor BBM Elnusa Petrofin',
    address: 'Jl. Poros Samarinda-Balikpapan KM 23, Samarinda',
    phoneNumber: '(0541) 123456'
  },
  doInformation: {
    doNumber: '',
    doDateCreated: `${new Date().toISOString().split('T')[0]}`,
    poCustomerNumber: {},
    soNumber: ''
  }
})

// ── Nomor DO otomatis: {urutan}/DO/{tahun}/{romawi-bulan}/{tanggal} ──
const romanMonths = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']

async function generateDoNumber() {
  try {
    const res = await get<{ total: number }>('/delivery-orders', {
      page: 1,
      page_size: 1
    })
    const seq = (res.total || 0) + 1
    const now = new Date()
    const year = now.getFullYear()
    const month = romanMonths[now.getMonth()]
    const day = String(now.getDate()).padStart(2, '0')
    return `${String(seq).padStart(3, '0')}/DO/${year}/${month}/${day}`
  } catch {
    return ''
  }
}

onMounted(async () => {
  // Saat membuat DO baru (bukan edit), isi nomor DO otomatis
  if (!editingDoId.value && !doHeader.doInformation.doNumber) {
    const number = await generateDoNumber()
    if (number) doHeader.doInformation.doNumber = number
  }
})
const doReceiver = reactive<OperationsDOReceiverState>({
  customerName: 'PT. Surya Tambang Energi',
  customerId: '',
  customerAddress: 'Jl. A. W. Syahrani No. 45, Samarinda',
  receiverInformation: {
    name: 'Dedi Kurniawan',
    phoneNumber: '0812 5617 8230'
  },
  receiverDateReceived: `${new Date().toISOString().split('T')[0]}`
})
const doTransport = reactive<OperationsDOTransportState>({
  transportName: 'PT. Armada Kaltim Sejahtera',
  transportId: 'AKS-001',
  transportAddress: 'Jl. Pelita No. 18, Samarinda',
  driverInformation: {
    name: 'Supriyanto',
    phoneNumber: '0812 3027 4491'
  },
  transportDateReceived: `${new Date().toISOString().split('T')[0]}`,
  helperName: undefined
})
const doDetailsTransport = reactive<OperationsDODetailsTransportState>({
  dueDate: '2026-08-11',
  total: 10000,
  products: [],
  productInformation: {
    name: 'Bio Solar',
    qty: 10000,
    topSeal: 'TS-001',
    bottomSeal: 'BS-001',
    temperature: 32
  },
  transportInformation: {
    startKm: 12500,
    endKm: 12720,
    sgMeter: 0.841,
    // isWaterFree: true, // need to discuss
    timeInformation: {
      departureTime: '07:00',
      arrivalTime: '12:30',
      depotArrivalTime: '13:15',
      unloadingTime: '13:30'
    },
    transportNumber: 'KT 1832 AJ',
    transportType: 'Tangki'
  }
})
const doAdditional = reactive<OperationsDOAdditionalState>({
  notes: [
    {
      note: 'Sebelum BBM diserahterimakan, mohon periksa terlebih dahulu surat tera, jarum tera, segel, kualitas, SGMeter, kuantitas, kadar air, flow meter yang digunakan'
    },
    {
      note: 'Setelah pembongkaran, BBM industri yang sudah diterima dengan baik dan ditanda tangani kedua belah pihak, tidak dapat dikembalikan dan BBM tersebut sudah tidak menjadi tanggung jawab kami'
    },
    {
      note: 'Lainnya :'
    }
  ],
  t2Depot: 125.1,
  t2Unloading: 125.2,
  indexSensitivity: 0.5,
  fuelReceived: 10000
})
const doFooter = reactive<OperationsDOFooterState>({
  companyCoordinator: user.value?.name || 'Bambang Nugroho',
  distributionAdmin: user.value?.name || 'Rina Marlina',
  receiver: 'Dedi Kurniawan',
  driver: 'Supriyanto'
})

const { data: existingDeliveryOrder, pending: pendingExisting } = await useAsyncData(
  () => `delivery-order-edit-${editingDoId.value}`,
  async () => {
    if (!editingDoId.value) return null
    return await get<DeliveryOrdersDetails>(
      `/delivery-orders/${editingDoId.value}`
    )
  },
  { default: () => null, server: false, watch: [editingDoId] }
)

function hydrateFormFromExistingDeliveryOrder(
  value: DeliveryOrdersDetails | null
) {
  if (!value) return

  const details = value.details || {}
  const existingPo = details.doInformation?.poCustomerNumber

  // Cari di poTransportirList berdasarkan id_po_transportir atau po_transportir_number
  const ptFromList = value.id_po_transportir
    ? poTransportirList.value.find(pt => pt.id === value.id_po_transportir)
    : poTransportirList.value.find(pt => pt.poTransportirNumber === value.po_transportir_number)

  const poNumber = ptFromList?.purchaseOrderNumber
    || existingPo?.purchaseOrderNumber
    || value.po_number
  const poId = ptFromList?.purchaseOrderId
    || value.id_purchase_order
    || existingPo?.id

  Object.assign(doHeader.companyInformation, details.companyInformation || {})
  Object.assign(doHeader.doInformation, {
    ...(details.doInformation || {}),
    poCustomerNumber: {
      ...(existingPo || {}),
      id: poId,
      purchaseOrderNumber: poNumber,
      customerName: ptFromList?.customerName ?? existingPo?.customerName ?? value.customer_name,
      customerId: ptFromList?.customerId ?? existingPo?.customerId ?? value.customer_id,
      fuelTotalQty: existingPo?.fuelTotalQty ?? value.fuel_total
    }
  })

  // Set id_po_transportir untuk edit
  if (value.id_po_transportir) {
    selectedPoTransportirId.value = value.id_po_transportir
  }

  Object.assign(doReceiver, {
    customerName: details.customerName || value.customer_name || '',
    customerId: details.customerId || value.customer_id || '',
    customerAddress: details.customerAddress || '',
    receiverInformation: details.receiverInformation || {
      name: undefined,
      phoneNumber: undefined
    },
    receiverDateReceived:
      details.receiverDateReceived || doReceiver.receiverDateReceived
  })

  Object.assign(doTransport, {
    transportName: details.transportName || value.transport_name || '',
    transportId: details.transportId || '',
    transportAddress: details.transportAddress || '',
    driverInformation: details.driverInformation || {
      name: undefined,
      phoneNumber: undefined
    },
    transportDateReceived:
      details.transportDateReceived || doTransport.transportDateReceived,
    helperName: details.helperName || undefined
  })

  Object.assign(doDetailsTransport, {
    dueDate: details.dueDate || undefined,
    total: details.total || value.fuel_total || 0,
    products:
      (details as unknown as Record<string, unknown>).selectedProducts
      || (details as unknown as Record<string, unknown>).products
      || [],
    productInformation:
      details.productInformation || doDetailsTransport.productInformation,
    transportInformation:
      details.transportInformation || doDetailsTransport.transportInformation
  })

  Object.assign(doAdditional, {
    notes: details.notes || doAdditional.notes,
    t2Depot: details.t2Depot,
    t2Unloading: details.t2Unloading,
    indexSensitivity: details.indexSensitivity,
    fuelReceived:
      details.fuelReceived || details.total || value.fuel_total || 0
  })

  Object.assign(doFooter, {
    companyCoordinator:
      details.companyCoordinator || doFooter.companyCoordinator,
    distributionAdmin: details.distributionAdmin || doFooter.distributionAdmin,
    receiver: details.receiver || undefined,
    driver: details.driver || details.driverInformation?.name || undefined
  })
}

watch(existingDeliveryOrder, hydrateFormFromExistingDeliveryOrder, {
  immediate: true
})

const stepper = useTemplateRef('stepper')

function previousNavigation() {
  stepper.value?.prev()
}

function onFormSubmitToNext() {
  stepper.value?.next()
}

async function buildPreviewPdf() {
  const doData = {
    ...doHeader,
    ...doReceiver,
    ...doTransport,
    ...doDetailsTransport,
    ...doAdditional,
    ...doFooter
  }
  return await buildDeliveryOrderPdf(doData as unknown as Parameters<typeof buildDeliveryOrderPdf>[0])
}

// ── Saat user memilih PO Transportir (via poCustomerNumber) ──
watch(
  () => doHeader.doInformation.poCustomerNumber,
  (value) => {
    if (value && typeof value === 'object' && 'id' in value) {
      console.log('Selected PO Transportir / PO Customer:', value)
      doReceiver.customerName = value.customerName || ''
      doReceiver.customerId = value.customerId || ''
      // Lengkapi alamat customer dari tabel customers berdasarkan customer_id
      const customer = customersById.value.get(value.customerId || '')
      if (customer) {
        if (customer.address) doReceiver.customerAddress = customer.address
        if (customer.name) doReceiver.customerName = customer.name
      }
      doDetailsTransport.total = value.fuelTotalQty || 0
      doDetailsTransport.productInformation.qty = value.fuelTotalQty || 0
      doAdditional.fuelReceived = value.fuelTotalQty || 0
      if (value.id) {
        selectedPoId.value = value.id
      }

      // Resolve PO Transportir dari id_purchase_order (value.id)
      const pt = poTransportirList.value.find(
        p => p.purchaseOrderId === value.id
      )
      if (pt) {
        selectedPoTransportirId.value = pt.id
        // Auto-fill transport name dari receiver PO Transportir
        if (pt.transportName) {
          doTransport.transportName = pt.transportName
        }
        // Auto-fill daftar item (products) dari PO Transportir — semua item tersedia, user pilih mana yang diantar
        const ptProducts = (pt.details as Partial<PoTransportirDetails>).products || []
        doDetailsTransport.products = ptProducts.map((p: { name?: string, qty?: number, delivered?: boolean, delivered_at?: string }) => ({
          name: p.name || 'Solar',
          qty: p.qty || 0,
          selected: Boolean(p.delivered),
          delivered: Boolean(p.delivered),
          delivered_at: p.delivered_at || undefined
        }))
        if (ptProducts.length > 0) {
          const firstProduct = ptProducts[0]
          if (firstProduct) {
            doDetailsTransport.total = firstProduct.qty || pt.total || value.fuelTotalQty || 0
            doDetailsTransport.productInformation.qty = firstProduct.qty || 0
            doDetailsTransport.productInformation.name = firstProduct.name || 'Bio Solar'
            doAdditional.fuelReceived = firstProduct.qty || 0
          }
        }
      } else {
        selectedPoTransportirId.value = null
      }
    }
  }
)

async function onFormSubmit() {
  try {
    if (loading.value) return

    loading.value = true

    const doData = {
      ...doHeader,
      ...doReceiver,
      ...doTransport,
      ...doDetailsTransport,
      ...doAdditional,
      ...doFooter
    }

    // Hitung total dari item yang dipilih (banyak item yang diantar) — exclude item yang sudah pernah diantar
    const selectedProducts = (doData.products || []).filter(
      (p: { selected?: boolean, delivered?: boolean }) =>
        p.selected && !p.delivered
    )
    const totalSelected = selectedProducts.length
      ? selectedProducts.reduce(
          (sum: number, p: { qty?: number }) => sum + (p.qty || 0),
          0
        )
      : (doData.total || 0)

    const doPost: DeliveryOrderPost = {
      do_number: doData.doInformation.doNumber,
      customer_id: doData.customerId,
      date: doData.doInformation.doDateCreated,
      fuel_total: totalSelected,
      id_purchase_order: doData.doInformation.poCustomerNumber.id || '',
      id_po_transportir: selectedPoTransportirId.value || null,
      po_number:
        doData.doInformation.poCustomerNumber.purchaseOrderNumber || '',
      status: 'created',
      transport_name: doData.transportName,
      details: {
        ...doData,
        selectedProducts,
        total: totalSelected
      }
    }

    const res = editingDoId.value
      ? await put<DeliveryOrdersDetails, DeliveryOrderPost>(
          `/delivery-orders/${editingDoId.value}`,
          doPost
        )
      : await post<DeliveryOrdersDetails, DeliveryOrderPost>('/delivery-orders', doPost)

    console.log('Data submitted')
    console.log(res)
    toast.add({
      title: 'Sukses',
      icon: 'i-lucide-check-circle',
      description: editingDoId.value
        ? 'Data Delivery Order berhasil dilengkapi'
        : 'Data Delivery Order berhasil dibuat',
      color: 'success'
    })
  } catch (e: unknown) {
    toast.add({ title: 'Gagal', description: (e as Error).message, color: 'error' })
  } finally {
    loading.value = false
  }
}

// ── PO Transportir dropdown items (menggantikan PO Customer dropdown) ──
const poTransportirItems = computed(() =>
  poTransportirList.value.map((entry) => {
    return {
      label: entry.poTransportirNumber,
      value: {
        id: entry.purchaseOrderId,
        purchaseOrderNumber: entry.purchaseOrderNumber,
        customerName: entry.customerName,
        customerId: entry.customerId,
        fuelTotalQty: entry.total
      },
      customerName: entry.customerName,
      subtitle: entry.transportName
    }
  })
)

const links = [
  [
    {
      label: 'Buat Delivery Order',
      icon: 'i-lucide-truck',
      to: '/operations/delivery-order'
    },
    {
      label: 'Upload Delivery Order (Yang sudah dikembalikan)',
      icon: 'i-lucide-file-output',
      to: '/operations/delivery-order-returned'
    }
  ]
] satisfies NavigationMenuItem[][]

definePageMeta({ layout: 'operations' })
</script>

<template>
  <UDashboardPanel id="do" :ui="{ body: 'w-full' }">
    <template #header>
      <UDashboardNavbar
        title="Form Pembuatan Delivery Order"
        :ui="{ right: 'gap-3' }"
      >
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>

      <UDashboardToolbar>
        <template #left>
          <!-- NOTE: The `-ms-1` class is used to align with the `DashboardSidebarCollapse` button here. -->
          <UNavigationMenu :items="links" highlight class="-mx-1 flex-1" />
        </template>
      </UDashboardToolbar>
    </template>

    <template #body>
      <div
        v-if="pendingLinked || pendingExisting"
        class="space-y-4 w-full p-4"
      >
        <div class="space-y-2">
          <USkeleton class="h-4 w-32 rounded" />
          <USkeleton class="h-10 w-full rounded-lg" />
        </div>
        <div class="space-y-2">
          <USkeleton class="h-4 w-40 rounded" />
          <USkeleton class="h-10 w-full rounded-lg" />
        </div>
      </div>
      <UStepper
        v-else
        ref="stepper"
        disabled
        :items
      >
        <template #doHeader>
          <OperationsDOHeaderForm
            v-model="doHeader"
            :po-transportirs="poTransportirItems"
            :has-previous="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmitToNext"
          />
        </template>

        <template #doReceiver>
          <OperationsDOReceiverForm
            v-model="doReceiver"
            :has-previous="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmitToNext"
          />
        </template>

        <template #doTransport>
          <OperationsDOTransportForm
            v-model="doTransport"
            :has-previous="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmitToNext"
          />
        </template>

        <template #doDetailsTransport>
          <OperationsDODetailsTransportForm
            v-model="doDetailsTransport"
            :has-previous="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmitToNext"
          />
        </template>

        <template #doAdditional>
          <OperationsDOAdditionalForm
            v-model="doAdditional"
            :has-previous="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmitToNext"
          />
        </template>

        <template #doFooter>
          <OperationsDOFooterForm
            v-model="doFooter"
            :is-loading="loading"
            :has-previous="stepper?.hasPrev"
            @previous="previousNavigation"
            @preview="previewOpen = true"
            @submit="onFormSubmit"
          />
        </template>
      </UStepper>

      <DocumentPreviewModal
        :open="previewOpen"
        title="Preview Surat Pengantar Pengiriman (Delivery Order)"
        :build-pdf="buildPreviewPdf"
        @close="previewOpen = false"
      />
    </template>
  </UDashboardPanel>
</template>
