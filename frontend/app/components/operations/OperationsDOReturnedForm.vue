<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import { operationsDOSchema, type OperationsDOState } from '~/types/schemas'

const emit = defineEmits<{
  submit: []
}>()

const state = defineModel<OperationsDOState>({ required: true })

function onSubmit(_event: FormSubmitEvent<OperationsDOState>) {
  emit('submit')
}

const value = ref<string>()

const deliveryOrders = ref([
  {
    label: 'PT. MIGAS KUKAR MANDIRI',
    value: '1086/DO/MAP/V/2026'
  },
  {
    label: 'PT. BERAU MINERAL ENERGI',
    value: '1092/DO/BME/V/2026'
  },
  {
    label: 'PT. KALTIM OIL SERVICES',
    value: '1098/DO/KOS/V/2026'
  }
])
</script>

<template>
  <UForm
    id="po-customer"
    :schema="operationsDOSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <UFormField name="deliveryOrder" label="Nomor Delivery Order" required>
        <USelect
          v-model="state.deliveryOrderNumber"
          :items="deliveryOrders"
          placeholder="Pilih "
          value-key="value"
          :ui="{ content: 'min-w-fit' }"
          class="w-full"
        >
          <template #item-label="{ item }">
            {{ item.label }}

            <span class="text-muted text-xs"> ({{ item.value }}) </span>
          </template>
        </USelect>
      </UFormField>

      <UFormField
        name="doFile"
        label="File Delivery Order Yang Dikembalikan"
        required
      >
        <UFileUpload
          v-model="state.doDocument"
          label="Upload File Delivery Order"
          description="Format file .pdf dengan max 5MB"
        />
      </UFormField>

      <div class="flex justify-end pt-4">
        <UButton type="submit" trailing-icon="i-lucide-arrow-right">
          Upload DO
        </UButton>
      </div>
    </UPageCard>
  </UForm>
</template>
