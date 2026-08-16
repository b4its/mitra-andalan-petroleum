<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import {
  operationsDOHeaderSchema,
  type OperationsDOHeaderState
} from '~/types/schemas'

defineProps<{
  purchaseOrders: {
    label: string
    customerName: string
    subtitle: string
    value: Record<string, unknown>
  }[]
  hasPrevious: boolean | undefined
}>()

const emit = defineEmits<{
  submit: []
  previous: []
}>()

const state = defineModel<OperationsDOHeaderState>({ required: true })

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<OperationsDOHeaderState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="do-header"
    :schema="operationsDOHeaderSchema"
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

        <UFormField name="companySubName" label="Sub Nama" required>
          <UInput
            v-model="state.companyInformation.nameSub"
            type="text"
            autocomplete="off"
            placeholder="contoh Distributor for Elnusa Petrofin"
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
            type="text"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <USeparator />

      <p>Informasi Surat Delivery Order</p>

      <div class="flex w-full gap-4">
        <UFormField name="doNumber" label="Nomor Delivery Order" required>
          <UInput
            v-model="state.doInformation.doNumber"
            type="text"
            autocomplete="off"
            placeholder="001/DO/2026/VIII/12"
          />
        </UFormField>

        <UFormField name="doDateCreated" label="Tanggal Delivery Order" required>
          <UInput
            v-model="state.doInformation.doDateCreated"
            type="date"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <div class="flex w-full gap-4">
        <!-- <UFormField name="poCustomerNumber" label="Nomor Purchase Order Customer" required>
          <UInput
            v-model="state.doInformation.poCustomerNumber"
            type="text"
            autocomplete="off"
            placeholder="001/DO/2026/VIII/12"
          />
        </UFormField> -->

        <UFormField
          name="poCustomerNumber"
          label="Nomor Surat Purchase Order Customer"
          required
        >
          <USelectMenu
            v-model="state.doInformation.poCustomerNumber"
            :items="purchaseOrders"
            placeholder="Pilih Surat Purchase Order"
            value-key="value"
            :ui="{ content: 'min-w-fit' }"
            class="w-full"
          >
            <template #item-label="{ item }">
              {{ item.label }}

              <span class="text-muted text-xs">
                ({{ item.customerName }})
              </span>
            </template>
          </USelectMenu>
        </UFormField>

        <UFormField name="soNumber" label="Nomor SO" required>
          <UInput
            v-model="state.doInformation.soNumber"
            type="text"
            autocomplete="off"
            placeholder="001/DO/2026/VIII/12"
          />
        </UFormField>
      </div>

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
