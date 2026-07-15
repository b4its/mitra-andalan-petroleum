<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui";
import { addCustomerSchema, type AddCustomerState } from "~/types/schemas";

const open = ref(false);

const state = reactive<Partial<AddCustomerState>>({
  name: "",
  email: "",
});

const toast = useToast();
async function onSubmit(event: FormSubmitEvent<AddCustomerState>) {
  toast.add({
    title: "Success",
    description: `New customer ${event.data.name} added`,
    color: "success",
  });
  open.value = false;
}
</script>

<template>
  <UModal
    v-model:open="open"
    title="New customer"
    description="Add a new customer to the database"
  >
    <UButton label="New customer" icon="i-lucide-plus" />

    <template #body>
      <UForm
        :schema="addCustomerSchema"
        :state="state"
        class="space-y-4"
        @submit="onSubmit"
      >
        <UFormField label="Name" placeholder="John Doe" name="name">
          <UInput v-model="state.name" class="w-full" />
        </UFormField>
        <UFormField
          label="Email"
          placeholder="john.doe@example.com"
          name="email"
        >
          <UInput v-model="state.email" class="w-full" />
        </UFormField>
        <div class="flex justify-end gap-2">
          <UButton
            label="Cancel"
            color="neutral"
            variant="subtle"
            @click="open = false"
          />
          <UButton
            label="Create"
            color="primary"
            variant="solid"
            type="submit"
          />
        </div>
      </UForm>
    </template>
  </UModal>
</template>
