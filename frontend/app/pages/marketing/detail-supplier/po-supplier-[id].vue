<script setup lang="ts">
import type { Details, PurchaseOrderDetails } from '~/types/marketing'
import { usePoSupplierPdf } from '~/composables/usePoSupplierPdf'

const pdfLink = ref<string | null>(null)
const route = useRoute()
const idPoLetter = route.params.id
const { get } = useApi()
const { buildPoSupplierPdf } = usePoSupplierPdf()

const { data: purchaseOrderDetails, pending } = await useAsyncData(
  'purchase-order-detail-po-supplier',
  async () => {
    const res = await get<PurchaseOrderDetails>(
      `/purchase-orders/${idPoLetter}`
    )
    return res
  }
)

const details = computed<Details | null>(() => purchaseOrderDetails.value?.details ?? null)

const loadPdf = async () => {
  const d = details.value
  if (!d?.signed) return
  pdfLink.value = await buildPoSupplierPdf(d, {
    supplierName: purchaseOrderDetails.value?.supplier_name || '',
    poNumber: purchaseOrderDetails.value?.po_number || ''
  })
}

watch(
  details,
  (d) => {
    if (d && !pdfLink.value) loadPdf()
  },
  { immediate: true }
)

onMounted(() => {
  loadPdf()
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
  </main>
</template>
