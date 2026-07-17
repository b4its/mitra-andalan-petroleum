<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui";
import {
  marketingPOCustomerSchema,
  type MarketingPOCustomerState,
} from "~/types/schemas";

const emit = defineEmits<{
  submit: [];
}>();

const state = defineModel<MarketingPOCustomerState>({ required: true });

function onSubmit(_event: FormSubmitEvent<MarketingPOCustomerState>) {
  emit("submit");
}

const value = ref<string>();

const offeringLetters = ref([
  {
    label: "PT. MIGAS KUKAR MANDIRI",
    value: "722/MAP/II-06/26",
    deliveryOrderNumbers: ["1086/DO/MAP/V/2026", "1087/DO/MAP/V/2026"],
  },
  {
    label: "PT. BERAU MINERAL ENERGI",
    value: "723/MAP/II-06/26",
    deliveryOrderNumbers: ["1092/DO/BME/V/2026", "1093/DO/BME/V/2026"],
  },
  {
    label: "PT. KALTIM OIL SERVICES",
    value: "724/MAP/II-06/26",
    deliveryOrderNumbers: ["1098/DO/KOS/V/2026", "1099/DO/KOS/V/2026"],
  },
]);
</script>

<template>
  <UForm
    id="po-customer"
    :schema="marketingPOCustomerSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <UFormField name="offeringLetter" label="Nomor Surat Penawaran" required>
        <USelect
          v-model="value"
          :items="offeringLetters"
          placeholder="Pilih Surat Penawaran"
          value-key="value"
          :ui="{ content: 'min-w-fit' }"
          class="w-full"
        >
          <template #item-label="{ item }">
            {{ item.label }}

            <span class="text-muted text-xs"> ({{ item.value }}) </span>
          </template>
        </USelect>
      </UFormField>

      <UFormField name="poFile" label="File Purchase Order Customer" required>
        <UFileUpload
          label="Upload File Purchase Order"
          description="Format file .pdf dengan max 5MB"
        />
      </UFormField>

      <div class="flex justify-end pt-4">
        <UButton type="submit" trailing-icon="i-lucide-arrow-right">
          Upload PO Customer
        </UButton>
      </div>
    </UPageCard>
  </UForm>
</template>
