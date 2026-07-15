<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui";
import {
  marketingPOCustomerSchema,
  type MarketingPOCustomerState,
} from "~/types/schemas";

const emit = defineEmits<{
  submit: [];
}>();

const state = defineModel<MarketingPOCustomerState>({ required: true });

function onSubmit(_event: FormSubmitEvent<MarketingPOCustomerState>) {
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
    id="letter-footer"
    :schema="marketingPOCustomerSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <UFormField name="offeringLetter" label="Nomor Surat Penawaran" required>
        <USelect
          v-model="value"
          :items="users"
          placeholder="Pilih Surat Penawaran"
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

      <UFormField name="poFile" label="File Purchase Order Customer" required>
        <UFileUpload
          label="Upload File Purchase Order"
          description="Format file .pdf dengan max 5MB"
        />
      </UFormField>

      <div class="flex justify-end pt-4">
        <UButton type="submit" trailing-icon="i-lucide-arrow-right">
          Upload PO Customer
        </UButton>
      </div>
    </UPageCard>
  </UForm>
</template>
