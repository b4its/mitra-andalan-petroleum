<script setup lang="ts">
import type { StepperItem, NavigationMenuItem } from "@nuxt/ui";
import { type OperationsDOState } from "~/types/schemas";

const items: StepperItem[] = [
  {
    title: "Upload Surat DO",
    slot: "doReturned",
    icon: "i-lucide-receipt-text",
  },
];

const doReturned = reactive<OperationsDOState>({
  deliveryOrderNumber: "1086/DO/MAP/V/2026",
  doDocument: undefined,
});

function onDoSubmit() {
  console.log("Data submitted");
  console.log({ ...doReturned });
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
        <template #doReturned>
          <!-- <MarketingPOCustomerForm v-model="doReturned" @submit="onDoSubmit" /> -->
          <OperationsDOReturnedForm v-model="doReturned" @submit="onDoSubmit" />
        </template>
      </UStepper>
    </template>
  </UDashboardPanel>
</template>
