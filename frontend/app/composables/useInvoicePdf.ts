import angkaTerbilang from '@develoka/angka-terbilang-js'
import { useChangeCase } from '@vueuse/integrations/useChangeCase.js'
import logoImage from '~/assets/images/map-logo-only.jpg'
import type { TableCell } from 'pdfmake'
import type { InvoiceDetailsData } from '~/types/finance'

/**
 * Bangun PDF Invoice dari data details.
 * Dipakai oleh halaman detail (surat) maupun preview sebelum simpan.
 */
export function useInvoicePdf() {
  const { user } = useAuth()

  async function buildInvoicePdf(details: InvoiceDetailsData): Promise<string | null> {
    const pdfMake = usePDFMake()
    if (!pdfMake || import.meta.server) return null

    const letterIds = details?.customerPurchaseInformation?.deliveryOrderNumberData || []
    const formattedLetterIds = (() => {
      const ids = letterIds
      if (!ids?.length) return ''
      const first = ids[0]!
      if (ids.length === 1) return first
      const suffix = first.substring(first.indexOf('/'))
      const numbers = ids.map((id: string) => id.split('/')[0])
      return numbers.join(',') + suffix
    })()

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

    return await pdfMake
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
                    text: 'Ditagih Kepada',
                    color: '#fff',
                    bold: true
                  },
                  {
                    text: 'Titik Pengiriman',
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
              widths: ['*', '*', '*'],
              body: [
                [
                  {
                    text: 'No. Invoice',
                    bold: true,
                    alignment: 'center',
                    border: [true, false, true, true]
                  },
                  {
                    text: 'Tanggal Invoice',
                    bold: true,
                    alignment: 'center',
                    border: [true, false, true, true]
                  },
                  {
                    text: 'No. Delivery Order',
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
                    text: `${formattedLetterIds}`,
                    verticalAlignment: 'middle',
                    alignment: 'center'
                  }
                ],
                [
                  {
                    text: 'No. PO Customer',
                    bold: true,
                    alignment: 'center',
                    border: [true, false, true, true]
                  },
                  {
                    text: 'Syarat',
                    bold: true,
                    alignment: 'center'
                  },
                  {
                    text: 'Jatuh Tempo',
                    bold: true,
                    alignment: 'center'
                  }
                ],
                [
                  {
                    text: `${details.customerPurchaseInformation.customerPurchaseOrderNumber.purchaseOrderNumber}`,
                    verticalAlignment: 'middle',
                    alignment: 'center'
                  },
                  {
                    text: `${details.invoiceInformation.terms} ${details.invoiceInformation.terms === 1 ? 'Day' : 'Days'} After Delivery`,
                    verticalAlignment: 'middle',
                    alignment: 'center'
                  },
                  {
                    text: formatDate(details.invoiceInformation.invoiceDueDate),
                    verticalAlignment: 'middle',
                    alignment: 'center'
                  }
                ],
                [
                  {
                    text: 'Tax No (Faktur Pajak)',
                    bold: true,
                    alignment: 'center'
                  },
                  {},
                  {}
                ],
                [
                  {
                    text: `${details.customerPurchaseInformation.taxInvoiceNumber}`,
                    verticalAlignment: 'middle',
                    alignment: 'center',
                    colSpan: 3
                  },
                  {},
                  {}
                ]
              ]
            }
          },
          {
            marginTop: 10,
            layout: {
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
                    text: 'JUMLAH',
                    bold: true,
                    alignment: 'center',
                    verticalAlignment: 'middle',
                    colSpan: 2
                  },
                  {},
                  {
                    text: 'DESKRIPSI',
                    bold: true,
                    alignment: 'center',
                    verticalAlignment: 'middle',
                    rowSpan: 2
                  },
                  {
                    text: 'HARGA (IDR)',
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
                    text: 'JML',
                    bold: true,
                    alignment: 'center',
                    verticalAlignment: 'middle'
                  },
                  {
                    text: 'SATUAN',
                    bold: true,
                    alignment: 'center',
                    verticalAlignment: 'middle'
                  },
                  {},
                  {
                    text: 'SATUAN',
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
                  {
                    text: 'Subtotal',
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
                    text: 'Syarat dan Ketentuan:',
                    bold: true,
                    colSpan: 4,
                    border: [false, false, false, false]
                  },
                  {},
                  {},
                  {
                    text: 'Total Keseluruhan',
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
                    text: 'Semua cek dibayarkan kepada',
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
                    text: 'Nama Bank',
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
                    text: 'No. Rekening',
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
                    text: 'Nama Rekening',
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
                    text: 'Apabila pembayaran tidak diterima sampai tanggal jatuh tempo, dikenakan denda bunga 2% per bulan',
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
                    text: 'Penjual berhak menolak pengiriman apabila syarat pembayaran belum dipenuhi, dan tidak bertanggung jawab atas akibat langsung maupun tidak langsung yang timbul kemudian',
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
                    text: 'Barang yang sudah terjual tidak dapat dikembalikan',
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
                    text: 'Invoice dianggap LUNAS setelah penjual menerima jumlah penuh pada rekening tersebut',
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

  return { buildInvoicePdf }
}
