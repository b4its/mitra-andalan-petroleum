<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import {
  operationsDOAdditionalSchema,
  type OperationsDOAdditionalState
} from '~/types/schemas'

const emit = defineEmits<{
  submit: []
  previous: []
}>()

const state = defineModel<OperationsDOAdditionalState>({ required: true })

function emptyNote() {
  return { note: '' }
}

const notes = computed(() => state.value.notes)

function addNote() {
  if (!state.value.notes) {
    state.value.notes = []
  }
  state.value.notes.push(emptyNote())
}

function removeNote(index: number) {
  state.value.notes.splice(index, 1)
}

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<OperationsDOAdditionalState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="do-additional"
    :schema="operationsDOAdditionalSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Catatan Pengiriman</p>

      <div class="flex w-full gap-4">
        <UFormField name="t2Depot" label="T2 Depo" required>
          <UInputNumber
            v-model="state.t2Depot"
            class="w-full"
            :min="1"
            placeholder="125.1"
          />
        </UFormField>

        <UFormField name="t2Unloading" label="T2 Bongkar" required>
          <UInputNumber
            v-model="state.t2Unloading"
            class="w-full"
            :min="1"
            placeholder="125.1"
          />
        </UFormField>
      </div>

      <div class="flex w-full gap-4">
        <UFormField
          name="indexSensitivity"
          label="Kepekaan Index (buku tera mobil)"
          required
        >
          <UInputNumber
            v-model="state.indexSensitivity"
            class="w-full"
            :min="1"
          />
        </UFormField>

        <UFormField name="fuelReceived" label="BBM Diterima" required>
          <UInputNumber
            v-model="state.fuelReceived"
            class="w-full"
            :min="1"
            placeholder="5000"
          />
        </UFormField>
      </div>

      <USeparator />

      <div class="space-y-3">
        <p>Catatan Tambahan</p>

        <div
          v-for="(note, index) in notes"
          :key="`note-${index}`"
          class="flex items-end gap-2"
        >
          <UFormField
            :name="`note.${index}.name`"
            label="Ketentuan"
            class="w-full"
          >
            <UInput v-model="note.note" placeholder="Ketentuan 1" />
          </UFormField>

          <UButton
            icon="i-lucide-trash-2"
            color="error"
            variant="ghost"
            :disabled="state.notes.length === 1"
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
          Selanjutnya
        </UButton>
      </div>
    </UPageCard>
  </UForm>
</template>
