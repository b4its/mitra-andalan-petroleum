<script setup lang="ts">
import { faker } from "@faker-js/faker";

const pdfLink = ref<string | null>(null);
const route = useRoute();
const idOfferingLetter = route.params.id;

const loadPdf = async () => {
  const pdfMake = usePDFMake();
  if (!pdfMake) return;

  const lineItems = Array.from({ length: 6 }, () => {
    const qty = faker.number.int({ min: 1, max: 20 });
    const rate = faker.number.float({ min: 50, max: 500, fractionDigits: 2 });
    return {
      description: faker.commerce.productName(),
      category: faker.commerce.department(),
      qty,
      rate,
      amount: qty * rate,
    };
  });

  const subtotal = lineItems.reduce((sum, item) => sum + item.amount, 0);
  const tax = subtotal * 0.085;
  const total = subtotal + tax;

  const fmt = (n: number) =>
    n.toLocaleString("en-US", { style: "currency", currency: "USD" });

  const invoiceNumber = `INV-${faker.number.int({ min: 1000, max: 9999 })}`;
  const issueDate = new Date();
  const dueDate = new Date();
  dueDate.setDate(dueDate.getDate() + 30);

  pdfLink.value = await pdfMake
    .createPdf({
      info: {
        title: `Surat Penawaran #${idOfferingLetter}`,
        author: "PT. Mitra Andalan Petroleum",
        creator: "User",
        producer: "PT. Mitra Andalan Petroleum",
      },
      pageMargins: [72, 42, 72, 10],
      content: [
        {
          background: "#0ff",
          text: "LOGO\nPT. Mitra Andalan Petroleum\nYour Trusted Partner".toUpperCase(),
        },
        {
          text: `Samarinda, ${formatDateDoc(issueDate)}`,
          alignment: "right",
          marginTop: 10,
          marginBottom: 15,
        },
        {
          layout: "noBorders",
          table: {
            widths: ["auto", "auto", "*"],
            body: [
              [
                {
                  text: "Perihal",
                },
                {
                  text: ":",
                },
                {
                  text: [
                    "Surat Penawaran Harga Bahan Bakar Minyak Bio diesel ",
                    {
                      text: "Periode 01 – 14 Juli 2026",
                      bold: true,
                    },
                  ],
                  decoration: "underline",
                },
              ],
              [
                {
                  text: "Nomor",
                },
                {
                  text: ":",
                },
                {
                  text: "123/MAP/II-06/26",
                },
              ],
            ],
          },
        },
        {
          text: [
            "Kepada Yth.\n",
            { text: "PT. Mitra Andalan Petroleum".toUpperCase(), bold: true },
          ],
          marginTop: 15,
        },
        {
          text: "Dengan Hormat,",
          marginTop: 15,
        },
        {
          text: "Berikut ini kami sampaikan penawaran Bahan Bakar Minyak Bio diesel dengan perincian sebagai berikut:",
          marginTop: 15,
          marginBottom: 5,
        },
        {
          layout: {
            defaultBorder: false,
            paddingLeft: function (i) {
              return i === 3 ? -2 : 0;
            },
            paddingBottom: function () {
              return 1;
            },
            paddingTop: function () {
              return 1;
            },
          },
          table: {
            widths: ["auto", "auto", "auto", "*"],
            body: [
              [
                {
                  text: "1.",
                },
                {
                  text: "Supply Point",
                },
                {
                  text: ":",
                },
                {
                  text: "Terminal Bahan Bakar Minyak (TBBM) Palaran",
                },
              ],
              [
                {
                  text: "2.",
                },
                {
                  text: "Jaminan Kualitas",
                },
                {
                  text: ":",
                },
                {
                  text: "Sesuai dengan spesifikasi SK Dirjen Migas",
                },
              ],
              [
                {
                  text: "3.",
                },
                {
                  text: "Custody Transfer",
                },
                {
                  text: ":",
                },
                {
                  text: "Flowmeter terkalibrasi oleh instansi berwenangdi TBBM Palaran",
                },
              ],
              [
                {
                  text: "4.",
                },
                {
                  text: "Prosedur Bongkar",
                },
                {
                  text: ":",
                },
                {
                  text: "Jarum Tera/Sounding Tanki Truck di lokasi penerima",
                },
              ],
              [
                {
                  text: "5.",
                },
                {
                  text: "Satuan Volume",
                },
                {
                  text: ":",
                },
                {
                  text: "Liter observed",
                },
              ],
              [
                {
                  text: "6.",
                },
                {
                  text: "Toleransi Volume",
                },
                {
                  text: ":",
                },
                {
                  text: "0.25%",
                },
              ],
              [
                {
                  text: "7.",
                },
                {
                  text: "Rekening Pembayaran",
                },
                {
                  text: ":",
                },
                {
                  text: "",
                },
              ],
              [
                {
                  text: "BANK MANDIRI cab Segiri\nNo Rek: 1480002719998\nA/N. PT. MITRA ANDALAN PETROLEUM",
                  bold: true,
                  colSpan: 4,
                  alignment: "center",
                  marginBottom: 5,
                },
              ],
              [
                {
                  text: "8.",
                },
                {
                  text: "Harga Bahan Bakar Minyak:",
                  colSpan: 3,
                  marginBottom: 5,
                },
              ],
            ],
          },
        },
        {
          layout: {
            paddingTop: function (i) {
              return i === 0 ? 5 : 2;
            },
            paddingBottom: function (i) {
              return i === 0 ? 10 : 2;
            },
            paddingLeft: function (i) {
              return i === 0 ? 15 : 5;
            },
          },
          marginLeft: 15,
          table: {
            widths: ["*", "*", "*"],
            headerRows: 1,
            body: [
              [
                {
                  text: "KETERANGAN",
                  style: {
                    bold: true,
                  },
                },
                {
                  text: "KET",
                  style: {
                    alignment: "center",
                    bold: true,
                  },
                },
                {
                  text: "TRUCK 10 KL\nSite BSSR / BAS Tanah Datar",
                  style: {
                    alignment: "center",
                    bold: true,
                  },
                },
              ],
              [
                {
                  text: "PRODUK",
                  style: {
                    bold: true,
                  },
                },
                {
                  text: "",
                },
                {
                  text: "Bio Diesel B50 / B40 if stock still",
                  style: {
                    alignment: "center",
                  },
                },
              ],
              [
                {
                  text: "HARGA PRODUK",
                  style: {
                    bold: true,
                  },
                },
                {
                  text: "PPKB Include",
                  style: {
                    alignment: "center",
                  },
                },
                {
                  text: formatCurrency(17950),
                  style: {
                    alignment: "center",
                  },
                },
              ],
              [
                {
                  text: "",
                  style: {
                    bold: true,
                  },
                },
                {
                  text: "OAT",
                  style: {
                    alignment: "center",
                  },
                },
                {
                  text: formatCurrency(450),
                  style: {
                    alignment: "center",
                  },
                },
              ],
              [
                {
                  text: "PPN (11%)",
                  style: {
                    bold: true,
                  },
                },
                {
                  text: "HARGA JUAL & ONGKOS ANGKUT",
                  style: {
                    alignment: "center",
                  },
                },
                {
                  text: formatCurrency(2024),
                  style: {
                    alignment: "center",
                  },
                },
              ],
              [
                {
                  text: "TOTAL",
                  style: {
                    bold: true,
                    alignment: "center",
                  },
                  colSpan: 2,
                },
                {},
                {
                  text: formatCurrency(20424),
                  style: {
                    alignment: "center",
                    bold: true,
                  },
                },
              ],
            ],
          },
        },

        // custom list using *** bullet
        {
          marginTop: 10,
          marginLeft: 15,
          columns: [
            { text: "***", width: "auto", marginRight: 3, bold: true },
            {
              text: "Harga sewaktu-waktu dapat berubah mengikuti harga keekonomian Pertamina",
            },
          ],
        },
        {
          marginTop: 1,
          marginLeft: 15,
          columns: [
            { text: "***", width: "auto", marginRight: 3, bold: true },
            {
              text: "Stock BBM sewaktu-waktu dapat berubah mengikuti posisi stock BBM di depo terdekat",
            },
          ],
        },
        {
          marginTop: 1,
          marginLeft: 15,
          columns: [
            { text: "***", width: "auto", marginRight: 3, bold: true },
            {
              text: "B50 / B40 if stock still available",
            },
          ],
        },
        {
          text: [
            "Mohon Purchase Order (PO) dapat dikirimkan minimal ",
            { text: "3 (tiga) hari ", bold: true },
            "sebelum pengaliran/muat dari terminal.",
          ],
          marginTop: 15,
        },
        {
          text: "Demikian surat penawaran ini kami sampaikan, kami ucapkan terimakasih.",
        },
        {
          text: "Hormat Kami,",
          marginTop: 15,
        },
        {
          text: "Placeholder Signature MAP",
          italics: true,
          marginTop: 25,
          marginBottom: 25,
        },
        {
          text: "(Stenly Boseke)",
          bold: true,
        },
        {
          layout: {
            defaultBorder: false,
            paddingLeft: function (i) {
              return i === 2 ? -2 : 0;
            },
            paddingTop: function () {
              return 0;
            },
            paddingBottom: function () {
              return 0;
            },
          },
          marginLeft: 320,
          table: {
            widths: ["auto", "auto", "auto"],
            body: [
              [
                {
                  text: "Address",
                },
                {
                  text: ":",
                },
                {
                  text: "Jl. Belatuk No. 63\nSamarinda, 75117\nIndonesia",
                },
              ],
              [
                {
                  text: "Phone",
                },
                {
                  text: ":",
                },
                {
                  text: "0541-1234567",
                },
              ],
              [
                {
                  text: "Email",
                },
                {
                  text: ":",
                },
                {
                  text: "marketing.map@example.com",
                },
              ],
            ],
          },
        },
        // {
        //   columns: [
        //     {
        //       width: "*",
        //       stack: [
        //         { text: "BILL TO", style: "sectionLabel" },
        //         { text: faker.person.fullName(), style: "clientName" },
        //         { text: faker.company.name(), style: "clientDetail" },
        //         {
        //           text: `${faker.location.streetAddress()}\n${faker.location.city()}, ${faker.location.state({ abbreviated: true })} ${faker.location.zipCode()}`,
        //           style: "clientDetail",
        //         },
        //         { text: faker.internet.email(), style: "clientEmail" },
        //       ],
        //     },
        //     {
        //       width: "*",
        //       stack: [
        //         { text: "PROJECT", style: "sectionLabel" },
        //         { text: faker.commerce.productName(), style: "clientName" },
        //         { text: "Professional Services", style: "clientDetail" },
        //         {
        //           text: `Reference: REF-${faker.number.int({ min: 100, max: 999 })}`,
        //           style: "clientDetail",
        //         },
        //       ],
        //     },
        //   ],
        //   columnGap: 20,
        //   marginBottom: 20,
        // },
        // {
        //   table: {
        //     headerRows: 1,
        //     widths: ["*", 50, 80, 80],
        //     body: [
        //       [
        //         { text: "Description", style: "th" },
        //         { text: "Qty", style: "th", alignment: "center" },
        //         { text: "Rate", style: "th", alignment: "right" },
        //         { text: "Amount", style: "th", alignment: "right" },
        //       ],
        //       ...lineItems.map(
        //         (item) =>
        //           [
        //             {
        //               stack: [
        //                 { text: item.description, style: "itemName" },
        //                 { text: item.category, style: "itemCategory" },
        //               ],
        //             },
        //             {
        //               text: String(item.qty),
        //               alignment: "center" as const,
        //               style: "cell",
        //             },
        //             {
        //               text: fmt(item.rate),
        //               alignment: "right" as const,
        //               style: "cell",
        //             },
        //             {
        //               text: fmt(item.amount),
        //               alignment: "right" as const,
        //               style: "cell",
        //             },
        //           ] as const,
        //       ),
        //     ] as any,
        //   },
        //   layout: {
        //     fillColor: (rowIndex: number) =>
        //       rowIndex === 0
        //         ? "#0f172a"
        //         : rowIndex % 2 === 0
        //           ? "#f8fafc"
        //           : null,
        //     hLineWidth: (rowIndex: number) => (rowIndex === 0 ? 0 : 0.5),
        //     vLineWidth: () => 0,
        //     hLineColor: "#e2e8f0",
        //     paddingBottom: () => 9,
        //     paddingTop: () => 9,
        //     paddingLeft: () => 10,
        //     paddingRight: () => 10,
        //   },
        //   marginBottom: 0,
        // },
        // {
        //   table: {
        //     widths: ["*", 80],
        //     body: [
        //       [
        //         { text: "Subtotal", style: "summaryLabel" },
        //         { text: fmt(subtotal), style: "summaryValue" },
        //       ],
        //       [
        //         { text: "Tax (8.5%)", style: "summaryLabel" },
        //         { text: fmt(tax), style: "summaryValue" },
        //       ],
        //       [
        //         { text: "Total Due", style: "totalLabel" },
        //         { text: fmt(total), style: "totalValue" },
        //       ],
        //     ],
        //   },
        //   layout: {
        //     hLineWidth: (i: number) => (i === 2 ? 1.5 : 0.5),
        //     vLineWidth: () => 0,
        //     hLineColor: (i: number) => (i === 2 ? "#0f172a" : "#e2e8f0"),
        //     paddingTop: () => 8,
        //     paddingBottom: () => 8,
        //     paddingLeft: () => 10,
        //     paddingRight: () => 10,
        //   },
        //   marginBottom: 22,
        // },
        // {
        //   columns: [
        //     {
        //       width: "*",
        //       stack: [
        //         { text: "PAYMENT TERMS", style: "sectionLabel" },
        //         {
        //           text: "Payment is due within 30 days of the invoice date. Late payments are subject to a 1.5% monthly finance charge.",
        //           style: "noteText",
        //         },
        //       ],
        //     },
        //     {
        //       width: "*",
        //       stack: [
        //         { text: "BANK TRANSFER DETAILS", style: "sectionLabel" },
        //         {
        //           text:
        //             "Bank: First National Bank\nAccount: 1234-5678-9012\nRouting: 021000021\nRef: " +
        //             invoiceNumber,
        //           style: "noteText",
        //         },
        //       ],
        //     },
        //   ],
        //   columnGap: 20,
        // },
      ],
      defaultStyle: {
        color: "#1d293d",
        fontSize: 9,
      },
      styles: {
        invoiceTitle: {
          fontSize: 28,
          bold: true,
          color: "#0f172a",
          characterSpacing: 2,
          marginBottom: 8,
        },
        companyName: {
          fontSize: 11,
          bold: true,
          color: "#0f172a",
          marginBottom: 3,
        },
        companyAddress: {
          color: "#64748b",
          lineHeight: 1.4,
        },
        metaLabel: {
          color: "#64748b",
          fontSize: 8,
        },
        metaValue: {
          bold: true,
          color: "#0f172a",
          fontSize: 8,
        },
        statusBadge: {
          bold: true,
          color: "#dc2626",
          fontSize: 8,
        },
        sectionLabel: {
          fontSize: 7,
          color: "#94a3b8",
          bold: true,
          characterSpacing: 1,
          marginBottom: 5,
        },
        clientName: {
          fontSize: 11,
          bold: true,
          color: "#0f172a",
          marginBottom: 2,
        },
        clientDetail: {
          color: "#475569",
          lineHeight: 1.4,
        },
        clientEmail: {
          color: "#0084d1",
          decoration: "underline",
        },
        th: {
          bold: true,
          color: "#ffffff",
          fontSize: 8,
        },
        itemName: {
          bold: true,
          color: "#0f172a",
        },
        itemCategory: {
          color: "#64748b",
          fontSize: 8,
          marginTop: 2,
        },
        cell: {
          color: "#475569",
        },
        summaryLabel: {
          color: "#475569",
          alignment: "right",
        },
        summaryValue: {
          color: "#475569",
          alignment: "right",
        },
        totalLabel: {
          bold: true,
          color: "#0f172a",
          fontSize: 11,
          alignment: "right",
        },
        totalValue: {
          bold: true,
          color: "#0f172a",
          fontSize: 11,
          alignment: "right",
        },
        noteText: {
          color: "#64748b",
          lineHeight: 1.4,
        },
      },
    })
    .getDataUrl();
};

onMounted(() => {
  loadPdf();
});
</script>

<template>
  <main class="h-180 w-full">
    <iframe v-if="pdfLink" :src="pdfLink" class="h-full w-full" />
  </main>
</template>
