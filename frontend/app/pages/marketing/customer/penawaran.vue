<script setup lang="ts">
import type { StepperItem } from '@nuxt/ui'
import type { ResUploads } from '~/types'
import type { OfferingLetterPost, Customer } from '~/types/marketing'
import type {
  MarketingOLDetailsState,
  MarketingOLFooterState,
  MarketingOLHeaderState
} from '~/types/schemas'

const { user } = useAuth()
const { get } = useApi()

const { data: customerList, pending } = await useAsyncData('customers', async () => {
  const res = await get<Customer[]>('/customers')
  return res.map((receiver: Customer) => ({
    id: receiver.id,
    name: receiver.name,
    npwp: receiver.npwp,
    address: receiver.address,
    phone: receiver.phone,
    email: receiver.email
  }))
}, { default: () => [] })

const receivers = computed(() =>
  customerList.value.map((receiver: Customer) => {
    return {
      label: receiver.name,
      value: receiver.id,
      npwp: receiver.npwp,
      address: receiver.address
    }
  })
)

const items: StepperItem[] = [
  { title: 'Kop Surat Penawaran', slot: 'letterHeader' },
  { title: 'Rincian Penawaran', slot: 'letterOfferDetails' },
  { title: 'Penutup Surat Penawaran', slot: 'letterFooter' }
]

const letterHeader = reactive<MarketingOLHeaderState>({
  location: 'Samarinda',
  date: '2026-08-11',
  offeringLetterNumber: '722/MAP/II-06/26',
  regarding: 'Surat Penawaran Harga Bahan Bakar Minyak Bio Diesel',
  receiver: ''
})

const letterOfferDetails = reactive<MarketingOLDetailsState>({
  supplyPoint: 'Terminal BBM Balikpapan',
  qualityAssurance: 'Sesuai spesifikasi produk Pertamina',
  custodyTransfer: 'Alat ukur flow meter yang terkalibrasi',
  unloadingProcedure: 'Dibongkar dari truk tangki ke tangki timbun customer',
  volumeUnit: 'LITER',
  volumeTolerance: 0.005,
  paymentTerm: 30,
  latePenalty: 0.01,
  servicePattern: 'Pengiriman truk tangki ke lokasi customer',
  personInCharge: {
    name: user.value?.name || 'User',
    phoneNumber: '08123456789'
  },
  paymentAddress: {
    bankName: 'BCA - Samarinda',
    accountNumber: '123456789',
    accountName: 'PT. Mitra Andalan Petroleum'
  },
  fuelPrices: {
    logisticInformation: 'Truk Tangki',
    productName: 'Bio Diesel',
    hppPrice: 17450,
    basePrice: 17950,
    totalPrice: 0,
    sellingPrice: {
      ppkb: 0,
      oat: 0,
      ppn: 0
    },
    percentageNum: {
      oat: 0.01,
      ppkb: 0.005,
      ppn: 0.11
    }
  },
  informasiTambahan: ['Harga dapat berubah mengikuti harga keekonomian Pertamina']
})

const letterFooter = reactive<MarketingOLFooterState>({
  purchaseOrderDeadline: 14,
  offeror: {
    name: user.value?.name || 'User',
    signature: undefined
  },
  companyInformation: {
    address: 'Jl. D. I. Panjaitan No. 25, Samarinda',
    phoneNumber: '0541-2832313',
    email: 'cs@map.co.id'
  }
})

const stepper = useTemplateRef('stepper')

function previousNavigation() {
  stepper.value?.prev()
}

function onHeaderSubmit() {
  stepper.value?.next()
}

function onDetailsSubmit() {
  stepper.value?.next()
}

const toast = useToast()
const { post, postFile, del } = useApi()

async function onFooterSubmit() {
  let createdId: string | null = null
  try {
    const res = await post<any, OfferingLetterPost>('/offering-letters', {
      customer_id: letterHeader.receiver,
      date: letterHeader.date,
      location: letterHeader.location,
      offering_letter_number: letterHeader.offeringLetterNumber,
      regarding: letterHeader.regarding,
      receiver: letterHeader.receiver,
      status: 'created',
      transport_price: letterOfferDetails.fuelPrices.sellingPrice.ppn,
      fuel_total_price: letterOfferDetails.fuelPrices.totalPrice,
      created_by: user.value?.id ?? null,
      details: {
        ...letterHeader,
        ...letterOfferDetails,
        ...letterFooter,
        offeror: { ...letterFooter.offeror, signature: undefined }
      }
    })
    createdId = res.id
    console.log(res)

    const signature = letterFooter.offeror.signature
    if (!signature) {
      throw new Error('Tanda tangan belum diunggah')
    }

    const resUpload = await postFile<ResUploads[]>('/upload', {
      files: [signature],
      folder: 'marketing',
      document_type: 'ol',
      document_id: res.id
    })

    console.log(resUpload)

    toast.add({
      title: 'Sukses',
      icon: 'i-lucide-check-circle',
      description: 'Data Penawaran berhasil dibuat',
      color: 'success'
    })

    // console.log({ ...letterHeader, ...letterOfferDetails, ...letterFooter });
  } catch (e: any) {
    if (createdId) {
      await del(`/offering-letters/${createdId}`).catch(() => undefined)
    }
    toast.add({ title: 'Error', description: e.message, color: 'error' })
  }
}

definePageMeta({ layout: 'marketing' })
</script>

<template>
  <div v-if="pending" class="space-y-4 py-4">
    <div v-for="i in 3" :key="i" class="space-y-2">
      <USkeleton class="h-4 w-32 rounded" />
      <USkeleton class="h-10 w-full rounded-lg" />
    </div>
  </div>
  <UStepper
    v-else
    ref="stepper"
    disabled
    :items
  >
    <template #letterHeader>
      <MarketingOLHeaderForm
        v-model="letterHeader"
        :receivers="receivers"
        :has-previous="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onHeaderSubmit"
      />
    </template>

    <template #letterOfferDetails>
      <MarketingOLDetailsForm
        v-model="letterOfferDetails"
        :has-previous="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onDetailsSubmit"
      />
    </template>

    <template #letterFooter>
      <MarketingOLFooterForm
        v-model="letterFooter"
        :has-previous="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFooterSubmit"
      />
    </template>
  </UStepper>
</template>
