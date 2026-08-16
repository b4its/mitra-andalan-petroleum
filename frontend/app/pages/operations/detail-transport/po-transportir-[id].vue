<script setup lang="ts">
import type { PoTransportirsDetails } from '~/types/operations'
import { usePoTransportPdf } from '~/composables/usePoTransportPdf'

const pdfLink = ref<string | null>(null)
const route = useRoute()
const idPoTransportir = route.params.id
const { get } = useApi()
const { buildPoTransportPdf } = usePoTransportPdf()

const { data: poData, pending }
  = await useAsyncData<PoTransportirsDetails | null>(
    'po-transportir-details',
    async () => {
      const res = await get<PoTransportirsDetails>(
        `/po-transportir/${idPoTransportir}`
      )
      return res
    },
    { default: () => null, server: false }
  )

const details = computed<PoTransportirsDetails['details'] | null>(
  () => poData.value?.details ?? null
)

const loadPdf = async () => {
  const d = details.value
  if (!d) return
  pdfLink.value = await buildPoTransportPdf(d)
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
      <USkeleton class="h-6 w-48 rounded" />
      <USkeleton class="h-4 w-80 rounded" />
      <USkeleton class="h-40 w-full rounded-lg" />
    </div>
    <iframe v-else-if="pdfLink" :src="pdfLink" class="h-full w-full" />
    <div
      v-else-if="!details"
      class="flex flex-col items-center justify-center h-full gap-3 text-muted"
    >
      <UIcon name="i-lucide-file-x" class="size-12" />
      <p class="text-sm font-medium">
        Data PO Transportir Belum Lengkap
      </p>
    </div>
  </main>
</template>
