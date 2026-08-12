<script setup lang="ts">
import type { StepperItem } from '@nuxt/ui'
import type {
  Customer,
  OfferingLetters,
  PurchaseOrdersCustomerPost
} from '~/types/marketing'
import type {
  MarketingPOAdditionalState,
  MarketingPOAssociateState,
  MarketingPOCompanyState,
  MarketingPODetailsState
} from '~/types/schemas'

const { get, post } = useApi()

const toast = useToast()
const { user } = useAuth()

const { data: supplierList, pending: pendingSuppliers } = await useAsyncData('suppliers', async () => {
  const res = await get<Customer[]>('/suppliers')
  return res.map((receiver: Customer) => ({
    id: receiver.id,
    name: receiver.name,
    npwp: receiver.npwp,
    address: receiver.address,
    phone: receiver.phone,
    email: receiver.email
  }))
}, { default: () => [] })

const { data: OlData, pending: pendingOlData } = await useAsyncData(
  'offering-letters-supplier-po',
  async () => {
    const res = await get<{ items: OfferingLetters[] }>('/offering-letters', {
      page: 1,
      page_size: 50
    })
    return res.items.map((ol: OfferingLetters) => ({
      id: ol.id,
      offeringLetterNumber: ol.offering_letter_number,
      customerName: ol.customer_name,
      customerId: ol.customer_id,
      fuelTotalPrice: ol.fuel_total_price,
      transportPrice: ol.transport_price,
      dateCreated: ol.created_at.toString(),
      dateChanged: ol.updated_at.toString(),
      status: ol.status
    }))
  },
  {
    default: () => []
  }
)

const offeringLetters = computed(() =>
  OlData.value
    .filter(ol => ol.status === 'po_received')
    .map((ol) => {
      return {
        label: ol.customerName,
        value: {
          id: ol.id,
          offeringLetterNumber: ol.offeringLetterNumber,
          customerName: ol.customerName,
          customerId: ol.customerId,
          fuelTotalPrice: ol.fuelTotalPrice,
          transportPrice: ol.transportPrice,
          dateCreated: ol.dateCreated,
          dateChanged: ol.dateChanged,
          status: ol.status
        },
        olNumber: ol.offeringLetterNumber
      }
    })
)

const suppliers = computed(() =>
  supplierList.value.map((supplier: Customer) => {
    return {
      label: supplier.name,
      value: {
        id: supplier.id,
        name: supplier.name,
        npwp: supplier.npwp,
        address: supplier.address,
        contactPerson: supplier.phone,
        email: supplier.email
      }
    }
  })
)

const items: StepperItem[] = [
  { title: 'Informasi Perusahaan', slot: 'companyInformation' },
  { title: 'Informasi Mitra', slot: 'associateInformation' },
  { title: 'Detail Purchase Order', slot: 'poDetails' },
  { title: 'Informasi Tambahan', slot: 'additionalDetails' }
]

const letterCompanyMain = reactive<MarketingPOCompanyState>({
  companyInformation: {
    name: 'PT. Mitra Andalan Petroleum',
    address: '',
    npwp: '02.123.456.7-901.000',
    contactPerson: '0541-2832313',
    email: 'cs@map.co.id'
  }
})

const letterCompanyAssociate = reactive<MarketingPOAssociateState>({
  receiver: {
    id: '',
    name: 'PT. Sumber Rejeki Transport',
    address: '',
    contactPerson: '081298765432',
    email: 'marketing@sumberrejeki.co.id',
    npwp: '01.234.567.8-901.000'
  }
})

const letterOfferDetails = reactive<MarketingPODetailsState>({
  po: {
    date: '2026-08-11',
    number: '0543/PO/MAP/I/05/26'
  },
  vat: 0.11,
  paymentAddress: {
    bankName: 'BCA - Samarinda',
    accountNumber: '123456789',
    accountName: 'PT. Mitra Andalan Petroleum'
  },
  selectedOfferingLetter: {},
  products: [
    {
      name: 'Bio Diesel',
      qty: 10000,
      unit: 'LITER',
      price: 17950,
      totalPrice: 179500000,
      ppkb: 0,
      pph: 0,
      ppn: 0
    }
  ],
  totalProductsPrice: 179500000
})

const letterAdditional = reactive<MarketingPOAdditionalState>({
  termAndCondition: 'Pembayaran 30 hari setelah dokumen lengkap diterima',
  delivery: {
    loadingTerminal: 'Terminal BBM Balikpapan',
    loadingDate: '2026-08-11',
    picOperationMap: 'Budi Santoso',
    distance: 120
  },
  details: 'Pengiriman dilakukan bertahap sesuai kebutuhan customer',
  forwarder: {
    trucking: 'Truk Tangki 32.000 L - PT. Sumber Rejeki Transport'
  },
  signed: {
    createdBy: user.value?.name || '',
    approvedBy: 'Dwi Hartanto'
  }
})

const stepper = useTemplateRef('stepper')

function previousNavigation() {
  stepper.value?.prev()
}

function onFormSubmitToNext() {
  stepper.value?.next()
}

const loading = ref(false)

async function onFormSubmit() {
  try {
    if (loading.value) return

    loading.value = true

    const poData = {
      ...letterCompanyMain,
      ...letterCompanyAssociate,
      ...letterOfferDetails,
      ...letterAdditional
    }

    const res = await post<any, PurchaseOrdersCustomerPost>(
      '/purchase-orders',
      {
        po_number: poData.po.number,
        type: 'supplier',
        customer_id: null,
        supplier_id: poData.receiver.id || '',
        date: poData.po.date,
        total: poData.totalProductsPrice,
        status: 'created',
        created_by: user.value?.id ?? null,
        details: {
          ...letterCompanyMain,
          ...letterCompanyAssociate,
          ...letterOfferDetails,
          ...letterAdditional
        }
      }
    )
    console.log(res)

    // console.log({
    //   po_number: poData.po.number,
    //   type: "supplier",
    //   customer_id: null,
    //   supplier_id: poData.receiver.id || "",
    //   date: poData.po.date,
    //   total: poData.totalProductsPrice,
    //   status: "created",
    //   details: {
    //     ...letterCompanyMain,
    //     ...letterCompanyAssociate,
    //     ...letterOfferDetails,
    //     ...letterAdditional,
    //   },
    // });

    toast.add({
      title: 'Sukses',
      icon: 'i-lucide-check-circle',
      description: 'Data Penawaran berhasil dibuat',
      color: 'success'
    })

    // console.log({ ...letterHeader, ...letterOfferDetails, ...letterFooter });
  } catch (e: any) {
    toast.add({ title: 'Gagal', description: e.message, color: 'error' })
  } finally {
    loading.value = false
  }
}

definePageMeta({ layout: 'marketing' })
</script>

<template>
  <div v-if="pendingSuppliers || pendingOlData" class="space-y-4 py-4">
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
    <template #companyInformation>
      <MarketingPOCompanyForm
        v-model="letterCompanyMain"
        :has-previous="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>

    <template #associateInformation>
      <MarketingPOAssociateForm
        v-model="letterCompanyAssociate"
        :receivers="suppliers"
        :has-previous="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>

    <template #poDetails>
      <MarketingPODetailsForm
        v-model="letterOfferDetails"
        :offering-letters="offeringLetters"
        :has-previous="stepper?.hasPrev"
        is-supplier
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>

    <template #additionalDetails>
      <MarketingPOAdditionalForm
        v-model="letterAdditional"
        :has-previous="stepper?.hasPrev"
        :is-loading="loading"
        @previous="previousNavigation"
        @submit="onFormSubmit"
      />
    </template>
  </UStepper>
</template>
