<script setup lang="ts">
import type { StepperItem } from "@nuxt/ui";
import type { OfferingLetterPost } from "~/types/marketing";
import {
  type MarketingOLDetailsState,
  type MarketingOLFooterState,
  type MarketingOLHeaderState,
} from "~/types/schemas";

const { user } = useAuth();

const items: StepperItem[] = [
  { title: "Kop Surat Penawaran", slot: "letterHeader" },
  { title: "Rincian Penawaran", slot: "letterOfferDetails" },
  { title: "Penutup Surat Penawaran", slot: "letterFooter" },
];

const letterHeader = reactive<MarketingOLHeaderState>({
  location: "Samarinda",
  date: `${new Date().toISOString().split("T")[0]}`,
  offeringLetterNumber: "000/MAP/I-00/00",
  regarding: "Surat Penawaran Harga Bahan Bakar Minyak Bio diesel",
  receiver: "",
});

const letterOfferDetails = reactive<MarketingOLDetailsState>({
  supplyPoint: "ABC",
  qualityAssurance: "ABC",
  custodyTransfer: "ABC",
  unloadingProcedure: "ABC",
  volumeUnit: "Liter observed",
  volumeTolerance: 0.025,
  paymentTerm: 7,
  latePenalty: 0.02,
  servicePattern: "ABC",
  personInCharge: {
    name: user.value?.name || "User",
    phoneNumber: "08123456789",
  },
  paymentAddress: {
    bankName: "BANK BCA",
    accountNumber: "1234567",
    accountName: "PT. MITRA ANDALAN PETROLEUM",
  },
  fuelPrices: {
    logisticInformation: "TRUCK",
    productName: "Bio Diesel",
    basePrice: 17950,
    totalPrice: 0,
    sellingPrice: {
      ppkb: 0,
      oat: 0,
      ppn: 0,
    },
    percentageNum: {
      oat: 0,
      ppkb: 0.1,
      ppn: 0.11,
    },
  },
});

const letterFooter = reactive<MarketingOLFooterState>({
  purchaseOrderDeadline: 30,
  offeror: {
    name: user.value?.name || "User",
    signature: undefined,
  },
  companyInformation: {
    address: "Jl. Belatuk Samarinda, Indonesia",
    phoneNumber: "0541-1234567",
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

const toast = useToast();
const { post } = useApi();

async function onFooterSubmit() {
  try {
    // const res = await post<any, OfferingLetterPost>("/offering-letters", {
    //   customer_id: letterHeader.receiver,
    //   date: letterHeader.date,
    //   location: letterHeader.location,
    //   offering_letter_number: letterHeader.offeringLetterNumber,
    //   regarding: letterHeader.regarding,
    //   receiver: letterHeader.receiver,
    //   status: "created",
    //   transport_price: letterOfferDetails.fuelPrices.sellingPrice.ppn,
    //   fuel_total_price: letterOfferDetails.fuelPrices.totalPrice,
    // });
    // console.log(res);

    console.log({ ...letterHeader, ...letterOfferDetails, ...letterFooter });
  } catch (e: any) {
    toast.add({ title: "Error", description: e.message, color: "error" });
  }
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
