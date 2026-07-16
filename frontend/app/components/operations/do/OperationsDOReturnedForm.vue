<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui";
import { operationsDOSchema, type OperationsDOState } from "~/types/schemas";

const emit = defineEmits<{
  submit: [];
}>();

const state = defineModel<OperationsDOState>({ required: true });

function onSubmit(_event: FormSubmitEvent<OperationsDOState>) {
  emit("submit");
}

const value = ref<string>();

// todo: change to fetch offering letter data
const { data: users, execute } = await useLazyFetch(
  "https://jsonplaceholder.typicode.com/users",
  {
    key: "typicode-users-email",
    transform: (data: { id: number; name: string; email: string }[]) => {
      return data?.map((user) => ({
        label: user.name,
        email: user.email,
        value: String(user.id),
      }));
    },
    immediate: false,
  },
);

function onOpen() {
  if (!users.value?.length) {
    execute();
  }
}
</script>

<template>
  <UForm
    id="do-returned"
    :schema="operationsDOSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <UFormField name="doReturnedNumber" label="Nomor Surat DO" required>
        <USelect
          v-model="value"
          :items="users"
          placeholder="Pilih Surat DO"
          value-key="value"
          :ui="{ content: 'min-w-fit' }"
          class="w-full"
          @update:open="onOpen"
        >
          <template #item-label="{ item }">
            <!-- company name  -->
            {{ item.label }}

            <span class="text-muted text-xs">
              <!-- {{ item.email }} -->
              <!-- offering letter Id from fetch -->
              (722/MAP/II-06/26)
            </span>
          </template>
        </USelect>
      </UFormField>

      <UFormField
        name="doFile"
        label="File Delivery Order Yang Dikembalikan"
        required
      >
        <UFileUpload
          label="Upload File Delivery Order"
          description="Format file .pdf dengan max 5MB"
        />
      </UFormField>

      <div class="flex justify-end pt-4">
        <UButton type="submit" trailing-icon="i-lucide-arrow-right">
          Upload Surat DO
        </UButton>
      </div>
    </UPageCard>
  </UForm>
</template>
