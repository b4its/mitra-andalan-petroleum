<script setup lang="ts">
import type { StepperItem, NavigationMenuItem } from "@nuxt/ui";
import {
  type OperationsDOAdditionalState,
  type OperationsDODetailsTransportState,
  type OperationsDOFooterState,
  type OperationsDOHeaderState,
  type OperationsDOReceiverState,
  type OperationsDOTransportState,
} from "~/types/schemas";

const items: StepperItem[] = [
  { title: "Kop Surat Delivery Order", slot: "doHeader" },
  { title: "Mitra Penerima", slot: "doReceiver" },
  { title: "Agen/Transportir", slot: "doTransport" },
  { title: "Rincian Pengiriman", slot: "doDetailsTransport" },
  { title: "Catatan Tambahan", slot: "doAdditional" },
  { title: "Penutup Surat Delivery Order", slot: "doFooter" },
];

const doHeader = reactive<OperationsDOHeaderState>({
  companyInformation: {
    name: "PT. MITRA ANDALAN PETROLEUM",
    nameSub: "Distributor for Elnusa Petrofin",
    address: "Jl. Belatuk No. 63 Samarinda, 75117 Indonesia",
    phoneNumber: "0541-2832313", // add masking
  },
  doInformation: {
    doNumber: "1086/DO/MAP/V/2026",
    doDateCreated: `${new Date().toISOString().split("T")[0]}`,
    poCustomerNumber: undefined,
    soNumber: undefined,
  },
});
const doReceiver = reactive<OperationsDOReceiverState>({
  customerName: "PT. Sinergi Agro Industri",
  customerId: "PT. Sinergi Agro Industri",
  address: "Kebun Belidan",
  receiverInformation: {
    name: undefined,
    phoneNumber: undefined,
  },
  dateReceived: `${new Date().toISOString().split("T")[0]}`,
});
const doTransport = reactive<OperationsDOTransportState>({
  transportName: "PT. Karya Bersaudara Sinergi",
  transportId: "PT. Karya Bersaudara Sinergi",
  address: "Samarinda",
  driverInformation: {
    name: "Heru Irawan",
    phoneNumber: undefined,
  },
  dateReceived: `${new Date().toISOString().split("T")[0]}`,
});
const doDetailsTransport = reactive<OperationsDODetailsTransportState>({
  dueDate: undefined,
  total: 5000,
  productInformation: {
    name: "Bio diesel",
    qty: 5000,
    topSeal: undefined,
    bottomSeal: undefined,
    temperature: 0,
  },
  transportInformation: {
    startKm: undefined,
    endKm: undefined,
    sgMeter: undefined,
    // isWaterFree: true, // need to discuss
    timeInformation: {
      departureTime: undefined,
      arrivalTime: undefined,
      depotArrivalTime: undefined,
      unloadingTime: undefined,
    },
    transportNumber: "KT 8518 WB",
    transportType: undefined,
  },
});
const doAdditional = reactive<OperationsDOAdditionalState>({
  notes: [
    {
      note: "Catatan Tambahan 1",
    },
    {
      note: "Catatan Tambahan 2",
    },
    {
      note: "Lainnya :",
    },
  ],
  t2Depot: undefined,
  t2Unloading: undefined,
  indexSensitivity: undefined,
  fuelReceived: 5000,
});
const doFooter = reactive<OperationsDOFooterState>({
  companyCoordinator: "Stenly B",
  distributionAdmin: "Inka",
  receiver: undefined,
  driver: undefined,
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
    ...doHeader,
    ...doReceiver,
    ...doTransport,
    ...doDetailsTransport,
    ...doAdditional,
    ...doFooter,
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
  <UDashboardPanel :ui="{ body: 'w-full' }" id="do">
    <template #header>
      <UDashboardNavbar
        title="Form Pembuatan Delivery Order"
        :ui="{ right: 'gap-3' }"
      >
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>

      <UDashboardToolbar>
        <template #left>
          <!-- NOTE: The `-ms-1` class is used to align with the `DashboardSidebarCollapse` button here. -->
          <UNavigationMenu :items="links" highlight class="-mx-1 flex-1" />
        </template>
      </UDashboardToolbar>
    </template>

    <template #body>
      <UStepper disabled ref="stepper" :items>
        <template #doHeader>
          <OperationsDOHeaderForm
            v-model="doHeader"
            :hasPrevious="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmitToNext"
          />
        </template>

        <template #doReceiver>
          <OperationsDOReceiverForm
            v-model="doReceiver"
            :hasPrevious="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmitToNext"
          />
        </template>

        <template #doTransport>
          <OperationsDOTransportForm
            v-model="doTransport"
            :hasPrevious="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmitToNext"
          />
        </template>

        <template #doDetailsTransport>
          <OperationsDODetailsTransportForm
            v-model="doDetailsTransport"
            :hasPrevious="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmitToNext"
          />
        </template>

        <template #doAdditional>
          <OperationsDOAdditionalForm
            v-model="doAdditional"
            :hasPrevious="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmitToNext"
          />
        </template>

        <template #doFooter>
          <OperationsDOFooterForm
            v-model="doFooter"
            :hasPrevious="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmit"
          />
        </template>
      </UStepper>
    </template>
  </UDashboardPanel>
</template>
