<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import {
  operationsDOReceiverSchema,
  type OperationsDOReceiverState
} from '~/types/schemas'

const emit = defineEmits<{
  submit: []
  previous: []
}>()

const state = defineModel<OperationsDOReceiverState>({ required: true })

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<OperationsDOReceiverState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="do-receiver"
    :schema="operationsDOReceiverSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Informasi Customer</p>

      <div class="flex w-full gap-4">
        <UFormField name="customerName" label="Nama Customer" required>
          <UInput
            v-model="state.customerName"
            type="text"
            autocomplete="off"
            placeholder="PT. XYZ"
          />
        </UFormField>

        <!-- <UFormField name="customerId" label="ID Customer" required>
          <UInput
            v-model="state.customerId"
            type="text"
            autocomplete="off"
            placeholder="PT. XYZ"
          />
        </UFormField> -->
      </div>

      <UFormField name="address" label="Alamat" required>
        <UInput
          v-model="state.customerAddress"
          type="text"
          autocomplete="off"
          placeholder="Samarinda"
        />
      </UFormField>

      <USeparator />

      <p>Informasi Penerima BBM + HP</p>

      <div class="flex w-full gap-4">
        <UFormField name="fuelReceiver" label="Nama Penerima" required>
          <UInput
            v-model="state.receiverInformation.name"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="phoneNumber" label="Nomor Telepon" required>
          <UInput
            v-model="state.receiverInformation.phoneNumber"
            v-maska="'#### #### ####'"
            type="text"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <USeparator />

      <UFormField name="dateReceived" label="Tanggal Diterima" required>
        <UInput
          v-model="state.receiverDateReceived"
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
