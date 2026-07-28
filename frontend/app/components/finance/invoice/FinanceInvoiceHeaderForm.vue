<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import {
  financeInvoiceHeaderSchema,
  type FinanceInvoiceHeaderState
} from '~/types/schemas'

defineProps<{
  hasPrevious: boolean | undefined
}>()

const emit = defineEmits<{
  submit: []
  previous: []
}>()

const state = defineModel<FinanceInvoiceHeaderState>({ required: true })

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<FinanceInvoiceHeaderState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="invoice-header"
    :schema="financeInvoiceHeaderSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Informasi Perusahaan</p>

      <div class="flex w-full gap-4">
        <UFormField name="companyName" label="Nama" required>
          <UInput
            v-model="state.companyInformation.name"
            type="text"
            autocomplete="off"
            placeholder="PT. XYZ"
          />
        </UFormField>

        <UFormField name="companyEmail" label="Email" required>
          <UInput
            v-model="state.companyInformation.email"
            type="mail"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <div class="flex w-full gap-4">
        <UFormField name="address" label="Alamat" required>
          <UInput
            v-model="state.companyInformation.address"
            type="text"
            autocomplete="off"
            placeholder="PT. XYZ"
          />
        </UFormField>

        <UFormField name="phoneNumber" label="Nomor Telepon" required>
          <UInput
            v-model="state.companyInformation.phoneNumber"
            v-maska="'0541-#######'"
            type="text"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <USeparator />

      <p>Bill To & Delivery Point</p>

      <div class="flex w-full gap-4">
        <UFormField name="billTo" label="Bill To" required>
          <UTextarea
            v-model="state.billToInformation"
            class="w-full"
            :rows="4"
          />
        </UFormField>

        <UFormField name="deliveryPoint" label="Delivery Point" required>
          <UTextarea
            v-model="state.deliveryPointInformation"
            class="w-full"
            :rows="4"
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
