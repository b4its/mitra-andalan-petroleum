<script setup lang="ts">
import angkaTerbilang from "@develoka/angka-terbilang-js";
import { useChangeCase } from "@vueuse/integrations/useChangeCase.js";
import logoImage from "~/assets/images/map-logo-only.jpg";
const pdfLink = ref<string | null>(null);
const route = useRoute();
const idDoLetter = route.params.id;
const { user } = useAuth();

const loadPdf = async () => {
  const pdfMake = usePDFMake();
  if (!pdfMake) return;

  pdfLink.value = await pdfMake
    .createPdf({
      info: {
        title: `Delivery Order ${idDoLetter}`,
        author: "PT. Mitra Andalan Petroleum",
        creator: user.value?.name,
        producer: "PT. Mitra Andalan Petroleum",
      },
      pageMargins: [24, 15, 24, 15],
      pageSize: "A4",
      content: [
        {
          layout: {
            defaultBorder: false,
            paddingRight: function (i) {
              return 2;
            },
            paddingLeft: function (i) {
              return 2;
            },
            paddingBottom: function (i) {
              return 1;
            },
            paddingTop: function (i) {
              return 1;
            },
            fillColor: function (i) {
              return null;
            },
          },
          table: {
            widths: ["15%", "auto", "auto"],
            body: [
              [
                {
                  image: await toBase64(logoImage),
                  width: 40,
                  alignment: "center",
                  rowSpan: 4,
                },
                {
                  text: "PT. MITRA ANDALAN PETROLEUM",
                  style: {
                    bold: true,
                    fontSize: 20,
                    color: "#14469b",
                  },
                  colSpan: 2,
                },
                {},
              ],
              [
                {},
                {
                  text: "Your Trusted Partner",
                  style: {
                    bold: true,
                    italics: true,
                    fontSize: 14,
                    color: "#ff0000",
                  },
                  colSpan: 2,
                },
                {},
              ],
              [
                {},
                {
                  text: "Jl. D. I. Panjaitan No. 25 C-D, Samarinda 75117, Kalimantan Timur, Indonesia",
                  colSpan: 2,
                  fontSize: 8,
                },
                {},
              ],
              [
                {},
                {
                  text: "0541-2832313",
                  bold: true,
                  italics: true,
                  fontSize: 8,
                },
                {
                  text: "Email: marketing.mapetroleum@email.com",
                  bold: true,
                  italics: true,
                  marginRight: 60,
                  fontSize: 8,
                },
              ],
            ],
          },
        },
        {
          layout: {
            // defaultBorder: false,
            paddingRight: function (i) {
              return 2;
            },
            paddingLeft: function (i) {
              return 2;
            },
            paddingBottom: function (i) {
              return [0, 1].includes(i) ? 0 : 2;
            },
            paddingTop: function (i) {
              return [0, 1].includes(i) ? 0 : 2;
            },
            fillColor: function (i) {
              return [0, 2].includes(i) ? "#1d82d1" : null;
            },
          },
          table: {
            widths: ["*", "*"],
            body: [
              [
                {
                  text: "",
                  colSpan: 2,
                },
                {},
              ],
              [
                {
                  text: "INVOICE",
                  style: {
                    bold: true,
                    fontSize: 18,
                    alignment: "center",
                  },
                  border: [false, true, false, true],
                  colSpan: 2,
                },
                {},
              ],
              [
                {
                  text: "Bill To",
                  color: "#fff",
                  bold: true,
                },
                {
                  text: "Delivery Point",
                  color: "#fff",
                  bold: true,
                },
              ],
              [
                {
                  text: "PT. BINA SARANA SUKSES\nPENJARINGAN, JAKARTA UTARA, LANDMARK PLUIT,\nJALAN PLUIT SELATAN RAYA KOMPLEK PERKANTORAN\nNo. D17, PLUIT, JAKARTA UTARA - 14450",
                  bold: true,
                  lineHeight: 1.25,
                },
                {
                  text: "PT. BINA SARANA SUKSES\nTDM (PL02) - DS. MARANG KAYU,\nKEC. TENGGARONG, SEBERANG,\nKAB. KUKAR WORKSHOP BSS KM\n\n",
                  bold: true,
                  lineHeight: 1.25,
                },
              ],
            ],
          },
        },
        {
          layout: {
            // defaultBorder: false,

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
              return null;
            },
          },
          table: {
            widths: ["*", "*", "*", "*"],
            body: [
              [
                {
                  text: "Invoice No.",
                  bold: true,
                  alignment: "center",
                  border: [true, false, true, true],
                },
                {
                  text: "Invoice Date",
                  bold: true,
                  alignment: "center",
                  border: [true, false, true, true],
                },
                {
                  text: "No. DO",
                  bold: true,
                  alignment: "center",
                  border: [true, false, true, true],
                },
                {
                  text: "Customer PO No",
                  bold: true,
                  alignment: "center",
                  border: [true, false, true, true],
                },
              ],
              [
                {
                  text: "576/INV/MAP/2026",
                  verticalAlignment: "middle",
                  alignment: "center",
                },
                {
                  text: formatDate(new Date()),
                  verticalAlignment: "middle",
                  alignment: "center",
                },
                {
                  text: "1129, 1127, 1125, 1128, 1126, 1124, 1129, 1127, 1125, 1128, 1126, 1124, 1129, 1127, 1125, 1128, 1126, 1124, 1129, 1127, 1125, 1128, 1126, 1124, 1129, 1127, 1125, 1128, 1126, 1124, 1129, 1127, 1125, 1128, 1126, 1124, 1122/DO/MAP/VI/2026",

                  verticalAlignment: "middle",
                  alignment: "center",
                },
                {
                  text: "1200020145",
                  verticalAlignment: "middle",
                  alignment: "center",
                },
              ],
              [
                {
                  text: "Terms",
                  bold: true,
                  alignment: "center",
                },
                {
                  text: "Due Date",
                  bold: true,
                  alignment: "center",
                },
                {
                  text: "Tax No (Faktur Pajak)",
                  bold: true,
                  alignment: "center",
                },
                {
                  text: "SO No",
                  bold: true,
                  alignment: "center",
                },
              ],
              [
                {
                  text: "40 Days After Delivery",
                  verticalAlignment: "middle",
                  alignment: "center",
                },
                {
                  text: formatDate(new Date()),
                  verticalAlignment: "middle",
                  alignment: "center",
                },
                {
                  text: "04002600249829603",

                  verticalAlignment: "middle",
                  alignment: "center",
                },
                {
                  text: "",
                  verticalAlignment: "middle",
                  alignment: "center",
                },
              ],
            ],
          },
        },
        {
          marginTop: 10,
          layout: {
            // defaultBorder: false,
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
              return null;
            },
          },
          table: {
            widths: ["6%", "*", "*", "40%", "*", "*"],
            body: [
              [
                {
                  text: "ITEM",
                  bold: true,
                  alignment: "center",
                  verticalAlignment: "middle",
                  rowSpan: 2,
                },
                {
                  text: "QUANTITY",
                  bold: true,
                  alignment: "center",
                  verticalAlignment: "middle",

                  colSpan: 2,
                },
                {},
                {
                  text: "DESCRIPTION",
                  bold: true,
                  alignment: "center",
                  verticalAlignment: "middle",

                  rowSpan: 2,
                },
                {
                  text: "PRICE (IDR)",
                  bold: true,
                  alignment: "center",
                  verticalAlignment: "middle",

                  colSpan: 2,
                },
                {},
              ],
              [
                {},
                {
                  text: "QTY",
                  bold: true,
                  alignment: "center",
                  verticalAlignment: "middle",
                },
                {
                  text: "UNIT",
                  bold: true,
                  alignment: "center",
                  verticalAlignment: "middle",
                },
                {},
                {
                  text: "UNIT",
                  bold: true,
                  alignment: "center",
                  verticalAlignment: "middle",
                },
                {
                  text: "TOTAL",
                  bold: true,
                  alignment: "center",
                  verticalAlignment: "middle",
                },
              ],
            ],
          },
        },
        {
          layout: {
            // defaultBorder: false,
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
              return null;
            },
            hLineWidth: function () {
              return 0;
            },
          },
          table: {
            widths: ["6%", "*", "*", "40%", "*", "*"],
            body: [
              [
                {
                  text: "1",
                  alignment: "center",
                },
                {
                  text: "299.845",
                  alignment: "center",
                },
                {
                  text: "LITER",
                  alignment: "center",
                },
                {
                  text: "Extra Diesel B40",
                  alignment: "left",
                },
                {
                  text: "19.500,00",
                  alignment: "right",
                },
                {
                  text: "5.846.977.500",
                  alignment: "right",
                },
              ],
              [
                {
                  text: "",
                  alignment: "center",
                },
                {
                  text: "",
                  alignment: "center",
                },
                {
                  text: "",
                  alignment: "center",
                },
                {
                  text: "BIAYA TRANSPORT BBM",
                  alignment: "left",
                },
                {
                  text: "1.200,00",
                  alignment: "right",
                },
                {
                  text: "359.814.000",
                  alignment: "right",
                },
              ],
              [{}, {}, {}, {}, {}, {}],
              [{}, {}, {}, {}, {}, {}],
              [{}, {}, {}, {}, {}, {}],
              [{}, {}, {}, {}, {}, {}],
            ],
          },
        },
        {
          layout: {
            // defaultBorder: false,
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
              return null;
            },
          },
          table: {
            widths: ["6%", "*", "*", "40%", "*", "*"],
            body: [
              [
                {
                  text: useChangeCase(angkaTerbilang(6889538565), "capitalCase")
                    .value,
                  alignment: "center",
                  colSpan: 4,
                },
                {},
                {},
                {},
                {
                  text: "Sub Total",
                  bold: true,
                  alignment: "left",
                },
                {
                  text: "6.206.791.500",
                  alignment: "right",
                },
              ],
              [
                {
                  text: "",
                  colSpan: 4,
                  border: [false, false, false, false],
                },
                {},
                {},
                {},
                {
                  text: "Pre-Paid",
                  bold: true,
                  alignment: "left",
                },
                {
                  text: "",
                  alignment: "right",
                },
              ],
              [
                {
                  text: "",
                  colSpan: 4,
                  border: [false, false, false, false],
                },
                {},
                {},
                {},
                {
                  text: "Diskon",
                  bold: true,
                  alignment: "left",
                },
                {
                  text: "",
                  alignment: "right",
                },
              ],
              [
                {
                  text: "",
                  colSpan: 4,
                  border: [false, false, false, false],
                },
                {},
                {},
                {},
                {
                  text: "PPn",
                  bold: true,
                  alignment: "left",
                },
                {
                  text: "682.747.065",
                  alignment: "right",
                },
              ],
              [
                {
                  text: "Term and Conditions:",
                  bold: true,
                  colSpan: 4,
                  border: [false, false, false, false],
                },
                {},
                {},
                {},
                {
                  text: "Grand Total",
                  bold: true,
                  alignment: "left",
                },
                {
                  text: "6.889.538.565",
                  bold: true,
                  alignment: "right",
                },
              ],
            ],
          },
        },
        {
          marginLeft: 5,
          layout: {
            defaultBorder: false,
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
            fillColor: function (i) {
              return null;
            },
          },
          table: {
            widths: ["5%", "25%", "1%", "55%"],
            body: [
              [
                {
                  text: "1.",
                  alignment: "center",
                },
                {
                  text: "All check payable to",
                  colSpan: 3,
                },
                {},
                {},
              ],
              [
                {
                  text: "",
                },
                {
                  text: "Bank Name",
                  bold: true,
                },
                {
                  text: ":",
                  bold: true,
                },
                {
                  text: "MANDIRI - Cab Segiri",
                  bold: true,
                },
              ],
              [
                {
                  text: "",
                },
                {
                  text: "Bank Account No",
                  bold: true,
                },
                {
                  text: ":",
                  bold: true,
                },
                {
                  text: "1480002717776",
                  bold: true,
                },
              ],
              [
                {
                  text: "",
                },
                {
                  text: "Acct Name",
                  bold: true,
                },
                {
                  text: ":",
                  bold: true,
                },
                {
                  text: "PT. MITRA ANDALAN PETROLEUM",
                  bold: true,
                },
              ],
              [
                {
                  text: "2.",
                  alignment: "center",
                },
                {
                  text: "If payment has no been received by the stated date of payment, penalty of 2% interest per month will be imposed",
                  colSpan: 3,
                },
                {},
                {},
              ],
              [
                {
                  text: "3.",
                  alignment: "center",
                },
                {
                  text: "Seller has the right to refuse / decline delivery if payment terms has not been met, and shall not be held responsible for any direct or indirect consequences arising thereafter",
                  colSpan: 3,
                },
                {},
                {},
              ],
              [
                {
                  text: "4.",
                  alignment: "center",
                },
                {
                  text: "Goods sold are not refundable",
                  colSpan: 3,
                },
                {},
                {},
              ],
              [
                {
                  text: "5.",
                  alignment: "center",
                },
                {
                  text: "Invoice will be considered PAID once seller has received full amount on the stated account",
                  colSpan: 3,
                },
                {},
                {},
              ],
              [
                {
                  text: "6.",
                  alignment: "center",
                },
                {
                  text: "MAP Contact Number Fin & Acct Officer : 08123456789",
                  colSpan: 3,
                },
                {},
                {},
              ],
            ],
          },
        },
        {
          text: "PT. MITRA ANDALAN PETROLEUM",
          bold: true,
          marginTop: 15,
          marginBottom: 30,
        },
        {
          marginTop: 30,
          text: "Syannet",
          bold: true,
          decoration: "underline",
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
