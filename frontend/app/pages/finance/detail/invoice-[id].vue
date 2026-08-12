<script setup lang="ts">
import angkaTerbilang from '@develoka/angka-terbilang-js'
import { useChangeCase } from '@vueuse/integrations/useChangeCase.js'
import logoImage from '~/assets/images/map-logo-only.jpg'
import type { TableCell } from 'pdfmake'
import type { InvoiceDetailsData, InvoiceDetails } from '~/types/finance'

const pdfLink = ref<string | null>(null)
const route = useRoute()
const invoiceId = route.params.id
const { user } = useAuth()
const { get } = useApi()

const { data: invoiceDetails, pending } = await useAsyncData(
  'invoice-details',
  async () => {
    const res = await get<InvoiceDetails>(`/invoices/${invoiceId}`)
    return res
  }
)
const details: InvoiceDetailsData = invoiceDetails.value?.details as InvoiceDetailsData

const letterIds = ref(
  details?.customerPurchaseInformation?.deliveryOrderNumberData
)

const formattedLetterIds = computed(() => {
  if (!letterIds.value?.length) return ''

  if (letterIds.value.length === 1) return letterIds.value[0]

  const suffix = letterIds.value[0].substring(letterIds.value[0].indexOf('/'))
  const numbers = letterIds.value.map((id: string) => id.split('/')[0])

  return numbers.join(',') + suffix
})

const tableBodyDetails: TableCell[][] = []

for (let i = 0; i < 6; i++) {
  const product = details?.products[i]
  if (product) {
    tableBodyDetails.push([
      {
        text: (i + 1).toString(),
        alignment: 'center',
        border: [true, false, true, true]
      },
      {
        text: formatNumber(product.qty || 0),
        alignment: 'center',
        border: [true, false, true, true]
      },
      {
        text: product.unit || '',
        alignment: 'center',
        border: [true, false, true, true]
      },
      {
        text: product.name || '',
        alignment: 'left',
        border: [true, false, true, true]
      },
      {
        text: formatNumber(product.price || 0),
        alignment: 'center',
        border: [true, false, true, true]
      },
      {
        text: formatNumber(product.totalPrice || 0),
        alignment: 'center',
        border: [true, false, true, true]
      }
    ])
  } else {
    tableBodyDetails.push([
      { text: '', border: [true, false, true, true] },
      { text: '', border: [true, false, true, true] },
      { text: '', border: [true, false, true, true] },
      { text: '', border: [true, false, true, true] },
      { text: '', border: [true, false, true, true] },
      { text: '', border: [true, false, true, true] }
    ])
  }
}

const loadPdf = async () => {
  const pdfMake = usePDFMake()
  if (!pdfMake) return

  pdfLink.value = await pdfMake
    .createPdf({
      info: {
        title: `Invoice (${details.invoiceInformation.invoiceNumber}) | ${details.customerPurchaseInformation.customerPurchaseOrderNumber.customerName}`,
        author: 'PT. Mitra Andalan Petroleum',
        creator: user.value?.name,
        producer: 'PT. Mitra Andalan Petroleum'
      },
      pageMargins: [24, 15, 24, 15],
      pageSize: 'A4',
      content: [
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
            widths: ['15%', 'auto', 'auto'],
            body: [
              [
                {
                  image: await toBase64(logoImage),
                  width: 40,
                  alignment: 'center',
                  rowSpan: 4
                },
                {
                  text: `${details.companyInformation.name}`,
                  style: {
                    bold: true,
                    fontSize: 20,
                    color: '#14469b'
                  },
                  colSpan: 2
                },
                {}
              ],
              [
                {},
                {
                  text: 'Your Trusted Partner',
                  style: {
                    bold: true,
                    italics: true,
                    fontSize: 14,
                    color: '#ff0000'
                  },
                  colSpan: 2
                },
                {}
              ],
              [
                {},
                {
                  text: `${details.companyInformation.address}`,
                  colSpan: 2,
                  fontSize: 8
                },
                {}
              ],
              [
                {},
                {
                  text: `${details.companyInformation.phoneNumber}`,
                  bold: true,
                  italics: true,
                  fontSize: 8
                },
                {
                  text: `Email: ${details.companyInformation.email}`,
                  bold: true,
                  italics: true,
                  marginRight: 60,
                  fontSize: 8
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
            paddingBottom: function (i) {
              return [0, 1].includes(i) ? 0 : 2
            },
            paddingTop: function (i) {
              return [0, 1].includes(i) ? 0 : 2
            },
            fillColor: function (i) {
              return [0, 2].includes(i) ? '#1d82d1' : null
            }
          },
          table: {
            widths: ['*', '*'],
            body: [
              [
                {
                  text: '',
                  colSpan: 2
                },
                {}
              ],
              [
                {
                  text: 'INVOICE',
                  style: {
                    bold: true,
                    fontSize: 18,
                    alignment: 'center'
                  },
                  border: [false, true, false, true],
                  colSpan: 2
                },
                {}
              ],
              [
                {
                  text: 'Bill To',
                  color: '#fff',
                  bold: true
                },
                {
                  text: 'Delivery Point',
                  color: '#fff',
                  bold: true
                }
              ],
              [
                {
                  text: `${details.billToInformation}`,
                  bold: true,
                  lineHeight: 1.25
                },
                {
                  text: `${details.deliveryPointInformation}`,
                  bold: true,
                  lineHeight: 1.25
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
            widths: ['*', '*', '*', '*'],
            body: [
              [
                {
                  text: 'Invoice No.',
                  bold: true,
                  alignment: 'center',
                  border: [true, false, true, true]
                },
                {
                  text: 'Invoice Date',
                  bold: true,
                  alignment: 'center',
                  border: [true, false, true, true]
                },
                {
                  text: 'No. Delivery Order',
                  bold: true,
                  alignment: 'center',
                  border: [true, false, true, true]
                },
                {
                  text: 'Customer Purchase Order No',
                  bold: true,
                  alignment: 'center',
                  border: [true, false, true, true]
                }
              ],
              [
                {
                  text: `${details.invoiceInformation.invoiceNumber}`,
                  verticalAlignment: 'middle',
                  alignment: 'center'
                },
                {
                  text: formatDate(details.invoiceInformation.invoiceDate),
                  verticalAlignment: 'middle',
                  alignment: 'center'
                },
                {
                  // map into string like this
                  text: `${formattedLetterIds.value}`,

                  verticalAlignment: 'middle',
                  alignment: 'center'
                },
                {
                  text: `${details.customerPurchaseInformation.customerPurchaseOrderNumber.purchaseOrderNumber}`,
                  verticalAlignment: 'middle',
                  alignment: 'center'
                }
              ],
              [
                {
                  text: 'Terms',
                  bold: true,
                  alignment: 'center'
                },
                {
                  text: 'Due Date',
                  bold: true,
                  alignment: 'center'
                },
                {
                  text: 'Tax No (Faktur Pajak)',
                  bold: true,
                  alignment: 'center'
                },
                {
                  text: 'Sales Order No',
                  bold: true,
                  alignment: 'center'
                }
              ],
              [
                {
                  text: `${details.invoiceInformation.terms} ${details.invoiceInformation.terms === 1 ? 'Day' : 'Days'} After Delivery`,
                  verticalAlignment: 'middle',
                  alignment: 'center'
                },
                {
                  text: formatDate(details.invoiceInformation.invoiceDueDate),
                  verticalAlignment: 'middle',
                  alignment: 'center'
                },
                {
                  text: `${details.customerPurchaseInformation.taxInvoiceNumber}`,

                  verticalAlignment: 'middle',
                  alignment: 'center'
                },
                {
                  text: `${details.customerPurchaseInformation.salesOrderNumber || ''}`,
                  verticalAlignment: 'middle',
                  alignment: 'center'
                }
              ]
            ]
          }
        },
        {
          marginTop: 10,
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
            widths: ['6%', '*', '*', '40%', '*', '*'],
            body: [
              [
                {
                  text: 'ITEM',
                  bold: true,
                  alignment: 'center',
                  verticalAlignment: 'middle',
                  rowSpan: 2
                },
                {
                  text: 'QUANTITY',
                  bold: true,
                  alignment: 'center',
                  verticalAlignment: 'middle',

                  colSpan: 2
                },
                {},
                {
                  text: 'DESCRIPTION',
                  bold: true,
                  alignment: 'center',
                  verticalAlignment: 'middle',

                  rowSpan: 2
                },
                {
                  text: 'PRICE (IDR)',
                  bold: true,
                  alignment: 'center',
                  verticalAlignment: 'middle',

                  colSpan: 2
                },
                {}
              ],
              [
                {},
                {
                  text: 'QTY',
                  bold: true,
                  alignment: 'center',
                  verticalAlignment: 'middle'
                },
                {
                  text: 'UNIT',
                  bold: true,
                  alignment: 'center',
                  verticalAlignment: 'middle'
                },
                {},
                {
                  text: 'UNIT',
                  bold: true,
                  alignment: 'center',
                  verticalAlignment: 'middle'
                },
                {
                  text: 'TOTAL',
                  bold: true,
                  alignment: 'center',
                  verticalAlignment: 'middle'
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
            },
            hLineWidth: function () {
              return 0
            }
          },
          table: {
            widths: ['6%', '*', '*', '40%', '*', '*'],
            body: tableBodyDetails
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
            widths: ['6%', '*', '*', '40%', '*', '*'],
            body: [
              [
                {
                  text: useChangeCase(
                    angkaTerbilang(details.priceSummary.grandTotal),
                    'capitalCase'
                  ).value,
                  alignment: 'center',
                  colSpan: 4
                },
                {},
                {},
                {},
                {
                  text: 'Sub Total',
                  bold: true,
                  alignment: 'left'
                },
                {
                  text: `${formatNumber(details.priceSummary.subTotal || 0)}`,
                  alignment: 'right'
                }
              ],
              [
                {
                  text: '',
                  colSpan: 4,
                  border: [false, false, false, false]
                },
                {},
                {},
                {},
                {
                  text: 'Pre-Paid',
                  bold: true,
                  alignment: 'left'
                },
                {
                  text: `${formatNumber(details.priceSummary.prePaid || 0)}`,
                  alignment: 'right'
                }
              ],
              [
                {
                  text: '',
                  colSpan: 4,
                  border: [false, false, false, false]
                },
                {},
                {},
                {},
                {
                  text: 'Diskon',
                  bold: true,
                  alignment: 'left'
                },
                {
                  text: `${formatNumber(details.priceSummary.discount || 0)}`,
                  alignment: 'right'
                }
              ],
              [
                {
                  text: '',
                  colSpan: 4,
                  border: [false, false, false, false]
                },
                {},
                {},
                {},
                {
                  text: 'PPn',
                  bold: true,
                  alignment: 'left'
                },
                {
                  text: `${formatNumber(details.priceSummary.ppn || 0)}`,
                  alignment: 'right'
                }
              ],
              [
                {
                  text: 'Term and Conditions:',
                  bold: true,
                  colSpan: 4,
                  border: [false, false, false, false]
                },
                {},
                {},
                {},
                {
                  text: 'Grand Total',
                  bold: true,
                  alignment: 'left'
                },
                {
                  text: `${formatNumber(details.priceSummary.grandTotal || 0)}`,
                  bold: true,
                  alignment: 'right'
                }
              ]
            ]
          }
        },
        {
          marginLeft: 5,
          layout: {
            defaultBorder: false,
            paddingRight: function () {
              return 1
            },
            paddingLeft: function () {
              return 1
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
            widths: ['5%', '25%', '1%', '55%'],
            body: [
              [
                {
                  text: '1.',
                  alignment: 'center'
                },
                {
                  text: 'All check payable to',
                  colSpan: 3
                },
                {},
                {}
              ],
              [
                {
                  text: ''
                },
                {
                  text: 'Bank Name',
                  bold: true
                },
                {
                  text: ':',
                  bold: true
                },
                {
                  text: `${details.paymentInformation.bankName}`,
                  bold: true
                }
              ],
              [
                {
                  text: ''
                },
                {
                  text: 'Bank Account No',
                  bold: true
                },
                {
                  text: ':',
                  bold: true
                },
                {
                  text: `${details.paymentInformation.accountNumber}`,
                  bold: true
                }
              ],
              [
                {
                  text: ''
                },
                {
                  text: 'Acct Name',
                  bold: true
                },
                {
                  text: ':',
                  bold: true
                },
                {
                  text: `${details.paymentInformation.accountName}`,
                  bold: true
                }
              ],
              [
                {
                  text: '2.',
                  alignment: 'center'
                },
                {
                  text: 'If payment has no been received by the stated date of payment, penalty of 2% interest per month will be imposed',
                  colSpan: 3
                },
                {},
                {}
              ],
              [
                {
                  text: '3.',
                  alignment: 'center'
                },
                {
                  text: 'Seller has the right to refuse / decline delivery if payment terms has not been met, and shall not be held responsible for any direct or indirect consequences arising thereafter',
                  colSpan: 3
                },
                {},
                {}
              ],
              [
                {
                  text: '4.',
                  alignment: 'center'
                },
                {
                  text: 'Goods sold are not refundable',
                  colSpan: 3
                },
                {},
                {}
              ],
              [
                {
                  text: '5.',
                  alignment: 'center'
                },
                {
                  text: 'Invoice will be considered PAID once seller has received full amount on the stated account',
                  colSpan: 3
                },
                {},
                {}
              ],
              [
                {
                  text: '6.',
                  alignment: 'center'
                },
                {
                  text: `MAP Contact Number Fin & Acct Officer : ${details.companyInformation.phoneNumber || '-'}`,
                  colSpan: 3
                },
                {},
                {}
              ]
            ]
          }
        },
        {
          text: `${details.signature.companyName}`,
          bold: true,
          marginTop: 15,
          marginBottom: 30
        },
        {
          marginTop: 30,
          text: `${details.signature.createdBy}`,
          bold: true,
          decoration: 'underline'
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
