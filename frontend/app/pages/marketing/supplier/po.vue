<script setup lang="ts">
import type { StepperItem } from "@nuxt/ui";
import {
  marketingPOAdditionalSchema,
  marketingPOAssociateSchema,
  marketingPOCompanySchema,
  marketingPODetailsSchema,
  type MarketingPOAdditionalState,
  type MarketingPOAssociateState,
  type MarketingPOCompanyState,
  type MarketingPODetailsState,
} from "~/types/schemas";

const items: StepperItem[] = [
  { title: "Informasi Perusahaan", slot: "companyInformation" },
  { title: "Informasi Mitra", slot: "associateInformation" },
  { title: "Detail Purchase Order", slot: "poDetails" },
  { title: "Informasi Tambahan", slot: "additionalDetails" },
];

const letterCompanyMain = reactive<MarketingPOCompanyState>({
  companyInformation: {
    name: "PT. MITRA ANDALAN PETROLEUM",
    address: "Jl. Belatuk No. 63 Samarinda, 75117 Indonesia",
    npwp: "43.170.319.8-722.000",
    contactPerson: "0812 3456 7898", // add masking
    email: "marketing.mapetroleum@gmail.com",
  },
});

const letterCompanyAssociate = reactive<MarketingPOAssociateState>({
  associateInformation: {
    name: "PT. MIGAS KUKAR MANDIRI",
    address: "Jl. KH AGUS SALIM No. 32 SAMARINDA",
  },
});

const letterOfferDetails = reactive<MarketingPODetailsState>({
  po: {
    date: `${new Date().toISOString().split("T")[0]}`,
    number: "0543/PO/MAP/I/05/26",
  },
  vat: 0.11,
  paymentAddress: {
    bankName: "Bank Central Asia Cabang Sudirman, Samarinda",
    accountNumber: "027 8091972",
    accountName: "PT. Migas Kukar Mandiri",
  },
  products: [
    {
      name: "Bio Diesel",
      qty: 20000,
      unit: "Liter",
      price: 21800,
      totalPrice: 0,
    },
  ],
  totalProductsPrice: 0,
});

const letterAdditional = reactive<MarketingPOAdditionalState>({
  termAndCondition: "CBD",
  delivery: {},
  forwarder: {
    trucking: "TBA",
  },
  signed: {
    createdBy: "Fitri",
    approvedBy: "Stenly B",
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
    ...letterCompanyMain,
    ...letterCompanyAssociate,
    ...letterOfferDetails,
    ...letterAdditional,
  });
}

definePageMeta({ layout: "marketing" });
</script>

<template>
  <UStepper disabled ref="stepper" :items>
    <template #companyInformation>
      <MarketingPOCompanyForm
        v-model="letterCompanyMain"
        :hasPrevious="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>

    <template #associateInformation>
      <MarketingPOAssociateForm
        v-model="letterCompanyAssociate"
        :hasPrevious="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>

    <template #poDetails>
      <MarketingPODetailsForm
        v-model="letterOfferDetails"
        :hasPrevious="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmitToNext"
      />
    </template>

    <template #additionalDetails>
      <MarketingPOAdditionalForm
        v-model="letterAdditional"
        :hasPrevious="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFormSubmit"
      />
    </template>
  </UStepper>
</template>
