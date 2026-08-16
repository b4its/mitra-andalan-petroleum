<script setup lang="ts">
import type { StepperItem, NavigationMenuItem } from '@nuxt/ui'
import type {
  OperationsPOTransportDetailsState,
  OperationsPOTransportFooterState,
  OperationsPOTransportHeaderState
} from '~/types/schemas'
import type { PoTransportirsDetails, PoTransportirsPost } from '~/types/operations'

const toast = useToast()
const loading = ref(false)
const { user } = useAuth()
const { post } = useApi()

const items: StepperItem[] = [
  { title: 'Kop Surat PO Transportir', slot: 'poTransportHeader' },
  { title: 'Rincian PO Transportir', slot: 'poTransportDetails' },
  { title: 'Penutup Surat PO Transportir', slot: 'poTransportFooter' }
]

const poTransportHeader = reactive<OperationsPOTransportHeaderState>({
  date: `${new Date().toISOString().split('T')[0]}`,
  regarding: 'Purchase Order Transportir (PO) ',
  picPerson: 'Bpk Bambang Nugroho',
  poTransportNumber: '123/PO-TRANS/MAP/VIII/2026 ',
  receiver: 'PT. Surya Tambang Energi'
})

const poTransportDetails = reactive<OperationsPOTransportDetailsState>({
  products: [
    {
      name: 'Solar',
      loadingDate: `${new Date().toISOString().split('T')[0]}`,
      unloadingDate: `${new Date().toISOString().split('T')[0]}`,
      qty: 10000,
      ratePrice: 500,
      totalPrice: 0
    }
  ],
  percentageNum: {
    ppn: 0.11
  },
  priceSummary: {
    grandTotal: 0,
    ppn: 0,
    subTotal: 0
  }
})

const poTransportFooter = reactive<OperationsPOTransportFooterState>({
  loadingInformation: 'Masbro, Pendingin, Kutai Kartanegara, Kalimantan Timur',
  discharge: 'PT. Bina Sarana Sukses\nSite MHU - Kutai Kartanegara',
  termsOfPayment:
    '30 Hari kerja setelah invoice beserta kelengkapan dokumen selesai diverifikasi',
  shrinkageTolerance: 'Toleransi susut 0.3 %, Claim Susut Rp. 25.000,- / Liter',
  contactPerson: {
    companyName: 'PT. Mitra Andalan Petroleum',
    customerName: 'PT. Surya Tambang Energi',
    companyContactPerson: [
      {
        name: 'Nico Pratama',
        phoneNumber: '0812 3456 7890'
      }
    ],
    customerContactPerson: undefined
  },
  offeror: {
    name: 'Nico Pratama',
    signature: undefined
  }
})

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

    const poTransportData = {
      ...poTransportHeader,
      ...poTransportDetails,
      ...poTransportFooter
    }

    const total
      = poTransportData.priceSummary.grandTotal
        || poTransportData.products.reduce(
          (sum, p) => sum + (p.totalPrice || 0),
          0
        )

    const today = new Date().toISOString().split('T')[0]
    const poTransportPost: PoTransportirsPost = {
      po_number: poTransportData.poTransportNumber.trim(),
      date: poTransportData.date,
      pic_person: poTransportData.picPerson,
      receiver: poTransportData.receiver,
      total,
      status: 'created',
      details: {
        ...poTransportData,
        products: poTransportData.products.map(p => ({
          name: p.name,
          qty: p.qty,
          ratePrice: p.ratePrice,
          totalPrice: p.totalPrice,
          loadingDate: (p.loadingDate || today) as string,
          unloadingDate: (p.unloadingDate || today) as string
        }))
      },
      created_by: user.value?.id ?? null
    }

    const res = await post<PoTransportirsDetails, PoTransportirsPost>(
      '/po-transportir',
      poTransportPost
    )

    toast.add({
      title: 'Sukses',
      icon: 'i-lucide-check-circle',
      description: `Data PO Transportir ${res.po_number} berhasil dibuat`,
      color: 'success'
    })

    await navigateTo(
      `/operations/detail-transport/po-transportir-${res.id}`
    )
  } catch (e) {
    toast.add({
      title: 'Gagal',
      description: e instanceof Error ? e.message : 'Terjadi kesalahan',
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}

const links = [
  [
    {
      label: 'Buat PO Transportir',
      icon: 'i-lucide-warehouse',
      to: '/operations/po-transportir'
    }
  ]
] satisfies NavigationMenuItem[][]

definePageMeta({ layout: 'operations' })
</script>

<template>
  <UDashboardPanel id="do" :ui="{ body: 'w-full' }">
    <template #header>
      <UDashboardNavbar
        title="Form Pembuatan PO Transportir"
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
        <template #poTransportHeader>
          <OperationsPOTransportHeaderForm
            v-model="poTransportHeader"
            :has-previous="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmitToNext"
          />
        </template>

        <template #poTransportDetails>
          <OperationsPOTransportDetailsForm
            v-model="poTransportDetails"
            :has-previous="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmitToNext"
          />
        </template>

        <template #poTransportFooter>
          <OperationsPOTransportFooterForm
            v-model="poTransportFooter"
            :has-previous="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmit"
          />
        </template>
      </UStepper>
    </template>
  </UDashboardPanel>
</template>
