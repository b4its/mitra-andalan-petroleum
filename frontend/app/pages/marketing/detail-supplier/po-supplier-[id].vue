<script setup lang="ts">
// @ts-nocheck
import type {
  Details,
  PaymentAddress,
  Product,
  PurchaseOrderDetails,
} from "~/types/marketing";

const pdfLink = ref<string | null>(null);
const route = useRoute();
const idPoLetter = route.params.id;
const { user } = useAuth();

const { get } = useApi();

const { data: purchaseOrderDetails } = await useAsyncData(
  "purchase-order-detail-po-supplier",
  async () => {
    const res = await get<PurchaseOrderDetails>(
      `/purchase-orders/${idPoLetter}`,
    );
    return res;
  },
);

const details: Details = purchaseOrderDetails.value?.details;
const products: Product[] = details.products || [];
const paymentAddress: PaymentAddress = details.paymentAddress || {};

// 2. Initialize the table body array with the Header row
const tableBodyDetails = [
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

// 3. Generate exactly 8 rows reserved for products
for (let i = 0; i < 8; i++) {
  if (i < products.length) {
    // If product exists, populate the data
    const product = products[i];
    tableBodyDetails.push([
      {
        text: (i + 1).toString(),
        alignment: "center",
        border: [true, false, true, true],
      },
      {
        text: product.name || "",
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
    // If no product, output a blank row but keep the borders intact for the grid
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

// 4. Blank row ABOVE VAT
tableBodyDetails.push([{}, {}, {}, {}, {}, {}]);

// 5. VAT Row
tableBodyDetails.push([
  {},
  { text: `Include VAT ${formatPercent(details.vat || 0)}`, bold: true },
  {},
  {},
  {},
  {},
]);

// 6. Blank row BELOW VAT
tableBodyDetails.push([{}, {}, {}, {}, {}, {}]);

// 7. Transfer Detail Header
tableBodyDetails.push([
  {},
  { text: "Transfer Detail :", bold: true },
  {},
  {},
  {},
  {},
]);

// 8. 3 Reserved rows for Payment Address details
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
  },
  {},
  {},
  {},
  {},
]);

// 9. Blank row BELOW "No. Rek."
tableBodyDetails.push([{}, {}, {}, {}, {}, {}]);

// 10. Subtotal Row
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

const loadPdf = async () => {
  const pdfMake = usePDFMake();
  if (!pdfMake) return;

  pdfLink.value = await pdfMake
    .createPdf({
      info: {
        title: `Purchase Order (${purchaseOrderDetails.value?.po_number}) | ${purchaseOrderDetails.value?.supplier_name}`,
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
              return i === 0 ? "#e5e5e5" : null;
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
                      text: `${purchaseOrderDetails.value?.supplier_name}\n`,
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
                  text: `Jarak KM : ${formatToKm(details.delivery.distance) || ""}\nLoading Terminal : ${details.delivery.loadingTerminal || ""}\nLoading Date : ${details.delivery.loadingDate || ""}\nPIC OPERATION MAP : ${details.delivery.picOperationMap || ""}`,
                  border: [true, false, true, true],
                },
                {
                  text: `Trucking : ${details.forwarder.trucking}`,
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
                      text: `${details.signed.createdBy || ""}`,
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
                      text: `${details.signed.approvedBy || ""}`,
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
