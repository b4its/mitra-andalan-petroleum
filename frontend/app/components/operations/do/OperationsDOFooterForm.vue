<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui";
import {
  operationsDOFooterSchema,
  type OperationsDOFooterState,
} from "~/types/schemas";

const props = defineProps<{
  isLoading: boolean | undefined;
}>();

const emit = defineEmits<{
  submit: [];
  previous: [];
}>();

const state = defineModel<OperationsDOFooterState>({ required: true });

function previous() {
  emit("previous");
}

function onSubmit(_event: FormSubmitEvent<OperationsDOFooterState>) {
  emit("submit");
}
</script>

<template>
  <UForm
    id="do-footer"
    :schema="operationsDOFooterSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Tertanda Pengirim</p>

      <div class="flex w-full gap-4">
        <UFormField name="companyCoordinator" label="Koordinator MAP" required>
          <UInput
            type="text"
            v-model="state.companyCoordinator"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="distributionAdmin" label="Admin Distribusi" required>
          <UInput
            type="text"
            v-model="state.distributionAdmin"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <USeparator />

      <p>Tertanda Penerima dan Transportir</p>

      <div class="flex w-full gap-4">
        <UFormField name="receiver" label="Penerima" required>
          <UInput type="text" v-model="state.receiver" autocomplete="off" />
        </UFormField>

        <UFormField name="driver" label="Driver/Officer" required>
          <UInput type="text" v-model="state.driver" autocomplete="off" />
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

        <UButton
          :loading="isLoading"
          type="submit"
          trailing-icon="i-lucide-arrow-right"
        >
          Selesai
        </UButton>
      </div>
    </UPageCard>
  </UForm>
</template>
