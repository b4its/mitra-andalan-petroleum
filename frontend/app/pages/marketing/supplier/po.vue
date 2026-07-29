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

const { get, put, post, postFile } = useApi()

const toast = useToast()
const { user } = useAuth()

const { data: supplierList } = await useAsyncData('suppliers', async () => {
  const res = await get<Customer[]>('/suppliers')
  return res.map((receiver: Customer) => ({
    id: receiver.id,
    name: receiver.name,
    address: receiver.address,
    phone: receiver.phone,
    email: receiver.email
  }))
})

const { data: OlData } = await useAsyncData(
  'offering-letters',
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

const offeringLetters = ref(
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

const suppliers = ref(
  supplierList.value?.map((supplier: Customer) => {
    return {
      label: supplier.name,
      value: {
        id: supplier.id,
        name: supplier.name,
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
    name: 'PT. MITRA ANDALAN PETROLEUM',
    address: 'Jl. Belatuk Samarinda, Indonesia',
    npwp: '00.000.000.0-000.000',
    contactPerson: '0812 3456 7898', // add masking
    email: 'marketing.mapetroleum@gmail.com'
  }
})

const letterCompanyAssociate = reactive<MarketingPOAssociateState>({
  receiver: {
    id: '',
    name: '',
    address: '',
    contactPerson: '',
    email: '',
    npwp: ''
  }
})

const letterOfferDetails = reactive<MarketingPODetailsState>({
  po: {
    date: `${new Date().toISOString().split('T')[0]}`,
    number: '0123/PO/MAP/I/00/00'
  },
  vat: 0.11,
  paymentAddress: {
    bankName: 'BCA Samarinda',
    accountNumber: '123456789',
    accountName: 'PT. Sumber Jaya'
  },
  selectedOfferingLetter: undefined,
  products: [
    {
      name: 'Solar',
      qty: 0,
      unit: 'Liter',
      price: 0,
      totalPrice: 0
    }
  ],
  totalProductsPrice: 0
})

const letterAdditional = reactive<MarketingPOAdditionalState>({
  termAndCondition: 'ABC',
  delivery: {},
  forwarder: {
    trucking: 'ABC'
  },
  signed: {
    createdBy: user.value?.name || 'User',
    approvedBy: 'Admin'
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
    toast.add({ title: 'Error', description: e.message, color: 'error' })
  } finally {
    loading.value = false
  }
}

definePageMeta({ layout: 'marketing' })
</script>

<template>
  <UStepper ref="stepper" disabled :items>
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
