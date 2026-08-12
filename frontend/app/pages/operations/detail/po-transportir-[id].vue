<script setup lang="ts">
import logoImage from '~/assets/images/map-logo-only.jpg'
import type { DeliveryOrdersDetails, Details } from '~/types/operations'

const pdfLink = ref<string | null>(null)
const route = useRoute()
const idDoLetter = route.params.id
const { user } = useAuth()
const { get } = useApi()

const { data: doDetails, pending } = await useAsyncData<DeliveryOrdersDetails | null>(
  'po-transportir-details',
  async () => {
    const res = await get<DeliveryOrdersDetails>(`/delivery-orders/${idDoLetter}`)
    return res
  },
  { default: () => null, server: false }
)

const details = computed<Details | null>(() => doDetails.value?.details ?? null)

const loadPdf = async () => {
  const pdfMake = usePDFMake()
  if (!pdfMake) return
  const d = details.value
  if (!d) return

  const today = new Date()
  const romanMonths = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']

  pdfLink.value = await pdfMake
    .createPdf({
      info: {
        title: `Purchase Order Transportir (${d.doInformation?.doNumber || ''})`,
        author: 'PT. Mitra Andalan Petroleum',
        creator: user.value?.name,
        producer: 'PT. Mitra Andalan Petroleum'
      },
      pageMargins: [40, 40, 40, 40],
      pageSize: 'A4',
      content: [
        {
          image: await toBase64(logoImage),
          width: 110
        },
        {
          text: 'PT. MITRA ANDALAN PETROLEUM',
          bold: true,
          fontSize: 16,
          marginTop: 10
        },
        {
          text: `${d.companyInformation?.address || ''}\nPhone: ${d.companyInformation?.phoneNumber || ''}`,
          fontSize: 8,
          marginBottom: 15
        },
        {
          text: 'PURCHASE ORDER TRANSPORTIR',
          bold: true,
          fontSize: 14,
          alignment: 'center',
          marginBottom: 20
        },
        {
          layout: 'noBorders',
          table: {
            widths: ['auto', 'auto', '*'],
            body: [
              [
                { text: 'Nomor Purchase Order', bold: true },
                { text: ':' },
                { text: `PO-TR/${today.getFullYear()}/${romanMonths[today.getMonth()]}/${String(today.getDate()).padStart(2, '0')}` }
              ],
              [
                { text: 'Tanggal', bold: true },
                { text: ':' },
                { text: formatDateDoc(d.doInformation?.doDateCreated || today) }
              ],
              [
                { text: 'Nomor Delivery Order', bold: true },
                { text: ':' },
                { text: d.doInformation?.doNumber || '' }
              ]
            ]
          }
        },
        {
          text: [
            'Kepada Yth.\n',
            { text: `${d.transportName || ''}`.toUpperCase(), bold: true }
          ],
          marginTop: 15
        },
        {
          text: 'Dengan Hormat,',
          marginTop: 15
        },
        {
          text: 'Berikut kami sampaikan Purchase Order Transportir dengan perincian sebagai berikut:',
          marginTop: 10,
          marginBottom: 8
        },
        {
          layout: {
            paddingTop: function () { return 3 },
            paddingBottom: function () { return 3 }
          },
          table: {
            headerRows: 1,
            widths: ['auto', '*', 'auto', 'auto'],
            body: [
              [
                { text: 'No', bold: true, alignment: 'center' },
                { text: 'Produk', bold: true },
                { text: 'Qty', bold: true, alignment: 'center' },
                { text: 'Unit', bold: true, alignment: 'center' }
              ],
              [
                { text: '1', alignment: 'center' },
                { text: d.productInformation?.name || '' },
                { text: formatNumber(d.productInformation?.qty || 0), alignment: 'center' },
                { text: 'Liter', alignment: 'center' }
              ]
            ]
          }
        },
        {
          layout: 'noBorders',
          table: {
            widths: ['auto', 'auto', '*'],
            body: [
              [
                { text: 'Driver', bold: true },
                { text: ':' },
                { text: `${d.driverInformation?.name || ''} (${d.driverInformation?.phoneNumber || ''})` }
              ],
              [
                { text: 'Tanggal Pengiriman', bold: true },
                { text: ':' },
                { text: formatDateDoc(d.dueDate || d.transportDateReceived || '') }
              ],
              [
                { text: 'Kendaraan', bold: true },
                { text: ':' },
                { text: `${d.transportInformation?.transportType || ''} ${d.transportInformation?.transportNumber || ''}` }
              ]
            ]
          }
        },
        {
          text: 'Demikian Purchase Order Transportir ini kami sampaikan, atas kerja samanya kami ucapkan terima kasih.',
          marginTop: 20
        },
        {
          text: 'Hormat Kami,',
          marginTop: 25,
          marginBottom: 40
        },
        {
          text: `(${user.value?.name || ''})`,
          bold: true
        }
      ],
      defaultStyle: {
        color: '#000000',
        fontSize: 9
      }
    })
    .getDataUrl()
}

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
    <div v-else-if="!details" class="flex flex-col items-center justify-center h-full gap-3 text-muted">
      <UIcon name="i-lucide-file-x" class="size-12" />
      <p class="text-sm font-medium">
        Data Delivery Order Belum Lengkap
      </p>
    </div>
  </main>
</template>
