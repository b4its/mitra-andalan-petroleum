<script setup lang="ts">
const pdfLink = ref<string | null>(null);
const route = useRoute();
const idPoLetter = route.params.id;
const { user } = useAuth();

const loadPdf = async () => {
  const pdfMake = usePDFMake();
  if (!pdfMake) return;

  pdfLink.value = await pdfMake
    .createPdf({
      info: {
        title: `Purchase Order ${idPoLetter}`,
        author: "PT. Mitra Andalan Petroleum",
        creator: user.value?.name,
        producer: "PT. Mitra Andalan Petroleum",
      },
      pageMargins: [24, 24, 24, 24],
      pageSize: "A4",
      content: [
        {
          layout: {
            paddingLeft: function (i) {
              return 2;
            },
            paddingBottom: function (i) {
              return i === 1 ? 10 : 0;
            },
            paddingTop: function () {
              return 2;
            },
            fillColor: function (i) {
              return i === 0 ? "#9c9e9e" : null;
            },
          },
          table: {
            widths: ["*", "*"],
            body: [
              [
                {
                  text: "To",
                  colSpan: 2,
                  bold: true,
                },
                {},
              ],
              [
                {
                  text: [
                    {
                      text: "PT. MIGAS KUKAR MANDIRI\n",
                      bold: true,
                    },
                    "Jl. KH AGUS SALIM No. 32\n",
                    "SAMARINDA",
                  ],
                },
                {
                  text: [
                    {
                      text: "PT. MITRA ANDALAN PETROLEUM\n",
                      bold: true,
                    },
                    "Jl. D.I. Panjaitan No. 25 D\n",
                    "Samarinda 75117, Indonesia\n",
                    "Phone: 0541-2832313\n",
                    "Email: marketing.mapetroleum@gmail.com\n",
                    "NPWP: 43.170.319.8-722.000",
                  ],
                },
              ],
            ],
          },
        },
        {
          layout: {
            paddingRight: function (i) {
              return 1;
            },
            paddingLeft: function (i) {
              return 1;
            },
            paddingBottom: function (i) {
              return 1;
            },
            paddingTop: function (i) {
              return 1;
            },
          },
          table: {
            widths: ["auto", "*", "auto", "auto", "auto", 118],
            body: [
              // HEADER
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
                  text: `PO Date : ${formatDate(new Date())}`,
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
                  text: `PO Number : ${idPoLetter}`,
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
            paddingRight: function (i) {
              return 10;
            },
            paddingLeft: function (i) {
              return 10;
            },
            paddingBottom: function (i) {
              return 1;
            },
            paddingTop: function (i) {
              return 1;
            },
            fillColor: function (i) {
              return i === 0 ? "#9c9e9e" : null;
            },
          },
          table: {
            widths: ["auto", "*", "auto", "auto", "auto", 100],
            body: [
              // PRODUCT LIST
              // PRODUCT HEADER
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

              // PRODUCT BODY
              [
                {
                  text: "1",
                  alignment: "center",
                  border: [true, false, true, true],
                },
                {
                  text: "Bio Diesel",
                  alignment: "left",
                  border: [true, false, true, true],
                },
                {
                  text: "20000",
                  alignment: "center",
                  border: [true, false, true, true],
                },
                {
                  text: "Liter",
                  alignment: "center",
                  border: [true, false, true, true],
                },
                {
                  text: formatCurrency(21800),
                  alignment: "center",
                  border: [true, false, true, true],
                },
                {
                  text: formatCurrency(436000000),
                  alignment: "right",
                  border: [true, false, true, true],
                },
              ],
              [{}, {}, {}, {}, {}, {}],
              [{}, {}, {}, {}, {}, {}],
              [{}, {}, {}, {}, {}, {}],
              [{}, {}, {}, {}, {}, {}],
              [{}, {}, {}, {}, {}, {}],
              [{}, {}, {}, {}, {}, {}],
              [{}, {}, {}, {}, {}, {}],
              [{}, {}, {}, {}, {}, {}],
              [{}, {}, {}, {}, {}, {}],
              // 9 blank columns for products, the rest is for transfer detail
              [
                {},
                {
                  text: "include VAT 11%",
                  bold: true,
                },
                {},
                {},
                {},
                {},
              ],
              [{}, {}, {}, {}, {}, {}],
              [
                {},
                {
                  text: "Transfer Detail :",
                  bold: true,
                },
                {},
                {},
                {},
                {},
              ],
              [
                {},
                {
                  text: "Bank Central Asia (BCA) Cabang Sudirman, Samarinda",
                  bold: true,
                },
                {},
                {},
                {},
                {},
              ],
              [
                {},
                { text: "PT Migas Kukar Mandiri", bold: true },
                {},
                {},
                {},
                {},
              ],
              [{}, { text: "No. Rek. 012 07878212" }, {}, {}, {}, {}],
              [{}, {}, {}, {}, {}, {}],
              [
                {
                  text: "Subtotal",
                  colSpan: 5,
                  bold: true,
                  alignment: "right",
                },
                {},
                {},
                {},
                {},
                {
                  text: formatCurrency(436000000),
                  alignment: "right",
                  bold: true,
                },
              ],
            ],
          },
        },
        {
          layout: {
            paddingRight: function (i) {
              return 2;
            },
            paddingLeft: function (i) {
              return 2;
            },
            paddingBottom: function (i) {
              return 2;
            },
            paddingTop: function (i) {
              return 2;
            },
            fillColor: function (i) {
              return [0, 2].includes(i) ? "#9c9e9e" : null;
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
                  text: "CBD",
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
                  text: "Loading Terminal :\nLoading Date :\nPIC OPERATION MAP : ",
                  border: [true, false, true, true],
                },
                {
                  text: "Trucking : TBA",
                },
              ],
            ],
          },
        },
        {
          layout: {
            paddingRight: function (i) {
              return 2;
            },
            paddingLeft: function (i) {
              return 15;
            },
            paddingBottom: function (i) {
              return 15;
            },
            paddingTop: function (i) {
              return 2;
            },
          },
          table: {
            widths: ["*", "*"],
            body: [
              [
                {
                  text: [
                    {
                      text: "Created By\n\n\n\n\n\n\n",
                    },
                    {
                      text: "Fitri",
                    },
                  ],
                  border: [true, false, false, true],
                },
                {
                  text: [
                    {
                      text: "Approved By\n\n\n\n\n\n\n",
                    },
                    {
                      text: "Stenly B",
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
