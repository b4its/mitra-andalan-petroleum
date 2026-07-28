<script setup lang="ts">
import type { StepperItem, NavigationMenuItem } from '@nuxt/ui'
import type { Customer, PurchaseOrdersSupplier } from '~/types/marketing'
import type { DeliveryOrderPost } from '~/types/operations'
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
const loading = ref(false)

const { data: poCustomer } = await useAsyncData(
  'purchase-orders-customer',
  async () => {
    const res = await get<{ items: PurchaseOrdersSupplier[] }>(
      '/purchase-orders',
      { page: 1, page_size: 50, type: 'customer' }
    )
    return res.items.map((purchaseOrder: PurchaseOrdersSupplier) => ({
      id: purchaseOrder.id,
      purchaseOrderNumber: purchaseOrder.po_number,
      customerName: purchaseOrder.customer_name,
      customerId: purchaseOrder.customer_id,
      fuelTotalQty: purchaseOrder.total,
      dateCreated: purchaseOrder.created_at.toString(),
      dateChanged: purchaseOrder.updated_at.toString(),
      status: purchaseOrder.status
    }))
  },
  { default: () => [] }
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
    name: 'PT. MITRA ANDALAN PETROLEUM',
    nameSub: 'Distributor for Elnusa Petrofin',
    address: 'Jl. Belatuk Samarinda, Indonesia',
    phoneNumber: '0541-1234567' // add masking
  },
  doInformation: {
    doNumber: '0000/DO/MAP/I/0000',
    doDateCreated: `${new Date().toISOString().split('T')[0]}`,
    poCustomerNumber: undefined,
    soNumber: undefined
  }
})
const doReceiver = reactive<OperationsDOReceiverState>({
  customerName: 'PT. Sumber Jaya',
  customerId: 'PT. Sumber Jaya Nusantara',
  customerAddress: 'Samarinda',
  receiverInformation: {
    name: undefined,
    phoneNumber: undefined
  },
  receiverDateReceived: `${new Date().toISOString().split('T')[0]}`
})
const doTransport = reactive<OperationsDOTransportState>({
  transportName: 'PT. Transport Logistik',
  transportId: 'PT. Transport Logistik Nusantara',
  transportAddress: 'Samarinda',
  driverInformation: {
    name: 'Jaya',
    phoneNumber: undefined
  },
  transportDateReceived: `${new Date().toISOString().split('T')[0]}`,
  helperName: undefined
})
const doDetailsTransport = reactive<OperationsDODetailsTransportState>({
  dueDate: undefined,
  total: 5000,
  productInformation: {
    name: 'Bio diesel',
    qty: 5000,
    topSeal: undefined,
    bottomSeal: undefined,
    temperature: 0
  },
  transportInformation: {
    startKm: undefined,
    endKm: undefined,
    sgMeter: undefined,
    // isWaterFree: true, // need to discuss
    timeInformation: {
      departureTime: undefined,
      arrivalTime: undefined,
      depotArrivalTime: undefined,
      unloadingTime: undefined
    },
    transportNumber: 'KT 1234 AB',
    transportType: undefined
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
  t2Depot: undefined,
  t2Unloading: undefined,
  indexSensitivity: undefined,
  fuelReceived: 5000
})
const doFooter = reactive<OperationsDOFooterState>({
  companyCoordinator: 'Admin',
  distributionAdmin: user.value?.name || 'User',
  receiver: undefined,
  driver: undefined
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
      doDetailsTransport.total = value.fuelTotalQty || 0
      doDetailsTransport.productInformation.qty = value.fuelTotalQty || 0
      doAdditional.fuelReceived = value.fuelTotalQty || 0
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
      po_number:
        doData.doInformation.poCustomerNumber.purchaseOrderNumber || '',
      status: 'created',
      transport_name: doData.transportName,
      details: doData
    }

    const res = await post<any, DeliveryOrderPost>('/delivery-orders', doPost)

    console.log('Data submitted')
    console.log(res)
    // console.log(doPost);
    toast.add({
      title: 'Sukses',
      description: 'Data Delivery Order berhasil dibuat',
      color: 'success'
    })
  } catch (e: any) {
    toast.add({ title: 'Error', description: e.message, color: 'error' })
  } finally {
    loading.value = false
  }
}

const purchaseOrders = ref(
  poCustomer.value.map((po) => {
    return {
      label: po.purchaseOrderNumber,
      value: {
        id: po.id,
        purchaseOrderNumber: po.purchaseOrderNumber,
        customerName: po.customerName,
        customerId: po.customerId,
        dateCreated: po.dateCreated,
        dateChanged: po.dateChanged,
        fuelTotalQty: po.fuelTotalQty
      },
      customerName: po.customerName
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
      <UStepper ref="stepper" disabled :items>
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
