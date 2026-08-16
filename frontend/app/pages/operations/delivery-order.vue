<script setup lang="ts">
import type { StepperItem, NavigationMenuItem } from '@nuxt/ui'
import type { Customer, PurchaseOrdersSupplier } from '~/types/marketing'
import type {
  DeliveryOrderPost,
  DeliveryOrdersDetails
} from '~/types/operations'
import type {
  OperationsDOAdditionalState,
  OperationsDODetailsTransportState,
  OperationsDOFooterState,
  OperationsDOHeaderState,
  OperationsDOReceiverState,
  OperationsDOTransportState
} from '~/types/schemas'

const { user } = useAuth()
const { get, put, post } = useApi()
const toast = useToast()
const route = useRoute()
const loading = ref(false)
const selectedDoId = ref('')
const selectedPoId = ref('')
const editingDoId = computed(
  () =>
    (typeof route.query.do_id === 'string' ? route.query.do_id : '')
    || selectedDoId.value
)

const { data: purchaseOrderList, pending: pendingLinked } = await useAsyncData(
  'purchase-orders-customer-for-do',
  async () => {
    const res = await get<{ items: PurchaseOrdersSupplier[] }>(
      '/purchase-orders',
      {
        page: 1,
        page_size: 100,
        type: 'customer'
      }
    )
    return (res.items || []).map(po => ({
      id: po.id,
      purchaseOrderNumber: po.po_number,
      customerName: po.customer_name || '',
      customerId: po.customer_id || '',
      fuelTotalQty: po.total ?? 0,
      dateCreated: po.created_at?.toString() ?? '',
      dateChanged: po.updated_at?.toString() ?? ''
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
  const poNumber = existingPo?.purchaseOrderNumber ?? value.po_number
  const poFromList = purchaseOrderList.value.find(
    po => po.purchaseOrderNumber === poNumber
  )
  Object.assign(doHeader.companyInformation, details.companyInformation || {})
  Object.assign(doHeader.doInformation, {
    ...(details.doInformation || {}),
    poCustomerNumber: {
      ...(existingPo || {}),
      id: value.id_purchase_order || poFromList?.id || existingPo?.id,
      purchaseOrderNumber: poNumber,
      customerName: existingPo?.customerName ?? value.customer_name,
      customerId: existingPo?.customerId ?? value.customer_id,
      fuelTotalQty: existingPo?.fuelTotalQty ?? value.fuel_total
    }
  })

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

watch(
  () => doHeader.doInformation.poCustomerNumber,
  (value) => {
    if (value) {
      console.log(value)
      doReceiver.customerName = value.customerName || ''
      doReceiver.customerId = value.customerId || ''
      // Lengkapi alamat customer dari tabel customers berdasarkan customer_id PO
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
    const doPost: DeliveryOrderPost = {
      do_number: doData.doInformation.doNumber,
      customer_id: doData.customerId,
      date: doData.doInformation.doDateCreated,
      fuel_total: doData.total,
      id_purchase_order: doData.doInformation.poCustomerNumber.id || '',
      po_number:
        doData.doInformation.poCustomerNumber.purchaseOrderNumber || '',
      status: 'created',
      transport_name: doData.transportName,
      details: doData
    }

    const res = editingDoId.value
      ? await put<any, DeliveryOrderPost>(
          `/delivery-orders/${editingDoId.value}`,
          doPost
        )
      : await post<any, DeliveryOrderPost>('/delivery-orders', doPost)

    console.log('Data submitted')
    console.log(res)
    // console.log(doPost);
    toast.add({
      title: 'Sukses',
      icon: 'i-lucide-check-circle',
      description: editingDoId.value
        ? 'Data Delivery Order berhasil dilengkapi'
        : 'Data Delivery Order berhasil dibuat',
      color: 'success'
    })
  } catch (e: any) {
    toast.add({ title: 'Gagal', description: e.message, color: 'error' })
  } finally {
    loading.value = false
  }
}

const purchaseOrders = computed(() =>
  purchaseOrderList.value.map((entry) => {
    return {
      label: entry.purchaseOrderNumber,
      value: {
        id: entry.id,
        purchaseOrderNumber: entry.purchaseOrderNumber,
        customerName: entry.customerName,
        customerId: entry.customerId,
        dateCreated: entry.dateCreated,
        dateChanged: entry.dateChanged,
        fuelTotalQty: entry.fuelTotalQty
      },
      customerName: entry.customerName
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
            :purchase-orders="purchaseOrders"
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
            @submit="onFormSubmit"
          />
        </template>
      </UStepper>
    </template>
  </UDashboardPanel>
</template>
