<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import type { OfferingLetters } from '~/types/marketing'
import {
  marketingPOCustomerSchema,
  type MarketingPOCustomerState
} from '~/types/schemas'

const props = defineProps<{
  offeringLetters: any
}>()

const emit = defineEmits<{
  submit: []
}>()

const state = defineModel<MarketingPOCustomerState>({ required: true })

function onSubmit(_event: FormSubmitEvent<MarketingPOCustomerState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="po-customer"
    :schema="marketingPOCustomerSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <UFormField name="offeringLetter" label="Nomor Surat Penawaran" required>
        <USelectMenu
          v-model="state.selectedOfferingLetter"
          :items="offeringLetters"
          placeholder="Pilih Surat Penawaran"
          value-key="value"
          :ui="{ content: 'min-w-fit' }"
          class="w-full"
        >
          <template #item-label="{ item }">
            {{ item.label }}

            <span class="text-muted text-xs"> ({{ item.olNumber }}) </span>
          </template>
        </USelectMenu>
      </UFormField>

      <UFormField
        name="purchaseOrderNumber"
        label="Nomor Purchase Order Customer"
        required
      >
        <UInput
          v-model="state.purchaseOrderNumber"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <div class="flex gap-4">
        <UFormField
          name="total"
          label="Total (Liter)"
          class="w-full"
          required
        >
          <UInputNumber v-model="state.total" class="w-full" :min="1" />
        </UFormField>

        <UFormField name="poReceivedDate" label="PO Customer Diterima" required>
          <UInput
            v-model="state.poReceivedDate"
            type="date"
            autocomplete="off"
            class="w-full"
          />
        </UFormField>
      </div>

      <UFormField name="poFile" label="File Purchase Order Customer" required>
        <UFileUpload
          v-model="state.poDocument"
          label="Upload File Purchase Order"
          description="Format file .pdf dengan max 5MB"
        />
      </UFormField>

      <div class="flex justify-end pt-4">
        <UButton type="submit" trailing-icon="i-lucide-arrow-right">
          Upload PO Customer
        </UButton>
      </div>
    </UPageCard>
  </UForm>
</template>
