<script setup lang="ts">
import angkaTerbilang from '@develoka/angka-terbilang-js'
import { useChangeCase } from '@vueuse/integrations/useChangeCase.js'
import logoImage from '~/assets/images/map-logo-only.jpg'
import type { DeliveryOrdersDetails, Details } from '~/types/operations'

const pdfLink = ref<string | null>(null)
const route = useRoute()
const idDoLetter = route.params.id
const { user } = useAuth()

const { get } = useApi()

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
  if (!data) return ['Data delivery order']

  const required: Array<[string, unknown]> = [
    ['Nama perusahaan', data.companyInformation?.name],
    ['Alamat perusahaan', data.companyInformation?.address],
    ['Nomor DO', data.doInformation?.doNumber],
    ['Tanggal DO', data.doInformation?.doDateCreated],
    ['Nomor PO Customer', data.doInformation?.poCustomerNumber?.purchaseOrderNumber],
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
  const pdfMake = usePDFMake()
  if (!pdfMake) return
  if (!details.value || !isDetailsComplete.value) return

  const detailsData = details.value
  const surat = detailsData
  const tableBodyNotes: { text: string, border: [boolean, boolean, boolean, boolean] }[][] = [
    [
      {
        text: 'Catatan :',
        border: [true, false, true, false]
      }
    ]
  ]

  for (const note of surat.notes || []) {
    tableBodyNotes.push([
      {
        text: note.note || '',
        border: [true, false, true, false]
      }
    ])
  }

  pdfLink.value = await pdfMake
    .createPdf({
      info: {
        title: `Delivery Order ${idDoLetter}`,
        author: 'PT. Mitra Andalan Petroleum',
        creator: user.value?.name,
        producer: 'PT. Mitra Andalan Petroleum'
      },
      pageMargins: [24, 24, 24, 24],
      pageSize: 'A4',
      content: [
        {
          layout: {
            // defaultBorder: false,
            paddingRight: function () {
              return 10
            },
            paddingLeft: function () {
              return 10
            },
            paddingBottom: function () {
              return 10
            },
            paddingTop: function () {
              return 10
            },
            fillColor: function () {
              return null
            }
          },
          table: {
            widths: ['25%', '*'],
            body: [
              [
                {
                  image: await toBase64(logoImage),
                  width: 30,
                  alignment: 'center',
                  border: [true, true, false, false]
                },
                {
                  text: 'SURAT PENGANTAR PENGIRIMAN (DELIVERY ORDER)',
                  bold: true,
                  fontSize: 11,
                  border: [false, true, true, false]
                }
              ]
            ]
          }
        },
        {
          layout: {
            defaultBorder: false,
            paddingRight: function () {
              return 2
            },
            paddingLeft: function () {
              return 2
            },
            paddingBottom: function () {
              return 1
            },
            paddingTop: function () {
              return 1
            },
            fillColor: function () {
              return null
            }
          },
          table: {
            widths: ['*', '15%', 'auto', '30%'],
            body: [
              [
                {
                  text: `${surat.companyInformation.name}`,
                  bold: true,
                  border: [true, false, false, false]
                },
                {
                  text: ''
                },
                {
                  text: ''
                },
                {
                  text: '',
                  border: [false, false, true, false]
                }
              ],
              [
                {
                  text: `${surat.companyInformation.nameSub}`,
                  italics: true,
                  border: [true, false, false, false]
                },
                {
                  text: 'No. DO MAP',
                  bold: true
                },
                {
                  text: ':'
                },
                {
                  text: `${surat.doInformation.doNumber}`,
                  border: [false, false, true, false]
                }
              ],
              [
                {
                  text: `${surat.companyInformation.address}`,
                  border: [true, false, false, false]
                },
                {
                  text: 'Tgl. DO',
                  bold: true
                },
                {
                  text: ':'
                },
                {
                  text: formatDateDoc(surat.doInformation.doDateCreated),
                  border: [false, false, true, false]
                }
              ],
              [
                {
                  text: `${surat.companyInformation.phoneNumber}`,
                  border: [true, false, false, false]
                },
                {},
                {
                  text: ':'
                },
                {
                  text: '',
                  border: [false, false, true, false]
                }
              ],
              [
                {
                  text: '',
                  border: [true, false, false, false]
                },
                {
                  text: 'NO. PO Cust.',
                  bold: true
                },
                {
                  text: ':'
                },
                {
                  text: `${surat.doInformation.poCustomerNumber.purchaseOrderNumber}`,
                  border: [false, false, true, false]
                }
              ],
              [
                {
                  text: '',
                  border: [true, false, false, false]
                },
                {
                  text: 'No. SO',
                  bold: true
                },
                {
                  text: ':'
                },
                {
                  text: `${surat.doInformation.soNumber || ''}\n\n`,
                  border: [false, false, true, false]
                }
              ]
            ]
          }
        },
        {
          layout: {
            defaultBorder: false,
            paddingRight: function () {
              return 2
            },
            paddingLeft: function () {
              return 2
            },
            paddingBottom: function () {
              return 2
            },
            paddingTop: function () {
              return 2
            },
            fillColor: function () {
              return null
            }
          },
          table: {
            widths: ['auto', 'auto', '*', 'auto', 'auto', '*'],
            body: [
              [
                {
                  text: 'Diserahkan Kepada',
                  bold: true,
                  border: [true, true, false, false]
                },
                {
                  text: ':',
                  border: [false, true, false, false]
                },
                {
                  text: `${surat.customerName}`,
                  border: [false, true, false, false]
                },
                {
                  text: 'Agen/ Transportir',
                  bold: true,
                  border: [true, true, false, false]
                },
                {
                  text: ':',
                  border: [false, true, false, false]
                },
                {
                  text: `${surat.transportName}\n\n\n`,
                  border: [false, true, true, false]
                }
              ],
              [
                {
                  text: 'ID. Pelanggan',
                  bold: true,
                  border: [true, false, false, false]
                },
                {
                  text: ':'
                },
                {
                  text: `${surat.customerName}`
                },
                {
                  text: 'ID',
                  bold: true,
                  border: [true, false, false, false]
                },
                {
                  text: ':'
                },
                {
                  text: `${surat.transportId || ''}`,
                  border: [false, false, true, false]
                }
              ],
              [
                {
                  text: 'Alamat',
                  bold: true,
                  border: [true, false, false, false]
                },
                {
                  text: ':'
                },
                {
                  text: `${surat.customerAddress || ''}`,
                  border: [false, false, true, false]
                },
                {
                  text: 'Alamat',
                  bold: true,
                  border: [true, false, false, false]
                },
                {
                  text: ':'
                },
                {
                  text: `${surat.transportAddress || ''}\n\n\n`,
                  border: [false, false, true, false]
                }
              ],
              [
                {
                  text: 'Penerima BBM+HP',
                  bold: true,
                  border: [true, false, false, false]
                },
                {
                  text: ':'
                },
                {
                  text: `${surat.receiverInformation.name || ''}`
                },
                {
                  text: 'Driver+HP',
                  bold: true,
                  border: [true, false, false, false]
                },
                {
                  text: ':'
                },
                {
                  text: `${surat.driverInformation.name || ''} ${surat.driverInformation.phoneNumber ? '-' : ''} ${surat.driverInformation.phoneNumber || ''}\n\n\n`,
                  border: [false, false, true, false]
                }
              ],
              [
                {
                  text: '',
                  border: [true, false, false, false]
                },
                {
                  text: ''
                },
                {
                  text: ''
                },
                {
                  text: 'Kenet/Helper',
                  bold: true,
                  border: [true, false, false, false]
                },
                {
                  text: ':'
                },
                {
                  text: `${surat.helperName || ''}`,
                  border: [false, false, true, false]
                }
              ],
              [
                {
                  text: 'Tanggal',
                  bold: true,
                  border: [true, false, false, false]
                },
                {
                  text: ':'
                },
                {
                  text:
                    surat.receiverDateReceived === undefined
                      ? formatDateDoc(surat.receiverDateReceived)
                      : '',
                  border: [false, false, true, false]
                },
                {
                  text: 'Tanggal',
                  bold: true,
                  border: [true, false, false, false]
                },
                {
                  text: ':'
                },
                {
                  text:
                    surat.receiverDateReceived === undefined
                      ? formatDateDoc(surat.transportDateReceived)
                      : '',
                  border: [false, false, true, false]
                }
              ]
            ]
          }
        },
        {
          layout: {
            // defaultBorder: false,
            paddingRight: function () {
              return 2
            },
            paddingLeft: function () {
              return 2
            },
            paddingBottom: function () {
              return 2
            },
            paddingTop: function () {
              return 2
            },
            fillColor: function () {
              return null
            }
          },
          table: {
            widths: ['*', '*', '*', '*', '*', '*'],
            body: [
              [
                {
                  text: 'Tanggal Berlaku',
                  alignment: 'center',
                  bold: true,
                  colSpan: 2
                },
                {},
                {
                  text: 'Produk',
                  alignment: 'center',
                  bold: true,
                  colSpan: 2
                },
                {},
                {
                  text: 'Volume/ Kuantitas (Liter)',
                  alignment: 'center',
                  bold: true,
                  colSpan: 2
                },
                {}
              ],
              [
                {
                  text: `${surat.dueDate !== undefined ? formatDateDoc(surat.dueDate) : ''}`,
                  colSpan: 2,
                  alignment: 'center'
                },
                {},
                {
                  text: `${surat.productInformation.name || ''}`,
                  colSpan: 2,
                  alignment: 'center'
                },
                {},
                {
                  text: `${formatNumber(surat.productInformation.qty || 0)} Liter`,
                  colSpan: 2,
                  alignment: 'center'
                },
                {}
              ],
              [
                {
                  text: 'Dikirim Dengan',
                  bold: true
                },
                {},
                {
                  text: 'Segel Atas',
                  rowSpan: 2,
                  verticalAlignment: 'middle',
                  bold: true
                },
                {
                  text: `${surat.productInformation.topSeal || ''}`,
                  rowSpan: 2,
                  verticalAlignment: 'middle',
                  alignment: 'center'
                },
                {
                  text: 'Bebas Air',
                  bold: true
                },
                {
                  text: 'Ya / Tidak',
                  alignment: 'center'
                }
              ],
              [
                {
                  text: 'No. Kendaraan',
                  bold: true
                },
                {
                  text: `${surat.transportInformation.transportNumber || ''}`
                },
                {
                  text: ''
                },
                {
                  text: ''
                },
                {
                  text: 'Jam Berangkat',
                  bold: true
                },
                {
                  text: `${surat.transportInformation.timeInformation.departureTime || ''}`
                }
              ],
              [
                {
                  text: 'Km. Awal',
                  bold: true
                },
                {
                  text: `${surat.transportInformation.startKm || ''}`
                },
                {
                  text: 'Segel Bawah',
                  rowSpan: 2,
                  verticalAlignment: 'middle',
                  bold: true
                },
                {
                  text: `${surat.productInformation.bottomSeal || ''}`,
                  rowSpan: 2,
                  verticalAlignment: 'middle',
                  alignment: 'center'
                },
                {
                  text: 'Jam Tiba',
                  bold: true
                },
                {
                  text: `${surat.transportInformation.timeInformation.arrivalTime || ''}`
                }
              ],
              [
                {
                  text: 'Km. Akhir',
                  bold: true
                },
                {
                  text: `${surat.transportInformation.endKm || ''}`
                },
                {
                  text: ''
                },
                {
                  text: ''
                },
                {
                  text: 'Jam Mulai Pembongkaran',
                  bold: true
                },
                {
                  text: `${surat.transportInformation.timeInformation.unloadingTime || ''}`
                }
              ],
              [
                {
                  text: 'SG Meter',
                  bold: true
                },
                {
                  text: `${surat.transportInformation.sgMeter || ''}`
                },
                {
                  text: 'Temperatur',
                  bold: true
                },
                {
                  text: `${surat.productInformation.temperature || ''}`
                },
                {
                  text: 'Jam Tiba di Depo',
                  bold: true
                },
                {
                  text: `${surat.transportInformation.timeInformation.depotArrivalTime || ''}`
                }
              ],
              [
                { text: '', border: [true, true, false, true] },
                { text: '', border: [false, true, false, true] },
                { text: '', border: [false, true, false, true] },
                { text: '', border: [false, true, false, true] },
                { text: '', border: [false, true, false, true] },
                { text: '', border: [false, true, true, true] }
              ],
              [
                {
                  text: 'Jumlah (Liter)',
                  bold: true
                },
                {
                  text: `${formatNumber(surat.productInformation.qty || 0)} # (${useChangeCase(angkaTerbilang(surat.productInformation.qty), 'capitalCase').value} Liter) #`,
                  italics: true,
                  colSpan: 5
                },
                {},
                {},
                {},
                {}
              ]
            ]
          }
        },
        {
          layout: {
            // defaultBorder: false,
            paddingRight: function () {
              return 100
            },
            paddingLeft: function () {
              return 2
            },
            paddingBottom: function (i, node) {
              return i === node.table.body.length - 1 ? 15 : 2
            },
            paddingTop: function (i) {
              return i === 0 ? 15 : 2
            },
            fillColor: function () {
              return null
            }
          },
          table: {
            widths: ['*'],
            body: tableBodyNotes
          }
        },
        {
          layout: {
            defaultBorder: false,
            paddingRight: function () {
              return 2
            },
            paddingLeft: function () {
              return 2
            },
            paddingBottom: function () {
              return 15
            },
            paddingTop: function () {
              return 2
            },
            fillColor: function () {
              return null
            }
          },
          table: {
            widths: ['*', 'auto', '*', '*', 'auto', '*'],
            body: [
              [
                {
                  text: 'T2 DEPO',
                  bold: true,
                  border: [true, false, false, false]
                },
                {
                  text: ':'
                },
                {
                  text: '______________________'
                },
                {
                  text: 'KEPEKAAN INDEX\n(buku tera mobil)',
                  bold: true
                },
                {
                  text: ':'
                },
                {
                  text: '______________________',
                  border: [false, false, true, false]
                }
              ],
              [
                {
                  text: 'T2 BONGKAR',
                  bold: true,
                  border: [true, false, false, false]
                },
                {
                  text: ':'
                },
                {
                  text: '______________________'
                },
                {
                  text: 'BBM DITERIMA',
                  bold: true
                },
                {
                  text: ':'
                },
                {
                  text: '______________________ Liter',
                  border: [false, false, true, false]
                }
              ]
            ]
          }
        },
        {
          layout: {
            // defaultBorder: false,
            paddingRight: function () {
              return 10
            },
            paddingLeft: function () {
              return 10
            },
            paddingBottom: function () {
              return 2
            },
            paddingTop: function (i) {
              return i === 1 ? 75 : 2
            },
            fillColor: function (i) {
              return i === 0 ? '#e5e5e5' : null
            }
          },
          table: {
            widths: ['auto', 'auto', '*', '*'],
            body: [
              [
                {
                  text: 'Koordinator MAP',
                  alignment: 'center',
                  bold: true
                },
                {
                  text: 'Adm. Distribusi',
                  alignment: 'center',
                  bold: true
                },
                {
                  text: 'Penerima',
                  alignment: 'center',
                  bold: true
                },
                {
                  text: 'Driver/Officer',
                  alignment: 'center',
                  bold: true
                }
              ],
              [
                {
                  text: `${surat.companyCoordinator || ''}`,
                  alignment: 'center',
                  bold: true
                },
                {
                  text: `${surat.distributionAdmin || ''}`,
                  alignment: 'center',
                  bold: true
                },
                {
                  text: `${surat.receiver || ''}`,
                  alignment: 'center',
                  bold: true
                },
                {
                  text: `${surat.driver || ''}`,
                  alignment: 'center',
                  bold: true
                }
              ],
              [
                { text: '', border: [true, true, false, true] },
                { text: '', border: [false, true, false, true] },
                { text: '', border: [false, true, false, true] },
                { text: '', border: [false, true, true, true] }
              ]
            ]
          }
        }
      ],
      defaultStyle: {
        color: '#000000',
        fontSize: 9
      }
    })
    .getDataUrl()
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
            Lengkapi di Form DO
          </UButton>
        </div>
      </div>
    </UCard>
  </main>
</template>
