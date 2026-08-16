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
import { usePoSupplierPdf } from '~/composables/usePoSupplierPdf'

const { get, post } = useApi()

const toast = useToast()
const { user } = useAuth()
const previewOpen = ref(false)
const { buildPoSupplierPdf } = usePoSupplierPdf()

interface SupplierOption {
  id: string
  name: string
  npwp: string | null
  address: string
  phone: string
  email: string
}

const { data: supplierList, pending: pendingSuppliers } = await useAsyncData<SupplierOption[]>(
  'suppliers',
  async () => {
    const res = await get<Customer[]>('/suppliers')
    return res.map(
      (receiver: Customer): SupplierOption => ({
        id: receiver.id,
        name: receiver.name,
        npwp: receiver.npwp,
        address: receiver.address,
        phone: receiver.phone,
        email: receiver.email
      })
    )
  },
  { default: () => [] }
)

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
        label: ol.customerName || '',
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
  supplierList.value.map((supplier) => {
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
    npwp: '02.458.113.4-091.000',
    contactPerson: '0541-2832313',
    email: 'cs@map.co.id'
  }
})

const letterCompanyAssociate = reactive<MarketingPOAssociateState>({
  receiver: {
    id: '',
    name: 'PT. Surya Tambang Energi',
    address: 'Jl. A. W. Syahrani No. 45, Samarinda',
    contactPerson: '0812 5617 8230',
    email: 'cs@suryatambangenergi.co.id',
    npwp: '01.609.052.4-091.000'
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
    picOperationMap: 'Bambang Nugroho',
    distance: 120
  },
  details: 'Pengiriman dilakukan bertahap sesuai kebutuhan customer',
  forwarder: {
    trucking: 'Truk Tangki 32.000 L - PT. Armada Kaltim Sejahtera'
  },
  signed: {
    createdBy: user.value?.name || '',
    approvedBy: 'Ahmad Fauzi'
  }
})

const stepper = useTemplateRef('stepper')

function previousNavigation() {
  stepper.value?.prev()
}

function onFormSubmitToNext() {
  stepper.value?.next()
}

async function buildPreviewPdf() {
  const poData = {
    ...letterCompanyMain,
    ...letterCompanyAssociate,
    ...letterOfferDetails,
    ...letterAdditional
  }
  const supplier = supplierList.value.find(s => s.id === poData.receiver?.id)
  return await buildPoSupplierPdf(
    poData as unknown as Parameters<typeof buildPoSupplierPdf>[0],
    {
      supplierName: supplier?.name || '',
      poNumber: poData.po?.number || '',
      createdByBarcode: poData.signed?.createdBy
        ? generateBarcodeDataUrl(poData.signed.createdBy)
        : '',
      approvedByBarcode: poData.signed?.approvedBy
        ? generateBarcodeDataUrl(poData.signed.approvedBy)
        : ''
    }
  )
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

    const res = await post<unknown, PurchaseOrdersCustomerPost>(
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
  } catch (e: unknown) {
    toast.add({
      title: 'Gagal',
      description: e instanceof Error ? e.message : String(e),
      color: 'error'
    })
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
        @preview="previewOpen = true"
        @submit="onFormSubmit"
      />
    </template>
  </UStepper>

  <DocumentPreviewModal
    :open="previewOpen"
    title="Preview Purchase Order Supplier"
    :build-pdf="buildPreviewPdf"
    @close="previewOpen = false"
  />
</template>
