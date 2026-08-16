<script setup lang="ts">
import type { DeliveryOrdersDetails, Details } from '~/types/operations'
import { useDeliveryOrderPdf } from '~/composables/useDeliveryOrderPdf'

const pdfLink = ref<string | null>(null)
const route = useRoute()
const idDoLetter = route.params.id
const { get } = useApi()
const { buildDeliveryOrderPdf } = useDeliveryOrderPdf()

const { data: doDetails, pending } = await useAsyncData<DeliveryOrdersDetails | null>(
  'delivery-orders-details',
  async () => {
    const res = await get<DeliveryOrdersDetails>(
      `/delivery-orders/${idDoLetter}`
    )
    return res
  },
  { default: () => null, server: false }
)

const details = computed<Details | null>(() => doDetails.value?.details ?? null)
const completeFormPath = computed(() => `/operations/delivery-order?do_id=${idDoLetter}`)

function isFilled(value: unknown) {
  if (Array.isArray(value)) return value.length > 0
  if (typeof value === 'number') return Number.isFinite(value) && value > 0
  if (typeof value === 'string') return value.trim().length > 0
  return value !== undefined && value !== null
}

const missingFields = computed(() => {
  const data = details.value
  if (!data) return ['Data Delivery Order']

  const required: Array<[string, unknown]> = [
    ['Nama perusahaan', data.companyInformation?.name],
    ['Alamat perusahaan', data.companyInformation?.address],
    ['Nomor Delivery Order', data.doInformation?.doNumber],
    ['Tanggal Delivery Order', data.doInformation?.doDateCreated],
    ['Nomor Purchase Order Customer', data.doInformation?.poCustomerNumber?.purchaseOrderNumber],
    ['Nama customer', data.customerName],
    ['Nama penerima', data.receiverInformation?.name],
    ['Nama transportir', data.transportName],
    ['Nama driver', data.driverInformation?.name],
    ['Tanggal berlaku', data.dueDate],
    ['Nama produk', data.productInformation?.name],
    ['Volume produk', data.productInformation?.qty],
    ['Segel atas', data.productInformation?.topSeal],
    ['Segel bawah', data.productInformation?.bottomSeal],
    ['Nomor kendaraan', data.transportInformation?.transportNumber],
    ['Jenis transport', data.transportInformation?.transportType],
    ['KM awal', data.transportInformation?.startKm],
    ['KM akhir', data.transportInformation?.endKm],
    ['SG meter', data.transportInformation?.sgMeter],
    ['T2 depo', data.t2Depot],
    ['T2 bongkar', data.t2Unloading],
    ['Kepekaan index', data.indexSensitivity],
    ['BBM diterima', data.fuelReceived],
    ['Koordinator MAP', data.companyCoordinator],
    ['Admin distribusi', data.distributionAdmin],
    ['Penerima', data.receiver],
    ['Driver/Officer', data.driver]
  ]

  return required.filter(([, value]) => !isFilled(value)).map(([label]) => label)
})

const isDetailsComplete = computed(() => missingFields.value.length === 0)

const loadPdf = async () => {
  if (!details.value || !isDetailsComplete.value) return
  pdfLink.value = await buildDeliveryOrderPdf(details.value)
}

watch(
  isDetailsComplete,
  (complete) => {
    if (complete && !pdfLink.value) loadPdf()
  },
  { immediate: true }
)
</script>

<template>
  <main class="min-h-180 w-full">
    <div v-if="pending" class="h-180 w-full space-y-4 p-8">
      <USkeleton class="h-8 w-64 rounded" />
      <USkeleton class="h-4 w-80 rounded" />
      <USkeleton class="h-40 w-full rounded-lg" />
      <USkeleton class="h-32 w-full rounded-lg" />
      <USkeleton class="h-40 w-full rounded-lg" />
    </div>

    <iframe v-else-if="pdfLink" :src="pdfLink" class="h-180 w-full" />

    <UCard v-else class="mx-auto max-w-3xl">
      <template #header>
        <div class="flex items-start gap-3">
          <UIcon name="i-lucide-file-warning" class="mt-1 size-6 text-warning" />
          <div>
            <h2 class="text-lg font-semibold text-neutral-900 dark:text-neutral-50">
              Data Delivery Order belum lengkap
            </h2>
            <p class="text-sm text-neutral-500 dark:text-neutral-400">
              PDF tidak dapat dicetak sebelum data wajib dilengkapi.
            </p>
          </div>
        </div>
      </template>

      <div class="space-y-4">
        <p class="text-sm text-neutral-600 dark:text-neutral-300">
          Lengkapi data berikut di halaman form pembuatan Delivery Order, lalu buka kembali surat ini untuk mencetak PDF.
        </p>

        <div class="grid gap-2 sm:grid-cols-2">
          <UBadge
            v-for="field in missingFields"
            :key="field"
            color="warning"
            variant="soft"
            class="justify-start"
          >
            {{ field }}
          </UBadge>
        </div>

        <div class="flex flex-wrap justify-end gap-2 pt-2">
          <UButton
            icon="i-lucide-refresh-cw"
            color="neutral"
            variant="soft"
            @click="refreshNuxtData('delivery-orders-details')"
          >
            Cek Ulang Data
          </UButton>
          <UButton
            :to="completeFormPath"
            icon="i-lucide-clipboard-pen"
            color="primary"
          >
            Lengkapi di Form Delivery Order
          </UButton>
        </div>
      </div>
    </UCard>
  </main>
</template>
