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
const location = defineModel<string>('location', { default: '' })

const regionProvince = ref('')
const regionCity = ref('')
const baseStreet = ref('')

watch(
  () => state.value.companyInformation.address,
  (value) => {
    const suffix = [regionCity.value, regionProvince.value]
      .filter(Boolean)
      .join(', ')
    if (suffix && value && value.endsWith(suffix)) {
      baseStreet.value = value
        .slice(0, value.length - suffix.length)
        .replace(/[, ]+$/, '')
    } else {
      baseStreet.value = value
    }
  }
)

watch([regionProvince, regionCity], () => {
  location.value = regionCity.value
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

      <div class="w-full">
        <p class="text-sm font-medium text-muted mb-1.5">
          Lokasi <span class="text-red-500">*</span>
        </p>
        <WilayahLocationPicker
          v-model:province="regionProvince"
          v-model:city="regionCity"
        />
      </div>

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
