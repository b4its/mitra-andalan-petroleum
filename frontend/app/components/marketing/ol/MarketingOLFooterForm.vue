<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import {
  marketingOLFooterSchema,
  type MarketingOLFooterState
} from '~/types/schemas'

const emit = defineEmits<{
  submit: []
  previous: []
  preview: []
}>()

const state = defineModel<MarketingOLFooterState>({ required: true })
const location = defineModel<string>('location', { default: '' })

function onPreview() {
  emit('preview')
}

const deadlineOptions = [
  { label: '1 - 14', value: '1 - 14' },
  { label: '15 - 28', value: '15 - 28' },
  { label: '15 - 29', value: '15 - 29' },
  { label: '15 - 30', value: '15 - 30' },
  { label: '15 - 31', value: '15 - 31' },
  { label: 'Custom...', value: '__custom__' }
]

const deadlineCustom = ref(
  state.value.purchaseOrderDeadline
  && !deadlineOptions.some(o => o.value === state.value.purchaseOrderDeadline)
    ? state.value.purchaseOrderDeadline
    : ''
)

watch(
  () => state.value.purchaseOrderDeadline,
  (value) => {
    if (value === '__custom__') {
      deadlineCustom.value = ''
      state.value.purchaseOrderDeadline = ''
    } else if (!deadlineOptions.some(o => o.value === value)) {
      deadlineCustom.value = value || ''
    }
  }
)

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
        label="Tenggat Purchase Order"
        description="Pilih periode atau gunakan Custom untuk range bebas"
        required
      >
        <USelect
          v-model="state.purchaseOrderDeadline"
          :items="deadlineOptions"
          value-key="value"
          placeholder="Pilih periode tenggat"
        />
      </UFormField>

      <UFormField
        v-if="state.purchaseOrderDeadline === '__custom__'"
        name="purchaseOrderDeadlineCustom"
        label="Range Custom (hari)"
        required
      >
        <UInput
          v-model="deadlineCustom"
          type="text"
          placeholder="Contoh: 5 - 20 atau 30"
          @update:model-value="(v: string) => (state.purchaseOrderDeadline = v)"
        />
      </UFormField>

      <USeparator />

      <UFormField name="offerorName" label="Hormat Kami" required>
        <UInput v-model="state.offeror.name" type="text" autocomplete="off" />
      </UFormField>

      <USeparator />

      <p>Informasi Perusahaan</p>

      <UFormField name="address" label="Alamat" required>
        <UTextarea
          v-model="state.companyInformation.address"
          autocomplete="off"
          :rows="3"
          class="w-full"
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
          type="button"
          variant="ghost"
          color="neutral"
          leading-icon="i-lucide-arrow-left"
          @click="previous"
        >
          Sebelumnya
        </UButton>

        <div class="flex gap-2">
          <UButton
            type="button"
            color="info"
            variant="soft"
            leading-icon="i-lucide-eye"
            @click="onPreview"
          >
            Preview Dokumen
          </UButton>

          <UButton type="submit" trailing-icon="i-lucide-arrow-right">
            Selesai
          </UButton>
        </div>
      </div>
    </UPageCard>
  </UForm>
</template>
