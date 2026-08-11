<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import {
  marketingOLFooterSchema,
  type MarketingOLFooterState
} from '~/types/schemas'

const emit = defineEmits<{
  submit: []
  previous: []
}>()

const state = defineModel<MarketingOLFooterState>({ required: true })

const regionProvince = ref('')
const regionCity = ref('')
const baseStreet = ref(state.value.companyInformation.address)

watch([regionProvince, regionCity], () => {
  if (regionCity.value) {
    state.value.companyInformation.address = [
      baseStreet.value,
      regionCity.value,
      regionProvince.value
    ]
      .filter(Boolean)
      .join(', ')
  }
})

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<MarketingOLFooterState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="letter-footer"
    :schema="marketingOLFooterSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <UFormField
        name="purchaseOrderDeadline"
        label="Tenggat Purchase Order (PO)"
        required
      >
        <UInputNumber
          v-model="state.purchaseOrderDeadline"
          :ui="{
            root: 'w-full'
          }"
          orientation="vertical"
          :step="1"
          locale="id-ID"
          :format-options="{
            style: 'unit',
            unit: 'day',
            unitDisplay: 'long'
          }"
        />
      </UFormField>

      <USeparator />

      <UFormField name="offerorName" label="Hormat Kami" required>
        <UInput v-model="state.offeror.name" type="text" autocomplete="off" />
      </UFormField>

      <UFormField name="offerorSignature" label="Tanda Tangan" required>
        <UFileUpload
          v-model="state.offeror.signature"
          label="Upload File Tanda Tangan"
          description="Format file .png dengan max 50MB"
        />
      </UFormField>

      <USeparator />

      <p>Informasi Perusahaan</p>

      <UFormField name="address" label="Alamat" required>
        <UInput
          v-model="state.companyInformation.address"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <WilayahLocationPicker
        v-model:province="regionProvince"
        v-model:city="regionCity"
      />

      <div class="flex w-full gap-4">
        <UFormField name="phoneNumber" label="Nomor Telepon" required>
          <UInput
            v-model="state.companyInformation.phoneNumber"
            v-maska="'0541-#######'"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="email" label="Alamat Email" required>
          <UInput
            v-model="state.companyInformation.email"
            type="email"
            autocomplete="off"
          />
        </UFormField>
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
          Selesai
        </UButton>
      </div>
    </UPageCard>
  </UForm>
</template>
