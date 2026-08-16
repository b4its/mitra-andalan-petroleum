<script setup lang="ts">
import type { TableCell } from "pdfmake";
import logoImage from "~/assets/images/map-logo.jpeg";
import type { DeliveryOrdersDetails, Details } from "~/types/operations";

const pdfLink = ref<string | null>(null);
const route = useRoute();
const idDoLetter = route.params.id;
const { user } = useAuth();
const { get } = useApi();

const { data: doDetails, pending } =
  await useAsyncData<DeliveryOrdersDetails | null>(
    "po-transportir-details",
    async () => {
      const res = await get<DeliveryOrdersDetails>(
        `/delivery-orders/${idDoLetter}`,
      );
      return res;
    },
    { default: () => null, server: false },
  );

const details = computed<Details | null>(
  () => doDetails.value?.details ?? null,
);

const tableBodyDetails: TableCell[][] = [
  [
    {
      text: "NO",
      bold: true,
      verticalAlignment: "middle",
      alignment: "center",
    },
    {
      text: "DESKRIPSI",
      bold: true,
      verticalAlignment: "middle",
      alignment: "center",
    },
    {
      text: "Tanggal Loading",
      bold: true,
      verticalAlignment: "middle",
      alignment: "center",
    },
    {
      text: "Tanggal Bongkar",
      bold: true,
      verticalAlignment: "middle",
      alignment: "center",
    },
    {
      text: "VOL\n(LITER)",
      bold: true,
      verticalAlignment: "middle",
      alignment: "center",
    },
    {
      text: "RATE/LITER\n(RP.)",
      bold: true,
      verticalAlignment: "middle",
      alignment: "center",
    },
    {
      text: "TOTAL (Rp.)",
      bold: true,
      verticalAlignment: "middle",
      alignment: "center",
    },
  ],
];

let count = 1;
const productsDummy = [
  {
    name: "Bio Solar",
    loadingDate: "08-07-2026",
    unloadingDate: "08-07-2026",
    qty: 20_000,
    ratePrice: 300,
    totalPrice: 6_000_000,
  },
];

for (const product of productsDummy) {
  tableBodyDetails.push([
    {
      text: count.toString(),
      alignment: "center",
    },
    {
      text: product.name || "",
      alignment: "left",
    },
    {
      text: formatDateDoc(product.loadingDate) || "",
      alignment: "center",
    },
    {
      text: formatDateDoc(product.unloadingDate) || "",
      alignment: "center",
    },
    {
      text: product.qty || "",
      alignment: "center",
    },
    {
      text: formatCurrency(product.ratePrice) || "",
      alignment: "center",
    },
    {
      text: formatCurrency(product.totalPrice) || "",
      alignment: "center",
    },
  ]);
  count++;
}

tableBodyDetails.push([
  {
    text: "Total",
    bold: true,
    alignment: "center",
    colSpan: 6,
  },
  {},
  {},
  {},
  {},
  {},
  {
    text: `${formatCurrency(6_000_000)}`,
    alignment: "center",
  },
]);

tableBodyDetails.push([
  {
    text: "PPN",
    bold: true,
    alignment: "center",
    colSpan: 6,
  },
  {},
  {},
  {},
  {},
  {},
  {
    text: `${formatCurrency(660_000)}`,
    alignment: "center",
  },
]);

tableBodyDetails.push([
  {
    text: "Grand Total",
    bold: true,
    alignment: "center",
    colSpan: 6,
  },
  {},
  {},
  {},
  {},
  {},
  {
    text: `${formatCurrency(6_660_000)}`,
    alignment: "center",
  },
]);

const loadPdf = async () => {
  const pdfMake = usePDFMake();
  if (!pdfMake) return;
  const d = details.value;
  if (!d) return;

  const today = new Date();
  const romanMonths = [
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI",
    "VII",
    "VIII",
    "IX",
    "X",
    "XI",
    "XII",
  ];

  pdfLink.value = await pdfMake
    .createPdf({
      info: {
        title: `Purchase Order Transportir (${d.doInformation?.doNumber || ""})`,
        author: "PT. Mitra Andalan Petroleum",
        creator: user.value?.name,
        producer: "PT. Mitra Andalan Petroleum",
      },
      pageMargins: [72, 10, 48, 10],
      pageSize: "A4",
      content: [
        {
          image: await toBase64(logoImage),
          width: 160,
          marginLeft: -20,
        },
        {
          text: `Samarinda, ${formatDateDoc(new Date().toISOString().split("T")[0])}`,
          alignment: "right",
          marginRight: 35,
        },
        {
          layout: {
            defaultBorder: false,
            paddingLeft: function (i) {
              return i === 2 ? -2 : 0;
            },
            paddingTop: function (i) {
              return i === 0 ? 15 : 0;
            },
          },
          table: {
            widths: ["auto", "auto", "*"],
            body: [
              [
                {
                  text: "Perihal",
                  marginRight: 10,
                },
                {
                  text: ":",
                },
                {
                  text: `Purchase Order Transportir (PO)`,
                },
              ],
              [
                {
                  text: "Nomor",
                  marginRight: 10,
                },
                {
                  text: ":",
                },
                {
                  text: `368/PO-TRANS/MAP/VIII/2026`,
                },
              ],
            ],
          },
        },
        {
          marginTop: 15,
          marginBottom: 2,
          text: "Kepada Yth.",
        },
        {
          text: `PT. Anugrah Mahakam Energy`,
          bold: true,
        },
        {
          text: `PIC: Bpk Hence`,
          bold: true,
          marginTop: 15,
          marginBottom: 15,
        },
        {
          text: "Berikut ini kami kirimkan Purchase Order dengan detail sebagai berikut:",
          marginBottom: 15,
        },

        {
          layout: {
            // paddingTop: function (i) {
            //   return i === 0 ? 0 : 0;
            // },
            // paddingBottom: function (i) {
            //   return i === 0 ? 0 : 0;
            // },
            paddingLeft: function (i) {
              return 5;
            },
            paddingRight: function (i) {
              return 5;
            },
          },
          marginLeft: 5,
          table: {
            widths: ["auto", "*", "*", "*", "auto", "auto", "*"],
            body: tableBodyDetails,
          },
        },
        {
          layout: {
            defaultBorder: false,
          },
          marginTop: 10,
          table: {
            widths: ["auto", "25%", "auto", "*"],
            body: [
              [
                {
                  text: "1.",
                },
                {
                  text: "Loading",
                  // marginRight: 25,
                },
                {
                  text: ":",
                },
                {
                  text: `Masbro, Pendingin, Kutai Kartanegara, Kalimantan Timur`,
                  marginLeft: -5,
                },
              ],
              [
                {
                  text: "2.",
                },
                {
                  text: "Discharge",
                  // marginRight: 25,
                },
                {
                  text: ":",
                },
                {
                  text: `PT. Bina Sarana Sukses\nSite TDM /Separi - Kutai Kartanegara`,
                  bold: true,
                  marginLeft: -5,
                },
              ],
              [
                {
                  text: "3.",
                },
                {
                  text: "Terms of Payment",
                  // marginRight: 25,
                },
                {
                  text: ":",
                },
                {
                  text: `30 Hari kerja setelah invoice beserta kelengkapan dokumen selesai diverifikasi`,
                  marginLeft: -5,
                },
              ],
              [
                {
                  text: "4.",
                },
                {
                  text: `Toleransi susut 0.9 %, Claim Susut Rp. 25.000,- / Liter`,
                  bold: true,
                  colSpan: 3,
                },
                {},
                {},
              ],
              [
                {
                  text: "5.",
                },
                {
                  text: "Contact Person",
                  colSpan: 3,
                },
                {},
                {},
              ],
            ],
          },
        },
        {
          layout: {
            paddingTop: function (i) {
              return i === 1 ? 10 : 0;
            },
            paddingBottom: function (i, node) {
              return i === node.table.body.length - 1 ? 10 : 0;
            },
          },
          marginTop: 10,
          table: {
            widths: ["35%", "35%"],
            body: [
              [
                {
                  text: `PT. Mitra Andalan Petroleum`,
                  bold: true,
                  alignment: "center",
                },
                {
                  text: `PT. Bina Sarana Sukses`,
                  bold: true,
                  alignment: "center",
                },
              ],
              [
                {
                  text: `1.   Aditya\n Telp: 0812 3456 7890`,
                  border: [true, false, true, false],
                },
                {
                  text: "",
                  border: [true, false, true, false],
                },
              ],
              [
                {
                  text: `2.   Fitri\n Telp: 0812 3456 7890`,
                  border: [true, false, true, true],
                },
                {
                  text: "",
                  border: [true, false, true, true],
                },
              ],
            ],
          },
        },
        {
          text: "Hormat Kami,",
          marginTop: 25,
          marginBottom: logoImage ? 5 : 30,
        },
        {
          image: await toBase64(logoImage),
          width: 90,
        },
        {
          text: `(Stenly Boseke)`,
          marginTop: 30,
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
          marginLeft: 290,
          marginTop: 75,
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
                  text: `Jl Belatuk 63, Temindung Permai Samarinda, Indonesia`,
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
    <div v-if="pending" class="h-full w-full space-y-4 p-8">
      <USkeleton class="h-8 w-64 rounded" />
      <USkeleton class="h-6 w-48 rounded" />
      <USkeleton class="h-4 w-80 rounded" />
      <USkeleton class="h-40 w-full rounded-lg" />
    </div>
    <iframe v-else-if="pdfLink" :src="pdfLink" class="h-full w-full" />
    <div
      v-else-if="!details"
      class="flex flex-col items-center justify-center h-full gap-3 text-muted"
    >
      <UIcon name="i-lucide-file-x" class="size-12" />
      <p class="text-sm font-medium">Data PO Transportir Belum Lengkap</p>
    </div>
  </main>
</template>
