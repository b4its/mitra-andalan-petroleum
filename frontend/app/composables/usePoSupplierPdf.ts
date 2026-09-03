import type { TableCell } from "pdfmake";
import type { Details, PaymentAddress, Product } from "~/types/marketing";

/**
 * Bangun PDF Purchase Order Supplier dari data details.
 * Dipakai oleh halaman detail (surat) maupun preview sebelum simpan.
 */
export function usePoSupplierPdf() {
  const { user } = useAuth();

  async function buildPoSupplierPdf(
    details: Details,
    meta: {
      supplierName: string;
      poNumber: string;
    },
  ): Promise<string | null> {
    const pdfMake = usePDFMake();
    if (!pdfMake || import.meta.server) return null;

    const products: Product[] = details.products || [];
    const paymentAddress: PaymentAddress = details.paymentAddress || {};

    const tableBodyDetails: TableCell[][] = [
      [
        {
          text: "No",
          bold: true,
          alignment: "center",
          border: [true, false, true, true],
        },
        {
          text: "Product",
          bold: true,
          alignment: "center",
          border: [true, false, true, true],
        },
        {
          text: "Qty",
          bold: true,
          alignment: "center",
          border: [true, false, true, true],
        },
        {
          text: "Unit",
          bold: true,
          alignment: "center",
          border: [true, false, true, true],
        },
        {
          text: "Unit Price",
          bold: true,
          alignment: "center",
          border: [true, false, true, true],
        },
        {
          text: "Total",
          bold: true,
          alignment: "center",
          border: [true, false, true, true],
        },
      ],
    ];

    for (let i = 0; i < 8; i++) {
      if (i < products.length) {
        const product = products[i] as Product;
        tableBodyDetails.push([
          {
            text: (i + 1).toString(),
            alignment: "center",
            border: [true, false, true, true],
          },
          {
            text:
              product.name +
              (product.ppkb || product.pph || product.ppn
                ? `\nPPKB: ${formatCurrency(product.ppkb || 0)} | PPH: ${formatPercent(product.pph || 0)} | PPN: ${formatCurrency(product.ppn || 0)}`
                : ""),
            alignment: "left",
            border: [true, false, true, true],
          },
          {
            text: formatNumber(product.qty || 0),
            alignment: "center",
            border: [true, false, true, true],
          },
          {
            text: product.unit || "",
            alignment: "center",
            border: [true, false, true, true],
          },
          {
            text: formatCurrency(product.price || 0),
            alignment: "center",
            border: [true, false, true, true],
          },
          {
            text: formatCurrency(product?.totalPrice || 0),
            alignment: "right",
            border: [true, false, true, true],
          },
        ]);
      } else {
        tableBodyDetails.push([
          { text: "", border: [true, false, true, true] },
          { text: "", border: [true, false, true, true] },
          { text: "", border: [true, false, true, true] },
          { text: "", border: [true, false, true, true] },
          { text: "", border: [true, false, true, true] },
          { text: "", border: [true, false, true, true] },
        ]);
      }
    }

    tableBodyDetails.push([{}, {}, {}, {}, {}, {}]);
    tableBodyDetails.push([
      {},
      {
        text: `Include VAT ${formatPercent(details.vat || 0)}`,
        bold: true,
        italics: true,
      },
      {},
      {},
      {},
      {},
    ]);
    tableBodyDetails.push([{}, {}, {}, {}, {}, {}]);
    tableBodyDetails.push([
      {},
      { text: "Transfer Detail :", bold: true, italics: true },
      {},
      {},
      {},
      {},
    ]);
    tableBodyDetails.push([
      {},
      { text: paymentAddress.bankName || "", bold: true },
      {},
      {},
      {},
      {},
    ]);
    tableBodyDetails.push([
      {},
      { text: paymentAddress.accountName || "", bold: true },
      {},
      {},
      {},
      {},
    ]);
    tableBodyDetails.push([
      {},
      {
        text: paymentAddress.accountNumber
          ? `No. Rek. ${paymentAddress.accountNumber}`
          : "No. Rek. ",
        bold: true,
      },
      {},
      {},
      {},
      {},
    ]);
    tableBodyDetails.push([{}, {}, {}, {}, {}, {}]);
    tableBodyDetails.push([
      { text: "Subtotal", colSpan: 5, bold: true, alignment: "right" },
      {},
      {},
      {},
      {},
      {
        text: formatCurrency(details.totalProductsPrice || 0),
        alignment: "right",
        bold: true,
      },
    ]);

    return await pdfMake
      .createPdf({
        info: {
          title: `Purchase Order (${meta.poNumber}) | ${meta.supplierName}`,
          author: "PT. Mitra Andalan Petroleum",
          creator: user.value?.name,
          producer: "PT. Mitra Andalan Petroleum",
        },
        pageMargins: [24, 24, 24, 24],
        pageSize: "A4",
        content: [
          {
            layout: {
              paddingLeft: function () {
                return 2;
              },
              paddingBottom: function (i) {
                return i === 1 ? 10 : 0;
              },
              paddingTop: function () {
                return 2;
              },
              fillColor: function (i) {
                return i === 0 ? "#e5e5e5" : null;
              },
            },
            table: {
              widths: ["*", "*"],
              body: [
                [{ text: "To", colSpan: 2, bold: true }, {}],
                [
                  {
                    text: [
                      {
                        text: `${meta.supplierName}\n`,
                        bold: true,
                      },
                      `${details.receiver.address || ""}\n`,
                    ],
                  },
                  {
                    text: [
                      {
                        text: `${details.companyInformation.name || ""}\n`,
                        bold: true,
                      },
                      `${details.companyInformation.address || ""}\n`,
                      `Phone: ${details.companyInformation.contactPerson || ""}\n`,
                      `Email: ${details.companyInformation.email || ""}\n`,
                      `NPWP: ${details.companyInformation.npwp || ""}\n`,
                    ],
                  },
                ],
              ],
            },
          },
          {
            layout: {
              paddingRight: function () {
                return 1;
              },
              paddingLeft: function () {
                return 1;
              },
              paddingBottom: function () {
                return 1;
              },
              paddingTop: function () {
                return 1;
              },
            },
            table: {
              widths: ["auto", "*", "auto", "auto", "auto", 118],
              body: [
                [
                  {
                    text: "PURCHASE ORDER",
                    colSpan: 5,
                    rowSpan: 3,
                    bold: true,
                    alignment: "center",
                    verticalAlignment: "middle",
                    border: [true, false, true, true],
                  },
                  {},
                  {},
                  {},
                  {},
                  {
                    text: `PO Date : ${details.po.date}`,
                    bold: true,
                    border: [true, false, true, true],
                  },
                ],
                [
                  {},
                  {},
                  {},
                  {},
                  {},
                  {
                    text: `PO Number : \n${details.po.number}`,
                    bold: true,
                    border: [true, false, true, true],
                  },
                ],
                [{}, {}, {}, {}, {}, {}],
              ],
            },
          },
          {
            layout: {
              paddingRight: function () {
                return 10;
              },
              paddingLeft: function () {
                return 10;
              },
              paddingBottom: function () {
                return 1;
              },
              paddingTop: function () {
                return 1;
              },
              fillColor: function (i) {
                return i === 0 ? "#e5e5e5" : null;
              },
            },
            table: {
              widths: ["auto", "*", "auto", "auto", "auto", 100],
              body: tableBodyDetails,
            },
          },
          {
            layout: {
              paddingRight: function () {
                return 2;
              },
              paddingLeft: function () {
                return 2;
              },
              paddingBottom: function () {
                return 2;
              },
              paddingTop: function () {
                return 2;
              },
              fillColor: function (i) {
                return [0, 2].includes(i) ? "#e5e5e5" : null;
              },
            },
            table: {
              widths: ["*", "*"],
              body: [
                [
                  {
                    text: "Term & Condition",
                    bold: true,
                    border: [true, false, true, true],
                  },
                  {
                    text: "Details",
                    bold: true,
                    border: [true, false, true, true],
                  },
                ],
                [
                  {
                    text: `${details.termAndCondition}`,
                    border: [true, false, true, true],
                  },
                  {},
                ],
                [
                  {
                    text: "Delivery",
                    bold: true,
                    border: [true, false, true, true],
                  },
                  {
                    text: "Forwarder",
                    bold: true,
                    border: [true, false, true, true],
                  },
                ],
                [
                  {
                    text: `Distance KM : ${formatToKm(Number(details.delivery?.distance) || 0)}\nLoading Terminal : ${details.delivery?.loadingTerminal || ""}\nLoading Date : ${details.delivery?.loadingDate || ""}\nPIC OPERATION MAP : ${details.delivery?.picOperationMap || ""}`,
                    border: [true, false, true, true],
                  },
                  {
                    text: `Trucking : ${details.forwarder?.trucking}`,
                  },
                ],
              ],
            },
          },
          {
            layout: {
              paddingRight: function () {
                return 2;
              },
              paddingLeft: function () {
                return 15;
              },
              paddingBottom: function () {
                return 15;
              },
              paddingTop: function () {
                return 2;
              },
            },
            table: {
              widths: ["*", "*"],
              body: [
                [
                  {
                    stack: [
                      {
                        text: "Create By",
                        bold: true,
                      },
                      {
                        text: `\n\n\n\n(${details.signed.createdBy || ""})`,
                      },
                    ],
                    border: [true, false, false, true],
                  },
                  {
                    stack: [
                      {
                        text: "Approved By",
                        bold: true,
                      },
                      {
                        text: `\n\n\n\n(${details.signed.approvedBy || ""})`,
                      },
                    ],
                    border: [false, false, true, true],
                  },
                ],
              ],
            },
          },
        ],
        defaultStyle: {
          color: "#000000",
          fontSize: 9,
        },
      })
      .getDataUrl();
  }

  return { buildPoSupplierPdf };
}
