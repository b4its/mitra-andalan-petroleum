<script setup lang="ts">
import type { StepperItem } from "@nuxt/ui";

const items: StepperItem[] = [
  { title: "Kop Surat Penawaran", slot: "letterHeader" },
  { title: "Rincian Penawaran", slot: "letterOfferDetails" },
  { title: "Penutup Surat Penawaran", slot: "letterFooter" },
];

// fetch data based on id and insert into each reactive
const route = useRoute();
const idOfferingLetter = route.params.id;

const letterHeader = reactive({
  location: "Samarinda",
  date: `${new Date().toISOString().split("T")[0]}`,
  offeringLetterNumber: "722/MAP/II-06/26",
  regarding: "Surat Penawaran Harga Bahan Bakar Minyak Bio diesel",
  receiver: "",
});

const letterOfferDetails = reactive({
  supplyPoint: "Terminal Bahan Bakar Minyak (TBBM) Palaran",
  qualityAssurance: "Sesuai dengan spesifikasi SK Dirjen Migas",
  custodyTransfer:
    "Flowmeter terkalibrasi oleh instansi berwenang di TBBM Palaran",
  unloadingProcedure: "Jarum Tera/Sounding Tanki Truck di lokasi penerima",
  volumeUnit: "Liter observed",
  volumeTolerance: 0.025,
  paymentTerm: 7,
  latePenalty: 0.02,
  servicePattern: "Franco Penerima",
  personInCharge: {
    name: "Stenly",
    phoneNumber: "08123456789",
  },
  paymentAddress: {
    bankName: "BANK MANDIRI cab Segiri",
    accountNumber: "1480002719998",
    accountName: "PT. MITRA ANDALAN PETROLEUM",
  },
  fuelPrices: {
    logisticInformation: "TRUCK 10 KL Site BSSR / BAS Tanah Datar",
    productName: "Bio Diesel B50 / B40 if stock still",
    sellingPrice: {
      ppkb: 17950,
      oat: 450,
    },
    ppn: 2024,
  },
});

const letterFooter = reactive({
  purchaseOrderDeadline: 30,
  offeror: {
    name: "Stenly Boseke",
    signature: "map-signature.png",
  },
  companyInformation: {
    address: "Jl. Belatuk No. 63 Samarinda, 75117 Indonesia",
    phoneNumber: "0541-2832313", // add masking
    email: "marketing.mapetroleum@gmail.com",
  },
});

const stepper = useTemplateRef("stepper");

function previousNavigation() {
  stepper.value?.prev();
}

function onHeaderSubmit() {
  stepper.value?.next();
}

function onDetailsSubmit() {
  stepper.value?.next();
}

function onFooterSubmit() {
  console.log("Data submitted");
  console.log({ ...letterHeader, ...letterOfferDetails, ...letterFooter });
}

definePageMeta({ layout: "marketing" });
</script>

<template>
  <UStepper disabled ref="stepper" :items>
    <template #letterHeader>
      <MarketingOLHeaderForm
        v-model="letterHeader"
        :hasPrevious="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onHeaderSubmit"
      />
    </template>

    <template #letterOfferDetails>
      <MarketingOLDetailsForm
        v-model="letterOfferDetails"
        :hasPrevious="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onDetailsSubmit"
      />
    </template>

    <template #letterFooter>
      <MarketingOLFooterForm
        v-model="letterFooter"
        :hasPrevious="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFooterSubmit"
      />
    </template>
  </UStepper>
</template>
