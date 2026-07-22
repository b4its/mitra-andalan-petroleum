<script setup lang="ts">
import logoImage from "~/assets/images/map-logo.jpeg";

const pdfLink = ref<string | null>(null);
const route = useRoute();
const idOfferingLetter = route.params.id;
const { user } = useAuth();

const loadPdf = async () => {
  const pdfMake = usePDFMake();
  if (!pdfMake) return;

  const issueDate = new Date();

  pdfLink.value = await pdfMake
    .createPdf({
      info: {
        title: `Surat Penawaran #${idOfferingLetter}`,
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
