<script setup lang="ts">
import type { StepperItem, NavigationMenuItem } from "@nuxt/ui";
import type { Customer, PurchaseOrdersSupplier } from "~/types/marketing";
import type {
  DeliveryOrderPost,
  DeliveryOrdersDetails,
} from "~/types/operations";
import {
  type OperationsDOAdditionalState,
  type OperationsDODetailsTransportState,
  type OperationsDOFooterState,
  type OperationsDOHeaderState,
  type OperationsDOReceiverState,
  type OperationsDOTransportState,
} from "~/types/schemas";

const { user } = useAuth();
const { get, put, post } = useApi();
const toast = useToast();
const route = useRoute();
const loading = ref(false);
const selectedDoId = ref("");
const editingDoId = computed(
  () =>
    (typeof route.query.do_id === "string" ? route.query.do_id : "") ||
    selectedDoId.value,
);

const { data: linkedDeliveryOrders, pending: pendingLinked } = await useAsyncData(
  "delivery-orders-from-po-customer",
  async () => {
    const [posRes, dosRes] = await Promise.all([
      get<{ items: PurchaseOrdersSupplier[] }>("/purchase-orders", {
        page: 1,
        page_size: 100,
        type: "customer",
      }),
      get<{ items: DeliveryOrdersDetails[] }>("/delivery-orders", {
        page: 1,
        page_size: 100,
      }),
    ]);
    const poByNumber = new Map(
      (posRes.items || []).map((po) => [po.po_number, po] as const),
    );
    return (dosRes.items || [])
      .filter((do_) => poByNumber.has(do_.po_number))
      .map((do_) => {
        const po = poByNumber.get(do_.po_number)!;
        return {
          id: do_.id,
          doNumber: do_.do_number,
          purchaseOrderNumber: do_.po_number,
          customerName: po.customer_name || do_.customer_name || "",
          customerId: po.customer_id || do_.customer_id || "",
          fuelTotalQty: po.total ?? do_.fuel_total ?? 0,
          dateCreated: po.created_at?.toString() ?? "",
          dateChanged: po.updated_at?.toString() ?? "",
          status: do_.status,
        };
      });
  },
  { default: () => [], server: false },
);

const items: StepperItem[] = [
  { title: "Kop Surat Delivery Order", slot: "doHeader" },
  { title: "Customer Penerima", slot: "doReceiver" },
  { title: "Agen/Transportir", slot: "doTransport" },
  { title: "Rincian Pengiriman", slot: "doDetailsTransport" },
  { title: "Catatan Tambahan", slot: "doAdditional" },
  { title: "Penutup Surat Delivery Order", slot: "doFooter" },
];

const doHeader = reactive<OperationsDOHeaderState>({
  companyInformation: {
    name: "PT. MITRA ANDALAN PETROLEUM",
    nameSub: "Distributor for Elnusa Petrofin",
    address: "Jl. Belatuk Samarinda, Indonesia",
    phoneNumber: "0541-1234567", // add masking
  },
  doInformation: {
    doNumber: "0000/DO/MAP/I/0000",
    doDateCreated: `${new Date().toISOString().split("T")[0]}`,
    poCustomerNumber: {},
    soNumber: undefined,
  },
});
const doReceiver = reactive<OperationsDOReceiverState>({
  customerName: "PT. Sumber Jaya",
  customerId: "PT. Sumber Jaya Nusantara",
  customerAddress: "Samarinda",
  receiverInformation: {
    name: undefined,
    phoneNumber: undefined,
  },
  receiverDateReceived: `${new Date().toISOString().split("T")[0]}`,
});
const doTransport = reactive<OperationsDOTransportState>({
  transportName: "PT. Transport Logistik",
  transportId: "PT. Transport Logistik Nusantara",
  transportAddress: "Samarinda",
  driverInformation: {
    name: "Jaya",
    phoneNumber: undefined,
  },
  transportDateReceived: `${new Date().toISOString().split("T")[0]}`,
  helperName: undefined,
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
    transportNumber: "KT 1234 AB",
    transportType: undefined,
  },
});
const doAdditional = reactive<OperationsDOAdditionalState>({
  notes: [
    {
      note: "Sebelum BBM diserahterimakan, mohon periksa terlebih dahulu surat tera, jarum tera, segel, kualitas, SGMeter, kuantitas, kadar air, flow meter yang digunakan",
    },
    {
      note: "Setelah pembongkaran, BBM industri yang sudah diterima dengan baik dan ditanda tangani kedua belah pihak, tidak dapat dikembalikan dan BBM tersebut sudah tidak menjadi tanggung jawab kami",
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
  companyCoordinator: "Admin",
  distributionAdmin: user.value?.name || "User",
  receiver: undefined,
  driver: undefined,
});

const { data: existingDeliveryOrder, pending: pendingExisting } = await useAsyncData(
  () => `delivery-order-edit-${editingDoId.value}`,
  async () => {
    if (!editingDoId.value) return null;
    return await get<DeliveryOrdersDetails>(
      `/delivery-orders/${editingDoId.value}`,
    );
  },
  { default: () => null, server: false, watch: [editingDoId] },
);

function hydrateFormFromExistingDeliveryOrder(
  value: DeliveryOrdersDetails | null,
) {
  if (!value) return;

  const details = value.details || {};
  const existingPo = details.doInformation?.poCustomerNumber;
  Object.assign(doHeader.companyInformation, details.companyInformation || {});
  Object.assign(doHeader.doInformation, {
    ...(details.doInformation || {}),
    poCustomerNumber: {
      ...(existingPo || {}),
      id: value.id,
      doNumber: value.do_number,
      purchaseOrderNumber: existingPo?.purchaseOrderNumber ?? value.po_number,
      customerName: existingPo?.customerName ?? value.customer_name,
      customerId: existingPo?.customerId ?? value.customer_id,
      fuelTotalQty: existingPo?.fuelTotalQty ?? value.fuel_total,
    },
  });

  Object.assign(doReceiver, {
    customerName: details.customerName || value.customer_name || "",
    customerId: details.customerId || value.customer_id || "",
    customerAddress: details.customerAddress || "",
    receiverInformation: details.receiverInformation || {
      name: undefined,
      phoneNumber: undefined,
    },
    receiverDateReceived:
      details.receiverDateReceived || doReceiver.receiverDateReceived,
  });

  Object.assign(doTransport, {
    transportName: details.transportName || value.transport_name || "",
    transportId: details.transportId || "",
    transportAddress: details.transportAddress || "",
    driverInformation: details.driverInformation || {
      name: undefined,
      phoneNumber: undefined,
    },
    transportDateReceived:
      details.transportDateReceived || doTransport.transportDateReceived,
    helperName: details.helperName || undefined,
  });

  Object.assign(doDetailsTransport, {
    dueDate: details.dueDate || undefined,
    total: details.total || value.fuel_total || 0,
    productInformation:
      details.productInformation || doDetailsTransport.productInformation,
    transportInformation:
      details.transportInformation || doDetailsTransport.transportInformation,
  });

  Object.assign(doAdditional, {
    notes: details.notes || doAdditional.notes,
    t2Depot: details.t2Depot,
    t2Unloading: details.t2Unloading,
    indexSensitivity: details.indexSensitivity,
    fuelReceived:
      details.fuelReceived || details.total || value.fuel_total || 0,
  });

  Object.assign(doFooter, {
    companyCoordinator:
      details.companyCoordinator || doFooter.companyCoordinator,
    distributionAdmin: details.distributionAdmin || doFooter.distributionAdmin,
    receiver: details.receiver || undefined,
    driver: details.driver || details.driverInformation?.name || undefined,
  });
}

watch(existingDeliveryOrder, hydrateFormFromExistingDeliveryOrder, {
  immediate: true,
});

const stepper = useTemplateRef("stepper");

function previousNavigation() {
  stepper.value?.prev();
}

function onFormSubmitToNext() {
  stepper.value?.next();
}

watch(
  () => doHeader.doInformation.poCustomerNumber,
  (value) => {
    if (value) {
      console.log(value);
      doReceiver.customerName = value.customerName || "";
      doReceiver.customerId = value.customerId || "";
      doDetailsTransport.total = value.fuelTotalQty || 0;
      doDetailsTransport.productInformation.qty = value.fuelTotalQty || 0;
      doAdditional.fuelReceived = value.fuelTotalQty || 0;
      if (value.id) {
        selectedDoId.value = value.id;
      }
      if (value.doNumber) {
        doHeader.doInformation.doNumber = value.doNumber;
      }
    }
  },
);

async function onFormSubmit() {
  try {
    if (loading.value) return;

    loading.value = true;

    const doData = {
      ...doHeader,
      ...doReceiver,
      ...doTransport,
      ...doDetailsTransport,
      ...doAdditional,
      ...doFooter,
    };
    const doPost: DeliveryOrderPost = {
      do_number: doData.doInformation.doNumber,
      customer_id: doData.customerId,
      date: doData.doInformation.doDateCreated,
      fuel_total: doData.total,
      po_number:
        doData.doInformation.poCustomerNumber.purchaseOrderNumber || "",
      status: "created",
      transport_name: doData.transportName,
      details: doData,
    };

    const res = editingDoId.value
      ? await put<any, DeliveryOrderPost>(
          `/delivery-orders/${editingDoId.value}`,
          doPost,
        )
      : await post<any, DeliveryOrderPost>("/delivery-orders", doPost);

    console.log("Data submitted");
    console.log(res);
    // console.log(doPost);
    toast.add({
      title: "Sukses",
      icon: "i-lucide-check-circle",
      description: editingDoId.value
        ? "Data Delivery Order berhasil dilengkapi"
        : "Data Delivery Order berhasil dibuat",
      color: "success",
    });
  } catch (e: any) {
    toast.add({ title: "Error", description: e.message, color: "error" });
  } finally {
    loading.value = false;
  }
}

const purchaseOrders = computed(() =>
  linkedDeliveryOrders.value.map((entry) => {
    return {
      label: entry.doNumber,
      value: {
        id: entry.id,
        doNumber: entry.doNumber,
        purchaseOrderNumber: entry.purchaseOrderNumber,
        customerName: entry.customerName,
        customerId: entry.customerId,
        dateCreated: entry.dateCreated,
        dateChanged: entry.dateChanged,
        fuelTotalQty: entry.fuelTotalQty,
      },
      customerName: entry.customerName,
    };
  }),
);

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
      <div
        v-if="pendingLinked || pendingExisting"
        class="space-y-4 w-full p-4"
      >
        <div class="space-y-2">
          <USkeleton class="h-4 w-32 rounded" />
          <USkeleton class="h-10 w-full rounded-lg" />
        </div>
        <div class="space-y-2">
          <USkeleton class="h-4 w-40 rounded" />
          <USkeleton class="h-10 w-full rounded-lg" />
        </div>
      </div>
      <UStepper v-else disabled ref="stepper" :items>
        <template #doHeader>
          <OperationsDOHeaderForm
            :purchase-orders="purchaseOrders"
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
            :is-loading="loading"
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
