<script setup lang="ts">
import angkaTerbilang from "@develoka/angka-terbilang-js";
import logoImage from "~/assets/images/map-logo.jpeg";
import type { Customer, OfferingLetterPost } from "~/types/marketing";

const pdfLink = ref<string | null>(null);
const route = useRoute();
const { get } = useApi();

const idOfferingLetter = route.params.id;
const { data: offeringLetter } = await useAsyncData(
  "offering-letter-details",
  async () => {
    const res = await get<OfferingLetterPost>(
      `/offering-letters/${idOfferingLetter}`,
    );
    return res;
  },
);

const { data: customerDetail } = await useAsyncData(
  "customer-detail",
  async () => {
    const res = await get<Customer>(
      `/customers/${offeringLetter.value?.details.receiver}`,
    );
    return res;
  },
);

const details = offeringLetter.value?.details;

const { user } = useAuth();

const baseWithPpkb = computed(() => {
  if (!details) return 0;
  return details.fuelPrices.basePrice + details.fuelPrices.sellingPrice.ppkb;
});

const loadPdf = async () => {
  const pdfMake = usePDFMake();
  if (!pdfMake) return;

  pdfLink.value = await pdfMake
    .createPdf({
      info: {
        title: `Surat Penawaran (${details?.offeringLetterNumber}) | ${customerDetail.value?.name}`,
        author: "PT. Mitra Andalan Petroleum",
        creator: user.value?.name,
        producer: "PT. Mitra Andalan Petroleum",
      },
      pageSize: "A4",
      pageMargins: [72, 10, 72, 10],
      content: [
        {
          image: await toBase64(logoImage),
          width: 160,
        },
        {
          text: `Samarinda, ${formatDateDoc(details?.date || new Date())}`,
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
                    `${details?.regarding}`,
                    // {
                    //   text: "Periode 01 – 14 Juli 2026",
                    //   bold: true,
                    // },
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
                  text: `${details?.offeringLetterNumber}`,
                },
              ],
            ],
          },
        },
        {
          text: [
            "Kepada Yth.\n",
            { text: `${customerDetail.value?.name}`.toUpperCase(), bold: true },
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
                  text: `${details?.supplyPoint}`,
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
                  text: `${details?.qualityAssurance}`,
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
                  text: `${details?.custodyTransfer}`,
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
                  text: `${details?.unloadingProcedure}`,
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
                  text: `${details?.volumeUnit}`,
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
                  text: formatPercent(details?.volumeTolerance || 0),
                },
              ],
              [
                {
                  text: "7.",
                },
                {
                  text: "Term Pembayaran",
                },
                {
                  text: ":",
                },
                {
                  text: `${details?.paymentTerm} ${details?.paymentTerm || 0 > 1 ? "Days" : "Day"} after delivery`,
                },
              ],
              [
                {
                  text: "8.",
                },
                {
                  text: "Penalty Keterlambatan",
                },
                {
                  text: ":",
                },
                {
                  text: `${formatPercent(details?.latePenalty || 0)}`,
                },
              ],
              [
                {
                  text: "9.",
                },
                {
                  text: "Pola Pelayanan",
                },
                {
                  text: ":",
                },
                {
                  text: `${details?.servicePattern}`,
                },
              ],
              [
                {
                  text: "10.",
                },
                {
                  text: "Person In Charge",
                },
                {
                  text: ":",
                },
                {
                  text: `${details?.personInCharge.name} - ${details?.personInCharge.phoneNumber}`,
                },
              ],
              [
                {
                  text: "11.",
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
                  text: `${details?.paymentAddress.bankName}\nNo Rek: ${details?.paymentAddress.accountNumber}\nA/N. ${details?.paymentAddress.accountName}`,
                  bold: true,
                  colSpan: 4,
                  alignment: "center",
                  marginBottom: 5,
                },
              ],
              [
                {
                  text: "12.",
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
                  text: `${details?.fuelPrices.logisticInformation}`,
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
                  text: `${details?.fuelPrices.productName}`,
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
                  text: formatCurrency(baseWithPpkb.value),
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
                  text: formatCurrency(
                    details?.fuelPrices.sellingPrice.oat || 0,
                  ),
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
                  text: formatCurrency(
                    details?.fuelPrices.sellingPrice.ppn || 0,
                  ),
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
                  text: formatCurrency(details?.fuelPrices.totalPrice || 0),
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
            {
              text: `${details?.purchaseOrderDeadline || 0} (${angkaTerbilang(details?.purchaseOrderDeadline || 0)}) hari `,
              bold: true,
            },
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
          marginBottom: 25,
        },
        // {
        //   text: "Placeholder Signature MAP",
        //   italics: true,
        //   marginTop: 25,
        //   marginBottom: 25,
        // },
        {
          text: `(${details?.offeror.name})`,
          bold: true,
          marginTop: 25,
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
                  text: `${details?.companyInformation.address}`,
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
                  text: `${details?.companyInformation.phoneNumber}`,
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
                  text: `${details?.companyInformation.email}`,
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
