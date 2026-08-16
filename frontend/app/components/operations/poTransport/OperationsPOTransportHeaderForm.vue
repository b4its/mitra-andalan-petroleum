<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import {
  operationsPOTransportHeaderSchema,
  type OperationsPOTransportHeaderState
} from '~/types/schemas'

defineProps<{
  hasPrevious: boolean | undefined
}>()

const emit = defineEmits<{
  submit: []
  previous: []
}>()

const state = defineModel<OperationsPOTransportHeaderState>({ required: true })

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<OperationsPOTransportHeaderState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="po-transport-header"
    :schema="operationsPOTransportHeaderSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Informasi PO Transportir</p>

      <UFormField name="date" label="Tanggal Dibuat" required>
        <UInput v-model="state.date" type="date" autocomplete="off" />
      </UFormField>

      <UFormField name="regarding" label="Perihal Surat" required>
        <UInput
          v-model="state.regarding"
          type="text"
          autocomplete="off"
          placeholder="Surat Penawaran Harga Bahan Bakar Minyak Bio diesel"
        />
      </UFormField>

      <UFormField name="poTransportNumber" label="Nomor Surat" required>
        <UInput
          v-model="state.poTransportNumber"
          placeholder="Contoh 123/PO-TRANS/MAP/I/2026 "
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <div class="flex w-full gap-4">
        <UFormField name="receiver" label="Nama Transportir Penerima" required>
          <UInput
            v-model="state.receiver"
            type="text"
            autocomplete="off"
            placeholder="Alea"
          />
        </UFormField>

        <UFormField name="picPerson" label="Nama PIC" required>
          <UInput
            v-model="state.picPerson"
            type="text"
            autocomplete="off"
            placeholder="Alea"
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
