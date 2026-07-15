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
  location: string;
  date: string;
  offeringLetterNumber: string;
  regarding: string;
  receiver: string;
}>({ required: true });

const options = {
  mask: "###/AAA/AA-##/##",
  tokens: {
    A: { pattern: /[a-zA-Z]/, transform: (chr: string) => chr.toUpperCase() },
  },
};

const schema = z.object({
  location: z.string().min(2),
  date: z.string(),
  offeringLetterNumber: z.string(),
  regarding: z.string(),
  receiver: z.string().min(2),
});

type HeaderSchema = z.output<typeof schema>;

function previous() {
  emit("previous");
}

function onSubmit(_event: FormSubmitEvent<HeaderSchema>) {
  emit("submit");
}
</script>

<template>
  <UForm
    id="letter-header"
    :schema="schema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <div class="flex w-full gap-4">
        <UFormField name="location" label="Lokasi" required>
          <UInput
            v-model="state.location"
            type="text"
            autocomplete="off"
            placeholder="Samarinda"
          />
        </UFormField>

        <UFormField name="date" label="Tanggal Dibuat" required>
          <UInput v-model="state.date" type="date" autocomplete="off" />
        </UFormField>
      </div>

      <USeparator />

      <UFormField name="regarding" label="Perihal Surat" required>
        <UInput
          v-model="state.regarding"
          type="text"
          autocomplete="off"
          placeholder="Surat Penawaran Harga Bahan Bakar Minyak Bio diesel"
        />
      </UFormField>

      <UFormField name="offeringLetterNumber" label="Nomor Surat" required>
        <UInput
          v-model="state.offeringLetterNumber"
          v-maska="options"
          placeholder="Contoh 722/MAP/II-06/26"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <UFormField name="receiver" label="Yang Terhormat" required>
        <UInput
          v-model="state.receiver"
          type="text"
          autocomplete="off"
          placeholder="PT. XYZ"
        />
      </UFormField>

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
