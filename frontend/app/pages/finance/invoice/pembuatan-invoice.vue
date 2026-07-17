<script setup lang="ts">
import type { StepperItem, NavigationMenuItem } from "@nuxt/ui";
import type {
  FinanceInvoiceDetailsState,
  FinanceInvoiceFooterState,
  FinanceInvoiceHeaderState,
  FinanceInvoiceProductsState,
} from "~/types/schemas";

const items: StepperItem[] = [
  { title: "Kop Invoice", slot: "invoiceHeader" },
  { title: "Informasi Invoice", slot: "invoiceDetails" },
  { title: "Rincian Produk", slot: "invoiceProducts" },
  { title: "Penutup Invoice", slot: "invoiceFooter" },
];

const financeHeader = reactive<FinanceInvoiceHeaderState>({
  billToInformation:
    "PT. MITRA ANDALAN PETROLEUM\nJl. Belatuk No. 63 Samarinda, 75117 Indonesia",
  deliveryPointInformation:
    "PT. MIGAS KUKAR MANDIRI\nJl. KH AGUS SALIM No. 32 SAMARINDA",
  companyInformation: {
    name: "PT. MITRA ANDALAN PETROLEUM",
    address: "Jl. Belatuk No. 63 Samarinda, 75117 Indonesia",
    phoneNumber: "0541-2832313", // add masking
    email: "marketing.mapetroleum@gmail.com",
  },
});
const financeDetails = reactive<FinanceInvoiceDetailsState>({
  invoiceInformation: {
    invoiceNumber: "1086/INV/MAP/V/2026",
    invoiceDate: `${new Date().toISOString().split("T")[0]}`,
    invoiceDueDate: `${new Date().toISOString().split("T")[0]}`,
    terms: 45,
  },
  customerPurchaseInformation: {
    deliveryOrderNumberData: ["1086/DO/MAP/V/2026"],
    customerPurchaseOrderNumber: "1200020175",
    taxInvoiceNumber: "04002000909090",
    salesOrderNumber: undefined,
  },
});
const financeProducts = reactive<FinanceInvoiceProductsState>({
  products: [
    {
      name: "Bio Diesel",
      qty: 20000,
      unit: "Liter",
      price: 19500,
      totalPrice: 0,
    },
  ],
  priceSummary: {
    grandTotal: 0,
    subTotal: 0,
    ppn: 0,
    spellNumber: "",
    discount: undefined,
    prePaid: undefined,
  },
});
const financeFooter = reactive<FinanceInvoiceFooterState>({
  termsAndCondition: [
    {
      term: "Term 1",
    },
  ],
  paymentInformation: {
    bankName: "MANDIRI - Cab Segiri",
    accountNumber: "1480002719998",
    accountName: "PT. MITRA ANDALAN PETROLEUM",
  },
  signature: {
    companyName: "PT. MITRA ANDALAN PETROLEUM",
    createdBy: "Syannet",
  },
});

const stepper = useTemplateRef("stepper");

function previousNavigation() {
  stepper.value?.prev();
}

function onFormSubmitToNext() {
  stepper.value?.next();
}

function onFormSubmit() {
  console.log("Data submitted");
  console.log({
    ...financeHeader,
    ...financeDetails,
    ...financeProducts,
    ...financeFooter,
  });
}

definePageMeta({ layout: "finance" });
</script>

<template>
  <UStepper disabled ref="stepper" :items>
    <template #invoiceHeader>
      <FinanceInvoiceHeaderForm
        v-model="financeHeader"
        :hasPrevious="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>

    <template #invoiceDetails>
      <FinanceInvoiceDetailsForm
        v-model="financeDetails"
        :hasPrevious="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>

    <template #invoiceProducts>
      <FinanceInvoiceProductsForm
        v-model="financeProducts"
        :hasPrevious="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>

    <template #invoiceFooter>
      <FinanceInvoiceFooterForm
        v-model="financeFooter"
        :hasPrevious="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmit"
      />
    </template>
  </UStepper>
</template>
