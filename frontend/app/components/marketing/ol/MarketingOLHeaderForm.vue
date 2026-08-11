<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import {
  marketingOLHeaderSchema,
  type MarketingOLHeaderState
} from '~/types/schemas'

defineProps<{
  hasPrevious: boolean | undefined
  receivers: any
}>()

const emit = defineEmits<{
  submit: []
  previous: []
}>()

const state = defineModel<MarketingOLHeaderState>({ required: true })

const regionProvince = ref('')
const regionCity = ref('')

watch([regionProvince, regionCity], () => {
  if (regionCity.value) {
    state.value.location = [regionCity.value, regionProvince.value]
      .filter(Boolean)
      .join(', ')
  }
})

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<MarketingOLHeaderState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="letter-header"
    :schema="marketingOLHeaderSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <div class="flex w-full gap-4">
        <div class="w-full">
          <p class="text-sm font-medium text-muted mb-1.5">
            Lokasi <span class="text-red-500">*</span>
          </p>
          <WilayahLocationPicker
            v-model:province="regionProvince"
            v-model:city="regionCity"
          />
        </div>

        <UFormField name="date" label="Tanggal Dibuat" required>
          <UInput v-model="state.date" type="date" autocomplete="off" />
        </UFormField>
      </div>

      <USeparator />

      <UFormField name="regarding" label="Perihal Surat" required>
        <UInput
          v-model="state.regarding"
          type="text"
          autocomplete="off"
          placeholder="Surat Penawaran Harga Bahan Bakar Minyak Bio diesel"
        />
      </UFormField>

      <UFormField name="offeringLetterNumber" label="Nomor Surat" required>
        <UInput
          v-model="state.offeringLetterNumber"
          placeholder="Contoh 722/MAP/II-06/26"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <!-- <UFormField name="receiver" label="Yang Terhormat" required>
        <UInput
          v-model="state.receiver"
          type="text"
          autocomplete="off"
          placeholder="PT. XYZ"
        />
      </UFormField> -->

      <UFormField name="receiver" label="Yang Terhormat" required>
        <USelectMenu
          v-model="state.receiver"
          :items="receivers"
          placeholder="Pilih Customer"
          value-key="value"
          :ui="{ content: 'min-w-fit' }"
          class="w-full"
        >
          <template #item-label="{ item }">
            {{ item.label }}

            <span v-if="item.npwp" class="text-muted text-xs">
              · NPWP {{ item.npwp }}
            </span>
            <span v-if="item.address" class="text-muted text-xs">
              ({{ item.address }})
            </span>
          </template>
        </USelectMenu>
      </UFormField>

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
