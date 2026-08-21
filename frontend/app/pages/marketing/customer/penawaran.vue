<script setup lang="ts">
import type { StepperItem } from '@nuxt/ui'
import type {
  OfferingLetterPost,
  Customer,
  OfferingLetterDetails
} from '~/types/marketing'
import type {
  MarketingOLDetailsState,
  MarketingOLFooterState,
  MarketingOLHeaderState
} from '~/types/schemas'
import { useOfferingLetterPdf } from '~/composables/useOfferingLetterPdf'

definePageMeta({ layout: 'marketing' })

const { user } = useAuth()
const { get, post } = useApi()
const toast = useToast()
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
  customerList.value.map(receiver => ({
    label: receiver.name,
    value: receiver.id,
    npwp: receiver.npwp,
    address: receiver.address
  }))
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
  informasiTambahan: ['Harga dapat berubah mangikuti harga keekonomian Pertamina']
})

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

// Auto-fill offeror data from logged-in user's profile
if (user.value?.signature || user.value?.signatureCaption) {
  letterFooter.offeror.name = user.value.name || 'Pengguna'
  // Note: User must have uploaded signature in their profile for PDF generation
}

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

// Precio total bahan: basePrice + semua selling price (sama perhit seperti DetailsForm)
const fuelTotalPrice = computed(() => {
  const fp = letterOfferDetails.fuelPrices
  return (
    fp.basePrice
    + fp.sellingPrice.ppkb
    + (fp.sellingPrice.oat ?? 0)
    + fp.sellingPrice.ppn
    + (fp.sellingPrice.pph ?? 0)
  )
})

async function buildPreviewPdf(): Promise<string | null> {
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

// Validate signature requirement for offer letter creation
function validateUserSignature(): boolean {
  // Only marketing and admin roles need signature for offer letters
  const rolesNeedingSignature = ['marketing', 'admin']

  if (!user.value?.role || !rolesNeedingSignature.includes(user.value.role)) {
    return true // Other roles do not require signature
  }

  if (!user.value?.signature) {
    toast.add({
      title: 'Profil Belum Lengkap',
      description: 'Silakan upload tanda tangan terlebih dahulu di halaman profil sebelum membuat surat penawaran',
      color: 'warning'
    })

    // Navigate to profile page to complete signature setup
    useRouter().push('/admin/profile')
    return false
  }

  return true
}

async function onFooterSubmit() {
  // Check if user has signature configured
  if (!validateUserSignature()) return
  let createdId: string | null = null
  try {
    const details = {
      ...letterHeader,
      ...letterOfferDetails,
      ...letterFooter
    }
    const body: OfferingLetterPost = {
      offering_letter_number: letterHeader.offeringLetterNumber,
      customer_id: letterHeader.receiver,
      location: letterHeader.location,
      date: letterHeader.date,
      regarding: letterHeader.regarding,
      receiver: letterHeader.receiver,
      fuel_total_price: fuelTotalPrice.value,
      transport_price: 0,
      status: 'created',
      created_by: user.value?.id ?? null,
      details: details as unknown as OfferingLetterDetails
    }
    const res = await post<{ id: string }, OfferingLetterPost>(
      '/offering-letters',
      body
    )
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
      description: e instanceof Error ? e.message : 'Terjadi kesalahan saat membuat surat penawaran',
      color: 'error'
    })
  }
}

function onPreviewPdf() {
  if (!validateUserSignature()) return
  previewOpen.value = true
}
</script>

<template>
  <UDashboardPanel id="marketing-customer-penawaran">
    <template #header>
      <UDashboardNavbar title="Pembuatan Surat Penawaran">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="space-y-5 p-4">
        <USkeleton v-if="pending" class="h-16 rounded-lg" />
        <ClientOnly v-else>
          <UStepper ref="stepper" disabled :items>
            <template #letterHeader>
              <MarketingOLHeaderForm
                v-model="letterHeader"
                :has-previous="stepper?.hasPrev"
                :receivers="receivers"
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
                @preview="onPreviewPdf"
                @previous="previousNavigation"
                @submit="onFooterSubmit"
              />
            </template>
          </UStepper>

          <template #fallback>
            <div class="py-12 flex items-center justify-center">
              <UIcon name="i-lucide-loader-circle" class="size-8 animate-spin text-primary" />
            </div>
          </template>
        </ClientOnly>
      </div>

      <!-- Modal Preview PDF -->
      <DocumentPreviewModal
        :open="previewOpen"
        title="Preview Surat Penawaran"
        :build-pdf="buildPreviewPdf"
        @close="previewOpen = false"
      />
    </template>
  </UDashboardPanel>
</template>
