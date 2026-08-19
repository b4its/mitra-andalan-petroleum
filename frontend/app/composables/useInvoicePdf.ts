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

    const blue = '#1688d3'
    const borderColor = '#000000'
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
    const grandTotalInWords = `${useChangeCase(
      angkaTerbilang(details.priceSummary.grandTotal || 0),
      'capitalCase'
    ).value} Rupiah`
    const termText = `${details.invoiceInformation.terms} ${details.invoiceInformation.terms === 1 ? 'Day' : 'Days'} After Delivery`

    const lineLayout = {
      hLineColor: function () {
        return borderColor
      },
      vLineColor: function () {
        return borderColor
      },
      paddingRight: function () {
        return 2
      },
      paddingLeft: function () {
        return 2
      },
      paddingBottom: function () {
        return 1.5
      },
      paddingTop: function () {
        return 1.5
      }
    }

    const headerCell = (text: string): TableCell => ({
      text,
      bold: true,
      alignment: 'center',
      fillColor: blue,
      color: '#ffffff'
    })
    const infoHeaderCell = (text: string): TableCell => ({
      text,
      bold: true,
      alignment: 'center'
    })
    const infoValueCell = (text: string): TableCell => ({
      text,
      bold: true,
      alignment: 'center',
      verticalAlignment: 'middle',
      margin: [0, 13, 0, 13]
    })

    const tableBodyDetails: TableCell[][] = []

    for (let i = 0; i < Math.max(details.products.length, 3); i++) {
      const product = details?.products[i]
      tableBodyDetails.push([
        {
          text: product ? (i + 1).toString() : '',
          alignment: 'center',
          border: [true, false, true, false]
        },
        {
          text: product ? formatNumber(product.qty || 0) : '',
          alignment: 'center',
          border: [true, false, true, false]
        },
        {
          text: product?.unit || '',
          alignment: 'center',
          border: [true, false, true, false]
        },
        {
          text: product?.name || '',
          alignment: 'left',
          border: [true, false, true, false]
        },
        {
          text: product ? formatNumber(product.price || 0) : '',
          alignment: 'right',
          border: [true, false, true, false]
        },
        {
          text: product ? formatNumber(product.totalPrice || 0) : '',
          alignment: 'right',
          border: [true, false, true, false]
        }
      ])
    }

    return await pdfMake
      .createPdf({
        info: {
          title: `Invoice (${details.invoiceInformation.invoiceNumber}) | ${details.customerPurchaseInformation.customerPurchaseOrderNumber.customerName}`,
          author: 'PT. Mitra Andalan Petroleum',
          creator: user.value?.name,
          producer: 'PT. Mitra Andalan Petroleum'
        },
        pageMargins: [28, 12, 28, 18],
        pageSize: 'A4',
        content: [
          {
            layout: {
              defaultBorder: false,
              paddingRight: function () {
                return 1
              },
              paddingLeft: function () {
                return 1
              },
              paddingBottom: function () {
                return 0
              },
              paddingTop: function () {
                return 0
              }
            },
            table: {
              widths: [72, '*'],
              body: [
                [
                  {
                    image: await toBase64(logoImage),
                    width: 47,
                    alignment: 'center',
                    rowSpan: 4,
                    margin: [0, 2, 0, 0]
                  },
                  {
                    text: `${details.companyInformation.name}`,
                    bold: true,
                    fontSize: 19,
                    color: '#14469b',
                    margin: [0, 0, 0, 0]
                  }
                ],
                [
                  {},
                  {
                    text: 'Your Trusted Partner',
                    bold: true,
                    italics: true,
                    fontSize: 11,
                    color: '#e10600',
                    margin: [0, 0, 0, 1]
                  }
                ],
                [
                  {},
                  {
                    text: `${details.companyInformation.address}`,
                    fontSize: 7.5
                  }
                ],
                [
                  {},
                  {
                    columns: [
                      {
                        text: `Telp: ${details.companyInformation.phoneNumber}`,
                        bold: true,
                        italics: true,
                        fontSize: 7.5,
                        width: 145
                      },
                      {
                        text: `Email: ${details.companyInformation.email}`,
                        bold: true,
                        italics: true,
                        fontSize: 7.5,
                        width: '*'
                      }
                    ]
                  }
                ]
              ]
            }
          },
          {
            margin: [0, 4, 0, 0],
            table: {
              widths: ['*'],
              body: [[{ text: '', fillColor: blue, margin: [0, 2, 0, 2] }]]
            },
            layout: 'noBorders'
          },
          {
            text: 'INVOICE',
            bold: true,
            alignment: 'center',
            fontSize: 18,
            margin: [0, 0, 0, 0]
          },
          {
            layout: lineLayout,
            table: {
              widths: ['*', '*'],
              body: [
                [headerCell('Bill To'), headerCell('Delivery Point')],
                [
                  {
                    text: `${details.billToInformation}`,
                    bold: true,
                    lineHeight: 1.15,
                    margin: [0, 1, 0, 14]
                  },
                  {
                    text: `${details.deliveryPointInformation}`,
                    bold: true,
                    lineHeight: 1.15,
                    margin: [0, 1, 0, 14]
                  }
                ]
              ]
            }
          },
          {
            layout: lineLayout,
            table: {
              widths: ['26%', '20%', '30%', '24%'],
              body: [
                [
                  infoHeaderCell('Invoice No.'),
                  infoHeaderCell('Invoice Date'),
                  infoHeaderCell('No. DO'),
                  infoHeaderCell('Customer PO No')
                ],
                [
                  infoValueCell(`${details.invoiceInformation.invoiceNumber}`),
                  infoValueCell(formatDate(details.invoiceInformation.invoiceDate)),
                  {
                    ...infoValueCell(`${formattedLetterIds}`),
                    fontSize: 7.5,
                    margin: [0, 6, 0, 6]
                  },
                  infoValueCell(`${details.customerPurchaseInformation.customerPurchaseOrderNumber.purchaseOrderNumber}`)
                ],
                [
                  infoHeaderCell('Terms'),
                  infoHeaderCell('Due Date'),
                  infoHeaderCell('Tax No (Faktur Pajak)'),
                  infoHeaderCell('SO No')
                ],
                [
                  infoHeaderCell(termText),
                  infoHeaderCell(formatDate(details.invoiceInformation.invoiceDueDate)),
                  infoHeaderCell(`${details.customerPurchaseInformation.taxInvoiceNumber}`),
                  infoHeaderCell(`${details.customerPurchaseInformation.salesOrderNumber || ''}`)
                ]
              ]
            }
          },
          {
            margin: [0, 10, 0, 0],
            layout: lineLayout,
            table: {
              widths: ['6%', '9%', '12%', '45%', '14%', '14%'],
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
                    colSpan: 2
                  },
                  {}
                ],
                [
                  {},
                  { text: 'QTY', bold: true, alignment: 'center' },
                  { text: 'UNIT', bold: true, alignment: 'center' },
                  {},
                  { text: 'UNIT', bold: true, alignment: 'center' },
                  { text: 'TOTAL', bold: true, alignment: 'center' }
                ],
                ...tableBodyDetails,
                [
                  {
                    text: grandTotalInWords,
                    alignment: 'center',
                    colSpan: 4
                  },
                  {},
                  {},
                  {},
                  {
                    text: 'Sub Total',
                    bold: true
                  },
                  {
                    text: `${formatNumber(details.priceSummary.subTotal || 0)}`,
                    bold: true,
                    alignment: 'right'
                  }
                ],
                [
                  { text: '', colSpan: 4, border: [false, false, false, false] },
                  {},
                  {},
                  {},
                  { text: 'Pre-Paid', bold: true },
                  { text: `${formatNumber(details.priceSummary.prePaid || 0)}`, alignment: 'right' }
                ],
                [
                  { text: '', colSpan: 4, border: [false, false, false, false] },
                  {},
                  {},
                  {},
                  { text: 'Discount', bold: true },
                  { text: `${formatNumber(details.priceSummary.discount || 0)}`, alignment: 'right' }
                ],
                [
                  { text: '', colSpan: 4, border: [false, false, false, false] },
                  {},
                  {},
                  {},
                  { text: 'PPn', bold: true },
                  { text: `${formatNumber(details.priceSummary.ppn || 0)}`, alignment: 'right' }
                ],
                [
                  { text: '', colSpan: 4, border: [false, false, false, false] },
                  {},
                  {},
                  {},
                  { text: 'Grand Total', bold: true },
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
            text: 'Term and Conditions:',
            bold: true,
            margin: [2, 8, 0, 0],
            fontSize: 7.5
          },
          {
            margin: [2, 1, 0, 0],
            layout: {
              defaultBorder: false,
              paddingRight: function () {
                return 1
              },
              paddingLeft: function () {
                return 1
              },
              paddingBottom: function () {
                return 0.5
              },
              paddingTop: function () {
                return 0.5
              }
            },
            table: {
              widths: [16, 104, 5, '*'],
              body: [
                [
                  { text: '1.', alignment: 'center' },
                  { text: 'All check payable to', colSpan: 3 },
                  {},
                  {}
                ],
                [
                  { text: '' },
                  { text: 'Bank Name', bold: true },
                  { text: ':', bold: true },
                  { text: `${details.paymentInformation.bankName}`, bold: true }
                ],
                [
                  { text: '' },
                  { text: 'Bank Account No', bold: true },
                  { text: ':', bold: true },
                  { text: `${details.paymentInformation.accountNumber}`, bold: true }
                ],
                [
                  { text: '' },
                  { text: 'Acct Name', bold: true },
                  { text: ':', bold: true },
                  { text: `${details.paymentInformation.accountName}`, bold: true }
                ],
                [
                  { text: '2.', alignment: 'center' },
                  {
                    text: 'If payment has not been received by the stated date of payment, penalty of 2% interest per month will be imposed',
                    colSpan: 3
                  },
                  {},
                  {}
                ],
                [
                  { text: '3.', alignment: 'center' },
                  {
                    text: 'Seller has the right to refuse / decline delivery if payment terms has not been met, and shall not be held responsible for any direct or indirect consequences arising thereafter',
                    colSpan: 3
                  },
                  {},
                  {}
                ],
                [
                  { text: '4.', alignment: 'center' },
                  { text: 'Goods sold are not refundable', colSpan: 3 },
                  {},
                  {}
                ],
                [
                  { text: '5.', alignment: 'center' },
                  {
                    text: 'Invoice will be considered PAID once seller has received full amount on the stated account',
                    colSpan: 3
                  },
                  {},
                  {}
                ],
                [
                  { text: '6.', alignment: 'center' },
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
            margin: [0, 10, 0, 48],
            fontSize: 7.5
          },
          {
            text: `${details.signature.createdBy}`,
            bold: true,
            decoration: 'underline',
            fontSize: 7.5
          }
        ],
        defaultStyle: {
          color: '#000000',
          fontSize: 7
        }
      })
      .getDataUrl()
  }

  return { buildInvoicePdf }
}
