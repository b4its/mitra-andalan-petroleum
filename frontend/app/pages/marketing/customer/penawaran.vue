<script setup lang="ts">
import type { StepperItem } from '@nuxt/ui'
import type { ResUploads } from '~/types'
import type { OfferingLetterPost, Customer } from '~/types/marketing'
import type {
  MarketingOLDetailsState,
  MarketingOLFooterState,
  MarketingOLHeaderState,
} from "~/types/schemas";

const { user } = useAuth();
const { get } = useApi();

const { data: customerList, pending } = await useAsyncData("customers", async () => {
  const res = await get<Customer[]>("/customers");
  return res.map((receiver: Customer) => ({
    id: receiver.id,
    name: receiver.name,
    npwp: receiver.npwp,
    address: receiver.address,
    phone: receiver.phone,
    email: receiver.email,
  }));
}, { default: () => [] });

const receivers = computed(() =>
  customerList.value.map((receiver: Customer) => {
    return {
      label: receiver.name,
      value: receiver.id,
      npwp: receiver.npwp,
      address: receiver.address,
    };
  }),
);

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
    hppPrice: 0,
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
  informasiTambahan: [],
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
const { post, postFile, del } = useApi();

async function onFooterSubmit() {
  let createdId: string | null = null;
  try {
    const res = await post<any, OfferingLetterPost>("/offering-letters", {
      customer_id: letterHeader.receiver,
      date: letterHeader.date,
      location: letterHeader.location,
      offering_letter_number: letterHeader.offeringLetterNumber,
      regarding: letterHeader.regarding,
      receiver: letterHeader.receiver,
      status: "created",
      transport_price: letterOfferDetails.fuelPrices.sellingPrice.ppn,
      fuel_total_price: letterOfferDetails.fuelPrices.totalPrice,
      created_by: user.value?.id ?? null,
      details: {
        ...letterHeader,
        ...letterOfferDetails,
        ...letterFooter,
        offeror: { ...letterFooter.offeror, signature: undefined },
      },
    });
    createdId = res.id;
    console.log(res);

    const signature = letterFooter.offeror.signature;
    if (!signature) {
      throw new Error("Tanda tangan belum diunggah");
    }

    const resUpload = await postFile<ResUploads[]>('/upload', {
      files: [signature],
      folder: 'marketing',
      document_type: 'ol',
      document_id: res.id
    })

    console.log(resUpload);

    toast.add({
      title: "Sukses",
      icon: "i-lucide-check-circle",
      description: "Data Penawaran berhasil dibuat",
      color: "success",
    });

    // console.log({ ...letterHeader, ...letterOfferDetails, ...letterFooter });
  } catch (e: any) {
    if (createdId) {
      await del(`/offering-letters/${createdId}`).catch(() => undefined);
    }
    toast.add({ title: "Error", description: e.message, color: "error" });
  }
}

definePageMeta({ layout: "marketing" });
</script>

<template>
  <div v-if="pending" class="space-y-4 py-4">
    <div v-for="i in 3" :key="i" class="space-y-2">
      <USkeleton class="h-4 w-32 rounded" />
      <USkeleton class="h-10 w-full rounded-lg" />
    </div>
  </div>
  <UStepper v-else ref="stepper" disabled :items>
    <template #letterHeader>
      <MarketingOLHeaderForm
        v-model="letterHeader"
        :receivers="receivers"
        :has-previous="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onHeaderSubmit"
      />
    </template>

    <template #letterOfferDetails>
      <MarketingOLDetailsForm
        v-model="letterOfferDetails"
        :has-previous="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onDetailsSubmit"
      />
    </template>

    <template #letterFooter>
      <MarketingOLFooterForm
        v-model="letterFooter"
        :has-previous="stepper?.hasPrev"
        @previous="previousNavigation"
        @submit="onFooterSubmit"
      />
    </template>
  </UStepper>
</template>
