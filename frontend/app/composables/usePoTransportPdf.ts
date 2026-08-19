import type { TableCell } from 'pdfmake'
import logoImage from '~/assets/images/map-logo.jpeg'
import type { PoTransportirDetails } from '~/types/operations'

/**
 * Bangun PDF Purchase Order Transportir dari data details.
 * Dipakai oleh halaman detail (surat) maupun preview sebelum simpan.
 */
export function usePoTransportPdf() {
  const { user } = useAuth()

  async function buildPoTransportPdf(d: PoTransportirDetails): Promise<string | null> {
    const pdfMake = usePDFMake()
    if (!pdfMake || import.meta.server) return null

    const products = d.products || []
    const subTotal = products.reduce(
      (sum, p) => sum + (p.totalPrice || 0),
      0
    )
    const ppn = d.priceSummary?.ppn ?? Math.round(subTotal * (d.percentageNum?.ppn || 0.11))
    const grandTotal = d.priceSummary?.grandTotal ?? subTotal + ppn

    const tableBodyDetails: TableCell[][] = [
      [
        { text: 'NO', bold: true, verticalAlignment: 'middle', alignment: 'center' },
        { text: 'DESKRIPSI', bold: true, verticalAlignment: 'middle', alignment: 'center' },
        { text: 'Tanggal Loading', bold: true, verticalAlignment: 'middle', alignment: 'center' },
        { text: 'Tanggal Bongkar', bold: true, verticalAlignment: 'middle', alignment: 'center' },
        { text: 'VOL\n(LITER)', bold: true, verticalAlignment: 'middle', alignment: 'center' },
        { text: 'RATE/LITER\n(RP.)', bold: true, verticalAlignment: 'middle', alignment: 'center' },
        { text: 'TOTAL (Rp.)', bold: true, verticalAlignment: 'middle', alignment: 'center' }
      ]
    ]

    products.forEach((product, index) => {
      tableBodyDetails.push([
        { text: (index + 1).toString(), alignment: 'center' },
        { text: product.name || '', alignment: 'left' },
        { text: formatDateDoc(product.loadingDate) || '', alignment: 'center' },
        { text: formatDateDoc(product.unloadingDate) || '', alignment: 'center' },
        { text: product.qty || '', alignment: 'center' },
        { text: formatCurrency(product.ratePrice) || '', alignment: 'center' },
        { text: formatCurrency(product.totalPrice) || '', alignment: 'center' }
      ])
    })

    tableBodyDetails.push([
      { text: 'Total', bold: true, alignment: 'center', colSpan: 6 },
      {}, {}, {}, {}, {},
      { text: `${formatCurrency(subTotal)}`, alignment: 'center' }
    ])
    tableBodyDetails.push([
      { text: 'PPN', bold: true, alignment: 'center', colSpan: 6 },
      {}, {}, {}, {}, {},
      { text: `${formatCurrency(ppn)}`, alignment: 'center' }
    ])
    tableBodyDetails.push([
      { text: 'Total Keseluruhan', bold: true, alignment: 'center', colSpan: 6 },
      {}, {}, {}, {}, {},
      { text: `${formatCurrency(grandTotal)}`, alignment: 'center' }
    ])

    const companyContacts = d.contactPerson?.companyContactPerson || []
    const customerContacts = d.contactPerson?.customerContactPerson || []
    const rowCount = Math.max(companyContacts.length, customerContacts.length, 1)
    const contactRows: TableCell[][] = Array.from(
      { length: rowCount },
      (_, i) => [
        {
          text: companyContacts[i]
            ? `${i + 1}.   ${companyContacts[i]?.name}\n Telp: ${companyContacts[i]?.phoneNumber}`
            : '',
          border: [true, false, true,
            companyContacts.length > 1 && i === companyContacts.length - 1] as [boolean, boolean, boolean, boolean]
        },
        {
          text: customerContacts[i]
            ? `${i + 1}.   ${customerContacts[i]?.name}\n Telp: ${customerContacts[i]?.phoneNumber}`
            : '',
          border: [true, false, true,
            customerContacts.length > 1 && i === customerContacts.length - 1] as [boolean, boolean, boolean, boolean]
        }
      ]
    )

    return await pdfMake
      .createPdf({
        info: {
          title: `Purchase Order Transportir (${d.poTransportNumber || ''})`,
          author: 'PT. Mitra Andalan Petroleum',
          creator: user.value?.name,
          producer: 'PT. Mitra Andalan Petroleum'
        },
        pageMargins: [72, 10, 48, 10],
        pageSize: 'A4',
        content: [
          {
            image: await toBase64(logoImage),
            width: 160,
            marginLeft: -20
          },
          {
            text: `Samarinda, ${formatDateDoc(d.date || new Date())}`,
            alignment: 'right',
            marginRight: 35
          },
          {
            layout: {
              defaultBorder: false,
              paddingLeft: function (i) {
                return i === 2 ? -2 : 0
              },
              paddingTop: function (i) {
                return i === 0 ? 15 : 0
              }
            },
            table: {
              widths: ['auto', 'auto', '*'],
              body: [
                [
                  { text: 'Perihal', marginRight: 10 },
                  { text: ':' },
                  { text: d.regarding || 'Purchase Order Transportir (PO)' }
                ],
                [
                  { text: 'Nomor', marginRight: 10 },
                  { text: ':' },
                  { text: d.poTransportNumber || '' }
                ]
              ]
            }
          },
          {
            marginTop: 15,
            marginBottom: 2,
            text: 'Kepada Yth.'
          },
          {
            text: d.receiver || '',
            bold: true
          },
          {
            text: `PIC: ${d.picPerson || '-'}`,
            bold: true,
            marginTop: 15,
            marginBottom: 15
          },
          {
            text: 'Berikut ini kami kirimkan Purchase Order dengan detail sebagai berikut:',
            marginBottom: 15
          },
          {
            layout: {
              paddingLeft: function (_i) {
                return 5
              },
              paddingRight: function (_i) {
                return 5
              }
            },
            marginLeft: 5,
            table: {
              widths: ['auto', '*', '*', '*', 'auto', 'auto', '*'],
              body: tableBodyDetails
            }
          },
          {
            layout: {
              defaultBorder: false
            },
            marginTop: 10,
            table: {
              widths: ['auto', '25%', 'auto', '*'],
              body: [
                [
                  { text: '1.' },
                  { text: 'Pemuatan' },
                  { text: ':' },
                  { text: d.loadingInformation || '', marginLeft: -5 }
                ],
                [
                  { text: '2.' },
                  { text: 'Discharge' },
                  { text: ':' },
                  { text: d.discharge || '', bold: true, marginLeft: -5 }
                ],
                [
                  { text: '3.' },
                  { text: 'Syarat Pembayaran' },
                  { text: ':' },
                  { text: d.termsOfPayment || '', marginLeft: -5 }
                ],
                [
                  { text: '4.' },
                  { text: d.shrinkageTolerance || '', bold: true, colSpan: 3 },
                  {},
                  {}
                ],
                [
                  { text: '5.' },
                  { text: 'Kontak Person', colSpan: 3 },
                  {},
                  {}
                ]
              ]
            }
          },
          {
            layout: {
              paddingTop: function (i) {
                return i === 1 ? 10 : 0
              },
              paddingBottom: function (i, node) {
                return i === node.table.body.length - 1 ? 10 : 0
              }
            },
            marginTop: 10,
            table: {
              widths: ['35%', '35%'],
              body: [
                [
                  {
                    text: d.contactPerson?.companyName || '',
                    bold: true,
                    alignment: 'center'
                  },
                  {
                    text: d.contactPerson?.customerName || '',
                    bold: true,
                    alignment: 'center'
                  }
                ],
                ...contactRows
              ]
            }
          },
          {
            text: 'Hormat Kami,',
            marginTop: 25,
            marginBottom: logoImage ? 5 : 30
          },
          {
            text: `(${d.offeror?.name || '-'})`,
            marginTop: 30
          },
          {
            layout: {
              defaultBorder: false,
              paddingLeft: function (i) {
                return i === 2 ? -2 : 0
              },
              paddingTop: function () {
                return 0
              },
              paddingBottom: function () {
                return 0
              }
            },
            marginLeft: 290,
            marginTop: 75,
            table: {
              widths: ['auto', 'auto', 'auto'],
              body: [
                [
                  { text: 'Alamat' },
                  { text: ':' },
                  { text: `Jl Belatuk 63, Temindung Permai Samarinda, Indonesia` }
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

  return { buildPoTransportPdf }
}
