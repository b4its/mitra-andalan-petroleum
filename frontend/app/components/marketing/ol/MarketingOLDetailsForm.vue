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

const calculatePphPercent = computed(() => {
  return (
    state.value.fuelPrices.basePrice *
    (state.value.fuelPrices.percentageNum.pph || 0)
  );
});

const totalFuelPrices = computed(() => {
  return (
    calculatePpkbPercent.value +
    calculateOatPercent.value +
    calculatePpnPercent.value +
    calculatePphPercent.value +
    state.value.fuelPrices.basePrice
  );
});

watch(
  [
    calculatePpkbPercent,
    calculateOatPercent,
    calculatePpnPercent,
    calculatePphPercent,
    totalFuelPrices,
  ],
  ([ppkb, oat, ppn, pph, total]) => {
    state.value.fuelPrices.sellingPrice.ppkb = ppkb;
    state.value.fuelPrices.sellingPrice.oat = oat;
    state.value.fuelPrices.sellingPrice.ppn = ppn;
    state.value.fuelPrices.sellingPrice.pph = pph;
    state.value.fuelPrices.totalPrice = total;
  },
  { immediate: true },
);

function previous() {
  emit("previous");
}

function addInformasiTambahan() {
  if (!state.value.informasiTambahan) {
    state.value.informasiTambahan = [];
  }
  state.value.informasiTambahan.push("");
}

function removeInformasiTambahan(index: number) {
  state.value.informasiTambahan?.splice(index, 1);
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
            v-model="state.volumeTolerance"
            :ui="{
              root: 'w-full',
            }"
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

      <UFormField name="paymentMethod" label="Metode Pembayaran" required>
        <USelect
          v-model="state.paymentMethod"
          :items="[
            { label: 'Cash', value: 'cash' },
            { label: 'Kredit', value: 'kredit' },
          ]"
          value-key="value"
          placeholder="Pilih metode pembayaran"
          class="w-full"
        />
      </UFormField>

      <UFormField
        v-if="state.paymentMethod === 'cash'"
        name="cashMethod"
        label="Jenis Cash"
        required
      >
        <USelect
          v-model="state.cashMethod"
          :items="[
            {
              label: 'Cash Before Delivery (CBD)',
              value: 'cash_before_delivery',
            },
            {
              label: 'Cash After Delivery (CAD)',
              value: 'cash_after_delivery',
            },
          ]"
          value-key="value"
          placeholder="Pilih jenis cash"
          class="w-full"
        />
      </UFormField>

      <UFormField
        name="paymentTerm"
        :label="
          state.paymentMethod === 'cash'
            ? 'Term Pembayaran (Cash)'
            : 'Term Pembayaran (Kredit)'
        "
        required
      >
        <USelect
          v-model="state.paymentTerm"
          :items="[
            { label: '1 - 14', value: '1 - 14' },
            { label: '15 - 28', value: '15 - 28' },
            { label: '15 - 29', value: '15 - 29' },
            { label: '15 - 30', value: '15 - 30' },
            { label: '15 - 31', value: '15 - 31' },
          ]"
          value-key="value"
          placeholder="Pilih periode tenggat pembayaran"
          class="w-full"
        />
      </UFormField>

      <div class="flex w-full gap-4">
        <UFormField
          name="latePenalty"
          label="Penalty Keterlambatan"
          description="Per bulan (contoh: 2% = 2% per bulan dari nilai transaksi)"
          required
        >
          <UInputNumber
            v-model="state.latePenalty"
            :ui="{
              root: 'w-full',
            }"
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

      <UFormField name="hppPrice" label="HPP" required>
        <UInputNumber
          v-model="state.fuelPrices.hppPrice"
          :ui="{
            root: 'w-full',
          }"
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

      <UFormField name="basePrice" label="Harga Dasar Solar" required>
        <UInputNumber
          v-model="state.fuelPrices.basePrice"
          :ui="{
            root: 'w-full',
          }"
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
            v-model="state.fuelPrices.percentageNum.ppkb"
            :ui="{
              root: 'w-full',
            }"
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
            v-model="state.fuelPrices.percentageNum.oat"
            :ui="{
              root: 'w-full',
            }"
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
          v-model="state.fuelPrices.percentageNum.ppn"
          :ui="{
            root: 'w-full',
          }"
          orientation="vertical"
          :step="0.001"
          :format-options="{
            style: 'percent',
            minimumFractionDigits: 1,
          }"
        />
      </UFormField>

      <UFormField
        name="percentagePph"
        label="Persentase PPH"
        description="Kosongkan (0) jika tidak ada PPH — kalkulasi tetap seperti biasa"
      >
        <UInputNumber
          v-model="state.fuelPrices.percentageNum.pph"
          :ui="{
            root: 'w-full',
          }"
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
        label="PPN"
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

      <UFormField
        name="pph"
        label="PPH"
        description="Kosong jika tidak ada PPH"
      >
        <UInputNumber
          :ui="{
            root: 'w-full',
          }"
          :model-value="calculatePphPercent"
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

      <USeparator />

      <div class="space-y-3">
        <p>Informasi Tambahan</p>

        <div
          v-for="(item, index) in state.informasiTambahan || []"
          :key="`informasi-${index}`"
          class="flex items-end gap-2"
        >
          <UFormField
            :name="`informasiTambahan.${index}`"
            label="Keterangan"
            class="w-full"
          >
            <UInput
              v-model="state.informasiTambahan![index]"
              placeholder="Informasi tambahan 1"
            />
          </UFormField>

          <UButton
            icon="i-lucide-trash-2"
            color="error"
            variant="ghost"
            @click="removeInformasiTambahan(index)"
          />
        </div>

        <UButton
          icon="i-lucide-plus"
          color="neutral"
          variant="subtle"
          size="sm"
          label="Tambah Informasi"
          @click="addInformasiTambahan"
        />
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
          Selanjutnya
        </UButton>
      </div>
    </UPageCard>
  </UForm>
</template>
