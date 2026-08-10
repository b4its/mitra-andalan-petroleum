<script setup lang="ts">
import type { StepperItem, SelectMenuItem } from '@nuxt/ui'
import type { FinanceDeliveryOrders, InvoicePost } from '~/types/finance'
import type { PurchaseOrdersSupplier } from '~/types/marketing'
import type {
  FinanceInvoiceDetailsState,
  FinanceInvoiceFooterState,
  FinanceInvoiceHeaderState,
  FinanceInvoiceProductsState
} from '~/types/schemas'

const { get, post } = useApi()
const toast = useToast()
const { user } = useAuth()
const loading = ref(false)

const { data: poCustomer, pending: pendingPo } = await useAsyncData(
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

const { data: doCustomer, refresh, pending: pendingDo } = await useAsyncData(
  'delivery-orders-customer',
  async () => {
    const res = await get<{ items: FinanceDeliveryOrders[] }>(
      '/delivery-orders',
      { page: 1, page_size: 50 }
    )
    return res.items.map((d: FinanceDeliveryOrders) => ({
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
  { default: () => [], immediate: true }
)

const items: StepperItem[] = [
  { title: 'Kop Invoice', slot: 'invoiceHeader' },
  { title: 'Informasi Invoice', slot: 'invoiceDetails' },
  { title: 'Rincian Produk', slot: 'invoiceProducts' },
  { title: 'Penutup Invoice', slot: 'invoiceFooter' }
]

const financeHeader = reactive<FinanceInvoiceHeaderState>({
  billToInformation: '',
  deliveryPointInformation: '',
  companyInformation: {
    name: '',
    address: '',
    phoneNumber: '',
    email: ''
  }
})
const financeDetails = reactive<FinanceInvoiceDetailsState>({
  invoiceInformation: {
    invoiceNumber: '',
    invoiceDate: `${new Date().toISOString().split('T')[0]}`,
    invoiceDueDate: `${new Date().toISOString().split('T')[0]}`,
    terms: 0
  },
  customerPurchaseInformation: {
    deliveryOrderNumberData: [],
    customerPurchaseOrderNumber: {}, // needs to be dropdown like do data
    taxInvoiceNumber: '',
    salesOrderNumber: undefined
  }
})
const financeProducts = reactive<FinanceInvoiceProductsState>({
  products: [
    {
      name: '',
      qty: 0,
      unit: '',
      price: 0,
      totalPrice: 0
    }
  ],
  priceSummary: {
    grandTotal: 0,
    subTotal: 0,
    ppn: 0,
    spellNumber: '',
    discount: undefined,
    prePaid: undefined
  }
})
const financeFooter = reactive<FinanceInvoiceFooterState>({
  termsAndCondition: [],
  paymentInformation: {
    bankName: '',
    accountNumber: '',
    accountName: ''
  },
  signature: {
    companyName: '',
    createdBy: `${user.value?.name || ''}`
  }
})

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

const deliveryOrderGroups = computed<SelectMenuItem[][]>(() => {
  const selectedPO
    = financeDetails.customerPurchaseInformation.customerPurchaseOrderNumber

  // 1. If no DOs exist, or no PO is selected yet, return an empty array
  if (
    !doCustomer.value
    || doCustomer.value.length === 0
    || !selectedPO?.purchaseOrderNumber
  ) {
    return []
  }

  // 2. Client-Side Filter: Only keep DOs that match the selected PO number
  const filteredDOs = doCustomer.value.filter(
    doItem => doItem.purchaseOrderNumber === selectedPO.purchaseOrderNumber
  )

  // If there are no matching DOs, return empty
  if (filteredDOs.length === 0) return []

  // 3. Group the filtered array by customerName
  const grouped = filteredDOs.reduce(
    (acc, curr) => {
      if (!acc[curr.customerName]) {
        acc[curr.customerName] = []
      }

      acc[curr.customerName]!.push({
        label: curr.deliveryOrderNumber,
        value: curr.deliveryOrderNumber
      })

      return acc
    },
    {} as Record<string, SelectMenuItem[]>
  )

  // 4. Transform into the SelectMenuItem[][] structure Nuxt UI expects
  return Object.keys(grouped).map((customerName) => {
    return [
      {
        type: 'label',
        label: customerName
      },
      ...(grouped[customerName] ?? [])
    ]
  })
})

watch(
  () => financeDetails.customerPurchaseInformation.customerPurchaseOrderNumber,
  (newValue, oldValue) => {
    // Check if the user actually selected a new, different PO
    if (
      newValue
      && newValue.purchaseOrderNumber !== oldValue?.purchaseOrderNumber
    ) {
      // 1. Clear any selected DOs in the form state to prevent mismatched data
      financeDetails.customerPurchaseInformation.deliveryOrderNumberData = []

      // 2. (Optional) You can still call refresh() here if you want to ensure
      // your client-side pool of DO data is perfectly up to date with the server
      refresh()
    }
  }
)

watch(
  () => financeDetails.customerPurchaseInformation.customerPurchaseOrderNumber,
  (value) => {
    if (value) {
      console.log(value)
      // financeProducts.products[0].price = value.fuelTotalPrice;
      financeProducts.products[0]!.qty = value.fuelTotalQty ?? 0
    }
  }
)

const stepper = useTemplateRef('stepper')

function previousNavigation() {
  stepper.value?.prev()
}

function onFormSubmitToNext() {
  stepper.value?.next()
}

async function onFormSubmit() {
  try {
    if (loading.value) return

    loading.value = true

    const invoiceData = {
      ...financeHeader,
      ...financeDetails,
      ...financeProducts,
      ...financeFooter
    }

    await post<any, InvoicePost>('/invoices', {
      customer_id:
        invoiceData.customerPurchaseInformation.customerPurchaseOrderNumber
          .customerId || '',
      deadline_status: 'due_soon',
      invoice_status: 'unpaid',
      grand_total: invoiceData.priceSummary.grandTotal,
      invoice_number: invoiceData.invoiceInformation.invoiceNumber,
      terms_day: invoiceData.invoiceInformation.terms,
      details: invoiceData
    })

    toast.add({
      title: 'Success',
      icon: 'i-lucide-check-circle',
      description: 'Invoice berhasil dibuat',
      color: 'success'
    })
  } catch (e: any) {
    toast.add({
      title: 'Error',
      description: e.message,
      icon: 'i-lucide-alert-triangle',
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}

definePageMeta({ layout: 'finance' })
</script>

<template>
  <div v-if="pendingPo || pendingDo" class="space-y-4 py-4">
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
    <template #invoiceHeader>
      <FinanceInvoiceHeaderForm
        v-model="financeHeader"
        :has-previous="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>

    <template #invoiceDetails>
      <FinanceInvoiceDetailsForm
        v-model="financeDetails"
        :delivery-order-groups="deliveryOrderGroups"
        :purchase-orders="purchaseOrders"
        :has-previous="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>

    <template #invoiceProducts>
      <FinanceInvoiceProductsForm
        v-model="financeProducts"
        :has-previous="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>

    <template #invoiceFooter>
      <FinanceInvoiceFooterForm
        v-model="financeFooter"
        :has-previous="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmit"
      />
    </template>
  </UStepper>
</template>
