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
      pageMargins: [24, 24, 24, 24],
      pageSize: "A4",
      content: [
        {
          layout: {
            // defaultBorder: false,
            paddingRight: function (i) {
              return 10;
            },
            paddingLeft: function (i) {
              return 10;
            },
            paddingBottom: function (i) {
              return 10;
            },
            paddingTop: function (i) {
              return 10;
            },
            fillColor: function (i) {
              return null;
            },
          },
          table: {
            widths: ["25%", "*"],
            body: [
              [
                {
                  image: await toBase64(logoImage),
                  width: 30,
                  alignment: "center",
                  border: [true, true, false, false],
                },
                {
                  text: "SURAT PENGANTAR PENGIRIMAN (DELIVERY ORDER)",
                  bold: true,
                  fontSize: 11,
                  border: [false, true, true, false],
                },
              ],
            ],
          },
        },
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
            widths: ["*", "15%", "auto", "30%"],
            body: [
              [
                {
                  text: "PT. MITRA ANDALAN PETROLEUM",
                  bold: true,
                  border: [true, false, false, false],
                },
                {
                  text: "",
                },
                {
                  text: "",
                },
                {
                  text: "",
                  border: [false, false, true, false],
                },
              ],
              [
                {
                  text: "Distributor Agent for Elnusa Petrofin",
                  italics: true,
                  border: [true, false, false, false],
                },
                {
                  text: "No. DO MAP",
                  bold: true,
                },
                {
                  text: ":",
                },
                {
                  text: "1124/DO/MAP/VI/2026",
                  border: [false, false, true, false],
                },
              ],
              [
                {
                  text: "Jl. D.I. Panjaitan No. 25 C-D",
                  border: [true, false, false, false],
                },
                {
                  text: "Tgl. DO",
                  bold: true,
                },
                {
                  text: ":",
                },
                {
                  text: formatDateDoc(new Date()),
                  border: [false, false, true, false],
                },
              ],
              [
                {
                  text: "Samarinda, 75117, Kalimantan Timur",
                  border: [true, false, false, false],
                },
                {},
                {
                  text: ":",
                },
                {
                  text: "",
                  border: [false, false, true, false],
                },
              ],
              [
                {
                  text: "Indonesia",
                  border: [true, false, false, false],
                },
                {
                  text: "NO. PO Cust.",
                  bold: true,
                },
                {
                  text: ":",
                },
                {
                  text: "1200020145",
                  border: [false, false, true, false],
                },
              ],
              [
                {
                  text: "Telp : 0541-2832313",
                  border: [true, false, false, false],
                },
                {
                  text: "No. SO",
                  bold: true,
                },
                {
                  text: ":",
                },
                { text: "\n\n", border: [false, false, true, false] },
              ],
            ],
          },
        },
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
            widths: ["auto", "auto", "*", "auto", "auto", "*"],
            body: [
              [
                {
                  text: "Diserahkan Kepada",
                  bold: true,
                  border: [true, true, false, false],
                },
                {
                  text: ":",
                  border: [false, true, false, false],
                },
                {
                  text: "PT BINA SARANA SUKSES",
                  border: [false, true, false, false],
                },
                {
                  text: "Agen/ Transportir",
                  bold: true,
                  border: [true, true, false, false],
                },
                {
                  text: ":",
                  border: [false, true, false, false],
                },
                {
                  text: "PT RISKI JAYA ABADI MANDIRI\n\n\n",
                  border: [false, true, true, false],
                },
              ],
              [
                {
                  text: "ID. Pelanggan",
                  bold: true,
                  border: [true, false, false, false],
                },
                {
                  text: ":",
                },
                {
                  text: "PT BINA SARANA SUKSES",
                },
                {
                  text: "ID",
                  bold: true,
                  border: [true, false, false, false],
                },
                {
                  text: ":",
                },
                {
                  text: "",
                  border: [false, false, true, false],
                },
              ],
              [
                {
                  text: "Alamat",
                  bold: true,
                  border: [true, false, false, false],
                },
                {
                  text: ":",
                },
                {
                  text: "Site CDI - Kutai Barat",
                  border: [false, false, true, false],
                },
                {
                  text: "Alamat",
                  bold: true,
                  border: [true, false, false, false],
                },
                {
                  text: ":",
                },
                {
                  text: "Samarinda\n\n\n",
                  border: [false, false, true, false],
                },
              ],
              [
                {
                  text: "Penerima BBM+HP",
                  bold: true,
                  border: [true, false, false, false],
                },
                {
                  text: ":",
                },
                {
                  text: "",
                },
                {
                  text: "Driver+HP",
                  bold: true,
                  border: [true, false, false, false],
                },
                {
                  text: ":",
                },
                {
                  text: "Andika\n\n\n",
                  border: [false, false, true, false],
                },
              ],
              [
                {
                  text: "",
                  border: [true, false, false, false],
                },
                {
                  text: "",
                },
                {
                  text: "",
                },
                {
                  text: "Kenet/Helper",
                  bold: true,
                  border: [true, false, false, false],
                },
                {
                  text: ":",
                },
                {
                  text: "",
                  border: [false, false, true, false],
                },
              ],
              [
                {
                  text: "Tanggal",
                  bold: true,
                  border: [true, false, false, false],
                },
                {
                  text: ":",
                },
                {
                  text: formatDateDoc(new Date()),
                  border: [false, false, true, false],
                },
                {
                  text: "Tanggal",
                  bold: true,
                  border: [true, false, false, false],
                },
                {
                  text: ":",
                },
                {
                  text: formatDateDoc(new Date()),
                  border: [false, false, true, false],
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
            widths: ["*", "*", "*", "*", "*", "*"],
            body: [
              [
                {
                  text: "Tanggal Berlaku",
                  alignment: "center",
                  bold: true,
                  colSpan: 2,
                },
                {},
                {
                  text: "Produk",
                  alignment: "center",
                  bold: true,
                  colSpan: 2,
                },
                {},
                {
                  text: "Volume/ Kuantitas (Liter)",
                  alignment: "center",
                  bold: true,
                  colSpan: 2,
                },
                {},
              ],
              [
                {
                  text: "",
                  colSpan: 2,
                  alignment: "center",
                },
                {},
                {
                  text: "BIO DIESEL",
                  colSpan: 2,
                  alignment: "center",
                },
                {},
                {
                  text: "10,000 Liter",
                  colSpan: 2,
                  alignment: "center",
                },
                {},
              ],
              [
                {
                  text: "Dikirim Dengan",
                  bold: true,
                },
                {},
                {
                  text: "Segel Atas",
                  rowSpan: 2,
                  verticalAlignment: "middle",
                  bold: true,
                },
                {
                  text: "0009031",
                  rowSpan: 2,
                  verticalAlignment: "middle",
                  alignment: "center",
                },
                {
                  text: "Bebas Air",
                  bold: true,
                },
                {
                  text: "Ya / Tidak",
                  alignment: "center",
                },
              ],
              [
                {
                  text: "No. Kendaraan",
                  bold: true,
                },
                {
                  text: "KT 8092 NU",
                },
                {
                  text: "",
                },
                {
                  text: "",
                },
                {
                  text: "Jam Berangkat",
                  bold: true,
                },
                {
                  text: "",
                },
              ],
              [
                {
                  text: "Km. Awal",
                  bold: true,
                },
                {
                  text: "",
                },
                {
                  text: "Segel Bawah",
                  rowSpan: 2,
                  verticalAlignment: "middle",
                  bold: true,
                },
                {
                  text: "0009032",
                  rowSpan: 2,
                  verticalAlignment: "middle",
                  alignment: "center",
                },
                {
                  text: "Jam Tiba",
                  bold: true,
                },
                {
                  text: "",
                },
              ],
              [
                {
                  text: "Km. Akhir",
                  bold: true,
                },
                {
                  text: "",
                },
                {
                  text: "",
                },
                {
                  text: "",
                },
                {
                  text: "Jam Mulai Pembongkaran",
                  bold: true,
                },
                {
                  text: "",
                },
              ],
              [
                {
                  text: "SG Meter",
                  bold: true,
                },
                {
                  text: "",
                },
                {
                  text: "Temperatur",
                  bold: true,
                },
                {
                  text: "",
                },
                {
                  text: "Jam Tiba di Depo",
                  bold: true,
                },
                {
                  text: "",
                },
              ],
              [
                { text: "", border: [true, true, false, true] },
                { text: "", border: [false, true, false, true] },
                { text: "", border: [false, true, false, true] },
                { text: "", border: [false, true, false, true] },
                { text: "", border: [false, true, false, true] },
                { text: "", border: [false, true, true, true] },
              ],
              [
                {
                  text: "Jumlah (Liter)",
                  bold: true,
                },
                {
                  text: `10,000 # (${useChangeCase(angkaTerbilang(10000), "capitalCase").value} Liter) #`,
                  italics: true,
                  colSpan: 5,
                },
                {},
                {},
                {},
                {},
              ],
            ],
          },
        },
        {
          layout: {
            // defaultBorder: false,
            paddingRight: function (i) {
              return 100;
            },
            paddingLeft: function (i) {
              return 2;
            },
            paddingBottom: function (i, node) {
              return i === node.table.body.length - 1 ? 15 : 2;
            },
            paddingTop: function (i) {
              return i === 0 ? 15 : 2;
            },
            fillColor: function (i) {
              return null;
            },
          },
          table: {
            widths: ["*"],
            body: [
              [
                {
                  text: "Catatan :",
                  border: [true, false, true, false],
                },
              ],
              [
                {
                  text: "1. Sebelum BBM diserahterimakan, mohon periksa terlebih dahulu surat tera, jarum tera, segel, kualitas, SG Meter, kuantitas, kadar air, flow meter yang digunakan",
                  border: [true, false, true, false],
                },
              ],
              [
                {
                  text: "2. Setelah pembongkaran, BBM industri yang sudah diterima dengan baik dan ditanda tangani kedua belah pihak, tidak dapat dikembalikan dan BBM tersebut sudah tidak menjadi tanggung jawab kami",
                  border: [true, false, true, false],
                },
              ],
              [
                {
                  text: "3. Lainnya :",
                  border: [true, false, true, false],
                },
              ],
            ],
          },
        },
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
              return 15;
            },
            paddingTop: function (i) {
              return 2;
            },
            fillColor: function (i) {
              return null;
            },
          },
          table: {
            widths: ["*", "auto", "*", "*", "auto", "*"],
            body: [
              [
                {
                  text: "T2 DEPO",
                  bold: true,
                  border: [true, false, false, false],
                },
                {
                  text: ":",
                },
                {
                  text: "______________________",
                },
                {
                  text: "KEPEKAAN INDEX\n(buku tera mobil)",
                  bold: true,
                },
                {
                  text: ":",
                },
                {
                  text: "______________________",
                  border: [false, false, true, false],
                },
              ],
              [
                {
                  text: "T2 BONGKAR",
                  bold: true,
                  border: [true, false, false, false],
                },
                {
                  text: ":",
                },
                {
                  text: "______________________",
                },
                {
                  text: "BBM DITERIMA",
                  bold: true,
                },
                {
                  text: ":",
                },
                {
                  text: "______________________ Liter",
                  border: [false, false, true, false],
                },
              ],
            ],
          },
        },
        {
          layout: {
            // defaultBorder: false,
            paddingRight: function (i) {
              return 10;
            },
            paddingLeft: function (i) {
              return 10;
            },
            paddingBottom: function (i) {
              return 2;
            },
            paddingTop: function (i) {
              return i === 1 ? 75 : 2;
            },
            fillColor: function (i) {
              return i === 0 ? "#e5e5e5" : null;
            },
          },
          table: {
            widths: ["auto", "auto", "*", "*"],
            body: [
              [
                {
                  text: "Koordinator MAP",
                  alignment: "center",
                  bold: true,
                },
                {
                  text: "Adm. Distribusi",
                  alignment: "center",
                  bold: true,
                },
                {
                  text: "Penerima (Nama + Ttd + Stempel)",
                  alignment: "center",
                  bold: true,
                },
                {
                  text: "Driver/Officer",
                  alignment: "center",
                  bold: true,
                },
              ],
              [
                {
                  text: "Stenly B",
                  alignment: "center",
                  bold: true,
                },
                {
                  text: "Inka",
                  alignment: "center",
                  bold: true,
                },
                {
                  text: "",
                  alignment: "center",
                  bold: true,
                },
                {
                  text: "",
                  alignment: "center",
                  bold: true,
                },
              ],
              [
                { text: "", border: [true, true, false, true] },
                { text: "", border: [false, true, false, true] },
                { text: "", border: [false, true, false, true] },
                { text: "", border: [false, true, true, true] },
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
