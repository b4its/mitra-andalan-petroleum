<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui";
import {
  financeInvoiceHeaderSchema,
  type FinanceInvoiceHeaderState,
} from "~/types/schemas";

defineProps<{
  hasPrevious: boolean | undefined;
}>();

const emit = defineEmits<{
  submit: [];
  previous: [];
}>();

const state = defineModel<FinanceInvoiceHeaderState>({ required: true });

function previous() {
  emit("previous");
}

function onSubmit(_event: FormSubmitEvent<FinanceInvoiceHeaderState>) {
  emit("submit");
}
</script>

<template>
  <UForm
    id="invoice-header"
    :schema="financeInvoiceHeaderSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Heading</p>

      <USeparator />

      <div class="flex justify-between pt-4">
        <UButton
          variant="ghost"
          color="neutral"
          leading-icon="i-lucide-arrow-left"
          :disabled="!hasPrevious"
          @click="previous"
        >
          Sebelumnya
        </UButton>

        <UButton type="submit" trailing-icon="i-lucide-arrow-right">
          Selanjutnya
        </UButton>
      </div>
    </UPageCard>
  </UForm>
</template>
