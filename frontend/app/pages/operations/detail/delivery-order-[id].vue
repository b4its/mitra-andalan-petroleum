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

const { data: doDetails } = await useAsyncData(
  'delivery-orders-details',
  async () => {
    const res = await get<DeliveryOrdersDetails>(
      `/delivery-orders/${idDoLetter}`
    )
    return res
  },
  { default: () => [] }
)

const details: Details = doDetails.value?.details

const tableBodyNotes = [
  [
    [
      {
        text: 'Catatan :',
        border: [true, false, true, false]
      }
    ]
  ]
]

for (const note of details.notes) {
  tableBodyNotes.push([
    {
      text: note.note || '',
      border: [true, false, true, false]
    }
  ])
}

const loadPdf = async () => {
  const pdfMake = usePDFMake()
  if (!pdfMake) return

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
            paddingRight: function (i) {
              return 10
            },
            paddingLeft: function (i) {
              return 10
            },
            paddingBottom: function (i) {
              return 10
            },
            paddingTop: function (i) {
              return 10
            },
            fillColor: function (i) {
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
            paddingRight: function (i) {
              return 2
            },
            paddingLeft: function (i) {
              return 2
            },
            paddingBottom: function (i) {
              return 1
            },
            paddingTop: function (i) {
              return 1
            },
            fillColor: function (i) {
              return null
            }
          },
          table: {
            widths: ['*', '15%', 'auto', '30%'],
            body: [
              [
                {
                  text: `${details.companyInformation.name}`,
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
                  text: `${details.companyInformation.nameSub}`,
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
                  text: `${details.doInformation.doNumber}`,
                  border: [false, false, true, false]
                }
              ],
              [
                {
                  text: `${details.companyInformation.address}`,
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
                  text: formatDateDoc(details.doInformation.doDateCreated),
                  border: [false, false, true, false]
                }
              ],
              [
                {
                  text: `${details.companyInformation.phoneNumber}`,
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
                  text: `${details.doInformation.poCustomerNumber.purchaseOrderNumber}`,
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
                  text: `${details.doInformation.soNumber || ''}\n\n`,
                  border: [false, false, true, false]
                }
              ]
            ]
          }
        },
        {
          layout: {
            defaultBorder: false,
            paddingRight: function (i) {
              return 2
            },
            paddingLeft: function (i) {
              return 2
            },
            paddingBottom: function (i) {
              return 2
            },
            paddingTop: function (i) {
              return 2
            },
            fillColor: function (i) {
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
                  text: `${details.customerName}`,
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
                  text: `${details.transportName}\n\n\n`,
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
                  text: `${details.customerName}`
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
                  text: `${details.transportId || ''}`,
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
                  text: `${details.customerAddress || ''}`,
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
                  text: `${details.transportAddress || ''}\n\n\n`,
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
                  text: `${details.receiverInformation.name || ''}`
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
                  text: `${details.driverInformation.name || ''} ${details.driverInformation.phoneNumber ? '-' : ''} ${details.driverInformation.phoneNumber || ''}\n\n\n`,
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
                  text: `${details.helperName || ''}`,
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
                    details.receiverDateReceived === undefined
                      ? formatDateDoc(details.receiverDateReceived)
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
                    details.receiverDateReceived === undefined
                      ? formatDateDoc(details.transportDateReceived)
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
            paddingRight: function (i) {
              return 2
            },
            paddingLeft: function (i) {
              return 2
            },
            paddingBottom: function (i) {
              return 2
            },
            paddingTop: function (i) {
              return 2
            },
            fillColor: function (i) {
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
                  text: `${details.dueDate !== undefined ? formatDateDoc(details.dueDate) : ''}`,
                  colSpan: 2,
                  alignment: 'center'
                },
                {},
                {
                  text: `${details.productInformation.name || ''}`,
                  colSpan: 2,
                  alignment: 'center'
                },
                {},
                {
                  text: `${formatNumber(details.productInformation.qty || 0)} Liter`,
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
                  text: `${details.productInformation.topSeal || ''}`,
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
                  text: `${details.transportInformation.transportNumber || ''}`
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
                  text: `${details.transportInformation.timeInformation.departureTime || ''}`
                }
              ],
              [
                {
                  text: 'Km. Awal',
                  bold: true
                },
                {
                  text: `${details.transportInformation.startKm || ''}`
                },
                {
                  text: 'Segel Bawah',
                  rowSpan: 2,
                  verticalAlignment: 'middle',
                  bold: true
                },
                {
                  text: `${details.productInformation.bottomSeal || ''}`,
                  rowSpan: 2,
                  verticalAlignment: 'middle',
                  alignment: 'center'
                },
                {
                  text: 'Jam Tiba',
                  bold: true
                },
                {
                  text: `${details.transportInformation.timeInformation.arrivalTime || ''}`
                }
              ],
              [
                {
                  text: 'Km. Akhir',
                  bold: true
                },
                {
                  text: `${details.transportInformation.endKm || ''}`
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
                  text: `${details.transportInformation.timeInformation.unloadingTime || ''}`
                }
              ],
              [
                {
                  text: 'SG Meter',
                  bold: true
                },
                {
                  text: `${details.transportInformation.sgMeter}`
                },
                {
                  text: 'Temperatur',
                  bold: true
                },
                {
                  text: `${details.productInformation.temperature || ''}`
                },
                {
                  text: 'Jam Tiba di Depo',
                  bold: true
                },
                {
                  text: `${details.transportInformation.timeInformation.depotArrivalTime || ''}`
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
                  text: `${formatNumber(details.productInformation.qty || 0)} # (${useChangeCase(angkaTerbilang(details.productInformation.qty), 'capitalCase').value} Liter) #`,
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
            paddingRight: function (i) {
              return 100
            },
            paddingLeft: function (i) {
              return 2
            },
            paddingBottom: function (i, node) {
              return i === node.table.body.length - 1 ? 15 : 2
            },
            paddingTop: function (i) {
              return i === 0 ? 15 : 2
            },
            fillColor: function (i) {
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
            paddingRight: function (i) {
              return 2
            },
            paddingLeft: function (i) {
              return 2
            },
            paddingBottom: function (i) {
              return 15
            },
            paddingTop: function (i) {
              return 2
            },
            fillColor: function (i) {
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
            paddingRight: function (i) {
              return 10
            },
            paddingLeft: function (i) {
              return 10
            },
            paddingBottom: function (i) {
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
                  text: 'Penerima (Nama + Ttd + Stempel)',
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
                  text: `${details.companyCoordinator || ''}`,
                  alignment: 'center',
                  bold: true
                },
                {
                  text: `${details.distributionAdmin || ''}`,
                  alignment: 'center',
                  bold: true
                },
                {
                  text: `${details.receiver || ''}`,
                  alignment: 'center',
                  bold: true
                },
                {
                  text: `${details.driver || ''}`,
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

onMounted(() => {
  loadPdf()
})
</script>

<template>
  <main class="h-180 w-full">
    <iframe v-if="pdfLink" :src="pdfLink" class="h-full w-full" />
  </main>
</template>
