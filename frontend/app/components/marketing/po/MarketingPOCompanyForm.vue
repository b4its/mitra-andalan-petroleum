<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import {
  marketingPOCompanySchema,
  type MarketingPOCompanyState
} from '~/types/schemas'

defineProps<{
  hasPrevious: boolean | undefined
}>()

const emit = defineEmits<{
  submit: []
  previous: []
}>()

const state = defineModel<MarketingPOCompanyState>({ required: true })

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

function onSubmit(_event: FormSubmitEvent<MarketingPOCompanyState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="letter-company"
    :schema="marketingPOCompanySchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Informasi Perusahaan</p>

      <UFormField name="companyName" label="Nama Perusahaan" required>
        <UInput
          v-model="state.companyInformation.name"
          type="text"
          autocomplete="off"
        />
      </UFormField>

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

      <UFormField name="npwp" label="NPWP" required>
        <UInput
          v-model="state.companyInformation.npwp"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <div class="flex w-full gap-4">
        <UFormField name="phoneNumber" label="Nomor Telepon" required>
          <UInput
            v-model="state.companyInformation.contactPerson"
            v-maska="'#### #### ####'"
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
