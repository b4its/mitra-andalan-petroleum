export interface ExportColumn {
  header: string
  accessor: (row: any) => string | number
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

export function useExport() {
  function buildRows(columns: ExportColumn[], rows: any[]) {
    return rows.map(row => columns.map(col => {
      const value = col.accessor(row)
      return value === null || value === undefined ? '' : value
    }))
  }

  function toCSV(filename: string, columns: ExportColumn[], rows: any[]) {
    const csv = [
      columns.map(col => `"${String(col.header).replace(/"/g, '""')}"`).join(';'),
      ...buildRows(columns, rows).map(line =>
        line.map(value => `"${String(value).replace(/"/g, '""')}"`).join(';')
      )
    ].join('\n')
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
    downloadBlob(blob, `${filename}.csv`)
  }

  async function toExcel(filename: string, sheetName: string, columns: ExportColumn[], rows: any[]) {
    const { utils, writeFile } = await import('xlsx')
    const sheet = utils.aoa_to_sheet([
      columns.map(col => col.header),
      ...buildRows(columns, rows)
    ])
    const workbook = utils.book_new()
    utils.book_append_sheet(workbook, sheet, sheetName)
    writeFile(workbook, `${filename}.xlsx`)
  }

  function toPDF(
    filename: string,
    title: string,
    columns: ExportColumn[],
    rows: any[],
    options?: { subtitle?: string, totals?: { label: string, value: string | number }[] }
  ) {
    const pdfMake = usePDFMake()
    if (!pdfMake) return

    const body: { text: string }[][] = [
      columns.map(col => ({
        text: col.header,
        style: 'tableHeader',
        bold: true,
        alignment: 'left'
      }))
    ]

    for (const row of buildRows(columns, rows)) {
      body.push(row.map(value => ({
        text: String(value),
        alignment: 'left'
      })))
    }

    const content: any[] = [
      {
        text: title,
        style: 'title'
      }
    ]
    if (options?.subtitle) {
      content.push({ text: options.subtitle, style: 'subtitle', margin: [0, 0, 0, 10] })
    }
    content.push({
      layout: {
        hLineWidth: (i: number) => (i === 0 || i === body.length ? 0.6 : 0.2),
        vLineWidth: () => 0,
        paddingLeft: () => 6,
        paddingRight: () => 6,
        paddingTop: () => 4,
        paddingBottom: () => 4
      },
      table: {
        headerRows: 1,
        widths: Array(columns.length).fill('*'),
        body
      }
    })

    if (options?.totals?.length) {
      for (const total of options.totals) {
        content.push({
          columns: [
            { text: '', width: '*' },
            {
              text: `${total.label}:`,
              style: 'total',
              width: 'auto',
              alignment: 'right'
            },
            {
              text: String(total.value),
              style: 'total',
              width: 'auto',
              alignment: 'right'
            }
          ],
          margin: [0, 6, 0, 0]
        })
      }
    }

    pdfMake.createPdf({
      info: {
        title,
        author: 'PT. Mitra Andalan Petroleum'
      },
      pageMargins: [32, 24, 32, 24],
      pageSize: 'A4',
      styles: {
        title: {
          fontSize: 14,
          bold: true
        },
        subtitle: {
          fontSize: 10,
          color: '#555555'
        },
        tableHeader: {
          fontSize: 9,
          bold: true,
          fillColor: '#f1f5f9'
        },
        total: {
          fontSize: 10,
          bold: true,
          margin: [0, 4, 0, 0]
        }
      },
      content
    }).download(`${filename}.pdf`)
  }

  return { toCSV, toExcel, toPDF }
}
