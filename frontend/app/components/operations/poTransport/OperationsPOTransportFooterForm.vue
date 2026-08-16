<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import {
  operationsPOTransportFooterSchema,
  type OperationsPOTransportFooterState
} from '~/types/schemas'

defineProps<{
  hasPrevious: boolean | undefined
}>()

const emit = defineEmits<{
  submit: []
  previous: []
}>()

const state = defineModel<OperationsPOTransportFooterState>({ required: true })

function emptyContact() {
  return {
    name: '',
    phoneNumber: ''
  }
}

const companyContacts = computed(
  () => state.value.contactPerson.companyContactPerson
)

const customerContacts = computed(
  () => state.value.contactPerson.customerContactPerson
)

function addItem(item: 'companyContactPerson' | 'customerContactPerson') {
  if (!state.value.contactPerson[item]) {
    state.value.contactPerson[item] = []
  }
  state.value.contactPerson[item].push(emptyContact())
}

function removeItem(
  item: 'companyContactPerson' | 'customerContactPerson',
  index: number
) {
  if (!state.value.contactPerson[item]) {
    state.value.contactPerson[item] = []
  }

  state.value.contactPerson[item].splice(index, 1)
}

// function addItem() {
//   if (!state.value.contactPerson.companyContactPerson) {
//     state.value.contactPerson.companyContactPerson = [];
//   }
//   state.value.contactPerson.companyContactPerson.push(emptyContact());
// }

// function removeItem(index: number) {
//   if (!state.value.contactPerson.companyContactPerson) {
//     state.value.contactPerson.companyContactPerson = [];
//   }

//   state.value.contactPerson.companyContactPerson.splice(index, 1);
// }

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<OperationsPOTransportFooterState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="po-transport-footer"
    :schema="operationsPOTransportFooterSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Informasi Tambahan PO Transportir</p>

      <UFormField name="loadingInformation" label="Loading" required>
        <UInput
          v-model="state.loadingInformation"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <UFormField name="discharge" label="Discharge" required>
        <UTextarea
          v-model="state.discharge"
          class="w-full"
          :rows="4"
          autocomplete="off"
        />
      </UFormField>

      <UFormField name="receiver" label="Terms of Payment" required>
        <UInput v-model="state.termsOfPayment" type="text" autocomplete="off" />
      </UFormField>

      <UFormField name="shrinkageTolerance" label="Toleransi Susut" required>
        <UInput
          v-model="state.shrinkageTolerance"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <USeparator />
      <p>Informasi Contact Person Perusahaan</p>

      <UFormField name="companyName" label="Nama Perusahaan" required>
        <UInput
          v-model="state.contactPerson.companyName"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <div
        v-for="(contact, index) in companyContacts"
        :key="`contact-${index}`"
        class="flex items-end gap-2"
      >
        <UFormField
          :name="`contactPerson.companyContactPerson.${index}.name`"
          label="Nama"
          class="w-full"
          required
        >
          <UInput v-model="contact.name" placeholder="Nama kontak" />
        </UFormField>

        <UFormField
          :name="`contactPerson.companyContactPerson.${index}.phoneNumber`"
          label="Nomor Telepon"
          class="w-full"
          required
        >
          <UInput v-model="contact.phoneNumber" placeholder="Nomor Telepon" />
        </UFormField>

        <UButton
          icon="i-lucide-trash-2"
          color="error"
          variant="ghost"
          @click="removeItem('companyContactPerson', index)"
        />
      </div>

      <UButton
        icon="i-lucide-plus"
        color="neutral"
        variant="subtle"
        size="sm"
        label="Tambah kontak"
        @click="addItem('companyContactPerson')"
      />

      <USeparator />
      <p>Informasi Contact Person Customer</p>

      <UFormField name="companyName" label="Nama Perusahaan" required>
        <UInput
          v-model="state.contactPerson.customerName"
          type="text"
          autocomplete="off"
        />
      </UFormField>

      <div
        v-for="(contact, index) in customerContacts"
        :key="`contact-${index}`"
        class="flex items-end gap-2"
      >
        <UFormField
          :name="`contactPerson.companyContactPerson.${index}.name`"
          label="Nama"
          class="w-full"
          required
        >
          <UInput v-model="contact.name" placeholder="Nama kontak" />
        </UFormField>

        <UFormField
          :name="`contactPerson.companyContactPerson.${index}.phoneNumber`"
          label="Nomor Telepon"
          class="w-full"
          required
        >
          <UInput v-model="contact.phoneNumber" placeholder="Nomor Telepon" />
        </UFormField>

        <UButton
          icon="i-lucide-trash-2"
          color="error"
          variant="ghost"
          @click="removeItem('customerContactPerson', index)"
        />
      </div>

      <UButton
        icon="i-lucide-plus"
        color="neutral"
        variant="subtle"
        size="sm"
        label="Tambah kontak"
        @click="addItem('customerContactPerson')"
      />

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
