<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import {
  operationsDOTransportSchema,
  type OperationsDOTransportState
} from '~/types/schemas'

const emit = defineEmits<{
  submit: []
  previous: []
}>()

const state = defineModel<OperationsDOTransportState>({ required: true })

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<OperationsDOTransportState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="do-transport"
    :schema="operationsDOTransportSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Informasi Agen/Transportir</p>

      <div class="flex w-full gap-4">
        <UFormField name="transportName" label="Nama Agen/Transportir" required>
          <UInput
            v-model="state.transportName"
            type="text"
            autocomplete="off"
            placeholder="PT. XYZ"
          />
        </UFormField>

        <UFormField name="transportId" label="ID Agen/Transportir" required>
          <UInput
            v-model="state.transportId"
            type="text"
            autocomplete="off"
            placeholder="PT. XYZ"
          />
        </UFormField>
      </div>

      <UFormField name="transportAddress" label="Alamat" required>
        <UInput
          v-model="state.transportAddress"
          type="text"
          autocomplete="off"
          placeholder="Samarinda"
        />
      </UFormField>

      <USeparator />

      <p>Informasi Penerima</p>

      <div class="flex w-full gap-4">
        <UFormField name="driverInformation.name" label="Nama Driver" required>
          <UInput
            v-model="state.driverInformation.name"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="driverInformation.phoneNumber" label="Nomor Telepon" required>
          <UInput
            v-model="state.driverInformation.phoneNumber"
            type="text"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <USeparator />

      <UFormField name="transportDateReceived" label="Tanggal Diterima" required>
        <UInput
          v-model="state.transportDateReceived"
          type="date"
          autocomplete="off"
        />
      </UFormField>

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
