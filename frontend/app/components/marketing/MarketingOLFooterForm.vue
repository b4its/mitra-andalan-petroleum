<script setup lang="ts">
import * as z from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";

const emit = defineEmits<{
  submit: [];
  previous: void;
}>();

const state = defineModel<{
  purchaseOrderDeadline: number;
  offeror: {
    name: string;
    signature: string;
  };
  companyInformation: {
    address: string;
    phoneNumber: string;
    email: string;
  };
}>({ required: true });

const schema = z.object({
  purchaseOrderDeadline: z.number(),
  offeror: z.object({
    name: z.string(),
    signature: z.string(),
  }),
  companyInformation: z.object({
    address: z.string(),
    phoneNumber: z.string(),
    email: z.email(),
  }),
});

type FooterSchema = z.output<typeof schema>;

function previous() {
  emit("previous");
}

function onSubmit(_event: FormSubmitEvent<FooterSchema>) {
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
      <UFormField
        name="purchaseOrderDeadline"
        label="Tenggat Purchase Order (PO)"
        required
      >
        <UInputNumber
          :ui="{
            root: 'w-full',
          }"
          v-model="state.purchaseOrderDeadline"
          orientation="vertical"
          :step="1"
          locale="id-ID"
          :format-options="{
            style: 'unit',
            unit: 'day',
            unitDisplay: 'long',
          }"
        />
      </UFormField>

      <USeparator />

      <UFormField name="offerorName" label="Hormat Kami" required>
        <UInput v-model="state.offeror.name" type="text" autocomplete="off" />
      </UFormField>

      <UFormField name="offerorSignature" label="Tanda Tangan" required>
        <UFileUpload
          label="Upload File Tanda Tangan"
          description="Format file .png dengan max 2MB"
        />
      </UFormField>

      <USeparator />

      <p>Informasi Perusahaan</p>

      <UFormField name="address" label="Alamat" required>
        <UInput
          v-model="state.companyInformation.address"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <div class="flex w-full gap-4">
        <UFormField name="phoneNumber" label="Nomor Telepon" required>
          <UInput
            v-model="state.companyInformation.phoneNumber"
            v-maska="'0541-#######'"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="email" label="Alamat Email" required>
          <UInput
            v-model="state.companyInformation.email"
            type="email"
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
