<script setup lang="ts">
import type { StepperItem } from "@nuxt/ui";
import { type MarketingPOCustomerState } from "~/types/schemas";

const items: StepperItem[] = [
  {
    title: "Upload PO Customer",
    slot: "poCustomer",
    icon: "i-lucide-receipt-text",
  },
];

const poCustomer = reactive<MarketingPOCustomerState>({
  offeringLetterNumber: "722/MAP/II-06/26",
  poDocument: undefined,
});

function onPoCustomerSubmit() {
  console.log("Data submitted");
  console.log({ ...poCustomer });
}

definePageMeta({ layout: "marketing" });
</script>

<template>
  <UStepper disabled ref="stepper" :items>
    <template #poCustomer>
      <MarketingPOCustomerForm
        v-model="poCustomer"
        @submit="onPoCustomerSubmit"
      />
    </template>
  </UStepper>
</template>
