<script setup lang="ts">
import * as z from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";

const emit = defineEmits<{
  submit: [];
  previous: void;
}>();

const state = defineModel<{
  supplyPoint: string;
  qualityAssurance: string;
  custodyTransfer: string;
  unloadingProcedure: string;
  volumeUnit: string;
  volumeTolerance: number;
  paymentTerm: number;
  latePenalty: number;
  servicePattern: string;
  personInCharge: {
    name: string;
    phoneNumber: string;
  };
  paymentAddress: {
    bankName: string;
    accountNumber: string;
    accountName: string;
  };
  fuelPrices: {
    logisticInformation: string;
    productName: string;
    sellingPrice: {
      ppkb: number;
      oat: number | null;
    };
    ppn: number;
  };
}>({ required: true });

const schema = z.object({
  supplyPoint: z.string(),
  qualityAssurance: z.string(),
  custodyTransfer: z.string(),
  unloadingProcedure: z.string(),
  volumeUnit: z.string(),
  volumeTolerance: z.number().min(0),
  paymentTerm: z.number().min(1),
  latePenalty: z.number().min(0.01),
  servicePattern: z.string(),
  personInCharge: z.object({
    name: z.string(),
    phoneNumber: z.string().length(11, "Phone Number"),
  }),
  paymentAddress: z.object({
    bankName: z.string(),
    accountNumber: z.string(),
    accountName: z.string(),
  }),
  fuelPrices: z.object({
    logisticInformation: z.string(),
    productName: z.string(),
    sellingPrice: z.object({
      ppkb: z.number(),
      oat: z.number().nullable(),
    }),
    ppn: z.number(),
  }),
});

type DetailsSchema = z.output<typeof schema>;

const totalFuelPrices = computed(() => {
  return (
    (state.value.fuelPrices?.sellingPrice.ppkb ?? 0) +
    (state.value.fuelPrices?.sellingPrice.oat ?? 0) +
    (state.value.fuelPrices?.ppn ?? 0)
  );
});

function previous() {
  emit("previous");
}

function onSubmit(_event: FormSubmitEvent<DetailsSchema>) {
  emit("submit");
}
</script>

<template>
  <UForm
    id="letter-details"
    :schema="schema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <UFormField name="supplyPoint" label="Supply Point" required>
        <UInput
          v-model="state.supplyPoint"
          type="text"
          autocomplete="off"
          placeholder="PT. XYZ"
        />
      </UFormField>

      <UFormField name="qualityAssurance" label="Jaminan Kualitas" required>
        <UInput
          v-model="state.qualityAssurance"
          type="text"
          autocomplete="off"
          placeholder="PT. XYZ"
        />
      </UFormField>

      <USeparator />

      <UFormField name="custodyTransfer" label="Custody Transfer" required>
        <UInput
          v-model="state.custodyTransfer"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <UFormField name="unloadingProcedure" label="Prosedur Bongkar" required>
        <UInput
          v-model="state.unloadingProcedure"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <USeparator />

      <div class="flex w-full gap-4">
        <UFormField name="volumeUnit" label="Satuan Volume" required>
          <UInput v-model="state.volumeUnit" type="text" autocomplete="off" />
        </UFormField>

        <UFormField name="volumeTolerance" label="Toleransi Volume" required>
          <UInputNumber
            :ui="{
              root: 'w-full',
            }"
            v-model="state.volumeTolerance"
            orientation="vertical"
            :step="0.005"
            :format-options="{
              style: 'percent',
              minimumFractionDigits: 1,
            }"
          />
        </UFormField>
      </div>

      <USeparator />

      <UFormField name="paymentTerm" label="Term Pembayaran" required>
        <UInputNumber
          :ui="{
            root: 'w-full',
          }"
          v-model="state.paymentTerm"
          orientation="vertical"
          :step="1"
          locale="id-ID"
          :format-options="{
            style: 'unit',
            unit: 'week',
            unitDisplay: 'long',
          }"
        />
      </UFormField>

      <div class="flex w-full gap-4">
        <UFormField name="latePenalty" label="Penalty Keterlambatan" required>
          <UInputNumber
            :ui="{
              root: 'w-full',
            }"
            v-model="state.latePenalty"
            orientation="vertical"
            :step="0.01"
            :format-options="{
              style: 'percent',
            }"
          />
        </UFormField>

        <UFormField name="servicePattern" label="Pola Pelayanan" required>
          <UInput
            v-model="state.servicePattern"
            type="text"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <USeparator />

      <p>Person In Charge</p>

      <div class="flex w-full gap-4">
        <UFormField name="personName" label="Nama" required>
          <UInput
            v-model="state.personInCharge.name"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="personNumber" label="Nomor Telepon" required>
          <UInput
            v-model="state.personInCharge.phoneNumber"
            type="text"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <USeparator />

      <p>Rekening Pembayaran</p>

      <div class="flex w-full gap-4">
        <UFormField name="bankName" label="Nama Bank" required>
          <UInput
            v-model="state.paymentAddress.bankName"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="accountNumber" label="Nomor Rekening" required>
          <UInput
            v-model="state.paymentAddress.accountNumber"
            type="text"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <UFormField name="accountName" label="Nama Rekening" required>
        <UInput
          v-model="state.paymentAddress.accountName"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <USeparator />

      <p>Harga Bahan Bakar Minyak</p>

      <div class="flex w-full gap-4">
        <UFormField
          name="logisticInformation"
          label="Informasi Logistik"
          required
        >
          <UInput
            v-model="state.fuelPrices.logisticInformation"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="productName" label="Produk" required>
          <UInput
            v-model="state.fuelPrices.productName"
            type="text"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <div class="flex w-full gap-4">
        <UFormField name="ppkb" label="PPKB" required>
          <UInputNumber
            :ui="{
              root: 'w-full',
            }"
            v-model="state.fuelPrices.sellingPrice.ppkb"
            :increment="false"
            :decrement="false"
            :format-options="{
              style: 'currency',
              currency: 'IDR',
              currencyDisplay: 'narrowSymbol',
              currencySign: 'standard',
            }"
          />
        </UFormField>

        <UFormField name="oat" label="OAT" required>
          <UInputNumber
            :ui="{
              root: 'w-full',
            }"
            v-model="state.fuelPrices.sellingPrice.oat"
            :increment="false"
            :decrement="false"
            :format-options="{
              style: 'currency',
              currency: 'IDR',
              currencyDisplay: 'narrowSymbol',
              currencySign: 'standard',
            }"
          />
        </UFormField>
      </div>

      <UFormField
        name="ppn"
        label="PPN (11%)"
        description="Harga Jual & Ongkos Angkut"
        required
      >
        <UInputNumber
          :ui="{
            root: 'w-full',
          }"
          v-model="state.fuelPrices.ppn"
          :increment="false"
          :decrement="false"
          :format-options="{
            style: 'currency',
            currency: 'IDR',
            currencyDisplay: 'narrowSymbol',
            currencySign: 'standard',
          }"
        />
      </UFormField>

      <UFormField name="total" label="Total">
        <UInputNumber
          :ui="{
            root: 'w-full',
          }"
          :model-value="totalFuelPrices"
          :increment="false"
          :decrement="false"
          :format-options="{
            style: 'currency',
            currency: 'IDR',
            currencyDisplay: 'narrowSymbol',
            currencySign: 'standard',
          }"
          disabled
        />
      </UFormField>

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
          Selanjutnya
        </UButton>
      </div>
    </UPageCard>
  </UForm>
</template>
