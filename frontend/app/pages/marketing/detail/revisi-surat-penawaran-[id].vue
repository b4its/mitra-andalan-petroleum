<script setup lang="ts">
import type { StepperItem } from "@nuxt/ui";
import type { ResUploads, Uploads } from "~/types";
import type { Customer, OfferingLetterPost } from "~/types/marketing";
import {
  type MarketingOLDetailsState,
  type MarketingOLFooterState,
  type MarketingOLHeaderState,
} from "~/types/schemas";

const toast = useToast();
const { get, put, postFile } = useApi();

const { data: customerList } = await useAsyncData("customers", async () => {
  const res = await get<Customer[]>("/customers");
  return res.map((receiver: Customer) => ({
    id: receiver.id,
    name: receiver.name,
    address: receiver.address,
    phone: receiver.phone,
    email: receiver.email,
  }));
});

const receivers = ref(
  customerList.value?.map((receiver: Customer) => {
    return {
      label: receiver.name,
      value: receiver.id,
      address: receiver.address,
    };
  }),
);

const items: StepperItem[] = [
  { title: "Kop Surat Penawaran", slot: "letterHeader" },
  { title: "Rincian Penawaran", slot: "letterOfferDetails" },
  { title: "Penutup Surat Penawaran", slot: "letterFooter" },
];

// fetch data based on id and insert into each reactive
const route = useRoute();
const idOfferingLetter = route.params.id;

const { data: offeringLetter } = await useAsyncData(
  "offering-letter",
  async () => {
    const res = await get<OfferingLetterPost>(
      `/offering-letters/${idOfferingLetter}`,
    );
    return res;
  },
);

const letterHeader = reactive<MarketingOLHeaderState>({
  location: offeringLetter.value?.details.location || "",
  date:
    new Date(offeringLetter.value?.details.date || new Date())
      .toISOString()
      .split("T")[0] ?? "",
  offeringLetterNumber: offeringLetter.value?.offering_letter_number || "",
  regarding: offeringLetter.value?.details.regarding || "",
  receiver: offeringLetter.value?.details.receiver || "",
});

const letterOfferDetails = reactive<MarketingOLDetailsState>({
  supplyPoint: offeringLetter.value?.details.supplyPoint || "",
  qualityAssurance: offeringLetter.value?.details.qualityAssurance || "",
  custodyTransfer: offeringLetter.value?.details.custodyTransfer || "",
  unloadingProcedure: offeringLetter.value?.details.unloadingProcedure || "",
  volumeUnit: offeringLetter.value?.details.volumeUnit || "",
  volumeTolerance: offeringLetter.value?.details.volumeTolerance || 0,
  paymentTerm: offeringLetter.value?.details.paymentTerm || 0,
  latePenalty: offeringLetter.value?.details.latePenalty || 0,
  servicePattern: offeringLetter.value?.details.servicePattern || "",
  personInCharge: {
    name: offeringLetter.value?.details.personInCharge.name || "",
    phoneNumber: offeringLetter.value?.details.personInCharge.phoneNumber || "",
  },
  paymentAddress: {
    bankName: offeringLetter.value?.details.paymentAddress.bankName || "",
    accountNumber:
      offeringLetter.value?.details.paymentAddress.accountNumber || "",
    accountName: offeringLetter.value?.details.paymentAddress.accountName || "",
  },
  fuelPrices: {
    logisticInformation:
      offeringLetter.value?.details.fuelPrices.logisticInformation || "",
    productName: offeringLetter.value?.details.fuelPrices.productName || "",
    basePrice: offeringLetter.value?.details.fuelPrices.basePrice || 0,
    totalPrice: offeringLetter.value?.details.fuelPrices.totalPrice || 0,
    sellingPrice: {
      ppkb: offeringLetter.value?.details.fuelPrices.sellingPrice.ppkb || 0,
      oat: offeringLetter.value?.details.fuelPrices.sellingPrice.oat || 0,
      ppn: offeringLetter.value?.details.fuelPrices.sellingPrice.ppn || 0,
    },
    percentageNum: {
      oat: offeringLetter.value?.details.fuelPrices.percentageNum.oat || 0,
      ppkb: offeringLetter.value?.details.fuelPrices.percentageNum.ppkb || 0,
      ppn: offeringLetter.value?.details.fuelPrices.percentageNum.ppn || 0,
    },
  },
});

const letterFooter = reactive<MarketingOLFooterState>({
  purchaseOrderDeadline:
    offeringLetter.value?.details.purchaseOrderDeadline || 0,
  offeror: {
    name: offeringLetter.value?.details.offeror.name || "",
    signature: undefined,
  },
  companyInformation: {
    address: offeringLetter.value?.details.companyInformation.address || "",
    phoneNumber:
      offeringLetter.value?.details.companyInformation.phoneNumber || "", // add masking
    email: offeringLetter.value?.details.companyInformation.email || "",
  },
});

const { data: signature } = await useAsyncData("signature", async () => {
  const res = await get<ResUploads[]>(
    `/uploads?document_type=ol&document_id=${letterHeader.offeringLetterNumber}`,
  );

  return {
    url: res[0]?.url,
  };
});

async function loadExistingFile() {
  const url = `http://localhost:8000${signature.value?.url}`;
  const response = await fetch(url);
  const blob = await response.blob();
  const filename = url.split("/").pop()!;
  letterFooter.offeror.signature = new File([blob], filename, {
    type: blob.type,
  });
}

onMounted(loadExistingFile);

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

async function onFooterSubmit() {
  try {
    const res = await put<any, OfferingLetterPost>(
      `/offering-letters/${idOfferingLetter}`,
      {
        customer_id: letterHeader.receiver,
        date: letterHeader.date,
        location: letterHeader.location,
        offering_letter_number: letterHeader.offeringLetterNumber,
        regarding: letterHeader.regarding,
        receiver: letterHeader.receiver,
        status: "under_revision",
        transport_price: letterOfferDetails.fuelPrices.sellingPrice.ppn,
        fuel_total_price: letterOfferDetails.fuelPrices.totalPrice,
        details: {
          ...letterHeader,
          ...letterOfferDetails,
          ...letterFooter,
        },
      },
    );
    console.log(res);

    const signature = letterFooter.offeror.signature;
    if (!signature) {
      throw new Error("Tanda tangan belum diunggah");
    }

    const resUpload = await postFile<Uploads>("/upload", {
      files: [signature],
      folder: "marketing",
      document_type: "ol",
      document_id: letterHeader.offeringLetterNumber,
    });

    console.log(resUpload);

    toast.add({
      title: "Sukses",
      icon: "i-lucide-check-circle",
      description: "Data Penawaran berhasil dibuat",
      color: "success",
    });

    // console.log({ ...letterHeader, ...letterOfferDetails, ...letterFooter });
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
        :receivers="receivers"
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
