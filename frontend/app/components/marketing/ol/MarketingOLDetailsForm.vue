<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui";
import {
  marketingOLDetailsSchema,
  type MarketingOLDetailsState,
} from "~/types/schemas";

const emit = defineEmits<{
  submit: [];
  previous: [];
}>();

const state = defineModel<MarketingOLDetailsState>({ required: true });

const calculatePpkbPercent = computed(() => {
  return (
    state.value.fuelPrices.basePrice * state.value.fuelPrices.percentageNum.ppkb
  );
});

const calculateOatPercent = computed(() => {
  return (
    state.value.fuelPrices.basePrice * state.value.fuelPrices.percentageNum.oat
  );
});

const calculatePpnPercent = computed(() => {
  return (
    state.value.fuelPrices.basePrice * state.value.fuelPrices.percentageNum.ppn
  );
});

const totalFuelPrices = computed(() => {
  return (
    calculatePpkbPercent.value +
    calculateOatPercent.value +
    calculatePpnPercent.value +
    state.value.fuelPrices.basePrice
  );
});

watch(
  [
    calculatePpkbPercent,
    calculateOatPercent,
    calculatePpnPercent,
    totalFuelPrices,
  ],
  ([ppkb, oat, ppn, total]) => {
    state.value.fuelPrices.sellingPrice.ppkb = ppkb;
    state.value.fuelPrices.sellingPrice.oat = oat;
    state.value.fuelPrices.sellingPrice.ppn = ppn;
    state.value.fuelPrices.totalPrice = total;
  },
  { immediate: true },
);

function previous() {
  emit("previous");
}

function onSubmit(_event: FormSubmitEvent<MarketingOLDetailsState>) {
  emit("submit");
}
</script>

<template>
  <UForm
    id="letter-details"
    :schema="marketingOLDetailsSchema"
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

      <UFormField name="basePrice" label="Harga Dasar Solar" required>
        <UInputNumber
          :ui="{
            root: 'w-full',
          }"
          v-model="state.fuelPrices.basePrice"
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

      <div class="flex w-full gap-4">
        <UFormField name="percentagePpkb" label="Persentase PPKB" required>
          <UInputNumber
            :ui="{
              root: 'w-full',
            }"
            v-model="state.fuelPrices.percentageNum.ppkb"
            orientation="vertical"
            :step="0.001"
            :format-options="{
              style: 'percent',
              minimumFractionDigits: 1,
            }"
          />
        </UFormField>

        <UFormField name="percentageOat" label="Persentase OAT" required>
          <UInputNumber
            :ui="{
              root: 'w-full',
            }"
            v-model="state.fuelPrices.percentageNum.oat"
            orientation="vertical"
            :step="0.001"
            :format-options="{
              style: 'percent',
              minimumFractionDigits: 1,
            }"
          />
        </UFormField>
      </div>

      <UFormField name="percentagePpn" label="Persentase PPN" required>
        <UInputNumber
          :ui="{
            root: 'w-full',
          }"
          v-model="state.fuelPrices.percentageNum.ppn"
          orientation="vertical"
          :step="0.001"
          :format-options="{
            style: 'percent',
            minimumFractionDigits: 1,
          }"
        />
      </UFormField>

      <USeparator />

      <div class="flex w-full gap-4">
        <UFormField name="ppkb" label="PPKB" required>
          <UInputNumber
            :ui="{
              root: 'w-full',
            }"
            :model-value="calculatePpkbPercent"
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

        <UFormField name="oat" label="OAT" required>
          <UInputNumber
            :ui="{
              root: 'w-full',
            }"
            :model-value="calculateOatPercent"
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
          :model-value="calculatePpnPercent"
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
