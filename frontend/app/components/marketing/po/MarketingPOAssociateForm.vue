<script setup lang="ts">
import * as z from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";

defineProps<{
  hasPrevious: boolean | undefined;
}>();

const emit = defineEmits<{
  submit: [];
  previous: [];
}>();

const state = defineModel<{
  associateInformation: {
    name: string;
    address: string;
    npwp?: string;
    contactPerson?: string;
    email?: string;
  };
}>({ required: true });

const schema = z.object({
  associateInformation: z.object({
    name: z.string(),
    address: z.string(),
    npwp: z.string().optional(),
    contactPerson: z.string().optional(),
    email: z.email().optional(),
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
    id="letter-associate"
    :schema="schema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Informasi Perusahaan Mitra</p>

      <UFormField name="companyName" label="Nama Perusahaan" required>
        <UInput
          v-model="state.associateInformation.name"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <UFormField name="address" label="Alamat" required>
        <UInput
          v-model="state.associateInformation.address"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <UFormField name="npwp" label="NPWP">
        <UInput
          v-model="state.associateInformation.npwp"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <div class="flex w-full gap-4">
        <UFormField name="phoneNumber" label="Nomor Telepon">
          <UInput
            v-model="state.associateInformation.contactPerson"
            v-maska="'#### #### ####'"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="email" label="Alamat Email">
          <UInput
            v-model="state.associateInformation.email"
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
