import logoImage from '~/assets/images/map-logo.jpeg'
import type { Content } from 'pdfmake/interfaces'
import type { OfferingLetterDetails } from '~/types/marketing'

/**
 * Bangun PDF Surat Penawaran dari data details + nama customer.
 * Dipakai oleh halaman detail (surat) maupun preview sebelum simpan.
 */
export function useOfferingLetterPdf() {
  const { user } = useAuth()

  function buildSignatureBarcodeData(name: string): string {
    return generateBarcodeDataUrl(name)
  }

  async function buildOfferingLetterPdf(
    details: OfferingLetterDetails,
    customerName: string,
    extra?: {
      signatureBarcode?: string
      signatureCaption?: string
    }
  ): Promise<string | null> {
    const pdfMake = usePDFMake()
    if (!pdfMake || import.meta.server) return null

    const signatureCaption = extra?.signatureCaption || details?.offeror?.name || user.value?.name || ''
    const signatureBarcode = extra?.signatureBarcode || buildSignatureBarcodeData(details?.offeror?.name || user.value?.name || '')

    const signatureBlock: Content[] = signatureBarcode
      ? [
          {
            image: signatureBarcode,
            width: 40,
            alignment: 'center',
            marginTop: 8
          },
          {
            text: `(${signatureCaption})`,
            bold: true,
            marginTop: 0,
            alignment: 'center'
          }
        ]
      : [
          {
            text: `(${details?.offeror.name})`,
            bold: true,
            marginTop: 30
          }
        ]

    const paymentMethodLabel = (() => {
      const method = details.paymentMethod
      const cashMethod = details.cashMethod
      const term = details.paymentTerm || ''
      if (method === 'cash') {
        const cashLabel = cashMethod === 'cash_before_delivery' ? 'Tunai Sebelum Pengiriman' : 'Tunai Setelah Pengiriman'
        return `${cashLabel} — ${term}`
      }
      return `Kredit — ${term}`
    })()

    const baseWithPpkb = details.fuelPrices.basePrice + details.fuelPrices.sellingPrice.ppkb
    const pphAmount = details.fuelPrices.sellingPrice.pph || 0

    return await pdfMake
      .createPdf({
        info: {
          title: `Surat Penawaran (${details?.offeringLetterNumber}) | ${customerName}`,
          author: 'PT. Mitra Andalan Petroleum',
          creator: user.value?.name,
          producer: 'PT. Mitra Andalan Petroleum'
        },
        pageSize: 'A4',
        pageMargins: [72, 10, 72, 10],
        content: [
          {
            image: await toBase64(logoImage),
            width: 160
          },
          {
            text: details
              ? `${details.location.split(',')[0]!.trim()}, ${formatDateDoc(details.date || new Date())}`
              : formatDateDoc(new Date()),
            alignment: 'right',
            marginTop: 10,
            marginBottom: 15
          },
          {
            layout: 'noBorders',
            table: {
              widths: ['auto', 'auto', '*'],
              body: [
                [
                  { text: 'Perihal' },
                  { text: ':' },
                  {
                    text: [`${details?.regarding}`],
                    decoration: 'underline'
                  }
                ],
                [
                  { text: 'Nomor' },
                  { text: ':' },
                  { text: `${details?.offeringLetterNumber}` }
                ]
              ]
            }
          },
          {
            text: [
              'Kepada Yth.\n',
              { text: `${customerName}`.toUpperCase(), bold: true }
            ],
            marginTop: 15
          },
          {
            text: 'Dengan Hormat,',
            marginTop: 15
          },
          {
            text: 'Berikut ini kami sampaikan penawaran Bahan Bakar Minyak Bio diesel dengan perincian sebagai berikut:',
            marginTop: 15,
            marginBottom: 5
          },
          {
            layout: {
              defaultBorder: false,
              paddingLeft: function (i) {
                return i === 3 ? -2 : 0
              },
              paddingBottom: function () {
                return 1
              },
              paddingTop: function () {
                return 1
              }
            },
            table: {
              widths: ['auto', 'auto', 'auto', '*'],
              body: [
                [
                  { text: '1.' },
                  { text: 'Supply Point' },
                  { text: ':' },
                  { text: `${details?.supplyPoint}` }
                ],
                [
                  { text: '2.' },
                  { text: 'Jaminan Kualitas' },
                  { text: ':' },
                  { text: `${details?.qualityAssurance}` }
                ],
                [
                  { text: '3.' },
                  { text: 'Serah Terima' },
                  { text: ':' },
                  { text: `${details?.custodyTransfer}` }
                ],
                [
                  { text: '4.' },
                  { text: 'Prosedur Bongkar' },
                  { text: ':' },
                  { text: `${details?.unloadingProcedure}` }
                ],
                [
                  { text: '5.' },
                  { text: 'Satuan Volume' },
                  { text: ':' },
                  { text: `${details?.volumeUnit}` }
                ],
                [
                  { text: '6.' },
                  { text: 'Toleransi Volume' },
                  { text: ':' },
                  { text: formatPercent(details?.volumeTolerance || 0) }
                ],
                [
                  { text: '7.' },
                  { text: 'Metode & Term Pembayaran' },
                  { text: ':' },
                  { text: `${paymentMethodLabel}` }
                ],
                [
                  { text: '8.' },
                  { text: 'Penalty Keterlambatan' },
                  { text: ':' },
                  { text: `${formatPercent(details?.latePenalty || 0)} per bulan` }
                ],
                [
                  { text: '9.' },
                  { text: 'Pola Pelayanan' },
                  { text: ':' },
                  { text: `${details?.servicePattern}` }
                ],
                [
                  { text: '10.' },
                  { text: 'Penanggung Jawab' },
                  { text: ':' },
                  { text: `${details?.personInCharge.name} - ${details?.personInCharge.phoneNumber}` }
                ],
                [
                  { text: '11.' },
                  { text: 'Rekening Pembayaran' },
                  { text: ':' },
                  { text: '' }
                ],
                [
                  {
                    text: `${details?.paymentAddress.bankName}\nNo Rek: ${details?.paymentAddress.accountNumber}\nA/N. ${details?.paymentAddress.accountName}`,
                    bold: true,
                    colSpan: 4,
                    alignment: 'center',
                    marginBottom: 5
                  }
                ],
                [
                  {
                    text: '12.'
                  },
                  {
                    text: 'Harga Bahan Bakar Minyak:',
                    colSpan: 3,
                    marginBottom: 5
                  }
                ]
              ]
            }
          },
          {
            layout: {
              paddingTop: function (i) {
                return i === 0 ? 5 : 2
              },
              paddingBottom: function (i) {
                return i === 0 ? 10 : 2
              },
              paddingLeft: function (i) {
                return i === 0 ? 15 : 5
              }
            },
            marginLeft: 15,
            table: {
              widths: ['*', '*', '*'],
              headerRows: 1,
              body: [
                [
                  { text: 'KETERANGAN', style: { bold: true } },
                  { text: 'KET', style: { alignment: 'center', bold: true } },
                  {
                    text: `${details?.fuelPrices.logisticInformation}`,
                    style: { alignment: 'center', bold: true }
                  }
                ],
                [
                  { text: 'PRODUK', style: { bold: true } },
                  { text: '' },
                  {
                    text: `${details?.fuelPrices.productName}`,
                    style: { alignment: 'center' }
                  }
                ],
                [
                  { text: 'HARGA JUAL', style: { bold: true } },
                  { text: 'PPKB Include', style: { alignment: 'center' } },
                  {
                    text: formatCurrency(baseWithPpkb),
                    style: { alignment: 'center' }
                  }
                ],
                [
                  { text: '', style: { bold: true } },
                  { text: 'OAT', style: { alignment: 'center' } },
                  {
                    text: formatCurrency(details?.fuelPrices.sellingPrice.oat || 0),
                    style: { alignment: 'center' }
                  }
                ],
                [
                  { text: 'PPN (11%)', style: { bold: true } },
                  { text: 'HARGA JUAL & ONGKOS ANGKUT', style: { alignment: 'center' } },
                  {
                    text: formatCurrency(details?.fuelPrices.sellingPrice.ppn || 0),
                    style: { alignment: 'center' }
                  }
                ],
                ...(pphAmount > 0
                  ? ([
                      { text: 'PPH', style: { bold: true } },
                      { text: 'PPH (final)', style: { alignment: 'center' } },
                      {
                        text: formatCurrency(pphAmount),
                        style: { alignment: 'center' }
                      }
                    ] as Content[])
                  : []),
                [
                  {
                    text: 'TOTAL',
                    style: { bold: true, alignment: 'center' },
                    colSpan: 2
                  },
                  {},
                  {
                    text: formatCurrency(details?.fuelPrices.totalPrice || 0),
                    style: { alignment: 'center', bold: true }
                  }
                ]
              ]
            }
          },
          {
            marginTop: 10,
            marginLeft: 15,
            columns: [
              { text: '***', width: 'auto', marginRight: 3, bold: true },
              {
                text: 'Harga sewaktu-waktu dapat berubah mengikuti harga keekonomian Pertamina'
              }
            ]
          },
          {
            marginTop: 1,
            marginLeft: 15,
            columns: [
              { text: '***', width: 'auto', marginRight: 3, bold: true },
              {
                text: 'Stock BBM sewaktu-waktu dapat berubah mengikuti posisi stock BBM di depo terdekat'
              }
            ]
          },
          {
            marginTop: 1,
            marginLeft: 15,
            columns: [
              { text: '***', width: 'auto', marginRight: 3, bold: true },
              { text: 'B50 / B40 jika stok masih tersedia' }
            ]
          },
          ...(details?.informasiTambahan?.filter(Boolean) || []).map(
            informasi => ({
              marginTop: 1,
              marginLeft: 15,
              columns: [
                { text: '***', width: 'auto', marginRight: 3, bold: true },
                { text: informasi }
              ]
            })
          ),
          {
            text: [
              'Mohon Purchase Order dapat dikirimkan pada periode ',
              {
                text: `${details?.purchaseOrderDeadline || '1 - 14'} `,
                bold: true
              },
              'hari sebelum pengaliran/muat dari terminal.'
            ],
            marginTop: 15
          },
          {
            text: 'Demikian surat penawaran ini kami sampaikan, kami ucapkan terimakasih.'
          },
          {
            text: 'Hormat Kami,',
            marginTop: 15,
            marginBottom: signatureBarcode ? 5 : 30
          },
          ...signatureBlock,
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
            marginLeft: 320,
            table: {
              widths: ['auto', 'auto', 'auto'],
              body: [
                [
                  { text: 'Alamat' },
                  { text: ':' },
                  { text: `${details?.companyInformation.address}` }
                ],
                [
                  { text: 'Telepon' },
                  { text: ':' },
                  { text: `${details?.companyInformation.phoneNumber}` }
                ],
                [
                  { text: 'Email' },
                  { text: ':' },
                  { text: `${details?.companyInformation.email}` }
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

  return { buildOfferingLetterPdf }
}
