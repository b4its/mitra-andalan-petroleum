<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import {
  financeInvoiceFooterSchema,
  type FinanceInvoiceFooterState
} from '~/types/schemas'

defineProps<{
  hasPrevious: boolean | undefined
}>()

const emit = defineEmits<{
  submit: []
  previous: []
}>()

const state = defineModel<FinanceInvoiceFooterState>({ required: true })

function emptyNote() {
  return { term: '' }
}

const termAndConditions = computed(() => state.value.termsAndCondition)

function addNote() {
  if (!state.value.termsAndCondition) {
    state.value.termsAndCondition = []
  }
  state.value.termsAndCondition.push(emptyNote())
}

function removeNote(index: number) {
  state.value.termsAndCondition.splice(index, 1)
}

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<FinanceInvoiceFooterState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="invoice-footer"
    :schema="financeInvoiceFooterSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Rekening Pembayaran</p>

      <div class="flex w-full gap-4">
        <UFormField name="bankName" label="Nama Bank" required>
          <UInput
            v-model="state.paymentInformation.bankName"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="accountNumber" label="Nomor Rekening" required>
          <UInput
            v-model="state.paymentInformation.accountNumber"
            type="text"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <UFormField name="accountName" label="Nama Rekening" required>
        <UInput
          v-model="state.paymentInformation.accountName"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <USeparator />

      <div class="space-y-3">
        <p>Catatan Tambahan</p>

        <div
          v-for="(term, index) in termAndConditions"
          :key="`note-${index}`"
          class="flex items-end gap-2"
        >
          <UFormField
            :name="`note.${index}.name`"
            label="Ketentuan"
            class="w-full"
            required
          >
            <UInput v-model="term.term" placeholder="Ketentuan 1" />
          </UFormField>

          <UButton
            icon="i-lucide-trash-2"
            color="error"
            variant="ghost"
            :disabled="state.termsAndCondition.length === 1"
            @click="removeNote(index)"
          />
        </div>

        <UButton
          icon="i-lucide-plus"
          color="neutral"
          variant="subtle"
          size="sm"
          label="Tambah Catatan"
          @click="addNote"
        />
      </div>

      <USeparator />

      <p>Tertanda Pengirim</p>

      <div class="flex w-full gap-4">
        <UFormField name="companyName" label="Nama Perusahaan" required>
          <UInput
            v-model="state.signature.companyName"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="createdBy" label="Dibuat Oleh" required>
          <UInput
            v-model="state.signature.createdBy"
            type="text"
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
          Selesai
        </UButton>
      </div>
    </UPageCard>
  </UForm>
</template>
