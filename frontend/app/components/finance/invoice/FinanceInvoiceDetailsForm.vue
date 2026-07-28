<script setup lang="ts">
import type { FormSubmitEvent, SelectMenuItem } from '@nuxt/ui'
import {
  financeInvoiceDetailsSchema,
  type FinanceInvoiceDetailsState
} from '~/types/schemas'

defineProps<{
  hasPrevious: boolean | undefined
}>()

const emit = defineEmits<{
  submit: []
  previous: []
}>()

const deliveryOrderGroups = [
  [
    {
      type: 'label',
      label: 'PT. MIGAS KUKAR MANDIRI'
    },
    {
      label: '1086/DO/MAP/V/2026',
      value: '1086/DO/MAP/V/2026'
    },
    {
      label: '1087/DO/MAP/V/2026',
      value: '1087/DO/MAP/V/2026'
    }
  ],
  [
    {
      type: 'label',
      label: 'PT. BERAU MINERAL ENERGI'
    },
    {
      label: '1092/DO/BME/V/2026',
      value: '1092/DO/BME/V/2026'
    },
    {
      label: '1093/DO/BME/V/2026',
      value: '1093/DO/BME/V/2026'
    }
  ],
  [
    {
      type: 'label',
      label: 'PT. KALTIM OIL SERVICES'
    },
    {
      label: '1098/DO/KOS/V/2026',
      value: '1098/DO/KOS/V/2026'
    },
    {
      label: '1099/DO/KOS/V/2026',
      value: '1099/DO/KOS/V/2026'
    }
  ]
] satisfies SelectMenuItem[][]

const state = defineModel<FinanceInvoiceDetailsState>({ required: true })

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<FinanceInvoiceDetailsState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="invoice-details"
    :schema="financeInvoiceDetailsSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Invoice Information</p>

      <div class="flex w-full gap-4">
        <UFormField name="invoiceNumber" label="Nomor Invoice" required>
          <UInput
            v-model="state.invoiceInformation.invoiceNumber"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField
          name="invoiceTerms"
          label="Terms Day After Delivery"
          required
        >
          <UInputNumber
            v-model="state.invoiceInformation.terms"
            class="w-full"
            :min="1"
            locale="id-ID"
            :format-options="{
              style: 'unit',
              unit: 'day',
              unitDisplay: 'long'
            }"
          />
        </UFormField>
      </div>

      <div class="flex w-full gap-4">
        <UFormField
          name="invoiceDate"
          label="Invoice Date"
          required
          class="flex-1"
        >
          <UInput
            v-model="state.invoiceInformation.invoiceDate"
            type="date"
            autocomplete="off"
            class="w-full"
          />
        </UFormField>

        <UFormField
          name="invoiceDueDate"
          label="Invoice Due Date"
          required
          class="flex-1"
        >
          <UInput
            v-model="state.invoiceInformation.invoiceDueDate"
            type="date"
            autocomplete="off"
            class="w-full"
          />
        </UFormField>
      </div>

      <USeparator />

      <p>Customer Purchase Information</p>

      <div class="flex w-full gap-4">
        <UFormField
          name="customerPurchaseOrderNumber"
          label="Customer PO No"
          required
        >
          <UInput
            v-model="
              state.customerPurchaseInformation.customerPurchaseOrderNumber
            "
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField
          name="taxInvoiceNumber"
          label="Tax No (Faktur Pajak)"
          required
        >
          <UInput
            v-model="state.customerPurchaseInformation.taxInvoiceNumber"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="salesOrderNumber" label="SO No" required>
          <UInput
            v-model="state.customerPurchaseInformation.salesOrderNumber"
            type="text"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <UFormField
        name="deliveryOrderNumberData"
        label="Delivery Order Number"
        required
      >
        <USelectMenu
          v-model="state.customerPurchaseInformation.deliveryOrderNumberData"
          multiple
          value-key="value"
          placeholder="Select delivery order numbers"
          :items="deliveryOrderGroups"
          class="w-full"
        />
      </UFormField>

      <USeparator />

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
