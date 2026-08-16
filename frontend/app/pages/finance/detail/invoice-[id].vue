<script setup lang="ts">
import type { InvoiceDetailsData, InvoiceDetails } from '~/types/finance'
import { useInvoicePdf } from '~/composables/useInvoicePdf'

const pdfLink = ref<string | null>(null)
const route = useRoute()
const invoiceId = route.params.id
const { get } = useApi()
const { buildInvoicePdf } = useInvoicePdf()

const { data: invoiceDetails, pending } = await useAsyncData(
  'invoice-details',
  async () => {
    const res = await get<InvoiceDetails>(`/invoices/${invoiceId}`)
    return res
  }
)
const details: InvoiceDetailsData = invoiceDetails.value?.details as InvoiceDetailsData

const loadPdf = async () => {
  if (!details?.companyInformation) return
  pdfLink.value = await buildInvoicePdf(details)
}

onMounted(() => {
  if (details?.companyInformation) {
    loadPdf()
  }
})
</script>

<template>
  <main class="h-180 w-full">
    <div v-if="pending" class="h-full w-full space-y-4 p-8">
      <USkeleton class="h-8 w-64 rounded" />
      <USkeleton class="h-4 w-80 rounded" />
      <USkeleton class="h-40 w-full rounded-lg" />
      <USkeleton class="h-32 w-full rounded-lg" />
      <USkeleton class="h-40 w-full rounded-lg" />
    </div>
    <iframe v-else-if="pdfLink" :src="pdfLink" class="h-full w-full" />
    <div
      v-else-if="!details?.companyInformation"
      class="flex flex-col items-center justify-center h-full gap-3 text-muted"
    >
      <UIcon name="i-lucide-file-x" class="size-12" />
      <p class="text-sm font-medium">
        Data Invoice Belum Lengkap
      </p>
      <p class="text-xs">
        Lengkapi data invoice terlebih dahulu.
      </p>
    </div>
  </main>
</template>
