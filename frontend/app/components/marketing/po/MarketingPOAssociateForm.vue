<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import { watch } from 'vue'
import { formatNPWP } from '~/utils'
import {
  marketingPOAssociateSchema,
  type MarketingPOAssociateState
} from '~/types/schemas'

interface ReceiverOption {
  label: string
  value: unknown
  npwp?: string | null
  address?: string | null
}

defineProps<{
  hasPrevious: boolean | undefined
  receivers: ReceiverOption[]
}>()

const emit = defineEmits<{
  submit: []
  previous: []
}>()

const state = defineModel<MarketingPOAssociateState>({ required: true })

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<MarketingPOAssociateState>) {
  emit('submit')
}

watch(
  () => state.value?.receiver,
  (value) => {
    if (!state.value || !value) return
    state.value.receiver.name = value.name
    state.value.receiver.npwp = formatNPWP(value.npwp) || undefined
    state.value.receiver.address = value.address || undefined
    state.value.receiver.contactPerson = value.contactPerson || undefined
    state.value.receiver.email = value.email || undefined
  }
)
</script>

<template>
  <UForm
    id="letter-associate"
    :schema="marketingPOAssociateSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Informasi Perusahaan Mitra</p>

      <!-- <UFormField name="companyName" label="Nama Perusahaan" required>
        <UInput
          v-model="state.associateInformation.name"
          type="text"
          autocomplete="off"
        />
      </UFormField> -->

      <UFormField name="receiver" label="Nama Perusahaan Supplier" required>
        <USelectMenu
          v-model="state.receiver"
          :items="receivers"
          placeholder="Pilih Supplier"
          value-key="value"
          :ui="{ content: 'min-w-fit' }"
          class="w-full"
        >
          <template #item-label="{ item }">
            {{ item.label }}

            <span v-if="item.npwp" class="text-muted text-xs">
              · NPWP {{ formatNPWP(item.npwp) }}
            </span>
            <span v-if="item.address" class="text-muted text-xs">
              ({{ item.address }})
            </span>
          </template>
        </USelectMenu>
      </UFormField>

      <UFormField name="address" label="Alamat">
        <UTextarea
          v-model="state.receiver.address"
          autocomplete="off"
          :rows="3"
          class="w-full"
        />
      </UFormField>

      <UFormField name="npwp" label="NPWP">
        <UInput
          v-model="state.receiver.npwp"
          v-maska="'##.###.###.#-###.###'"
          inputmode="numeric"
          placeholder="00.000.000.0-000.000"
          autocomplete="off"
        />
      </UFormField>

      <div class="flex w-full gap-4">
        <UFormField name="phoneNumber" label="Nomor Telepon">
          <UInput
            v-model="state.receiver.contactPerson"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="email" label="Alamat Email">
          <UInput
            v-model="state.receiver.email"
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
