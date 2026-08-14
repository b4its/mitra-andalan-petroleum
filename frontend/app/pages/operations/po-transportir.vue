<script setup lang="ts">
import type { StepperItem, NavigationMenuItem } from "@nuxt/ui";
import type { Customer, PurchaseOrdersSupplier } from "~/types/marketing";
import type {
  DeliveryOrderPost,
  DeliveryOrdersDetails,
} from "~/types/operations";
import type {
  OperationsDOAdditionalState,
  OperationsDODetailsTransportState,
  OperationsDOFooterState,
  OperationsDOHeaderState,
  OperationsDOReceiverState,
  OperationsDOTransportState,
  OperationsPOTransportDetailsState,
  OperationsPOTransportFooterState,
  OperationsPOTransportHeaderState,
} from "~/types/schemas";

const { user } = useAuth();
const { get, put, post } = useApi();
const toast = useToast();
const route = useRoute();
const loading = ref(false);

const items: StepperItem[] = [
  { title: "Kop Surat PO Transportir", slot: "poTransportHeader" },
  { title: "Rincian PO Transportir", slot: "poTransportDetails" },
  { title: "Penutup Surat PO Transportir", slot: "poTransportFooter" },
];

const poTransportHeader = reactive<OperationsPOTransportHeaderState>({
  date: `${new Date().toISOString().split("T")[0]}`,
  regarding: "Purchase Order Transportir (PO) ",
  picPerson: "Bpk Budi",
  poTransportNumber: "123/PO-TRANS/MAP/VIII/2026 ",
  receiver: "PT. Sumber Energi",
});

const poTransportDetails = reactive<OperationsPOTransportDetailsState>({
  products: [
    {
      name: "Solar",
      loadingDate: `${new Date().toISOString().split("T")[0]}`,
      unloadingDate: `${new Date().toISOString().split("T")[0]}`,
      qty: 10000,
      ratePrice: 500,
      totalPrice: 0,
    },
  ],
  percentageNum: {
    ppn: 0.11,
  },
  priceSummary: {
    grandTotal: 0,
    ppn: 0,
    subTotal: 0,
  },
});

const poTransportFooter = reactive<OperationsPOTransportFooterState>({
  loadingInformation: "Masbro, Pendingin, Kutai Kartanegara, Kalimantan Timur",
  discharge: "PT. Bina Sarana Sukses\nSite MHU - Kutai Kartanegara",
  termsOfPayment:
    "30 Hari kerja setelah invoice beserta kelengkapan dokumen selesai diverifikasi",
  shrinkageTolerance: "Toleransi susut 0.3 %, Claim Susut Rp. 25.000,- / Liter",
  contactPerson: {
    companyName: "PT. Mitra Andalan Petroleum",
    customerName: "PT. Sumber Energi",
    companyContactPerson: [
      {
        name: "Budi Santoso",
        phoneNumber: "081234567890",
      },
    ],
    customerContactPerson: undefined,
  },
  offeror: {
    name: "Stenly Boseke",
    signature: undefined,
  },
});

const stepper = useTemplateRef("stepper");

function previousNavigation() {
  stepper.value?.prev();
}

function onFormSubmitToNext() {
  stepper.value?.next();
}

async function onFormSubmit() {
  try {
    if (loading.value) return;

    loading.value = true;

    const poTrasnportData = {
      ...poTransportHeader,
      ...poTransportDetails,
      ...poTransportFooter,
    };

    console.log("Data submitted");
    console.log(poTrasnportData);
    toast.add({
      title: "Sukses",
      icon: "i-lucide-check-circle",
      description: "Data PO Transportir berhasil dibuat",
      color: "success",
    });
  } catch (e: any) {
    toast.add({ title: "Gagal", description: e.message, color: "error" });
  } finally {
    loading.value = false;
  }
}

const links = [
  [
    {
      label: "Buat PO Transportir",
      icon: "i-lucide-warehouse",
      to: "/operations/po-transportir",
    },
  ],
] satisfies NavigationMenuItem[][];

definePageMeta({ layout: "operations" });
</script>

<template>
  <UDashboardPanel id="do" :ui="{ body: 'w-full' }">
    <template #header>
      <UDashboardNavbar
        title="Form Pembuatan PO Transportir"
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
      <UStepper ref="stepper" disabled :items>
        <template #poTransportHeader>
          <OperationsPOTransportHeaderForm
            v-model="poTransportHeader"
            :has-previous="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmitToNext"
          />
        </template>

        <template #poTransportDetails>
          <OperationsPOTransportDetailsForm
            v-model="poTransportDetails"
            :has-previous="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmitToNext"
          />
        </template>

        <template #poTransportFooter>
          <OperationsPOTransportFooterForm
            v-model="poTransportFooter"
            :has-previous="stepper?.hasPrev"
            @previous="previousNavigation"
            @submit="onFormSubmit"
          />
        </template>
      </UStepper>
    </template>
  </UDashboardPanel>
</template>
