<script setup lang="ts">
import type { StepperItem } from "@nuxt/ui";

const items: StepperItem[] = [
  {
    title: "Upload PO Customer",
    slot: "poCustomer",
    icon: "i-lucide-receipt-text",
  },
];

const poCustomer = reactive({
  offeringLetterNumber: "722/MAP/II-06/26",
});

const stepper = useTemplateRef("stepper");

function previousNavigation() {
  stepper.value?.prev();
}

function onHeaderSubmit() {
  stepper.value?.next();
}

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
