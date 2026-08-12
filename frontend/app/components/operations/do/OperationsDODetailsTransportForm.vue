<script setup lang="ts">
import { Time } from '@internationalized/date'
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

function toTime(value: string | undefined): Time | null {
  if (!value) return null
  const match = /^(\d{1,2}):(\d{2})(?::(\d{2}))?$/.exec(value)
  if (!match) return null
  return new Time(Number(match[1]), Number(match[2]), match[3] ? Number(match[3]) : 0)
}

function fromTime(value: unknown): string | undefined {
  if (!value) return undefined
  if (typeof value === 'string') return value
  if (typeof (value as { toString?: unknown }).toString === 'function') {
    return (value as { toString: () => string }).toString()
  }
  return undefined
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
        <UFormField name="productInformation.name" label="Nama Produk" required>
          <UInput
            v-model="state.productInformation.name"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="productInformation.qty" label="Volume/Kuantitas (Liter)" required>
          <UInputNumber
            v-model="state.productInformation.qty"
            class="w-full"
            :min="1"
          />
        </UFormField>
      </div>

      <div class="flex w-full gap-4">
        <UFormField name="productInformation.topSeal" label="Segel Atas" required>
          <UInput
            v-model="state.productInformation.topSeal"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="productInformation.bottomSeal" label="Segel Bawah" required>
          <UInput
            v-model="state.productInformation.bottomSeal"
            type="text"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <UFormField name="productInformation.temperature" label="Temperature" required>
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
        <UFormField name="transportInformation.transportType" label="Dikirim Dengan" required>
          <UInput
            v-model="state.transportInformation.transportType"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="transportInformation.transportNumber" label="No. Kendaraan" required>
          <UInput
            v-model="state.transportInformation.transportNumber"
            type="text"
            autocomplete="off"
            placeholder="contoh KT 1234 AB"
          />
        </UFormField>
      </div>

      <div class="flex w-full gap-4">
        <UFormField name="transportInformation.startKm" label="Km. Awal" required>
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

        <UFormField name="transportInformation.endKm" label="Km. Akhir" required>
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

        <UFormField name="transportInformation.sgMeter" label="SG Meter" required>
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
          name="transportInformation.timeInformation.departureTime"
          label="Jam Berangkat"
        >
          <UInputTime
            :model-value="toTime(state.transportInformation.timeInformation.departureTime)"
            class="w-full justify-center"
            :hour-cycle="24"
            @update:model-value="state.transportInformation.timeInformation.departureTime = fromTime($event)"
          />
        </UFormField>

        <UFormField
          class="w-full"
          name="transportInformation.timeInformation.arrivalTime"
          label="Jam Tiba"
        >
          <UInputTime
            :model-value="toTime(state.transportInformation.timeInformation.arrivalTime)"
            class="w-full justify-center"
            :hour-cycle="24"
            @update:model-value="state.transportInformation.timeInformation.arrivalTime = fromTime($event)"
          />
        </UFormField>
      </div>

      <div class="flex w-full gap-4">
        <UFormField
          class="w-full"
          name="transportInformation.timeInformation.unloadingTime"
          label="Jam Mulai Pembongkaran"
        >
          <UInputTime
            :model-value="toTime(state.transportInformation.timeInformation.unloadingTime)"
            class="w-full justify-center"
            :hour-cycle="24"
            @update:model-value="state.transportInformation.timeInformation.unloadingTime = fromTime($event)"
          />
        </UFormField>

        <UFormField
          class="w-full"
          name="transportInformation.timeInformation.depotArrivalTime"
          label="Jam Tiba di Depo"
        >
          <UInputTime
            :model-value="toTime(state.transportInformation.timeInformation.depotArrivalTime)"
            class="w-full justify-center"
            :hour-cycle="24"
            @update:model-value="state.transportInformation.timeInformation.depotArrivalTime = fromTime($event)"
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
