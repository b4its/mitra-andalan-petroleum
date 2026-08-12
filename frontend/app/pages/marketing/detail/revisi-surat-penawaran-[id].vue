<script setup lang="ts">
import type { StepperItem } from '@nuxt/ui'
import type { ResUploads } from '~/types'
import type { Customer, OfferingLetterPost } from '~/types/marketing'
import type {
  MarketingOLDetailsState,
  MarketingOLFooterState,
  MarketingOLHeaderState
} from '~/types/schemas'

const toast = useToast()
const { get, put, postFile } = useApi()

const { data: customerList, pending: pendingCustomers } = await useAsyncData('customers', async () => {
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

// fetch data based on id and insert into each reactive
const route = useRoute()
const idOfferingLetter = route.params.id

const { data: offeringLetter, pending: pendingOL } = await useAsyncData(
  'offering-letter',
  async () => {
    const res = await get<OfferingLetterPost>(
      `/offering-letters/${idOfferingLetter}`
    )
    return res
  }
)

const letterHeader = reactive<MarketingOLHeaderState>({
  location: offeringLetter.value?.details.location || '',
  date:
    new Date(offeringLetter.value?.details.date || '2026-08-11')
      .toISOString()
      .split('T')[0] ?? '',
  offeringLetterNumber: offeringLetter.value?.offering_letter_number
    || '722/MAP/II-06/26',
  regarding: offeringLetter.value?.details.regarding
    || 'Surat Penawaran Harga Bahan Bakar Minyak Bio Diesel',
  receiver: offeringLetter.value?.details.receiver || ''
})

const letterOfferDetails = reactive<MarketingOLDetailsState>({
  supplyPoint: offeringLetter.value?.details.supplyPoint
    || 'Terminal BBM Balikpapan',
  qualityAssurance: offeringLetter.value?.details.qualityAssurance
    || 'Sesuai spesifikasi produk Pertamina',
  custodyTransfer: offeringLetter.value?.details.custodyTransfer
    || 'Alat ukur flow meter yang terkalibrasi',
  unloadingProcedure: offeringLetter.value?.details.unloadingProcedure
    || 'Dibongkar dari truk tangki ke tangki timbun customer',
  volumeUnit: offeringLetter.value?.details.volumeUnit || 'LITER',
  volumeTolerance: offeringLetter.value?.details.volumeTolerance || 0.005,
  paymentTerm: offeringLetter.value?.details.paymentTerm || '30 Hari',
  latePenalty: offeringLetter.value?.details.latePenalty || 0.01,
  servicePattern: offeringLetter.value?.details.servicePattern
    || 'Pengiriman truk tangki ke lokasi customer',
  personInCharge: {
    name: offeringLetter.value?.details.personInCharge.name || 'Budi Santoso',
    phoneNumber: offeringLetter.value?.details.personInCharge.phoneNumber
      || '08123456789'
  },
  paymentAddress: {
    bankName: offeringLetter.value?.details.paymentAddress.bankName
      || 'BCA - Samarinda',
    accountNumber:
      offeringLetter.value?.details.paymentAddress.accountNumber
      || '123456789',
    accountName: offeringLetter.value?.details.paymentAddress.accountName
      || 'PT. Mitra Andalan Petroleum'
  },
  fuelPrices: {
    hppPrice: offeringLetter.value?.details.fuelPrices.hppPrice || 0,
    logisticInformation:
      offeringLetter.value?.details.fuelPrices.logisticInformation
      || 'Truk Tangki',
    productName: offeringLetter.value?.details.fuelPrices.productName
      || 'Bio Diesel',
    hppPrice: offeringLetter.value?.details.fuelPrices.hppPrice || 17450,
    basePrice: offeringLetter.value?.details.fuelPrices.basePrice || 17950,
    totalPrice: offeringLetter.value?.details.fuelPrices.totalPrice || 0,
    sellingPrice: {
      ppkb: offeringLetter.value?.details.fuelPrices.sellingPrice.ppkb || 0,
      oat: offeringLetter.value?.details.fuelPrices.sellingPrice.oat || 0,
      ppn: offeringLetter.value?.details.fuelPrices.sellingPrice.ppn || 0,
      pph: offeringLetter.value?.details.fuelPrices.sellingPrice.pph || 0
    },
    percentageNum: {
      oat: offeringLetter.value?.details.fuelPrices.percentageNum.oat || 0.01,
      ppkb: offeringLetter.value?.details.fuelPrices.percentageNum.ppkb
        || 0.005,
      ppn: offeringLetter.value?.details.fuelPrices.percentageNum.ppn || 0.11,
      pph: offeringLetter.value?.details.fuelPrices.percentageNum.pph || 0
    }
  },
  informasiTambahan:
    offeringLetter.value?.details.informasiTambahan
    || ['Harga dapat berubah mengikuti harga keekonomian Pertamina']
})

const letterFooter = reactive<MarketingOLFooterState>({
  purchaseOrderDeadline:
    offeringLetter.value?.details.purchaseOrderDeadline || '1 - 14',
  offeror: {
    name: offeringLetter.value?.details.offeror.name || 'Budi Santoso',
    signature: undefined
  },
  companyInformation: {
    address: offeringLetter.value?.details.companyInformation.address
      || '',
    phoneNumber:
      offeringLetter.value?.details.companyInformation.phoneNumber
      || '0541-2832313', // add masking
    email: offeringLetter.value?.details.companyInformation.email
      || 'cs@map.co.id'
  }
})

const { data: signature, pending: pendingSignature } = await useAsyncData('signature', async () => {
  let res = await get<ResUploads[]>('/uploads', {
    document_type: 'ol',
    document_id: idOfferingLetter
  })

  if (!res.length && letterHeader.offeringLetterNumber) {
    res = await get<ResUploads[]>('/uploads', {
      document_type: 'ol',
      document_id: letterHeader.offeringLetterNumber
    })
  }

  return {
    url: res[0]?.url
  }
})

const loadedSignatureFile = ref<File | null>(null)

async function loadExistingFile() {
  if (!signature.value?.url) return
  const url = signature.value.url
  const response = await fetch(url)
  if (!response.ok) return
  const blob = await response.blob()
  const filename = url.split('/').pop()!
  const file = new File([blob], filename, {
    type: blob.type
  })
  letterFooter.offeror.signature = file
  loadedSignatureFile.value = file
}

onMounted(loadExistingFile)

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

async function onFooterSubmit() {
  try {
    const res = await put<any, OfferingLetterPost>(
      `/offering-letters/${idOfferingLetter}`,
      {
        customer_id: letterHeader.receiver,
        date: letterHeader.date,
        location: letterHeader.location,
        offering_letter_number: letterHeader.offeringLetterNumber,
        regarding: letterHeader.regarding,
        receiver: letterHeader.receiver,
        status: 'under_revision',
        transport_price: letterOfferDetails.fuelPrices.sellingPrice.ppn,
        fuel_total_price: letterOfferDetails.fuelPrices.totalPrice,
        details: {
          ...letterHeader,
          ...letterOfferDetails,
          ...letterFooter,
          offeror: { ...letterFooter.offeror, signature: undefined }
        }
      }
    )
    console.log(res)

    const signature = letterFooter.offeror.signature
    if (!signature) {
      throw new Error('Tanda tangan belum diunggah')
    }

    if (signature !== loadedSignatureFile.value) {
      const resUpload = await postFile<ResUploads[]>('/upload', {
        files: [signature],
        folder: 'marketing',
        document_type: 'ol',
        document_id: String(idOfferingLetter)
      })

      console.log(resUpload)
      loadedSignatureFile.value = signature
    }

    toast.add({
      title: 'Sukses',
      icon: 'i-lucide-check-circle',
      description: 'Data Penawaran berhasil dibuat',
      color: 'success'
    })

    // console.log({ ...letterHeader, ...letterOfferDetails, ...letterFooter });
  } catch (e: any) {
    toast.add({ title: 'Gagal', description: e.message, color: 'error' })
  }
}

definePageMeta({ layout: 'marketing' })
</script>

<template>
  <div v-if="pendingOL || pendingCustomers || pendingSignature" class="space-y-4 py-4">
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
        v-model:location="letterHeader.location"
        :has-previous="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFooterSubmit"
      />
    </template>
  </UStepper>
</template>
