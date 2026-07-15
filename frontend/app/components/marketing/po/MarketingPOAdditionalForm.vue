<script setup lang="ts">
import * as z from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";

const emit = defineEmits<{
  submit: [];
  previous: [];
}>();

const state = defineModel<{
  termAndCondition: string;
  delivery: {
    loadingTerminal?: string;
    loadingDate?: string;
    picOperationMap?: string;
  };
  details?: string;
  forwarder: {
    trucking: string;
  };
  signed: {
    createdBy: string;
    approvedBy: string;
  };
}>({ required: true });

const schema = z.object({
  termAndCondition: z.string(),
  delivery: z.object({
    loadingTerminal: z.string().optional(),
    loadingDate: z.string().optional(),
    picOperationMap: z.string().optional(),
  }),
  details: z.string().optional(),
  forwarder: z.object({
    trucking: z.string(),
  }),
  signed: z.object({
    createdBy: z.string(),
    approvedBy: z.string(),
  }),
});

type POAdditionalInfoSchema = z.output<typeof schema>;

function previous() {
  emit("previous");
}

function onSubmit(_event: FormSubmitEvent<POAdditionalInfoSchema>) {
  emit("submit");
}
</script>

<template>
  <UForm
    id="letter-footer"
    :schema="schema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <div class="flex w-full gap-4">
        <UFormField name="termAndCondition" label="Term & Condition" required>
          <UInput
            v-model="state.termAndCondition"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="details" label="Details">
          <UInput v-model="state.details" type="text" autocomplete="off" />
        </UFormField>
      </div>

      <USeparator />

      <p>Delivery</p>

      <UFormField name="loadingTerminal" label="Loading Terminal">
        <UInput
          v-model="state.delivery.loadingTerminal"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <UFormField name="loadingDate" label="Loading Date">
        <UInput
          v-model="state.delivery.loadingDate"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <UFormField name="picOperationMap" label="PIC OPERATION MAP">
        <UInput
          v-model="state.delivery.picOperationMap"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <USeparator />

      <p>Forwarder</p>

      <UFormField name="trucking" label="Trucking" required>
        <UInput
          v-model="state.forwarder.trucking"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <USeparator />

      <p>Signed</p>

      <div class="flex w-full gap-4">
        <UFormField name="createdBy" label="Created By" required>
          <UInput
            v-model="state.signed.createdBy"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="approvedBy" label="Approved By">
          <UInput
            v-model="state.signed.approvedBy"
            type="text"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <div class="flex justify-between pt-4">
        <UButton
          variant="ghost"
          color="neutral"
          leading-icon="i-lucide-arrow-left"
          @click="previous"
        >
          Sebelumnya
        </UButton>

        <UButton type="submit" trailing-icon="i-lucide-arrow-right">
          Selesai
        </UButton>
      </div>
    </UPageCard>
  </UForm>
</template>
