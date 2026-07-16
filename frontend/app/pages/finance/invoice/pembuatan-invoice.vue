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

const financeHeader = reactive<FinanceInvoiceHeaderState>({});
const financeDetails = reactive<FinanceInvoiceDetailsState>({});
const financeProducts = reactive<FinanceInvoiceProductsState>({});
const financeFooter = reactive<FinanceInvoiceFooterState>({});

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

const links = [
  [
    {
      label: "Buat Delivery Order",
      icon: "i-lucide-truck",
      to: "/operations/delivery-order",
    },
    {
      label: "Upload Delivery Order (Yang sudah dikembalikan)",
      icon: "i-lucide-file-output",
      to: "/operations/delivery-order-returned",
    },
  ],
] satisfies NavigationMenuItem[][];

definePageMeta({ layout: "operations" });
</script>

<template>
  <UStepper disabled ref="stepper" :items>
    <template #invoiceHeader>
      <InvoiceHeaderForm
        v-model="financeHeader"
        :hasPrevious="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>

    <template #invoiceDetails>
      <InvoiceDetailsForm
        v-model="financeDetails"
        :hasPrevious="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>

    <template #invoiceProducts>
      <InvoiceProductsForm
        v-model="financeProducts"
        :hasPrevious="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>

    <template #invoiceFooter>
      <InvoiceFooterForm
        v-model="financeFooter"
        :hasPrevious="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>
  </UStepper>
</template>
