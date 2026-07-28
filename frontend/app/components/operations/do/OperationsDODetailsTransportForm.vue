<script setup lang="ts">
import type { Time } from '@internationalized/date'
import type { FormSubmitEvent } from '@nuxt/ui'
import {
  operationsDODetailsTransportSchema,
  type OperationsDODetailsTransportState
} from '~/types/schemas'

const emit = defineEmits<{
  submit: []
  previous: []
}>()

// Vehicle Number Regex masking
// const options = {
//   mask: ["A #### AA", "A #### AAA", "AA #### AA", "AA #### AAA"],
//   tokens: {
//     A: {
//       pattern: /[A-Za-z]/,
//       transform: (chunk: string) => chunk.toUpperCase(),
//     },
//     "#": { pattern: /[0-9]/ },
//   },
// };

const state = defineModel<OperationsDODetailsTransportState>({
  required: true
})

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<OperationsDODetailsTransportState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="do-details-transport"
    :schema="operationsDODetailsTransportSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Informasi Detail Pengiriman</p>

      <UFormField name="dueDate" label="Tanggal Berlaku" required>
        <UInput v-model="state.dueDate" type="date" autocomplete="off" />
      </UFormField>

      <UFormField name="total" label="Jumlah (Liter)" required>
        <UInputNumber v-model="state.total" class="w-full" :min="1" />
      </UFormField>

      <USeparator />

      <p>Informasi Produk</p>

      <div class="flex w-full gap-4">
        <UFormField name="productName" label="Nama Produk" required>
          <UInput
            v-model="state.productInformation.name"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="productQty" label="Volume/Kuantitas (Liter)" required>
          <UInputNumber
            v-model="state.productInformation.qty"
            class="w-full"
            :min="1"
          />
        </UFormField>
      </div>

      <div class="flex w-full gap-4">
        <UFormField name="topSeal" label="Segel Atas" required>
          <UInput
            v-model="state.productInformation.topSeal"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="bottomSeal" label="Segel Bawah" required>
          <UInput
            v-model="state.productInformation.bottomSeal"
            type="text"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <UFormField name="temperature" label="Temperature" required>
        <UInputNumber
          v-model="state.productInformation.temperature"
          class="w-full"
          :format-options="{
            style: 'unit',
            unit: 'celsius',
            unitDisplay: 'short'
          }"
        />
      </UFormField>

      <USeparator />

      <p>Informasi Agen/Transportir</p>

      <div class="flex w-full gap-4">
        <UFormField name="transportType" label="Dikirim Dengan" required>
          <UInput
            v-model="state.transportInformation.transportType"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="transportNumber" label="No. Kendaraan" required>
          <UInput
            v-model="state.transportInformation.transportNumber"
            type="text"
            autocomplete="off"
            placeholder="contoh KT 1234 AB"
          />
        </UFormField>
      </div>

      <div class="flex w-full gap-4">
        <UFormField name="topSeal" label="Km. Awal" required>
          <UInputNumber
            v-model="state.transportInformation.startKm"
            class="w-full"
            :min="1"
            :format-options="{
              style: 'unit',
              unit: 'kilometer',
              unitDisplay: 'short'
            }"
            :increment="false"
            :decrement="false"
          />
        </UFormField>

        <UFormField name="bottomSeal" label="Km. Akhir" required>
          <UInputNumber
            v-model="state.transportInformation.endKm"
            class="w-full"
            :min="1"
            :format-options="{
              style: 'unit',
              unit: 'kilometer',
              unitDisplay: 'short'
            }"
            :increment="false"
            :decrement="false"
          />
        </UFormField>

        <UFormField name="sgMeter" label="SG Meter" required>
          <UInputNumber
            v-model="state.transportInformation.sgMeter"
            class="w-full"
            label="contoh: 0.841"
            :increment="false"
            :decrement="false"
          />
        </UFormField>
      </div>

      <div class="flex w-full gap-4">
        <UFormField
          class="w-full"
          name="departureTime"
          label="Jam Berangkat"
          required
        >
          <UInputTime
            v-model="state.transportInformation.timeInformation.departureTime"
            class="w-full justify-center"
            :hour-cycle="24"
          />
        </UFormField>

        <UFormField
          class="w-full"
          name="arrivalTime"
          label="Jam Tiba"
          required
        >
          <UInputTime
            v-model="state.transportInformation.timeInformation.arrivalTime"
            class="w-full justify-center"
            :hour-cycle="24"
          />
        </UFormField>
      </div>

      <div class="flex w-full gap-4">
        <UFormField
          class="w-full"
          name="unloadingTime"
          label="Jam Mulai Pembongkaran"
          required
        >
          <UInputTime
            v-model="state.transportInformation.timeInformation.unloadingTime"
            class="w-full justify-center"
            :hour-cycle="24"
          />
        </UFormField>

        <UFormField
          class="w-full"
          name="deportArrivalTime"
          label="Jam Tiba di Depo"
          required
        >
          <UInputTime
            v-model="
              state.transportInformation.timeInformation.depotArrivalTime
            "
            class="w-full justify-center"
            :hour-cycle="24"
          />
        </UFormField>
      </div>

      <USeparator />

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
