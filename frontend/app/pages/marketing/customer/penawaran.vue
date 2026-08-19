<script setup lang="ts">
import type { StepperItem } from '@nuxt/ui'
import type { ResUploads } from '~/types'
import type { OfferingLetterPost, Customer, CustomerPostData } from '~/types/marketing'
import type {
  MarketingOLDetailsState,
  MarketingOLFooterState,
  MarketingOLHeaderState
} from '~/types/schemas'
import { useOfferingLetterPdf } from '~/composables/useOfferingLetterPdf'

const { user } = useAuth()
const previewOpen = ref(false)
const { buildOfferingLetterPdf } = useOfferingLetterPdf()

interface CustomerOption {
  id: string
  name: string
  npwp: string | null
  address: string
  phone: string
  email: string
}

const { data: customerList, pending } = await useAsyncData<CustomerOption[]>(
  'customers',
  async () => {
    const res = await get<Customer[]>('/customers')
    return res.map(
      (receiver: Customer): CustomerOption => ({
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

const receivers = computed(() =>
  customerList.value.map((receiver) => {
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
  location: '',
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
  paymentMethod: 'kredit',
  cashMethod: undefined,
  paymentTerm: '1 - 14',
  latePenalty: 0.01,
  servicePattern: 'Pengiriman truk tangki ke lokasi customer',
  personInCharge: {
    name: user.value?.name || 'Pengguna',
    phoneNumber: ''
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
      ppn: 0,
      pph: 0
    },
    percentageNum: {
      oat: 0.01,
      ppkb: 0.005,
      ppn: 0.11,
      pph: 0
    }
  },
  informasiTambahan: ['Harga dapat berubah mengikuti harga keekonomian Pertamina']
})

// Auto-fill offeror data from logged-in user's profile
if (user.value?.signature || user.value?.signatureCaption) {
  letterFooter.offeror.name = user.value.name || 'Pengguna'
  // Note: User must have uploaded signature in their profile for PDF generation
}

const letterFooter = reactive<MarketingOLFooterState>({
  purchaseOrderDeadline: '1 - 14',
  offeror: {
    name: user.value?.name || 'Pengguna',
    signature: undefined
  },
  companyInformation: {
    address: '',
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

async function buildPreviewPdf() {
  const details = {
    ...letterHeader,
    ...letterOfferDetails,
    ...letterFooter
  }
  const customerName = customerList.value.find(
    c => c.id === letterHeader.receiver
  )?.name || letterFooter.companyInformation?.email || ''
  return await buildOfferingLetterPdf(
    details as unknown as OfferingLetterDetails,
    customerName
  )
}

const toast = useToast()
const { post, postFile, del } = useApi()

// Validate signature requirement for offer letter creation
function validateUserSignature(): boolean {
  // Only marketing and admin roles need signature for offer letters
  const rolesNeedingSignature = ["marketing", "admin"]
  
  if (!user.value?.role || !rolesNeedingSignature.includes(user.value.role)) {
    return true // Other roles do not require signature
  }
  
  if (!user.value?.signature) {
    toast.add({
      title: "Profil Belum Lengkap",
      description: "Silakan upload tanda tangan terlebih dahulu di halaman profil sebelum membuat surat penawaran",
      color: "warning"
    })
    
    // Navigate to profile page to complete signature setup
    useRouter().push("/admin/profile")
    return false
  }
  
  return true
}

async function onFooterSubmit() {
  // Check if user has signature configured
  if (!validateUserSignature()) return;
  let createdId: string | null = null
  try {
    const res = await post<{ id: string }, OfferingLetterPost>('/offering-letters', {
      customer_id: letterHeader.receiver,
      date: letterHeader.date,
      location: letterHeader.location,
      offering_letter_number: letterHeader.offeringLetterNumber,
      regarding: letterHeader.regarding,
      receiver: letterHeader.receiver,
      payment_method: letterOfferDetails.paymentMethod ?? null,
      payment_term: letterOfferDetails.paymentTerm,
      payment_tollerance: letterOfferDetails.volumeTolerance,
      purchase_order_deadline: letterFooter.purchaseOrderDeadline,
      late_penalty_percent: letterOfferDetails.latePenalty,
      price_service_type: letterOfferDetails.fuelPrices.logisticInformation,
      fuel_product_name: letterOfferDetails.fuelPrices.productName,
      fuel_hpp_price: letterOfferDetails.fuelPrices.hppPrice,
      fuel_base_price: letterOfferDetails.fuelPrices.basePrice,
      fuel_selling_ppkb_percent: letterOfferDetails.fuelPrices.percentageNum.ppkb,
      fuel_selling_oat_percent: letterOfferDetails.fuelPrices.percentageNum.oat,
      fuel_selling_ppn_percent: letterOfferDetails.fuelPrices.percentageNum.ppn,
      fuel_selling_pph_percent: letterOfferDetails.fuelPrices.percentageNum.pph,
      terms_and_conditions: letterOfferDetails.informasiTambahan
    })
    createdId = res.id
    toast.add({
      title: 'Berhasil',
      description: 'Surat penawaran berhasil dibuat'
    })
    if (createdId) {
      await navigateTo(`/marketing/detail/surat-penawaran-${createdId}`)
    }
  } catch (e) {
    console.error(e)
    toast.add({
      title: 'Gagal',
      description: 'Terjadi kesalahan saat membuat surat penawaran',
      color: 'danger'
    })
  }
}

async function onPreviewPdf() {
  if (!validateUserSignature()) return;
  const pdfContent = await buildPreviewPdf()
  if (pdfContent) {
    previewOpen.value = true
    const blob = new Blob([pdfContent], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    return { url }
  }
  return null
}

const offers = ref<{ id: string; number: string; customer: string }[]>([
  { id: '1', number: '722/MAP/II-06/26', customer: 'PT. Surya Tambang Energi' }
])
</script>

<template>
  <div class="grid gap-6 py-6 px-4 md:px-8">
    <NuxtCard class="col-span-full bg-white dark:bg-neutral-800 rounded-lg shadow-sm">
      <NuxtCardTitle class="text-xl font-bold">Pembuatan Surat Penawaran</NuxtCardTitle>
      <NuxtCardSeparator />
      <NuxtCardContent class="pt-6">
        <!-- Step Form -->
        <ClientOnly>
          <NuxtStepper v-slot="{ stepIndex }" :items="items" ref="stepper" orientation="vertical" class="mt-4">
            <!-- Letter Header Step -->
            <div v-show="stepIndex === 0" id="letterHeader" style="padding-top: 1rem;">
              <MarketingOLHeaderForm 
                v-model="letterHeader" 
                @submit="onHeaderSubmit"
              />
              <div class="flex justify-between mt-6 pt-4 border-t">
                <Button @click="previousNavigation" variant="outline">
                  Previous
                </Button>
                <Button 
                  :disabled="!letterHeader.date || !letterHeader.offeringLetterNumber"
                  @click="onHeaderSubmit"
                >
                  Next
                </Button>
              </div>
            </div>

            <!-- Letter Offer Details Step -->
            <div v-show="stepIndex === 1" id="letterOfferDetails" style="padding-top: 1rem;">
              <MarketingOLDetailsForm 
                v-model="letterOfferDetails" 
                @submit="onDetailsSubmit"
              />
              <div class="flex justify-between mt-6 pt-4 border-t">
                <Button @click="previousNavigation" variant="outline">
                  Previous
                </Button>
                <Button 
                  :disabled="!letterOfferDetails.supplyPoint"
                  @click="onDetailsSubmit"
                >
                  Next
                </Button>
              </div>
            </div>

            <!-- Letter Footer Step -->
            <div v-show="stepIndex === 2" id="letterFooter" style="padding-top: 1rem;">
              <MarketingOLFooterForm 
                v-model="letterFooter"
                @submit="onFooterSubmit"
              />
              <div class="flex justify-between mt-6 pt-4 border-t">
                <Button @click="previousNavigation" variant="outline">
                  Previous
                </Button>
                <Button 
                  :disabled="!letterFooter.offeror.name || !letterFooter.companyInformation.phoneNumber"
                  @click="onPreviewPdf"
                >
                  Preview PDF
                </Button>
                <Button 
                  :disabled="!letterFooter.offeror.name || !letterFooter.companyInformation.phoneNumber"
                  @click="onFooterSubmit"
                >
                  Create & Save
                </Button>
              </div>
            </div>
          </NuxtStepper>
          
          <!-- Loading State -->
          <template #fallback>
            <div class="py-12 flex items-center justify-center">
              <span class="animate-spin mr-2 text-primary">Loading...</span>
            </div>
          </template>
        </ClientOnly>
      </NuxtCardContent>
    </NuxtCard>

    <!-- Modal Preview PDF -->
    <DocumentPreviewModal 
      v-if="previewOpen" 
      @close="previewOpen = false"
    />
  </div>
</template>
