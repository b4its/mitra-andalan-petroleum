<script setup lang="ts">
import type { StepperItem } from '@nuxt/ui'
import type { Uploads } from '~/types'
import type {
  OfferingLetters,
  PurchaseOrdersCustomerPost
} from '~/types/marketing'
import type { MarketingPOCustomerState } from '~/types/schemas'

const { user } = useAuth()

const items: StepperItem[] = [
  {
    title: 'Upload PO Customer',
    slot: 'poCustomer',
    icon: 'i-lucide-receipt-text'
  }
]

const { get, put, post, postFile } = useApi()

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
    .filter(ol => ol.status !== 'po_received')
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

const poCustomer = reactive<MarketingPOCustomerState>({
  selectedOfferingLetter: {},
  poDocument: undefined,
  purchaseOrderNumber: '',
  poReceivedDate: new Date().toISOString().split('T')[0]?.toString() || '',
  total: 0
})

const toast = useToast()
async function onPoCustomerSubmit() {
  try {
    const poData = {
      ...poCustomer
    }
    const poPost: PurchaseOrdersCustomerPost = {
      po_number: poData.purchaseOrderNumber,
      type: 'customer',
      customer_id: poData.selectedOfferingLetter.customerId || '',
      supplier_id: null,
      date: poData.poReceivedDate,
      total: poData.total,
      status: 'created',
      created_by: user.value?.id ?? null
    }

    const res = await post<any, PurchaseOrdersCustomerPost>(
      '/purchase-orders',
      poPost
    )

    const olRes = await put<any, { status: 'po_received' }>(
      `/offering-letters/${poData.selectedOfferingLetter.id}`,
      {
        status: 'po_received'
      }
    )

    console.log('Data submitted')
    console.log(res)
    console.log(olRes)

    const poDocument = poCustomer.poDocument
    if (!poDocument) {
      throw new Error('Tanda tangan belum diunggah')
    }

    const resUpload = await postFile<Uploads>('/upload', {
      files: [poDocument],
      folder: 'marketing',
      document_type: 'po',
      document_id: poCustomer.purchaseOrderNumber
    })
    console.log(resUpload)

    // console.log(poDocument);
    // console.log(poPost);
    toast.add({
      title: 'Sukses',
      icon: 'i-lucide-check-circle',
      description: 'Data Purchase Order Customer berhasil ditambahkan',
      color: 'success'
    })
  } catch (e: any) {
    toast.add({ title: 'Error', description: e.message, color: 'error' })
  }
}

definePageMeta({ layout: 'marketing' })
</script>

<template>
  <UStepper ref="stepper" disabled :items>
    <template #poCustomer>
      <MarketingPOCustomerForm
        v-model="poCustomer"
        :offering-letters="offeringLetters"
        @submit="onPoCustomerSubmit"
      />
    </template>
  </UStepper>
</template>
