<script setup lang="ts">
import type { Customer, OfferingLetterPost } from '~/types/marketing'
import { useOfferingLetterPdf } from '~/composables/useOfferingLetterPdf'

const pdfLink = ref<string | null>(null)
const route = useRoute()
const { get } = useApi()
const { buildOfferingLetterPdf } = useOfferingLetterPdf()

const idOfferingLetter = route.params.id
const { data: offeringLetter, pending } = await useAsyncData(
  'offering-letter-details',
  async () => {
    const res = await get<OfferingLetterPost>(
      `/offering-letters/${idOfferingLetter}`
    )
    return res
  }
)

const { data: customerDetail, pending: pendingCustomer } = await useAsyncData(
  'customer-detail-surat',
  async () => {
    const res = await get<Customer>(
      `/customers/${offeringLetter.value?.details.receiver}`
    )
    return res
  }
)

const details = offeringLetter.value?.details

const { user } = useAuth()

// Caption tanda tangan user (penanda siapa yang menandatangani)
const { data: userProfile } = await useAsyncData(
  'user-profile-caption',
  async () => {
    if (!user.value?.id) return null
    return get<{ signature_caption?: string | null }>(
      `/profiles/${user.value.id}`
    )
  },
  { default: () => null, server: false }
)

const signatureCaption = computed(
  () =>
    userProfile.value?.signature_caption
    || details?.offeror?.name
    || user.value?.name
    || ''
)

const loadPdf = async () => {
  if (!details) return
  pdfLink.value = await buildOfferingLetterPdf(
    details,
    customerDetail.value?.name || details.receiver || '',
    { signatureCaption: signatureCaption.value }
  )
}

onMounted(() => {
  loadPdf()
})
</script>

<template>
  <main class="h-180 w-full">
    <div v-if="pending || pendingCustomer" class="h-full w-full space-y-4 p-8">
      <USkeleton class="h-8 w-64 rounded" />
      <USkeleton class="h-6 w-48 rounded" />
      <USkeleton class="h-4 w-80 rounded" />
      <USkeleton class="h-40 w-full rounded-lg" />
      <USkeleton class="h-32 w-full rounded-lg" />
      <USkeleton class="h-40 w-full rounded-lg" />
    </div>
    <iframe v-else-if="pdfLink" :src="pdfLink" class="h-full w-full" />
  </main>
</template>
